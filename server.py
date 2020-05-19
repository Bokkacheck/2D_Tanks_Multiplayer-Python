from Classes import *;
from Utils import *;
import time;


players = [PlayerData("bojan", 100, 10, 11), PlayerData("ivan", 200, 10, 11), PlayerData("goran", 300, 10, 11),PlayerData("olja", 100, 10, 11)];

def SendToAll(message):
    for user in users.values():
        user.send(message.ToString().encode());
    time.sleep(0.005);

def Send(message):
    users[message.reciever].send(message.ToString().encode());
    time.sleep(0.005);

def SendToAllExcept(ex,message):
    for key in users.keys():
        if key != ex:
            users[key].send(message.ToString().encode());
    time.sleep(0.005);

def LogIn(userSocket,message):
    for p in players:
        if p.name == message.sender:
            if message.sender in users:
                userSocket.send(Message("", "LOGINFAIL", "", message.sender, "Already logged").ToString().encode())
            else:
                users[msg.sender] = userSocket;
                pos = RandomV2();
                mesg = Message("", "NEWPLAYER", message.sender,str(pos.x) + ":" +str(pos.y) + ":0", p.Serialize());
                SendToAll(mesg);
            return;
    userSocket.send(Message("", "LOGINFAIL", "", message.sender, "User doesn't exist").ToString().encode())

def LogOut(message):
    if message.sender in users:
        users.pop(message.sender);
        SendToAll(Message("", "LOGOUT", message.sender, "",""));

socket = socket();
socket.bind(("127.0.0.1", 5000));
socket.listen(100);
users = dict();

while True:
    sock, addr = socket.accept();
    msg = Message(sock.recv(1024).decode());
    if msg.request == 'LOGIN':
        LogIn(sock,msg);
    elif msg.request == 'PLAYERINFO' or msg.request == 'BULLETINFO' or msg.request == 'NOTIFY':
        SendToAllExcept(msg.sender,msg);
    elif msg.request == 'BULLETHIT':
        SendToAll(msg);
    elif msg.request == 'LOGOUT':
        LogOut(msg);
