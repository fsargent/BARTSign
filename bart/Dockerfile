# base-image for python on any machine using a template variable,
# see more about dockerfile templates here: https://www.balena.io/docs/learn/develop/dockerfile/
FROM balenalib/raspberry-pi-python:3.7-build AS build

# use `install_packages` if you need to install dependencies,
# for instance if you need git, just uncomment the line below.
# RUN install_packages git

ENV PYROOT /pyroot
ENV PYTHONUSERBASE $PYROOT

# Set our working directory
WORKDIR /usr/src/app
RUN install_packages git \
  libtiff-dev \
  zlib1g-dev \
  libfreetype6-dev \
  liblcms1-dev \
  libwebp-dev \
  tcl8.5-dev \
  tk8.5-dev
RUN git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
RUN make -C ./rpi-rgb-led-matrix/bindings/python build-python PYTHON=$(which python3)
RUN pip install --upgrade pip
RUN pip install pipenv

COPY Pipfile* ./

RUN PIP_USER=1 PIPENV_NOSPIN=1 pipenv install '-e ./rpi-rgb-led-matrix/bindings/python' 
# RUN PIP_USER=1 PIP_IGNORE_INSTALLED=1 pipenv install --system --deploy --ignore-pipfile
COPY . ./

# FROM balenalib/raspberry-pi-python:latest
# COPY --from=builder $PYROOT/lib/ $PYROOT/lib/

# Enable udevd so that plugged dynamic hardware devices show up in our container.
ENV UDEV=1

# Run it!
ENTRYPOINT pipenv run python bart.py