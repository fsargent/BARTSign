# base-image for python on any machine using a template variable,
# see more about dockerfile templates here: https://www.balena.io/docs/learn/develop/dockerfile/
FROM balenalib/raspberry-pi-python:latest-buster-build

# use `install_packages` if you need to install dependencies,
# for instance if you need git, just uncomment the line below.
# RUN install_packages git

# Set our working directory
WORKDIR /usr/src/app
RUN install_packages git \
  python3-dev \
  python3-pip \
  python3-pillow \
  libtiff-dev \
  zlib1g-dev \
  libfreetype6-dev \
  liblcms1-dev \
  libwebp-dev \
  tcl8.5-dev \
  tk8.5-dev && \
  pip3 install pipenv
RUN git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
RUN make -C ./rpi-rgb-led-matrix/bindings/python build-python PYTHON=$(which python3)

COPY Pipfile* ./
RUN pipenv install '-e ./rpi-rgb-led-matrix/bindings/python'
COPY . ./

# Enable udevd so that plugged dynamic hardware devices show up in our container.
ENV UDEV=1

# Run it!
ENTRYPOINT pipenv run python bart.py