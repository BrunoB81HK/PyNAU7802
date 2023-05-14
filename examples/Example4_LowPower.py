""" Example4_LowPower.py
  Adapted from the SparkFun Qwiic Scale NAU7802 Arduino Library
  https://github.com/sparkfun/SparkFun_Qwiic_Scale_NAU7802_Arduino_Library

  Translated from the Example4_LowPower.ino example file
  https://github.com/sparkfun/SparkFun_Qwiic_Scale_NAU7802_Arduino_Library/tree/master/examples/Example4_LowPower
"""

import time

from PyNAU7802 import NAU7802


def setup() -> None:
    print("Qwiic Scale Example")

    if not myScale.begin():
        print("Scale not detected. Please check wiring. Freezing...")
        exit(1)

    print("Scale detected!")


def loop() -> None:
    myScale.powerDown()  # Power down to ~200nA
    time.sleep(1)
    myScale.powerUp()  # Power up scale. This scale takes ~600ms to boot and take reading.

    startTime = time.process_time()
    while not myScale.available():
        pass

    currentReading = myScale.getReading()
    print(f"Startup time: {time.process_time() - startTime}, {currentReading}")


if __name__ == "__main__":
    myScale = NAU7802()  # Create instance of the NAU7802 class

    setup()

    while True:
        loop()
