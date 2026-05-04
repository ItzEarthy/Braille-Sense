import nltk
import cv2 #import possible dependancies from blobdetect
import numpy 
import re
import string
from nltk.stem import WordNetLemmatizer
#from blobdetect import blobs

blob1 = ["100000","110000","100100"] #check letter translation
blob2 = ["001111","100000","110000","110000","100000"] #check number
blob3 = ["011011","011011"] #check parenthesis
#blob = blobs.split(" ") / if the string of blobs are one string seperated by spaces, or split into 6's
words = []
#alphabet
letters = {
    "100000" : "a",
    "110000" : "b",
    "100100" : "c",
    "100110" : "d",
    "100010" : "e",
    "110100" : "f",
    "110110" : "g",
    "110010" : "h",
    "010100" : "i",
    "010110" : "j",
    "101000" : "k",
    "111000" : "l",
    "101100" : "m",
    "101110" : "n",
    "101010" : "o",
    "111100" : "p",
    "111110" : "q",
    "111010" : "r",
    "011100" : "s",
    "011110" : "t",
    "101001" : "u",
    "111001" : "v",
    "010111" : "w",
    "101101" : "x",
    "101111" : "y",
    "101011" : "z",
    "010000" : ",",
    "001000" : "'",
    "001001" : "-",
    "010010" : ":",
    "011000" : ";",
    "010011" : ".",
    "011001" : "?",
    "011010" : "!",
    "011011" : "parenthesis",
    "001111" : "#",
    "000011" : "letterPrefix",
    "000001" : "capital",
    "000000" : " " 
}

numbers = {
    "a" : "1",
    "b" : "2",
    "c" : "3",
    "d" : "4",
    "e" : "5",
    "f" : "6",
    "g" : "7",
    "h" : "8",
    "i" : "9",
    "j" : "0"
}

captials = {
    "100000" : "A",
    "110000" : "B",
    "100100" : "C",
    "100110" : "D",
    "100010" : "E",
    "110100" : "F",
    "110110" : "G",
    "110010" : "H",
    "010100" : "I",
    "010110" : "J",
    "101000" : "K",
    "111000" : "L",
    "101100" : "M",
    "101110" : "N",
    "101010" : "O",
    "111100" : "P",
    "111110" : "Q",
    "111010" : "R",
    "011100" : "S",
    "011110" : "T",
    "101001" : "U",
    "111001" : "V",
    "010111" : "W",
    "101101" : "X",
    "101111" : "Y",
    "101011" : "Z"
}

word = ""
blob = blob1
p = False
if blob.length <= 0 : 
    print("error blob has no elements")
for i in blob :
    if blob[i].length != 6 :
        print("error letter length is not in Braille format")
    else :
        if blob[i] in letters:
            if letters[blob[i]] == "capital":
                word = word + captials[blob[i+1]]
            else:
                word = word + letters[blob[i]]
            if letters[blob[i]] == "#":
                for j in range(i+1, len(blob)):
                    if blob[j] == "000011":
                        break
                    if blob[j] in numbers:
                        word = word + numbers[blob[j]]
                    else:
                        break
            if letters[blob[i]] == "parenthesis":
                if not p:
                    word = word + "("
                    p = True
                else:
                    word = word + ")"
                    p = False
            if letters[blob[i]] == " ":
                words.append(word)
                word = ""

  
