from tkinter import *
import math;
import random
from Utils import *;

sizeX = 1260;
sizeY = 680;
angleOffset = 90;  # Slike pocinju uspravno


class Message:
    sep = ":-:";

    def __init__(self, txt="", req="", sen="", rec="", data=""):
        if txt != '':
            txt = txt.split(Message.sep);
            self.request = txt[0];
            self.sender = txt[1];
            self.reciever = txt[2];
            self.data = txt[3];
        else:
            self.request = req;
            self.sender = sen;
            self.reciever = rec;
            self.data = data;

    def ToString(self):
        return self.request + Message.sep + self.sender + Message.sep + self.reciever + Message.sep + self.data;


class Player:
    maxHealth = 100;
    size = 100;
    speed = 10;
    angle = 0;
    x = 0;
    y = 0;
    movement = zeroVec;
    pos = zeroVec;
    bullets = [];
    rateOfFire = 5;
    rateCounter = 0;
    name = "";
    def __init__(self, name, canvas):
        self.playerImages = [];
        for i in range(0, 36):
            self.playerImages.append(PhotoImage(file='playerRotated/' + str(i) + '.png'));
        for i in range(0, 5):
            self.bullets.append(Bullet(canvas))
        Player.name = name;
        self.currentHealth = self.maxHealth;
        self.canvas = canvas;
        self.pos = V2(random.randint(self.size, sizeX - self.size), random.randint(self.size, sizeY - self.size))
        self.image = self.canvas.create_image(self.pos.AsArgs(), image=self.playerImages[0]);
        self.change = False;
        self.bulletSend = "";

    def Update(self, pressedKeys):
        self.rateCounter += 1;
        self.Controll(pressedKeys);
        if self.change:
            self.Draw();
        for b in self.bullets:
            b.Update();

    def Controll(self, pressedKeys):
        move = 0;
        if pressedKeys.__len__() != 0:
            if ' ' in pressedKeys and pressedKeys.__len__() == 1:
                self.change = False;
            else:
                self.change = True;
            if 'w' in pressedKeys:
                move = self.speed;
            elif 's' in pressedKeys:
                move = -self.speed;
            if 'a' in pressedKeys:
                if move >= 0:
                    self.angle += 1;
                else:
                    self.angle -= 1;
            elif 'd' in pressedKeys:
                if move >= 0:
                    self.angle -= 1;
                else:
                    self.angle += 1;
            if self.angle == 36:
                self.angle = 0;
            if self.angle == -1:
                self.angle = 35
            radians = (self.angle * 10 + angleOffset) * math.pi / 180.0;
            self.movement = V2(math.cos(radians), -math.sin(radians)) * move;
            self.pos += self.movement;
            if ' ' in pressedKeys:
                self.Shoot();
        else:
            self.movement = V2(0, 0);
            self.change = False;

    def Draw(self):
        self.canvas.itemconfig(self.image, image=self.playerImages[self.angle]);
        self.canvas.move(self.image, self.movement.x, self.movement.y);

    def Shoot(self):
        if self.rateCounter >= self.rateOfFire:
            self.rateCounter = 0;
            for b in self.bullets:
                if not b.draw:
                    b.Reset(self.pos, self.angle);
                    self.bulletSend = b.Serialize().ToString();
                    return

    def Serialize(self):
        return Message("","PLAYERINFO",self.name,"all",str(self.pos.x) + ":" + str(self.pos.y) + ":" + str(self.angle))


class Bullet:
    speed = 20;
    color = 'blue';

    def __init__(self, canvas):
        self.draw = False;
        self.movement = V2(0, 0);
        self.canvas = canvas;
        self.pos = V2(-100, -100);
        self.circle = self.canvas.create_oval(-100, -100, -100, -100, fill=self.color);

    def Reset(self, pos, angle):
        radians = (angle * 10 + angleOffset) * math.pi / 180.0;
        self.movement = V2(self.speed * math.cos(radians), -(self.speed * math.sin(radians)))
        self.pos = pos + (self.movement * 2);
        coord = CentredCircle(self.pos.x, self.pos.y, 10);
        self.circle = self.canvas.create_oval(coord, fill=self.color);
        self.draw = True;

    def Update(self):
        if self.draw:
            self.pos += self.movement;
            self.canvas.move(self.circle, self.movement.x, self.movement.y)
            if self.pos.x > sizeX or self.pos.x < 0 or self.pos.y > sizeY or self.pos.y < 0:
                self.canvas.delete(self.circle);
                self.draw = False;

    def Serialize(self):
        return Message("","BULLETINFO",Player.name,"all",str(self.pos.x) + ":" + str(self.pos.y) + ":" + str(self.movement.x) + ":" + str(self.movement.y))


class RemotePlayer:
    remotePlayerImages = [];

    @staticmethod
    def SetRemotePlayerImages():
        RemotePlayer.remotePlayerImages = [];
        for i in range(0, 36):
            RemotePlayer.remotePlayerImages.append(PhotoImage(file='remoteRotated/' + str(i) + '.png'));

    def __init__(self, canvas, msg):
        self.bullets = [];
        for i in range(0, 5):
            self.bullets.append(Bullet(canvas))
        self.changePos = False;
        self.changeAngle = False;
        self.pos = zeroVec;
        self.angle = 0;
        self.canvas = canvas;
        self.bullets = [];
        self.movement = zeroVec;
        self.Set(msg);
        self.image = self.canvas.create_image(self.pos.AsArgs(), image=RemotePlayer.remotePlayerImages[0]);

    def Update(self, txt):
        self.Set(txt);
        self.Draw();
        for b in self.bullets:
            b.Update();

    def Set(self, msg):
        data = msg.data;
        x = float(data.split(":")[0]);
        y = float(data.split(":")[1]);
        newPos = V2(x, y);
        if self.pos != newPos:
            self.movement = newPos - self.pos;
            self.pos = newPos;
            self.changePos = True;
        else:
            self.movement = zeroVec;
            self.changePos = False;
        newAngle = int(data.split(":")[2]);
        if self.angle != newAngle:
            self.changeAngle = True
            self.angle = newAngle;
        else:
            self.changeAngle = False;

    def Draw(self):
        if self.changePos:
            self.canvas.move(self.image, self.movement.x, self.movement.y);
        if self.changeAngle:
            self.canvas.itemconfig(self.image, image=RemotePlayer.remotePlayerImages[self.angle]);


class RemoteBullet:
    speed = 20;
    color = 'red';

    def __init__(self, canvas):
        self.draw = False;
        self.movement = zeroVec;
        self.canvas = canvas;
        self.pos = zeroVec;
        self.circle = self.canvas.create_oval(-100, -100, -100, -100, fill=self.color);

    def Reset(self, msg):
        data = msg.data.split(":");
        self.pos = V2(float(data[0]), float(data[1]));
        self.movement = V2(float(data[2]), float(data[3]));
        coord = CentredCircle(self.pos.x, self.pos.y, 10);
        self.circle = self.canvas.create_oval(coord, fill=self.color);
        self.draw = True;

    def Update(self):
        if self.draw:
            self.pos += self.movement;
            self.canvas.move(self.circle, self.movement.x, self.movement.y)
            if self.pos.x > sizeX or self.pos.x < 0 or self.pos.y > sizeY or self.pos.y < 0:
                self.canvas.delete(self.circle);
                self.draw = False;
