from pprint import pformat
import os
from dotenv import load_dotenv
from base import Base
from rgbmatrix import graphics
import time
import requests
import json
import logging
import inflect
LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(format='%(asctime)s %(message)s', level=LOGLEVEL)
p = inflect.engine()

load_dotenv()

API_KEY = os.getenv("API_KEY")

# Inspiration and resources:
# https://uxdesign.cc/countdown-clocks-for-the-mta-79fa8013a0e7
# http://api.bart.gov/docs/etd/etd.aspx


class BARTSign(Base):
    def __init__(self, *args, **kwargs):
        super(BARTSign, self).__init__(*args, **kwargs)

    def run(self):
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        self.trains = self.getTrains()
        self.refresh_rate = 0.1  # This controls scrolling speed.
        self.scroller = 0
        self.font = graphics.Font()
        self.font.LoadFont("./rpi-rgb-led-matrix/fonts/5x7.bdf")
        timer = time.time()
        bart_api_update_seconds = 30
        second_row_train_index = 1
        counter = 0

        while True:
            self.offscreen_canvas.Clear()
            if type(self.trains) != Exception:
                self.printTrain(0, 0)
                self.printTrain(second_row_train_index, 1)
            else:
                self.drawError()

            # Get the new schedule every minute.
            if (timer + bart_api_update_seconds) < time.time():
                self.trains = self.getTrains()
                timer = time.time()

            self.offscreen_canvas = self.matrix.SwapOnVSync(
                self.offscreen_canvas)

            # Change the second row every number of seconds.
            counter = counter % (int(os.environ.get(
                'SECOND_ROW_SECONDS', 1))/self.refresh_rate)
            if counter == 0:
                second_row_train_index = 1 + \
                    (second_row_train_index %
                     min(int(os.environ.get('SECOND_ROW_TRAINS', 4)),
                         len(self.trains)))
                # Ensure the index can't be out of range of the number of trains we have.
                logging.debug("%s: %s train in %s minutes",
                              p.ordinal(1),
                              self.trains[0]["destination"],
                              str(self.trains[0]["minutes"])
                              )
                logging.debug("%s: %s train in %s minutes",
                              p.ordinal(second_row_train_index+1),
                              self.trains[second_row_train_index]["destination"],
                              str(self.trains[second_row_train_index]
                                  ["minutes"])
                              )
            counter += 1

            time.sleep(self.refresh_rate)

    def drawError(self):
        self.refresh_rate = 0.01
        font_height = 7
        len = graphics.DrawText(self.offscreen_canvas,
                                self.font,
                                self.scroller,
                                font_height,
                                graphics.Color(225, 0, 0),
                                f"Error: {self.trains.args[0]}")
        self.scroller -= 1
        if (self.scroller + len < -len):
            self.scroller = 0

    def getTrains(self):
        """
        Get trains from BART API and return a list of them.
        """
        try:
            bartURL = f'http://api.bart.gov/api/etd.aspx?cmd=etd&orig={self.args.station}&json=y&key={API_KEY}'
            if self.args.platform:
                bartURL = f'http://api.bart.gov/api/etd.aspx?cmd=etd&orig={self.args.station}&json=y&plat={self.args.platform}&key={API_KEY}'
            bart_response = requests.get(bartURL)
            logging.debug(pformat(bart_response.text))
            logging.debug(pformat(bart_response.text))
            if bart_response.status_code != 200:
                raise Exception("Couldn't connect to BART.",
                                str(bart_response.status_code))
            if "xml" in bart_response.headers['content-type']:
                raise Exception(bart_response.text.split("details")[1], "400")
            schedule = json.loads(bart_response.text)
            if hasattr("warning", schedule["root"]["message"]):
                raise Exception(schedule["root"]["message"]["warning"], "400")
            trains = []

            # Turn the format into an array of trains
            destinations = schedule["root"]["station"][0]["etd"]
            for destination in destinations:
                for train in destination["estimate"]:
                    train["destination"] = destination["destination"]
                    if train["minutes"] == "Leaving":
                        train["minutes"] = "0"
                    train["minutes"] = train["minutes"]

                    trains.append(train)

            trains = sorted(trains, key=lambda i: int(i['minutes']))

            logging.info(pformat(trains))

            if trains[0]["minutes"] == "0":
                trains[0]["minutes"] = "Now"

            return trains
        except (Exception) as e:
            logging.error(e.args)
            return e

    def printTrain(self, ref, position):
        """
        This is where we write out to the sign.
        """
        font_width = 5
        font_height = 7
        try:
            if isinstance(self.trains[ref]["color"], str):
                # Color the destinations the same color as the line.
                self.trains[ref]["color"] = graphics.Color(
                    *(tuple(int(self.trains[ref]["hexcolor"].lstrip('#')[i:i+2], 16) for i in (0, 2, 4))))

            # destination positioning.
            destination_x = 0
            destination_y = font_height + (position*(font_height+1))

            # arrival time positioning
            times_x = self.offscreen_canvas.width - \
                (len(self.trains[ref]["minutes"]) * font_width)
            times_y = font_height + (position*(font_height+1))

            self.trains[ref]["minutes_color"] = graphics.Color(0, 255, 0)

            # Render train position (ie 1st, 2nd, 3rd)
            graphics.DrawText(self.offscreen_canvas,
                              self.font,
                              destination_x,
                              destination_y,
                              graphics.Color(225, 225, 225),
                              p.ordinal(ref+1))
            # Render self.trains[ref] destination

            if self.trains[ref]["minutes"] != "Now":
                graphics.DrawText(self.offscreen_canvas,
                                  self.font,
                                  destination_x +
                                  len(p.ordinal(ref+1))*font_width,
                                  destination_y,
                                  self.trains[ref]["color"],
                                  self.trains[ref]["destination"])

            else:
                # Flash a train that's arriving now.
                if int(time.time() // .5 % 2) == 1:
                    graphics.DrawText(self.offscreen_canvas,
                                      self.font,
                                      destination_x +
                                      len(p.ordinal(ref+1))*font_width,
                                      destination_y,
                                      self.trains[ref]["color"],
                                      self.trains[ref]["destination"])

            # arrival time
            graphics.DrawText(self.offscreen_canvas,
                              self.font,
                              times_x,
                              times_y,
                              self.trains[ref]["minutes_color"],
                              str(self.trains[ref]["minutes"]))

        except IndexError:
            pass


# Main function
if __name__ == "__main__":
    bart_sign = BARTSign()
    if (not bart_sign.process()):
        bart_sign.print_help()
