#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-18 Richard Hull and contributors
# See LICENSE.rst for details.

from PIL import Image
from os.path import isfile
from components.widgets.common_functions import title_text
from components.widgets.common.base_widget_hotspot import BaseHotspot
from subprocess import check_output

def _create_bitmap_to_render(image, width, height):
    size_tuple = (width, height)
    # # Forces a square - [64, 64]
    # size = [min(*size_tuple)] * 2
    #
    # # Creates offset - (32, 0)
    # position = ((width - size[0]) // 2, height - size[1])
    # print(position)

    # Full screen
    size = [width, height]
    position = (0, 0)

    # Create new image with same size as display
    img_bitmap = Image.new("RGBA", size_tuple)
    # Resize frame and paste onto canvas image
    img_bitmap.paste(image.resize(size, resample=Image.LANCZOS), position)
    img_bitmap.resize((width, height))

    return img_bitmap


class Hotspot(BaseHotspot):
    def __init__(self, width, height, interval, **data):
        super(Hotspot, self).__init__(width, height, interval, self.render)

        self._frame_no = 0
        self._image = None
        self._error = True  # Until image is set
        self._error_text = ""

        self.title = data.get("title")
        self.project_path = None
        self.image_path = None
        self.loop = True
        self.playback_speed = 1.0
        self.update_props(**data)

    def _load_image(self):
        self._error = False
        self.image_path = self.project_path + "/animation.gif"
        if not isfile(self.image_path):
            self._error_text = "Invalid path for image file: " + str(self.image_path)
            self._error = True
            return

        try:
            self._image = Image.open(self.image_path)
            self._image.verify()

            # Need to close and re-open after verifying...
            self._image.close()
            self._image = Image.open(self.image_path)

            self._error = False
        except Exception as e:
            self._error_text = str(e)
            self._error = True

        if self._error:
            print(self._error_text)

    def _seek_next_frame_in_image(self):
        if self._image.is_animated:
            if self._frame_no + 1 < self._image.n_frames:
                self._frame_no += 1
            elif self.loop:
                self._frame_no = 0

        self._image.seek(self._frame_no)

        if self._image.is_animated:
            embedded_frame_speed_s = float(self._image.info['duration'] / 1000)
            self.interval = float(embedded_frame_speed_s / self.playback_speed)

    def update_props(self, **data):
        for key, value in data.items():
            if key == "project_path":
                self.project_path = value
                self._load_image()
            if key == "loop":
                self.loop = value
            if key == "playback_speed":
                self.playback_speed = value

    def is_project_running(self):
        code_file = self.project_path + "/start.sh"

        cmd = "pgrep -f \"" + self.project_path + "\" || true"
        output = check_output(cmd, shell=True).decode('ascii', 'ignore')
        
        pids = list(filter(None, output.split('\n')))

        return (len(pids) > 1)

    def render(self, draw, width, height):

        message = self.title

        if (self.is_project_running()):
            message += ": Running"
        else:
            message += ": Stopped"

        title_width, title_height = draw.textsize(message)

        if self._error:
            draw.text((width / 2 - title_width / 2, height / 2 - title_height / 2), text=message, fill="white")
        else:
            if self._image is not None:

                self._seek_next_frame_in_image()
                img_bitmap = _create_bitmap_to_render(self._image, width, height - title_height - 2)
                draw.bitmap(xy=(0, 0), bitmap=img_bitmap, fill="white")

                draw.text((width / 2 - title_width / 2, height - title_height - 1), text=message, fill="white")
