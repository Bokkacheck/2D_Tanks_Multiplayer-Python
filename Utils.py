import math;
from socket import *;


def SendToServer(data):
    s = socket();
    s.connect(("127.0.0.1", 5000));
    s.send(data.ToString().encode());
    s.close();


def CenterToCoords(x, y, w=100, h=-1):
    if h == -1:
        h = w;
    return x + w / 2, y + h / 2, x - w / 2, y - h / 2

class V2:

    def __init__(self, x, y):
        self.x = x;
        self.y = y;

    def LengthTo(self, sec):
        return math.sqrt(pow((self.x - sec.x), 2) + pow((self.y - sec.y), 2));

    def AsArgs(self):
        return self.x, self.y;

    def __neg__(self):
        return V2(-self.x, -self.y);

    def __add__(self, other):
        return V2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return V2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return V2(self.x * other, self.y * other);

    def __iadd__(self, other):
        self.x += other.x;
        self.y += other.y;
        return self;

    def __imul__(self, other):
        self.x = self.x - other.x;
        self.y = self.y - other.y;
        return self;

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y;

    def __ne__(self, other):
        return not self.__eq__(other);


zeroVec = V2(0, 0);


def CoordsToCenter(x,y,x1,y1):
    return V2((x+x)/2, (y+y1)/2);
