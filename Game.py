from tkinter import *
from threading import *
import time;
from Player import Player


def SendToServer():
    while True:
        time.sleep(0.5);
        print(player.Serialize());


def GameLoop():
    while True:
        time.sleep(0.05);
        player.Update(pressedKeys);


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

canvas = Canvas(root, width=1260, height=680, bg='yellow')
canvas.pack()

player = Player("bojan", canvas);

gameLoop = Thread(target=GameLoop);
gameLoop.start();
sendToServer = Thread(target=SendToServer);
sendToServer.start();
root.mainloop();
