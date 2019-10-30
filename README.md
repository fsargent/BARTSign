# BARTSign
Use Raspberry Pi to power a RBG Matrix Display to show BART Arrival times.

![image](i.imgur.com/iaVmHZhb.jpg)

Uses:
- 3x $25 [Medium 16x32 RGB LED matrix panel](https://www.adafruit.com/product/420)
- 1x $25 [5V 10A switching power supply](https://www.adafruit.com/product/658)
- 1x $35 [Raspberry Pi 3 - Model B+](https://www.adafruit.com/product/3775)


## Installation

```bash
sudo apt-get update && sudo apt-get install git python3-dev python3-pillow libtiff-dev  zlib1g-dev libfreetype6-dev liblcms1-dev libwebp-dev tcl8.5-dev tk8.5-dev -y
pip install --user pipenv
git clone git@github.com:fsargent/BARTSign.git
git submodule init
git submodule update
pipenv install
pipenv shell
# Setup https://github.com/hzeller/rpi-rgb-led-matrix/tree/master/bindings/python
sudo pipenv run make -C ./rpi-rgb-led-matrix/bindings/python build-python PYTHON=$(which python3)
sudo pipenv install '-e ./rpi-rgb-led-matrix/bindings/python' # runs setup.py install for pipenv
sudo pipenv run python3 bart.py
```
