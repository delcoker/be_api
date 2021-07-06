import re

regex = "^[A-Za-z0-9_-]*$"
word_array = ["b'Little", "ha@aaa"]
retu = []
for word in word_array:
    # print(re.findall(regex, word))
    # print(re.search(regex, word))

    if re.search("^[A-Za-z0-9_-]*$", word):
        print(word)
    if re.search(regex, word):
        retu.append(word)

print(retu)

print(bool(re.search("^[A-Za-z0-9_-]*$", 'inv@lid')))

54043
