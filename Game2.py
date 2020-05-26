import time;
from threading import *
from Classes import *
from Utils import *
from tkinter import messagebox
import os


def GetDataFromServer(sock):
    while game:
        msg = Message(sock.recv(1024).decode());
        if msg.request == 'NEWPLAYER':
            remotePlayers[msg.sender] = RemotePlayer(msg, canvas);
            SendToServer(player.GetInfoForNewPlayers());
        elif msg.request == 'NOTIFY':
            if msg.sender not in remotePlayers:
                remotePlayers[msg.sender] = RemotePlayer(msg, canvas);
        elif msg.request == 'PLAYERINFO':
            if msg.sender in remotePlayers:
                remotePlayers[msg.sender].Update(msg);
        elif msg.request == 'BULLETINFO':
            for r in remoteBullets:
                if not r.draw:
                    r.Reset(msg);
                    break;
        elif msg.request == 'BULLETHIT':
            for r in remoteBullets:
                if r.id == msg.data:
                    r.Disable();
            if msg.sender == player.data.name:
                player.TakeDamage(10, msg.data.split(";")[0]);
            else:
                remotePlayers[msg.sender].TakeDamage(10);
        elif msg.request == 'KILL':
            player.data.kills += 1;
            kills.set("Kills: " + str(player.data.kills));
        elif msg.request == 'LOGOUT':
            if msg.sender == player.data.name:
                sock.close();
                break;
            else:
                del remotePlayers[msg.sender];
        elif msg.request == 'SERVEROFF':
            messagebox.showinfo("Server off","Server is not active, game over");
            os._exit(0);


def GameLoop():
    while game:
        time.sleep(0.033);
        player.Update(pressedKeys);
        if player.change:
            SendToServer(player.Serialize());
        for r in remoteBullets:
            r.Update();


def KeyDown(event):
    if event.char in allowedCommands:
        pressedKeys[event.char] = True;


def KeyUp(event):
    if event.char in pressedKeys:
        pressedKeys.pop(event.char);


def Login():
    global player, game, userName;
    sock = socket();
    sock.connect(("127.0.0.1", 5000));
    sock.send(Message("", "LOGIN", userName.get(), "server", userName.get()).ToString().encode());
    msg = Message(sock.recv(1024).decode());
    if msg.request == "LOGINFAIL":
        messagebox.showinfo("Login fail", msg.data)
        sock.close();
        return;
    else:
        GameInit(msg);
        game = True;
        getDataFromServer = Thread(target=GetDataFromServer, args=(sock,));
        getDataFromServer.start();
        gameLoop = Thread(target=GameLoop);
        gameLoop.start();


def Logout():
    global userName, game;
    SendToServer(Message("", "LOGOUT", player.data.name, "", ""));
    game = False;
    userName = StringVar();
    gameFrame.pack_forget();
    MakeLogInEnvirnomet();


def GameInit(msg):
    global player, remoteBullets, remotePlayers, kills, deaths;
    MakeGameEnvirnoment();
    player = Player(msg, canvas);
    kills.set("Kills: " + str(player.data.kills));
    deaths.set("Deaths: " + str(player.data.deaths));
    player.kills = kills;
    player.deaths = deaths;
    remotePlayers = dict();
    RemotePlayer.remotePlayers = remotePlayers;
    remoteBullets = [];
    for i in range(0, 20):
        remoteBullets.append(RemoteBullet(canvas));


def MakeGameEnvirnoment():
    global gameFrame, canvas, loginFrame, kills, deaths
    gameFrame = Frame(root, bg='green');
    gameUIFrame = Frame(gameFrame);
    kills = StringVar();
    deaths = StringVar();
    Label(gameUIFrame, textvariable=kills, font=("Courier, Bold", 16)).pack(side=LEFT, padx=5);
    Label(gameUIFrame, textvariable=deaths, font=("Courier, Bold", 16)).pack(side=LEFT, padx=50);
    Button(gameUIFrame, text="Log Out", font=("Courier, Bold", 16), command=Logout, bg='red').pack(side=LEFT, padx=30);
    gameUIFrame.pack();
    canvas = Canvas(gameFrame, width=sizeX, height=sizeY, bg='yellow')
    canvas.pack()
    loginFrame.pack_forget();
    gameFrame.pack();


def MakeLogInEnvirnomet():
    global userName, password, loginFrame;
    loginFrame = Frame(root, width = 400, height = 200)
    Label(loginFrame, text='Multiplayer Tanks Battle',font=("Courier, Italic", 18)).pack(pady=20)
    Label(loginFrame, text='Enter your username to start game',font=("Courier", 12)).pack(pady = 20)
    userName = StringVar()
    Entry(loginFrame, textvariable=userName,font=("Courier", 12)).pack(pady=10);
    Button(loginFrame, text='Login', command=Login,font=("Courier", 12)).pack(pady=10);
    loginFrame.pack();


def OnExit():
    global game;
    if game:
        SendToServer(Message("", "LOGOUT", player.data.name, "", ""));
        game = False;
        time.sleep(0.1);
    root.destroy();


game = False;
player = None;
remoteBullets = [];
remotePlayers = {};
gameFrame = None;
canvas = None;
loginFrame = None;
userName = None;
password = None;
kills = None;
deaths = None;

pressedKeys = dict();
allowedCommands = ('w', 'a', 's', 'd', ' ');

root = Tk();
root.minsize(400, 200);
root.configure(background='blue')
Player.SetPlayerImages();
RemotePlayer.SetRemotePlayerImages();
root.bind("<KeyRelease>", KeyUp);
root.bind("<KeyPress>", KeyDown);
root.protocol("WM_DELETE_WINDOW", OnExit)
MakeLogInEnvirnomet();
root.mainloop();
