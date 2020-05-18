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
    size = 55;
    speed = 10;
    angle = 0;
    bullets = [];
    rateOfFire = 5;
    rateCounter = 0;
    name = "";

    def __init__(self, name, canvas):
        Player.name = name;
        self.playerImages = [];
        self.movement = zeroVec;
        self.pos = zeroVec;
        for i in range(0, 36):
            self.playerImages.append(PhotoImage(file='playerRotated/' + str(i) + '.png'));
        for i in range(0, 5):
            self.bullets.append(Bullet(canvas))
        self.health = self.maxHealth;
        self.canvas = canvas;
        self.pos = V2(random.randint(self.size, sizeX - self.size), random.randint(self.size, sizeY - self.size))
        self.image = self.canvas.create_image(self.pos.AsArgs(), image=self.playerImages[0]);
        self.change = False;
        self.coliderCounter = -1;
        self.bulletSend = "";
        self.healthBar = HealtBar(self.pos,self.canvas);

    def TakeDamage(self, amount):
        self.health -= amount;
        if self.health <= 0:
            SendToServer(Message("","PLAYERDEATT",Player.name,"all",Player.name))
            self.health = Player.maxHealth;
        self.healthBar.Change(self.health)

    def Update(self, pressedKeys):
        self.change = False;
        self.rateCounter += 1;

        if self.coliderCounter > 0:
            self.coliderCounter += 1;
            self.change = True;
        if self.coliderCounter == 5:
            self.coliderCounter = -1;
        if self.coliderCounter == -1:
            self.Controll(pressedKeys);
            self.CheckForCollision();

        if self.change:
            self.pos += self.movement;
            self.Draw();
            self.healthBar.Upate(self.movement);
        for b in self.bullets:
            b.Update();

    def CheckForCollision(self):
        radius = (self.size + RemotePlayer.size) / 2;
        for rp in RemotePlayer.remotePlayers.values():
            distance = self.pos.LengthTo(rp.pos);
            if distance <= radius:
                self.movement = (-self.movement + rp.movement) * 0.5;
                self.coliderCounter = 1;
                self.change = True;
                return True;

    def Controll(self, pressedKeys):
        move = 0;
        if pressedKeys.__len__() != 0:
            if ' ' not in pressedKeys or pressedKeys.__len__() != 1:
                self.change = True;

            if ' ' in pressedKeys:
                self.Shoot();

            if 'w' in pressedKeys:
                move = self.speed;
            elif 's' in pressedKeys:
                move = -self.speed;

            if 'a' in pressedKeys:
                if move >= 0:  # go front
                    self.angle += 1;
                else:  # go back
                    self.angle -= 1;
            elif 'd' in pressedKeys:
                if move >= 0:
                    self.angle -= 1;
                else:
                    self.angle += 1;

            if self.angle == 36:
                self.angle = 0;
            elif self.angle == -1:
                self.angle = 35

            radians = (self.angle * 10 + angleOffset) * math.pi / 180.0;
            self.movement = V2(math.cos(radians), -math.sin(radians)) * move;
        else:
            self.movement = zeroVec;

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
        return Message("", "PLAYERINFO", self.name, "all",
                       str(self.pos.x) + ":" + str(self.pos.y) + ":" + str(self.angle))


class Bullet:
    speed = 20;
    color = 'blue';
    size = 10;
    bulletCount = 0;

    def __init__(self, canvas):
        Bullet.bulletCount += 1;
        self.id = Player.name + str(Bullet.bulletCount);
        self.draw = False;
        self.movement = zeroVec
        self.canvas = canvas;
        self.pos = zeroVec;
        self.circle = self.canvas.create_oval(-10, -10, -10, -10, fill=self.color);

    def Reset(self, pos, angle):
        radians = (angle * 10 + angleOffset) * math.pi / 180.0;
        self.movement = V2(self.speed * math.cos(radians), -(self.speed * math.sin(radians)))
        self.pos = pos + (self.movement * 2);
        coord = CenterToCoords(self.pos.x, self.pos.y, 10);
        self.circle = self.canvas.create_oval(coord, fill=self.color);
        self.draw = True;

    def Update(self):
        if self.draw:
            self.CheckForCollision();
            self.pos += self.movement;
            self.canvas.move(self.circle, self.movement.x, self.movement.y)
            if self.pos.x > sizeX or self.pos.x < 0 or self.pos.y > sizeY or self.pos.y < 0:
                self.canvas.delete(self.circle);
                self.draw = False;

    def CheckForCollision(self):
        radius = (Bullet.size + RemotePlayer.size) / 2;
        for rp in RemotePlayer.remotePlayers.values():
            distance = self.pos.LengthTo(rp.pos);
            if distance <= radius:
                SendToServer(Message("", "BULLETHIT", rp.name, "all", self.id))
                self.canvas.delete(self.circle);
                self.draw = False;
                return True;
        return False;

    def Serialize(self):
        return Message("", "BULLETINFO", Player.name, "all",
                       str(self.pos.x) + ":" + str(self.pos.y) + ":" + str(self.movement.x) + ":" + str(
                           self.movement.y) + ":" + self.id);


class RemotePlayer:
    remotePlayerImages = [];
    remotePlayers = {};
    size = 55;

    @staticmethod
    def SetRemotePlayerImages():
        RemotePlayer.remotePlayerImages = [];
        for i in range(0, 36):
            RemotePlayer.remotePlayerImages.append(PhotoImage(file='remoteRotated/' + str(i) + '.png'));

    def __init__(self, canvas, msg):
        self.name = msg.sender;
        self.changePos = False;
        self.changeAngle = False;
        self.pos = zeroVec;
        self.angle = 0;
        self.canvas = canvas;
        self.bullets = [];
        self.movement = zeroVec;
        self.health = 100;
        self.Set(msg);
        self.image = self.canvas.create_image(self.pos.AsArgs(), image=RemotePlayer.remotePlayerImages[0]);
        self.healthBar = HealtBar(self.pos,self.canvas);

    def TakeDamage(self, amount):
        self.health -= amount;
        if self.health <= 0:
            self.health = Player.maxHealth;
        self.healthBar.Change(self.health);


    def Update(self, txt):
        self.Set(txt);
        self.Draw();
        self.healthBar.Upate(self.movement);

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
        self.circle = self.canvas.create_oval(-10, -10, -10, -10, fill=self.color);
        self.id = "";

    def Reset(self, msg):
        data = msg.data.split(":");
        self.id = data[4];
        self.pos = V2(float(data[0]), float(data[1]));
        self.movement = V2(float(data[2]), float(data[3]));
        coord = CenterToCoords(self.pos.x, self.pos.y, 10);
        self.circle = self.canvas.create_oval(coord, fill=self.color);
        self.draw = True;

    def Disable(self):
        self.draw = False;
        self.canvas.delete(self.circle);

    def Update(self):
        if self.draw:
            self.pos += self.movement;
            self.canvas.move(self.circle, self.movement.x, self.movement.y)
            if self.pos.x > sizeX or self.pos.x < 0 or self.pos.y > sizeY or self.pos.y < 0:
                self.canvas.delete(self.circle);
                self.draw = False;


class HealtBar:
    maxHealth = 100;

    def __init__(self,pos, canvas):
        self.canvas = canvas;
        self.back = canvas.create_rectangle(CenterToCoords(pos.x, pos.y - 50, 100, 10), fill='white')
        self.front = canvas.create_rectangle(CenterToCoords(pos.x, pos.y - 50, 100, 8), fill='red')
        self.pos = V2(pos.x,pos.y);

    def Upate(self, move):
        self.pos += move;
        self.canvas.move(self.back, move.x, move.y);
        self.canvas.move(self.front, move.x, move.y);

    def Change(self, amount):
        cords = CenterToCoords(self.pos.x - (HealtBar.maxHealth - amount) / 2, self.pos.y - 50, amount, 8);
        self.canvas.coords(self.front,cords);

