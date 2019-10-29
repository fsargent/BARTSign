#!/usr/bin/env python
from base import Base
from rgbmatrix import graphics
import time
import requests
import json
import inflect
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
p = inflect.engine()

load_dotenv()
API_KEY = os.getenv("API_KEY")

# https://github.com/fsargent/BARTSign
# https://github.com/hzeller/rpi-rgb-led-matrix
# https://uxdesign.cc/countdown-clocks-for-the-mta-79fa8013a0e7
# http://api.bart.gov/docs/etd/etd.aspx

class BARTSign(Base):
    def __init__(self, *args, **kwargs):
        super(BARTSign, self).__init__(*args, **kwargs)

    def run(self):
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.font_width = 5
        self.font_height = 7
        self.font = graphics.Font()
        self.font.LoadFont("./rpi-rgb-led-matrix/fonts/5x7.bdf")
        self.trains = self.getTrains()
        timer = time.time()

        while True:
            self.offscreen_canvas.Clear()
            self.printTrain(0, 0)
            # Second row will switch between the 2nd and 3rd trains every 5 seconds.
            self.printTrain(int(time.time() // 5 % 2) + 1, 1)

            # Get the new schedule every minute.
            if (timer + 60) < time.time():
                self.trains = self.getTrains()
                timer = time.time()

            self.offscreen_canvas = self.matrix.SwapOnVSync(
                self.offscreen_canvas)
            time.sleep(.25)

    def getTrains(self):
        schedule = requests.get(
            'http://api.bart.gov/api/etd.aspx?cmd=etd&orig=19th&json=y&plat=2&key='+API_KEY).json()
        logging.debug(schedule)
        trains = []
        destinations = schedule["root"]["station"][0]["etd"]
        for destination in destinations:
            for train in destination["estimate"]:
                train["destination"] = destination["destination"]
                if train["minutes"] == "Leaving":
                    train["minutes"] = "0"
                train["minutes"] = train["minutes"]
                trains.append(train)

        trains = sorted(trains, key=lambda i: int(i['minutes']))

        for train in trains:
            logging.info(train)

        if trains[0]["minutes"] == "0":
            trains[0]["minutes"] = "Now"

        return trains

    def printTrain(self, ref, position):
        if isinstance(self.trains[ref]["color"], str):
            self.trains[ref]["color"] = graphics.Color(
                *(tuple(int(self.trains[ref]["hexcolor"].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))))

        destination_x = 0
        destination_y = self.font_height + (position*(self.font_height+1))

        # Render train position
        graphics.DrawText(self.offscreen_canvas,
                          self.font,
                          destination_x,
                          destination_y,
                          graphics.Color(225, 225, 225),
                          p.ordinal(ref+1))

        # Render train destination, flash if now.
        if self.trains[ref]["minutes"] != "Now":
            graphics.DrawText(self.offscreen_canvas,
                              self.font,
                              destination_x +
                              len(p.ordinal(ref+1))*self.font_width,
                              destination_y,
                              self.trains[ref]["color"],
                              self.trains[ref]["destination"])
        else:
            if int(time.time() // .5 % 2) == 1:
                graphics.DrawText(self.offscreen_canvas,
                                  self.font,
                                  destination_x +
                                  len(p.ordinal(ref+1))*self.font_width,
                                  destination_y,
                                  self.trains[ref]["color"],
                                  self.trains[ref]["destination"])

        # Render arrival time
        times_x = self.offscreen_canvas.width - \
            (len(self.trains[ref]["minutes"]) * self.font_width)
        times_y = self.font_height + (position*(self.font_height+1))

        if self.trains[ref]["delay"] == "0":
            self.trains[ref]["minutes_color"] = graphics.Color(0, 255, 0)
            graphics.DrawText(self.offscreen_canvas,
                              self.font,
                              times_x,
                              times_y,
                              self.trains[ref]["minutes_color"],
                              str(self.trains[ref]["minutes"]))
        else:
            self.trains[ref]["minutes_color"] = graphics.Color(255, 0, 0)
            delay = self.trains[ref]["minutes"] + "d" + \
                str(round(int(self.trains[ref]["delay"])/60))
            times_x = self.offscreen_canvas.width - \
                (len(delay) * self.font_width)
            times_y = self.font_height + (position*(self.font_height+1))
            graphics.DrawText(self.offscreen_canvas,
                              self.font,
                              times_x,
                              times_y,
                              self.trains[ref]["minutes_color"],
                              delay)


# Main function
if __name__ == "__main__":
    bart_sign = BARTSign()
    if (not bart_sign.process()):
        bart_sign.print_help()
