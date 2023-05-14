import time

import smbus2

from .constants import *

###########################################
# Classes
###########################################
class NAU7802:
    """ Class to communicate with the NAU7802 """
    _i2cPort: smbus2.SMBus = None
    _zeroOffset: int = 0
    _calibrationFactor: float = 1.0

    def begin(self, wire_port: smbus2.SMBus = smbus2.SMBus(1), initialize: bool = True) -> bool:
        """ Check communication and initialize sensor """
        # Get user's options
        self._i2cPort = wire_port

        # Check if the device ACK's over I2C
        if not self.isConnected():
            # There are rare times when the sensor is occupied and doesn't ACK. A 2nd try resolves this.
            if not self.isConnected():
                return False

        result = True  # Accumulate a result as we do the setup

        if initialize:
            result &= self.reset()  # Reset all registers
            result &= self.powerUp()  # Power on analog and digital sections of the scale
            result &= self.setLDO(NAU7802_LDO_3V3)  # Set LDO to 3.3V
            result &= self.setGain(NAU7802_GAIN_128)  # Set gain to 128
            result &= self.setSampleRate(NAU7802_SPS_80)  # Set samples per second to 10
            result &= self.setRegister(NAU7802_ADC, 0x30)  # Turn off CLK_CHP. From 9.1 power on sequencing.
            result &= self.setBit(NAU7802_PGA_PWR_PGA_CAP_EN, NAU7802_PGA_PWR)  # Enable 330pF decoupling cap on ch. 2.
            # From 9.14 application circuit note.
            result &= self.calibrateAFE()  # Re - cal analog frontend when we change gain, sample rate, or channel

        return result

    def isConnected(self) -> bool:
        """ Returns true if device ACK's at the I2C address """
        try:
            self._i2cPort.read_byte(DEVICE_ADDRESS)
            return True  # All good
        except OSError:
            return False  # Sensor did not ACK

    def available(self) -> bool:
        """ Returns true if Cycle Ready bit is set (conversion is complete) """
        return self.getBit(NAU7802_PU_CTRL_CR, NAU7802_PU_CTRL)

    def getReading(self) -> int:
        """ Returns 24 bit reading. Assumes CR Cycle Ready bit
        (ADC conversion complete) has been checked by .available() """
        try:
            value_list = self._i2cPort.read_i2c_block_data(DEVICE_ADDRESS, NAU7802_ADCO_B2, 3)
        except OSError:
            return False  # Sensor did not ACK

        value = int.from_bytes(value_list, byteorder='big', signed=True)

        return value

    def getAverage(self, average_amount: int) -> int:
        """ Return the average of a given number of readings """
        total = 0
        samples_acquired = 0

        start_time = time.time()

        while samples_acquired < average_amount:
            if self.available():
                total += self.getReading()
                samples_acquired += 1

            if time.time() - start_time > 1.0:
                return 0  # Timeout - Bail with error

            time.sleep(0.001)

        total /= average_amount

        return total

    def calculateZeroOffset(self, average_amount: int = 8) -> None:
        """ Also called taring. Call this with nothing on the scale """
        self.setZeroOffset(self.getAverage(average_amount))

    def setZeroOffset(self, new_zero_offset: int) -> None:
        """ Sets the internal variable. Useful for users who are loading values from NVM. """
        self._zeroOffset = new_zero_offset

    def getZeroOffset(self) -> int:
        """ Ask library for this value.Useful for storing value into NVM. """
        return self._zeroOffset

    def calculateCalibrationFactor(self, weight_on_scale: float, average_amount: int = 8) -> None:
        """ Call this with the value of the thing on the scale.
        Sets the calibration factor based on the weight on scale and zero offset. """
        onScale = self.getAverage(average_amount)
        newCalFactor = (onScale - self._zeroOffset)/weight_on_scale
        self.setCalibrationFactor(newCalFactor)

    def setCalibrationFactor(self, new_cal_factor: float) -> None:
        """ Pass a known calibration factor into library.Helpful if users is loading settings from NVM. """
        self._calibrationFactor = new_cal_factor

    def getCalibrationFactor(self) -> float:
        """ Ask library for this value.Useful for storing value into NVM. """
        return self._calibrationFactor

    def getWeight(self, allow_negative_weights: bool = True, samples_to_take: int = 8) -> float:
        """ Once you 've set zero offset and cal factor, you can ask the library to do the calculations for you. """
        on_scale = self.getAverage(samples_to_take)

        # Prevent the current reading from being less than zero offset. This happens when the scale
        # is zero'd, unloaded, and the load cell reports a value slightly less than zero value
        # causing the weight to be negative or jump to millions of pounds

        if not allow_negative_weights:
            if on_scale < self._zeroOffset:
                on_scale = self._zeroOffset  # Force reading to zero

        weight = (on_scale - self._zeroOffset)/self._calibrationFactor
        return weight

    def setGain(self, gain_value: int) -> bool:
        """ Set the gain.x1, 2, 4, 8, 16, 32, 64, 128 are available """
        if gain_value > 0b111:
            gain_value = 0b111  # Error check

        value = self.getRegister(NAU7802_CTRL1)
        value &= 0b11111000  # Clear gain bits
        value |= gain_value  # Mask in new bits

        return self.setRegister(NAU7802_CTRL1, value)

    def setLDO(self, ldo_value: int) -> bool:
        """ Set the on board Low - Drop - Out voltage regulator to a given value.
        2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.2, 4.5 V are available """
        if ldo_value > 0b111:
            ldo_value = 0b111  # Error check

        # Set the value of the LDO
        value = self.getRegister(NAU7802_CTRL1)
        value &= 0b11000111  # Clear LDO bits
        value |= ldo_value << 3  # Mask in new LDO bits
        self.setRegister(NAU7802_CTRL1, value)

        return self.setBit(NAU7802_PU_CTRL_AVDDS, NAU7802_PU_CTRL)  # Enable the internal LDO

    def setSampleRate(self, rate: int) -> bool:
        """ Set the readings per second. 10, 20, 40, 80, and 320 samples per second is available """
        if rate > 0b111:
            rate = 0b111  # Error check

        value = self.getRegister(NAU7802_CTRL2)
        value &= 0b10001111  # Clear CRS bits
        value |= rate << 4  # Mask in new CRS bits

        return self.setRegister(NAU7802_CTRL2, value)

    def setChannel(self, channel_number: int) -> bool:
        """ Select between 1 and 2 """
        if channel_number == NAU7802_CHANNEL_1:
            return self.clearBit(NAU7802_CTRL2_CHS, NAU7802_CTRL2)  # Channel 1 (default)
        else:
            return self.setBit(NAU7802_CTRL2_CHS, NAU7802_CTRL2)  # Channel 2

    def calibrateAFE(self) -> bool:
        """ Synchronous calibration of the analog front end of the NAU7802.
        Returns true if CAL_ERR bit is 0 (no error) """
        self.beginCalibrateAFE()
        return self.waitForCalibrateAFE(1000)

    def beginCalibrateAFE(self) -> None:
        """ Begin asynchronous calibration of the analog front end of the NAU7802.
        Poll for completion with calAFEStatus() or wait with waitForCalibrateAFE(). """
        self.setBit(NAU7802_CTRL2_CALS, NAU7802_CTRL2)

    def waitForCalibrateAFE(self, timeout_ms: int = 0) -> bool:
        """ Wait for asynchronous AFE calibration to complete with optional timeout. """
        timeout_s = timeout_ms/1000
        begin = time.time()
        cal_ready = self.calAFEStatus()

        while cal_ready == NAU7802_CAL_IN_PROGRESS:
            if (timeout_ms > 0) & ((time.time() - begin) > timeout_s):
                break
            time.sleep(0.001)
            cal_ready = self.calAFEStatus()

        if cal_ready == NAU7802_CAL_SUCCESS:
            return True
        else:
            return False

    def calAFEStatus(self) -> int:
        """ Check calibration status. """
        if self.getBit(NAU7802_CTRL2_CALS, NAU7802_CTRL2):
            return NAU7802_CAL_IN_PROGRESS

        if self.getBit(NAU7802_CTRL2_CAL_ERROR, NAU7802_CTRL2):
            return NAU7802_CAL_FAILURE

        # Calibration passed
        return NAU7802_CAL_SUCCESS

    def reset(self) -> bool:
        """ Resets all registers to Power Of Defaults """
        self.setBit(NAU7802_PU_CTRL_RR, NAU7802_PU_CTRL)  # Set RR
        time.sleep(0.001)
        return self.clearBit(NAU7802_PU_CTRL_RR, NAU7802_PU_CTRL)  # Clear RR to leave reset state

    def powerUp(self) -> bool:
        """ Power up digital and analog sections of scale, ~2 mA """
        self.setBit(NAU7802_PU_CTRL_PUD, NAU7802_PU_CTRL)
        self.setBit(NAU7802_PU_CTRL_PUA, NAU7802_PU_CTRL)

        # Wait for Power Up bit to be set - takes approximately 200us
        counter = 0
        while not self.getBit(NAU7802_PU_CTRL_PUR, NAU7802_PU_CTRL):
            time.sleep(0.001)
            if counter > 100:
                return False  # Error
            counter += 1

        return True

    def powerDown(self) -> bool:
        """ Puts scale into low - power 200 nA mode """
        self.clearBit(NAU7802_PU_CTRL_PUD, NAU7802_PU_CTRL)
        return self.clearBit(NAU7802_PU_CTRL_PUA, NAU7802_PU_CTRL)

    def setIntPolarityHigh(self) -> bool:
        """ Set Int pin to be high when data is ready(default) """
        return self.clearBit(NAU7802_CTRL1_CRP, NAU7802_CTRL1)  # 0 = CRDY pin is high active (ready when 1)

    def setIntPolarityLow(self) -> bool:
        """ Set Int pin to be low when data is ready """
        return self.setBit(NAU7802_CTRL1_CRP, NAU7802_CTRL1)  # 1 = CRDY pin is low active (ready when 0)

    def getRevisionCode(self) -> int:
        """ Get the revision code of this IC.Always 0x0F. """
        revisionCode = self.getRegister(NAU7802_DEVICE_REV)
        return revisionCode & 0x0F

    def setBit(self, bit_number: int, register_address: int) -> bool:
        """ Mask & set a given bit within a register """
        value = self.getRegister(register_address)
        value |= (1 << bit_number)  # Set this bit
        return self.setRegister(register_address, value)

    def clearBit(self, bit_number: int, register_address: int) -> bool:
        """ Mask & clear a given bit within a register """
        value = self.getRegister(register_address)
        value &= ~(1 << bit_number)  # Set this bit
        return self.setRegister(register_address, value)

    def getBit(self, bit_number: int, register_address: int) -> bool:
        """ Return a given bit within a register """
        value = self.getRegister(register_address)
        value &= (1 << bit_number)  # Clear all but this bit
        return bool(value)

    def getRegister(self, register_address: int) -> int:
        """ Get contents of a register """
        try:
            return self._i2cPort.read_byte_data(DEVICE_ADDRESS, register_address)

        except OSError:
            return -1  # Sensor did not ACK

    def setRegister(self, register_address: int, value: int) -> bool:
        """ Send a given value to be written to given address.Return true if successful """
        try:
            self._i2cPort.write_byte_data(DEVICE_ADDRESS, register_address, value)
            return True

        except OSError:
            return False
