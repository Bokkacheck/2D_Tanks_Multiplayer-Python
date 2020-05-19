import time;
from threading import *
from Classes import *
from Utils import *


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
            else:
                remotePlayers
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
                player.TakeDamage(10);
            else:
                remotePlayers[msg.sender].TakeDamage(10);
        elif msg.request == 'LOGOUT':
            if msg.sender == player.data.name:
                sock.close();
                break;
            else:
                del remotePlayers[msg.sender];


def GameLoop():
    while game:
        time.sleep(0.04);
        player.Update(pressedKeys);
        if player.change:
            SendToServer(player.Serialize());
        if player.bulletSend != "":
            SendToServer(Message(player.bulletSend));
            player.bulletSend = "";
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
    MakeGameEnvirnoment();
    global player, remoteBullets, remotePlayers;
    player = Player(msg, canvas);
    remotePlayers = dict();
    RemotePlayer.remotePlayers = remotePlayers;
    remoteBullets = [];
    for i in range(0, 20):
        remoteBullets.append(RemoteBullet(canvas));


def MakeGameEnvirnoment():
    global gameFrame, canvas, loginFrame
    gameFrame = Frame(root);
    Button(gameFrame, text="Log Out", command=Logout).pack();
    canvas = Canvas(gameFrame, width=sizeX, height=sizeY, bg='yellow')
    canvas.pack()
    loginFrame.pack_forget();
    gameFrame.pack();


def MakeLogInEnvirnomet():
    global userName, password, loginFrame;
    loginFrame = Frame(root)
    userName = StringVar()
    Entry(loginFrame, textvariable=userName).pack();
    password = StringVar()
    Entry(loginFrame, textvariable=password).pack();
    Button(loginFrame, text='Login', command=Login).pack();
    loginFrame.pack();


def OnExit():
    global game;
    if game:
        SendToServer(Message("", "LOGOUT", player.data.name, "", ""));
        game = False;
        time.sleep(0.1);  # daj vremena da se unisti sva memorija iz threadova
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

pressedKeys = dict();
allowedCommands = ('w', 'a', 's', 'd', ' ');

root = Tk();
root.minsize(300,300);
Player.SetPlayerImages();
RemotePlayer.SetRemotePlayerImages();
root.bind("<KeyRelease>", KeyUp);
root.bind("<KeyPress>", KeyDown);
root.protocol("WM_DELETE_WINDOW", OnExit)
MakeLogInEnvirnomet();
root.mainloop();
