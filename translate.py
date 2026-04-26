import nltk
import re
import string
from nltk.stem import WordNetLemmatizer
#from Blobs import blobs/dots


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
    "010011" : ".",
    "011001" : "?",
    "011010" : "!",
    "001111" : "#",
    "000011" : "letterPrefix",
    "000001" : "capital"
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

#string word = ""
#for b in blobs:
#    for a in letters : 
#       if b == a :
#           if a == "#" :
#               go through b until a is the letter prefix setting word into numbers(a)
#                   
#           word = word + letters(a)
#create an unswapped string of letters without numbers yet



