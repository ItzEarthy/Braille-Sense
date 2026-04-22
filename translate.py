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
    "":"i",
    "":"j",
    "":"k",
    "":"l",
    "":"m",
    "":"n",
    "":"o",
    "":"p",
    "":"q",
    "":"r",
    "":"s",
    "":"t",
    "":"u",
    "":"v",
    "":"w",
    "":"x",
    "":"y",
    "":"z"
}


