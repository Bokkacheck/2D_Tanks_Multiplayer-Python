from tkinter import *
from threading import *
import time;
import math;
import random


def CentredCircle(x, y, r=100):
    return x + r / 2, y + r / 2, x - r / 2, y - r / 2


class V2:
    x = 0;
    y = 0;

    def __init__(self, x, y):
        self.x = x;
        self.y = y;

    def LengthTo(self, sec):
        return math.sqrt(pow(self.x - sec.x) + pow(self.y - sec.y));

    def AsArgs(self):
        return self.x,self.y;

    def AsTuple(self):
        return tuple(self.x,self.y);

    def __add__(self, other):
        return V2(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        return V2(self.x * other, self.y * other);

    def __iadd__(self, other):
        self.x += other.x;
        self.y += other.y;
        return self;

    def 	__imul__(self, other):
        self.x = self.x - other.x;
        self.y = self.y - other.y;
        return self;