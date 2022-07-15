from enum import Enum
from math import cos, pi, sin, sqrt
from jolly.sunvec.setting import SettingRange

GRAYSCALE = -1
FULLCOLOR = 0
PROTANOPIA = 1
DEUTERANOPIA = 2
TRITANOPIA = 3

class Spectrum():
    def __init__(self, list_settings : list):
        self.length = len(list_settings)
    def __len__(self):
        return self.length

class Color():
    def __init__(self, spectrum, vision_type=FULLCOLOR):
        self.spectrum = spectrum
        self.vision_type = vision_type

    def __len__(self):
        return len(self.spectrum)

    def __str__(self):
        pallet = self.color_spectrum()
        str_out = ""
        for rgb in pallet:
            str_out += (F"\nR={round(rgb[0],3)}, G={round(rgb[1],3)}, B={round(rgb[2],3)}")
        return str_out

    def set_spectrum(self, new_spectrum):
        self.spectrum = new_spectrum

    def color(self, index):
        red = self.r(index)
        green = self.g(index)
        blue = self.b(index)
        yellow = (red + green)/2
        cyan = (green + blue)/2
        
        
        
        if self.vision_type == FULLCOLOR:
            return red, green, blue
        elif self.vision_type == PROTANOPIA:
            return red - cyan, red - cyan, blue - yellow
        elif self.vision_type == DEUTERANOPIA: 
            return red - cyan , red - cyan, blue - yellow
        elif self.vision_type == TRITANOPIA: 
            return yellow - cyan, cyan - yellow, cyan - yellow

    def color_spectrum(self):
        pallet = []
        for i in range(0,len(self)+1):
            pallet.append(self.color(i))
        return pallet


class RingColor(Color):
    def __init__(self, spectrum, vision_type, max_angle=(7/4)*pi):  # TODO: Abstract angle away into a colorspace rep?
        super().__init__(spectrum, vision_type)
        if vision_type == FULLCOLOR:
            self.offset = -(1/8)*pi
        elif vision_type == PROTANOPIA:
            max_angle = -(3/4)*pi
            self.offset = (1/16)*pi
        elif vision_type == DEUTERANOPIA:
            max_angle = -(3/4)*pi
            self.offset = (1/16)*pi
        elif vision_type == TRITANOPIA:
            max_angle = -(3/4)*pi
            self.offset = (1/16)*pi
            
        self.theta = max_angle

    def r(self, index):
        return 1 - ( 
            pow(0 - sin(self.offset + (self.theta*(index/len(self)))),2) + \
            pow(1 - cos(self.offset + (self.theta*(index/len(self)))),2)
            ) / 2.25
            
    def g(self, index):
        return 1 - ( 
            pow(sqrt(3)/2 - sin(self.offset + (self.theta*(index/len(self)))),2) + \
            pow(-(1/2) - cos(self.offset + (self.theta*(index/len(self)))),2)
        ) / 2.25

    def b(self, index):
        return 1 - ( 
            pow(-sqrt(3)/2 - sin(self.offset + (self.theta*(index/len(self)))),2) + \
            pow(-(1/2) - cos(self.offset + (self.theta*(index/len(self)))),2)
        ) / 2.25
    






