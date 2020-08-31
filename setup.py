import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='PyNAU7802',
    version='0.1',
    author='Bruno-Pier Busque',
    author_email='bruno-pier.busque@usherbrooke.ca',
    description="Python port of the SparkFun Qwiic Scale NAU7802 Arduino Library",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/BrunoB81HK/PyNAU7802.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=["smbus2>=0.3"]
)
