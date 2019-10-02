#! /usr/bin/python3
import argparse

keys = ['abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ']

def main():
    parser = argparse.ArgumentParser(description="Ceaser Cipher tool")
    parser.add_argument("-d","--decrypt", type=str, help="text to decrypt")
    parser.add_argument("-e", "--encrypt", type=str, help="text to encrypt")
    parser.add_argument("-s", "--shift", type=int, help="cipher shift")
    args = parser.parse_args()

    dec_txt = args.decrypt 
    enc_txt = args.encrypt
    shift = args.shift

    if dec_txt:
        decrypt(shift, dec_txt)
    elif enc_txt:
        encrypt(shift, enc_txt)
    else:
        print("ERROR: Check arguments")


def encrypt(n, plaintext):
    result = '' # string to hold result

    for l in plaintext: # iterate through plaintext input
        try:
            if l == l.lower(): # if char is lowercase
                i = (keys[0].index(l) + n) % 26 # get index of shifted char
                result += keys[0][i] # append shifted char
            else: # else is upper case
                i = (keys[1].index(l) + n) % 26 # get index of shifted char
                result += keys[1][i] # append shifted char
        except ValueError:
            result += l # char is not in alphabet

    print(result)

def decrypt(n, ciphertext):
    """Decrypt the string and return the plaintext"""
    result = '' # string to hold result

    for l in ciphertext: # iterate through ciphertext input
        try:
            if l == l.lower(): # if char is lowercase
                i = (keys[0].index(l) - n) % 26 # get index of shifted char
                result += keys[0][i] # append shifted char
            else: # char is upper case
                i = (keys[1].index(l) - n) % 26 # get index of shifted char
                result += keys[1][i] # append shifted char
        except ValueError:
            result += l # char is not in alphabet

    print (result)


main()
