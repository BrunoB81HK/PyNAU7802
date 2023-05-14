""" Example6_AdvancedI2C.py
  Adapted from the SparkFun Qwiic Scale NAU7802 Arduino Library
  https://github.com/sparkfun/SparkFun_Qwiic_Scale_NAU7802_Arduino_Library

  Translated from the Example6_AdvancedI2C.ino example file
  https://github.com/sparkfun/SparkFun_Qwiic_Scale_NAU7802_Arduino_Library/tree/master/examples/Example6_AdvancedI2C
"""

from smbus2 import SMBus

from PyNAU7802 import NAU7802


def setup() -> None:
    print("Qwiic Scale Example")

    if not myScale.begin(bus):
        print("Scale not detected. Please check wiring. Freezing...")
        exit(1)

    print("Scale detected!")


def loop() -> None:
    if myScale.available():
        currentReading = myScale.getReading()
        print(f"Reading: {currentReading}")


if __name__ == "__main__":
    myScale = NAU7802()  # Create instance of the NAU7802 class
    bus = SMBus(1)
    # We can increase I2C clock speed to 400kHz, the NAU7802 supports it. This is set in the Raspberry Pi configs.
