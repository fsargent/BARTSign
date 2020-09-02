FROM balenalib/raspberry-pi-python:3.8.5-run

LABEL maintainer="Felix Sargent <felix.sargent@gmail.com>"

# Enable udevd so that plugged dynamic hardware devices show up in our container.
ENV UDEV=1

# Set our working directory
WORKDIR /usr/src/app
RUN install_packages git \
  dnsmasq \
  wireless-tools 

# Install resin-wifi-connect
RUN curl https://api.github.com/repos/balena-io/wifi-connect/releases/latest -s \
  | grep -hoP 'browser_download_url": "\K.*rpi\.tar\.gz' \
  | xargs -n1 curl -Ls \
  | tar -xvz -C /usr/src/app/
COPY . . 
RUN chmod +x /usr/src/app/start.sh
CMD /usr/src/app/start.sh
