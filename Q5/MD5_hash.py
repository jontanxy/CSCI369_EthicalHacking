import hashlib

VoucherCode = input("Enter your VoucherCode for hashing: ")

hash = hashlib.md5(b'kz1103891`}').hexdigest()

print(hash)
