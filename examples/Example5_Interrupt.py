""" Example5_Interrupt.py
  Adapted from the SparkFun Qwiic Scale NAU7802 Arduino Library
  https://github.com/sparkfun/SparkFun_Qwiic_Scale_NAU7802_Arduino_Library

  Translated from the Example5_Interrupt.ino example file
  https://github.com/sparkfun/SparkFun_Qwiic_Scale_NAU7802_Arduino_Library/tree/master/examples/Example5_Interrupt
"""

import RPi.GPIO as GPIO

from PyNAU7802 import NAU7802


def setup() -> None:
    print("Qwiic Scale Example")

    if not myScale.begin():
        print("Scale not detected. Please check wiring. Freezing...")
        exit(1)

    print("Scale detected!")

    # myScale.setIntPolarityHigh()  # Set Int pin to be high when data is ready (default)
    myScale.setIntPolarityLow()  # Set Int pin to be low when data is ready

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(interruptPin, GPIO.IN)


# Loop
def loop() -> None:
    if GPIO.input(interruptPin) == GPIO.LOW:
        currentReading = myScale.getReading()
        print(f"Reading: {currentReading}")




if __name__ == "__main__":
    myScale = NAU7802()  # Create instance of the NAU7802 class
    interruptPin = 2  # Tied to the INT pin on Qwiic Scale. Can be any pin.

    setup()

    while True:
        loop()
