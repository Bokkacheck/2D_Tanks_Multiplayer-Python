from socket import *
from Classes import Message;

sock = socket();
sock.bind(("127.0.0.1", 5000));
sock.listen(100);

users = dict();

while True:
    s, addr = sock.accept();
    msg = Message(s.recv(1024).decode());
    if msg.request == 'LOGIN':
        users[msg.data] = s;
    elif msg.request == 'PLAYERINFO' or msg.request == 'BULLETINFO':
        for k in users.keys():
            if k != msg.sender:
                users[k].send(msg.ToString().encode());
    elif msg.request == 'BULLETHIT':
        for k in users.keys():
            users[k].send(msg.ToString().encode());
