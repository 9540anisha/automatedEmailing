import unicodedata
import string

def count_special_chars(s):
    count = 0
    for char in s:
        if not (char.isalnum() or char in string.punctuation):
            try:
                name = unicodedata.name(char) # get the character name
                if "LATIN" not in name and "DIGIT" not in name:
                    count += 1
            except ValueError:
                count += 1
    return count
