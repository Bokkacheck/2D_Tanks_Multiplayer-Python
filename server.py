from Classes import *;
from Utils import *;
from threading import *;
import time;
import pymysql
import json
from functools import reduce
import datetime
import atexit;
import signal
import os;


def SendToAll(message):
    for user in users.values():
        user.send(message.ToString().encode());
    time.sleep(0.006);


def Send(message):
    users[message.reciever].send(message.ToString().encode());
    time.sleep(0.006);


def SendToAllExcept(ex, message):
    for key in users.keys():
        if key != ex:
            users[key].send(message.ToString().encode());
    time.sleep(0.006);


def LogIn(userSocket, message):
    p = list(filter((lambda x: x.name==message.sender),players));
    if p.__len__() == 1:
        p = p[0];
        if p.name in users:
            userSocket.send(Message("", "LOGINFAIL", "", message.sender, "Already logged").ToString().encode())
        else:
            users[p.name] = userSocket;
            pos = RandomV2();
            mesg = Message("", "NEWPLAYER", message.sender, str(pos.x) + ":" + str(pos.y) + ":0", p.Serialize());
            SendToAll(mesg);
    else:
        p = PlayerData(message.sender,100,0,0)
        players.append(p)
        ExecuteQuery("INSERT INTO PLAYERS (username,health,kills,deaths) values('"+p.name+"',100,0,0)")
        users[p.name] = userSocket;
        pos = RandomV2();
        mesg = Message("", "NEWPLAYER", message.sender, str(pos.x) + ":" + str(pos.y) + ":0", p.Serialize());
        SendToAll(mesg);


def LogOut(message):
    if message.sender in users:
        users.pop(message.sender);
        SendToAll(Message("", "LOGOUT", message.sender, "", ""));


def PlayerDeath(message):
    for p in players:
        if p.name == message.sender:
            p.deaths += 1;
            ExecuteQuery("UPDATE PLAYERS SET DEATHS = " + str(p.deaths) + " WHERE username = '"+p.name+"'")
        elif p.name == message.data.split(";")[0]:
            p.kills += 1;
            ExecuteQuery("UPDATE PLAYERS SET KILLS = "+str(p.kills) + " WHERE username = '"+p.name+"'")
            Send(Message("", "KILL", "", p.name, ""));


def GetDataFromDatabase():
    global players;
    db = pymysql.connect(host='localhost', port=3306, user='root', password='', db='pythondatabase')
    cursor = db.cursor();
    query = "SELECT * FROM PLAYERS";
    try:
        cursor.execute(query);
        players = list(map(lambda x: PlayerData(*x), cursor.fetchall()))
    except:
        # Ako dodje do problema sa bazom da postoje hardkodovani igraci radi probe
        players = [PlayerData("bojannrt417", 100, 0, 0), PlayerData("milovannrt1117", 100, 0, 0),
                   PlayerData("nikolanrt617", 100, 0, 0),
                   PlayerData("username", 100, 0, 0)];
        print("Error with database")
    db.close();

def ExecuteQuery(query):
    db = pymysql.connect(host='localhost', port=3306, user='root', password='', db='pythondatabase')
    cursor = db.cursor();
    try:
        cursor.execute(query)
        db.commit()
    except:
        print("Error on "+ query);
        db.rollback()
    db.close()

def WriteStatsInJSON():
    with open('STATS.txt', 'w') as outfile:
        kills = reduce((lambda x,y: x+y),(p.kills for p in players))
        deaths = reduce((lambda x,y: x+y),(p.deaths for p in players))
        data = {"Number of players":players.__len__(), "Number of kills":kills,
                "Number of deaths":deaths, "Date and time":str(datetime.datetime.now())};
        json.dump(data, outfile)


def ConsoleLine():
    while True:
        print("Enter 'EXIT' to stop server");
        command = str(input());
        if command == 'EXIT':
            SendToAll(Message("", "SERVEROFF", "", "", ""))
            WriteStatsInJSON();
            os._exit(0);
        else:
            print("Wrong command");

socket = socket();
socket.bind(("127.0.0.1", 5000));
socket.listen(100);
users = dict();
players = [];
GetDataFromDatabase();
atexit.register(WriteStatsInJSON);
signal.signal(signal.SIGTERM, WriteStatsInJSON);

consoleLine = Thread(target=ConsoleLine);
consoleLine.start();


while True:
    sock, addr = socket.accept();
    msg = Message(sock.recv(1024).decode());
    if msg.request == 'LOGIN':
        LogIn(sock, msg);
    elif msg.request == 'PLAYERINFO' or msg.request == 'BULLETINFO' or msg.request == 'NOTIFY':
        SendToAllExcept(msg.sender, msg);
    elif msg.request == 'BULLETHIT':
        SendToAll(msg);
    elif msg.request == 'LOGOUT':
        LogOut(msg);
    elif msg.request == 'PLAYERDEATH':
        PlayerDeath(msg);

