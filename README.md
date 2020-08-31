# PyNAU7802
Python port of the [SparkFun Qwiic Scale NAU7802 Arduino Library](https://github.com/sparkfun/SparkFun_Qwiic_Scale_NAU7802_Arduino_Library)

## Install

To install, simply use : `pip install PyNAU7802` in a terminal window

## How to use

The function name and arguments are the exact same as the original library, use it's 
[documentation](https://github.com/sparkfun/SparkFun_Qwiic_Scale_NAU7802_Arduino_Library)
to get started.

## Example

This package use smbus2 as the I2C bus. Here is a small working example :

```python
import PyNAU7802
import smbus2

# Create the bus
bus = smbus2.SMBus(1)

# Create the scale and initialize it
scale = PyNAU7802.NAU7802()
if scale.begin(bus):
    print("Connected!\n")
else:
    print("Can't find the scale, exiting ...\n")
    exit()

# Calculate the zero offset
print("Calculating the zero offset...")
scale.calculateZeroOffset()
print("The zero offset is : {0}\n".format(scale.getZeroOffset()))

print("Put a known mass on the scale.")
cal = float(input("Mass in kg? "))

# Calculate the calibration factor
print("Calculating the calibration factor...")
scale.calculateCalibrationFactor(cal)
print("The calibration factor is : {0:0.3f}\n".format(scale.getCalibrationFactor()))

input("Press [Enter] to measure a mass. ")
print("Mass is {0:0.3f} kg".format(scale.getWeight()))
```