""" Example3_Gain_SampleRate.py
  Adapted from the SparkFun Qwiic Scale NAU7802 Arduino Library
  https://github.com/sparkfun/SparkFun_Qwiic_Scale_NAU7802_Arduino_Library

  Translated from the Example3_Gain_SampleRate.ino example file
  https://github.com/sparkfun/SparkFun_Qwiic_Scale_NAU7802_Arduino_Library/tree/master/examples/Example3_Gain_SampleRate
"""

from PyNAU7802 import NAU7802, NAU7802_GAIN_2, NAU7802_SPS_40


def setup() -> None:
    print("Qwiic Scale Example")

    if not myScale.begin():
        print("Scale not detected. Please check wiring. Freezing...")
        exit(1)

    print("Scale detected!")

    myScale.setGain(NAU7802_GAIN_2)  # Gain can be set to 1, 2, 4, 8, 16, 32, 64, or 128.
    myScale.setSampleRate(NAU7802_SPS_40)  # Sample rate can be set to 10, 20, 40, 80, or 320Hz
    myScale.calibrateAFE()  # Does an internal calibration. Recommended after power up, gain changes, sample rate changes, or channel changes.


def loop() -> None:
    if myScale.available():
        currentReading = myScale.getReading()
        print(f"Reading: {currentReading}")


if __name__ == "__main__":
    myScale = NAU7802()  # Create instance of the NAU7802 class

    setup()

    while True:
        loop()
