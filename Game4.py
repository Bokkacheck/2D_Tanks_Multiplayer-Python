from tkinter import *
from threading import *
import time;
from Classes import *
from socket import *

userName = "olja";


def SendToServer(data):
    s = socket();
    s.connect(("127.0.0.1", 5000));
    s.send(data.ToString().encode());
    s.close();


def GetDataFromServer():
    s = socket();
    s.connect(("127.0.0.1", 5000));
    s.send(Message("","LOGIN",userName,"server",userName).ToString().encode());
    while True:
        msg = Message(s.recv(1024).decode());
        if msg.request == 'PLAYERINFO':
            if msg.sender in remotePlayers:
                remotePlayers[msg.sender].Update(msg);
            else:
                remotePlayers[msg.sender] = RemotePlayer(canvas,msg);
        elif msg.request == 'BULLETINFO':
            for r in remoteBullets:
                if not r.draw:
                    r.Reset(msg);
                    break;


def GameLoop():
    while True:
        time.sleep(0.04);
        player.Update(pressedKeys);
        for r in remoteBullets:
            r.Update();
        if player.bulletSend != "":
            SendToServer(Message(player.bulletSend));
            player.bulletSend = "";
        if player.change:
            SendToServer(player.Serialize());


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

player = Player(userName, canvas);
RemotePlayer.SetRemotePlayerImages();

remotePlayers = dict();

remoteBullets = [];
for i in range(0, 20):
    remoteBullets.append(RemoteBullet(canvas));

getDataFromServer = Thread(target=GetDataFromServer);
getDataFromServer.start();

gameLoop = Thread(target=GameLoop);
gameLoop.start();

root.mainloop();
