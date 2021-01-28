from setuptools import setup

from usb import __version__

setup(
    entry_points={"console_scripts": ["usb = usb:program.run"]},
    name="usb",
    packages=["usb"],
    version=__version__,
)
