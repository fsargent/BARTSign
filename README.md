# BARTSign

Use Raspberry Pi to power a RBG Matrix Display to show BART Arrival times.

![image](https://i.imgur.com/iaVmHZhb.jpg)

See the movie: https://imgur.com/gallery/my5vVdl

## Buy The Parts

- 3x \$25 [Medium 16x32 RGB LED matrix panel](https://www.adafruit.com/product/420)
- 1x \$25 [5V 10A switching power supply](https://www.adafruit.com/product/658)
- 1x \$35 [Raspberry Pi 3 - Model B+](https://www.adafruit.com/product/3775)

## Wire the Boards  

Follow [these instructions by the maker](https://github.com/hzeller/rpi-rgb-led-matrix/blob/master/wiring.md) of the RaspberryPi RGB Matrix Library.
I've edited the defaults of base.py to assume you're using 3x 16x32 boards. Inspect base.py to change these defaults, or via flags. It's predictable.

## Setup the Code

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
```

## Get a BART API key

 Get a BART API key from http://api.bart.gov/docs/overview/index.aspx

```bash
# Run it!
echo "API_KEY=XXX-XXX-XXX" > .env
sudo pipenv run python3 bart.py
```

```bash
$ sudo pipenv run python3 bart.py -h
optional arguments:
  -h, --help            show this help message and exit
  -s STATION, --station STATION
                        Display BART station. See http://api.bart.gov/docs/overview/abbrev.aspx.
                        Default: 19th
  -p PLATFORM, --platform PLATFORM
                        Which platform? Optional 1-4
```
