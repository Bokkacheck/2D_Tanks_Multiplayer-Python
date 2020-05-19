from socket import *
from Classes import Message;

def SendToAll(message):
    for user in users.values():
        user.send(message.ToString().encode());

def Send(message):
    users[message.reciever].send(message.ToString().encode());

def SendToAllExcept(ex,message):
    for key in users.keys():
        if key != ex:
            users[key].send(message.ToString().encode());

def LogIn(userSocket,message):
    if message.sender in users:
        print("Da");
        userSocket.send(Message("","LOGINFAIL","",message.sender,"Already logged").ToString().encode())
    else:
        users[msg.sender] = userSocket;
        Send(Message("","LOGINOK","",message.sender,"Successfully logged"));
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
    elif msg.request == 'PLAYERINFO' or msg.request == 'BULLETINFO':
        SendToAllExcept(msg.sender,msg);
    elif msg.request == 'BULLETHIT':
        SendToAll(msg);
    elif msg.request == 'LOGOUT':
        LogOut(msg);
