#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# A simple ArchiSteamFarm bot for matrix.
# Error Codes:
# 1 - Unknown problem has occured
# 2 - Could not find the server.
# 3 - Bad URL Format.
# 4 - Bad username/password.
# 11 - Wrong room format.
# 12 - Couldn't find room.

import sys
import configparser
import logging
import requests

from matrix_client.client import MatrixClient
from matrix_client.api import MatrixRequestError
from requests.exceptions import MissingSchema

# Get config from matrix-asf.conf.
conf = configparser.ConfigParser()
conf.read("matrix-asf.conf")
host = conf["matrix"]["host"]
username = conf["matrix"]["username"]
password = conf["matrix"]["password"]
room_id_alias = conf["matrix"]["room"]
admin = conf["matrix"]["admin"]

tl_key = conf["tuling"]["key"]
tl_userid = conf["tuling"]["userid"]

# Get tuling response.
def get_tl_response(msg):
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key'    : tl_key,
        'info'   : msg,
        'userid' : tl_userid,
    }
    try:
        r = requests.post(apiUrl, data=data).json()
        return r.get('text')
    except:
        return

# Get asf response,the ip address and port are default settings.
def get_asf_response(msg):
    ipcUrl = 'http://127.0.0.1:1242/IPC'
    try:
        r = requests.get(ipcUrl, params={'command':msg})
        return r.text
    except:
        return

# Filter the asf command and chat bot.
def get_autoreply(msg):
    if msg.startswith('!'):
        return get_asf_response(msg)
    elif conf["tuling"].getboolean("enable") == True:
        return get_tl_response(msg)


# Called when a message is recieved.
def on_message(room, event):
    if ((event['content']['msgtype'] == "m.text") and (event['sender'] == admin)):
        msg = event['content']['body']
        autoreply = get_autoreply(msg)
        if autoreply: room.send_text(autoreply)

def main(host, username, password, room_id_alias):
    client = MatrixClient(host)

    try:
        client.login_with_password(username, password)
    except MatrixRequestError as e:
        print(e)
        if e.code == 403:
            print("Bad username or password.")
            sys.exit(4)
        else:
            print("Check your sever details are correct.")
            sys.exit(2)
    except MissingSchema as e:
        print("Bad URL format.")
        print(e)
        sys.exit(3)

    try:
        room = client.join_room(room_id_alias)
    except MatrixRequestError as e:
        print(e)
        if e.code == 400:
            print("Room ID/Alias in the wrong format")
            sys.exit(11)
        else:
            print("Couldn't find room.")
            sys.exit(12)

    room.add_listener(on_message)
    client.start_listener_thread()

    while True:
        pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    main(host, username, password, room_id_alias)
