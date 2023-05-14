""" Example2_CompleteScale.py
  Adapted from the SparkFun Qwiic Scale NAU7802 Arduino Library
  https:# github.com/sparkfun/SparkFun_Qwiic_Scale_NAU7802_Arduino_Library

  Translated from the Example2_CompleteScale.ino example file
  https:# github.com/sparkfun/SparkFun_Qwiic_Scale_NAU7802_Arduino_Library/tree/master/examples/Example2_CompleteScale
"""

from PyNAU7802 import NAU7802, NAU7802_SPS_320
import pathlib
import json  # Needed to record user settings (replacing the Arduino's EEPROM)


class AverageWeights:

    def __init__(self, size: int) -> None:
        self.size = size
        self.weights = [0]*self.size
        self.current_spot = 0

    def add(self, weight: int | float) -> int | float:
        self.weights[self.current_spot] = weight
        self.current_spot += 1
        if self.current_spot == self.size:
            self.current_spot = 0
        return sum([w/self.size for w in self.weights])


def calibrateScale() -> None:
    print(f"\n\nScale calibration")

    input("Setup scale with no weight on it. Press a key when ready.")

    myScale.calculateZeroOffset(64)  # Zero or Tare the scale. Average over 64 readings.
    print(f"New zero offset: {myScale.getZeroOffset()}")

    input("Place known weight on scale. Press a key when weight is in place and stable.")

    def isfloat(num: str) -> bool:
        try:
            float(num)
            return True
        except ValueError:
            return False

    x = ""

    while not isfloat(x):
        x = input("Please enter the weight, without units, currently sitting on the scale (for example '4.25'): ")

    myScale.calculateCalibrationFactor(float(x), 64)  # Tell the library how much weight is currently on it

    print(f"\nNew cal factor: {myScale.getCalibrationFactor():0.2f}")
    print(f"New Scale Reading: {myScale.getWeight():0.2f}")

    recordSystemSettings()  # Commit these values to EEPROM


# Record the current system settings to EEPROM
def recordSystemSettings() -> None:
    # Get various values from the library and commit them to NVM
    global user_settings
    user_settings["CALIBRATION_FACTOR"] = myScale.getCalibrationFactor()
    user_settings["ZERO_OFFSET"] = myScale.getZeroOffset()

    with open(setting_filepath, 'w') as file:
        json.dump(user_settings, file)


# Reads the current system settings from EEPROM
# If anything looks weird, reset setting to default value
def readSystemSettings() -> None:
    global user_settings, settingsDetected

    if setting_filepath.exists():
        with open(setting_filepath, 'r') as file:
            user_settings = json.load(file)

    if "CALIBRATION_FACTOR" not in user_settings:
        user_settings["CALIBRATION_FACTOR"] = 0.0  # Default to 0.0
    if "ZERO_OFFSET" not in user_settings:
        user_settings["ZERO_OFFSET"] = 1000  # Default to 1000

    # Pass these values to the library
    myScale.setCalibrationFactor(user_settings["CALIBRATION_FACTOR"])
    myScale.setZeroOffset(user_settings["ZERO_OFFSET"])

    settingsDetected = True  # Assume for the moment that there are good cal values
    if user_settings["CALIBRATION_FACTOR"] < 0.1 or user_settings["ZERO_OFFSET"] == 1000:
        settingsDetected = False  # Defaults detected. Prompt user to cal scale.


def setup() -> None:
    print("Qwiic Scale Example")

    if not myScale.begin():
        print("Scale not detected. Please check wiring. Freezing...")
    exit(1)

    print("Scale detected!")

    readSystemSettings()  # Load zeroOffset and calibrationFactor from EEPROM
    myScale.setSampleRate(NAU7802_SPS_320)  # Increase to max sample rate
    myScale.calibrateAFE()  # Re-cal analog front end when we change gain, sample rate, or channel

    print(f"Zero offset: {myScale.getZeroOffset()}")
    print(f"Calibration factor: {myScale.getCalibrationFactor()}")


def loop() -> None:
    if myScale.available():
        currentReading = myScale.getReading()
        currentWeight = myScale.getWeight()
        avgWeight = avgWeights.add(currentWeight)

        print(f"Reading: {currentReading}"
              f"\tWeight: {currentWeight:0.2f}"
              f"\tAvgWeight: {avgWeight:0.2f}"
              f"\t{'Scale not calibrated!' if not settingsDetected else ''}")


if __name__ == "__main__":
    myScale = NAU7802()  # Create instance of the NAU7802 class

    # Dictionary to store user settings
    setting_filepath = pathlib.Path(__file__).parent.joinpath("settings.json")
    user_settings = {
        "CALIBRATION_FACTOR": 0.0,
        "ZERO_OFFSET": 1000
    }

    settingsDetected = False  # Used to prompt user to calibrate their scale

    # Create an array to take average of weights. This helps smooth out jitter.
    avgWeights = AverageWeights(4)

    setup()

    while True:
        loop()
