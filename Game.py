from tkinter import *
from threading import *
import time;
from Classes import *


def SendToServer():
    while True:
        time.sleep(0.5);


def GameLoop():
    while True:
        time.sleep(0.04);
        player.Update(pressedKeys);
        remotePlayer.Update(player.Serialize());
        if player.bulletSend!= "":
            print(player.bulletSend);
            for r in remoteBullets:
                if not r.draw:
                    r.Reset(player.bulletSend);
                    break;
            player.bulletSend = "";
        for r in remoteBullets:
            r.Update();



def KeyDown(event):
    if event.char in allowedCommands:
        pressedKeys[event.char] = True;


def KeyUp(event):
    if event.char in pressedKeys:
        pressedKeys.pop(event.char);


pressedKeys = dict();
allowedCommands = ('w', 'a', 's', 'd', ' ');

root = Tk();
root.bind("<KeyRelease>", KeyUp);
root.bind("<KeyPress>", KeyDown);

canvas = Canvas(root, width=sizeX, height=sizeY, bg='yellow')
canvas.pack()


player = Player("bojan", canvas);
RemotePlayer.SetRemotePlayerImages();
remotePlayer = RemotePlayer(canvas,player.Serialize());

remoteBullets = [];
for i in range(0,20):
    remoteBullets.append(RemoteBullet(canvas));

gameLoop = Thread(target=GameLoop);
gameLoop.start();
sendToServer = Thread(target=SendToServer);
sendToServer.start();
root.mainloop();
