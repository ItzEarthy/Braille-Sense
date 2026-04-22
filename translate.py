import nltk
import re
import string
from nltk.stem import WordNetLemmatizer
#from Blobs import blobs/dots

#translate "100000" into "a" and so on
#123456 is the number lines for each dot

#56 is the letter prefix symbol "dot 6" used after number symbol to swap back to letters
#000011 is 56

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
    "101011" : "z"
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

special = {
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


