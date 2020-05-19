from tkinter import *
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
    playerImages = [];

    @staticmethod
    def SetPlayerImages():
        for i in range(0, 36):
            Player.playerImages.append(PhotoImage(file='playerRotated/' + str(i) + '.png'));

    def __init__(self, name, canvas):
        if name == "":
            return
        self.name = name;
        self.maxHealth = 100;
        self.size = 55;
        self.speed = 10;
        self.angle = 0;
        self.bullets = [];
        self.rateOfFire = 5;
        self.rateCounter = 0;
        self.movement = zeroVec;
        self.pos = zeroVec;
        for i in range(0, 5):
            self.bullets.append(Bullet(self.name, canvas))
        self.health = self.maxHealth;
        self.canvas = canvas;
        self.pos = V2(random.randint(self.size, sizeX - self.size), random.randint(self.size, sizeY - self.size))
        self.image = self.canvas.create_image(self.pos.AsArgs(), image=Player.playerImages[0]);
        self.change = False;
        self.coliderCounter = -1;
        self.bulletSend = "";
        self.healthBar = HealtBar(self.name,self.maxHealth, self.pos, self.canvas);

    def TakeDamage(self, amount):
        self.health -= amount;
        if self.health <= 0:
            SendToServer(Message("", "PLAYERDEATT", self.name, "all", self.name))
            self.health = self.maxHealth;
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
        self.canvas.itemconfig(self.image, image=Player.playerImages[self.angle]);
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
        return Message("", "PLAYERINFO", self.name, "",
                       str(self.pos.x) + ":" + str(self.pos.y) + ":" + str(self.angle))


class Bullet:
    speed = 20;
    color = 'blue';
    size = 10;
    bulletCount = 0;

    def __init__(self, playerName, canvas):
        Bullet.bulletCount += 1;
        self.playerName = playerName;
        self.id = self.playerName + ";" + str(Bullet.bulletCount);
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
        return Message("", "BULLETINFO", self.playerName, "all",
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
        self.maxHealth = 100;
        self.Set(msg);
        self.image = self.canvas.create_image(self.pos.AsArgs(), image=RemotePlayer.remotePlayerImages[0]);
        self.healthBar = HealtBar(self.name,self.maxHealth, self.pos, self.canvas);

    def TakeDamage(self, amount):
        self.health -= amount;
        if self.health <= 0:
            self.health = 100;
        self.healthBar.Change(self.health);

    def Update(self, txt):
        self.Set(txt);
        self.Draw();
        self.healthBar.Upate(self.movement);

    def Set(self, msg):
        data = msg.data.split(":");
        try:
            x = float(data[0]);
            y = float(data[1]);
        except ValueError:
            return;
        newPos = V2(x, y);
        if self.pos != newPos:
            self.movement = newPos - self.pos;
            self.pos = newPos;
            self.changePos = True;
        else:
            self.movement = zeroVec;
            self.changePos = False;
        try:
            newAngle = int(data[2]);
        except ValueError:
            return;
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

    def __del__(self):
        del self.healthBar;
        self.canvas.delete(self.image);


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

    def __init__(self, name, maxHealth, pos, canvas):
        self.maxHealth = maxHealth
        self.canvas = canvas;
        self.back = canvas.create_rectangle(CenterToCoords(pos.x, pos.y - 55, 100, 15), fill='tomato')
        self.front = canvas.create_rectangle(CenterToCoords(pos.x, pos.y - 55, 100, 13), fill='red')
        self.text = canvas.create_text(pos.x, pos.y - 55, fill="white", font="Times 13 bold",
                                       text=str(self.maxHealth) + "/" + str(self.maxHealth));
        self.txtName = canvas.create_text(pos.x, pos.y - 80, fill="black", font="Times 13 bold", text=name);
        self.pos = V2(pos.x, pos.y);

    def Upate(self, move):
        self.pos += move;
        self.canvas.move(self.back, move.x, move.y);
        self.canvas.move(self.front, move.x, move.y);
        self.canvas.move(self.text, move.x, move.y);
        self.canvas.move(self.txtName, move.x, move.y);

    def Change(self, amount):
        cords = CenterToCoords(self.pos.x - (self.maxHealth - amount) / 2, self.pos.y - 55, amount, 13);
        self.canvas.coords(self.front, cords);
        self.canvas.itemconfig(self.text, text=str(amount) + "/" + str(self.maxHealth))

    def __del__(self):
        self.canvas.delete(self.text);
        self.canvas.delete(self.txtName);
        self.canvas.delete(self.back);
        self.canvas.delete(self.front);
