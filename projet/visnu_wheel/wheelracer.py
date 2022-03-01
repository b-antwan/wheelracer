import cv2
import math
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import sys
import os
from typing import List, Tuple
import threading
import time
import uinput
from matplotlib.backends.backend_agg import FigureCanvasAgg
# os.environ["KIVY_NO_CONSOLELOG"] = "1"

import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.properties import NumericProperty
from threading import Thread
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.config import Config

# Snippet gamepad:
class Gamepad:
    def __init__(
        self, x_min: int = -100, x_max: int = 100, y_min: int = -100, y_max: int = 100
    ):
        self.events = (
            uinput.ABS_X + (x_min, x_max, 0, 0),
            uinput.ABS_Y + (y_min, y_max, 0, 0),
        )
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.x_val = 0
        self.y_val = 0

    def pt(self):
        with uinput.Device(self.events) as device:
            while True:
                device.emit(uinput.ABS_X, int(self.x_val))
                device.emit(uinput.ABS_Y, int(self.y_val))
                time.sleep(0.1)

    def start(self):
        self.t = threading.Thread(target=self.pt)
        self.t.start()

    def stop(self):
        self.t.join()



Config.set("graphics", "width", "800")
Config.set("graphics", "height", "1600")

angles = []
preset = [20, 110, 40, 125, 255, 255, 130, 110, 110, 220, 215, 255]


def create_widgets() -> Tuple[List, List]:
    txt = ["hue_min", "sat_min", "val_min", "hue_max", "sat_max", "val_max"]
    labels = []
    sliders = []
    for i in range(12):
        s = Slider(min=0, max=255, value=preset[i])
        l = Label(text=txt[i % 6], padding=(0, 0))

        labels.append(l)
        sliders.append(s)

    return labels, sliders


class MyApp(App):
    def build(self) -> GridLayout:
        self.img = Image()
        self.left = Image()
        self.right = Image()
        self.both = Image()

        self.layout = GridLayout(cols=2, padding=(50, 50))

        self.labels, self.slider = create_widgets()

        first_sliderbox = BoxLayout(orientation="vertical")
        second_sliderbox = BoxLayout(orientation="vertical")

        first_sliderbox.add_widget(Label())
        for i in range(6):
            first_sliderbox.add_widget(self.labels[i])
            first_sliderbox.add_widget(self.slider[i])
        first_sliderbox.add_widget(Label())

        second_sliderbox.add_widget(Label())
        for i in range(6):
            second_sliderbox.add_widget(self.labels[i + 6])
            second_sliderbox.add_widget(self.slider[i + 6])
        second_sliderbox.add_widget(Label())
        self.angle = 0
        self.layout.add_widget(self.img)
        self.layout.add_widget(self.both)
        self.layout.add_widget(self.left)
        self.layout.add_widget(first_sliderbox)
        self.layout.add_widget(self.right)
        self.layout.add_widget(second_sliderbox)
        self.angleLabel = Label(text="Angle: 0")
        self.layout.add_widget(self.angleLabel)

        if len(sys.argv) > 1:
            self.vid = cv2.VideoCapture(sys.argv[1])
        else:
            self.vid = cv2.VideoCapture(0)
 
        # 30 fps
        self.event = Clock.schedule_interval(self.update, 1 / 30)

        self.pad = Gamepad()
        self.pad.start()
        return self.layout

    def update(self, dt: float) -> None:
        # Update video
        ret, frame = self.vid.read()

        try:
            tmp_img = self.masks(frame)
            self.angle = self.mark_angle(tmp_img[0], tmp_img[1], tmp_img[2])
            self.pad.x_val = self.angle
            angles.append(self.angle)
            self.angleLabel.text = "Angle: " + str(self.angle)
            self.img.texture = self.convert_img_to_texture(frame)
            self.left.texture = self.convert_img_to_texture(tmp_img[0])
            self.right.texture = self.convert_img_to_texture(tmp_img[1])
            self.both.texture = self.convert_img_to_texture(tmp_img[2])
            self.masks(frame)
            return
        except:
            Clock.unschedule(self.event)
            self.vid.release()
            path = input("Where would you like to save the angles file? ") 
            if path != "":
                with open(path, 'w+') as output_file:
                    for i in range(len(angles)):
                        output_file.write(str(angles[i]))
                        output_file.write(";")
            else:
                print("No path supplied, not going to create file :c")
            App.get_running_app().stop()
            Window.close()
            return

    def mark_angle(
        self, img_left: np.ndarray, img_right: np.ndarray, img: np.ndarray
    ) -> int:
        bnw_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
        bnw_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)

        cntrs_left, hier = cv2.findContours(
            bnw_left, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        cntrs_left.sort(key=cv2.contourArea, reverse=True)

        cntrs_right, hier = cv2.findContours(
            bnw_right, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        cntrs_right.sort(key=cv2.contourArea, reverse=True)
        try:
            big = [cntrs_left[0], cntrs_right[0]]
        except:
            return 0
        points = []
        for c in big:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                points.append((cX, cY))
                cv2.circle(img, (cX, cY), 8, (255, 0, 0), 5)
        try:
            cv2.line(img, points[1], points[0], (255, 0, 0), 5)
        except:
            return 0
        try:
            return -1.0 * int(
                np.rad2deg(
                    math.atan2(
                        (points[1][1] - points[0][1]), (points[1][0] - points[0][0])
                    )
                )
            )
        except:
            return 0

    def convert_img_to_texture(self, img: np.ndarray) -> Texture:
        buf_i = cv2.flip(img, 0)
        buf = buf_i.tostring()
        texture_i = Texture.create(size=(img.shape[1], img.shape[0]), colorfmt="bgr")
        texture_i.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        return texture_i

    def masks(self, img: np.ndarray) -> Tuple:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        u_r = np.array(
            [self.slider[9].value, self.slider[10].value, self.slider[11].value],
            dtype="int32",
        )
        l_r = np.array(
            [self.slider[6].value, self.slider[7].value, self.slider[8].value],
            dtype="int32",
        )

        u_l = np.array(
            [self.slider[3].value, self.slider[4].value, self.slider[5].value],
            dtype="int32",
        )
        l_l = np.array(
            [self.slider[0].value, self.slider[1].value, self.slider[2].value],
            dtype="int32",
        )

        mask_l = cv2.inRange(hsv, l_l, u_l)
        mask_r = cv2.inRange(hsv, l_r, u_r)

        frame_l = cv2.bitwise_and(img, img, mask=mask_l)
        frame_r = cv2.bitwise_and(img, img, mask=mask_r)

        bidon, frame_l = cv2.threshold(frame_l, 5, 255, cv2.THRESH_BINARY)
        bidon, frame_r = cv2.threshold(frame_r, 5, 255, cv2.THRESH_BINARY)

        frame_b = cv2.bitwise_or(frame_l, frame_r)

        return frame_l, frame_r, frame_b


print("Initializing GUI...")
my = MyApp()
my.run()
plt.plot(angles)
plt.show()

#Cette ligne freeze, le join ne se fait pas correctement
#Aucune idée pourquoi, un ctrl-c fait l'affaire visiblement
print("Il y a besoin de faire un Ctr-C!! Le programme ne quitte pas!")
my.pad.stop()
exit()
