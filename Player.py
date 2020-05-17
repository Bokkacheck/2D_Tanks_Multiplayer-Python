from tkinter import *
import math;
import random
from Utils import *;

sizeX = 1260;
sizeY = 680;
angleOffset = 90;  # Slike pocinju uspravno


class Player:
    maxHealth = 100;
    size = 100;
    speed = 10;
    angle = 0;
    x = 0;
    y = 0;
    movement = V2(0,0);
    pos = V2(0, 0);
    bullets = [];
    rateOfFire = 5;
    rateCounter = 0;

    def __init__(self, name, canvas):
        self.playerImages = [];
        for i in range(0, 36):
            self.playerImages.append(PhotoImage(file='playerRotated/' + str(i) + '.png'));
        for i in range(0, 15):
            self.bullets.append(Bullet(canvas))
        self.name = name;
        self.currentHealth = self.maxHealth;
        self.canvas = canvas;
        self.pos = V2(random.randint(self.size, sizeX - self.size),random.randint(self.size, sizeY - self.size))
        self.image = self.canvas.create_image(self.pos.AsArgs(), image=self.playerImages[0]);
        self.change = False;

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
            self.movement = V2(math.cos(radians),-math.sin(radians))*move;
            self.pos += self.movement;
            if ' ' in pressedKeys:
                self.Shoot();
        else:
            self.movement = V2(0,0);
            self.change = False;

    def Draw(self):
        self.canvas.itemconfig(self.image, image=self.playerImages[self.angle]);
        self.canvas.move(self.image,self.movement.x,self.movement.y);

    def Shoot(self):
        if self.rateCounter >= self.rateOfFire:
            self.rateCounter = 0;
            for b in self.bullets:
                if not b.draw:
                    b.Reset(self.pos,self.angle);
                    return
    def Serialize(self):
        txt = "POS:-:"+str(self.pos.x)+":"+str(self.pos.y)+":"+str(self.angle)+":-:BULLETS";
        for b in self.bullets:
            txt+= b.Serialize();
        return txt;


class Bullet:
    speed = 20;
    color = 'red';

    def __init__(self, canvas):
        self.draw = True;
        self.movement = V2(0,0);
        self.canvas = canvas;
        self.pos = V2(-100,-100);
        self.circle = self.canvas.create_oval(-100,-100,-100,-100, fill=self.color);

    def Reset(self, pos, angle):
        self.draw = True;
        radians = (angle * 10 + angleOffset) * math.pi / 180.0;
        self.movement = V2(self.speed * math.cos(radians), -(self.speed * math.sin(radians)))
        self.pos = pos+(self.movement*2);
        coord = CentredCircle(self.pos.x, self.pos.y, 10);
        self.circle = self.canvas.create_oval(coord, fill=self.color);

    def Update(self):
        if self.draw:
            self.pos += self.movement;
            self.canvas.move(self.circle, self.movement.x, self.movement.y)
            if self.pos.x > sizeX or self.pos.x < 0 or self.pos.y > sizeY or self.pos.y < 0:
                self.canvas.delete(self.circle);
                self.draw = False;

    def Serialize(self):
        return str(self.pos.x) + ":"+ str(self.pos.y);