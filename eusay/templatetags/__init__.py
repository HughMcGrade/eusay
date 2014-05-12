from django.conf import settings

text_file = open("badwords.txt", "r")
lines = text_file.readlines()
for line in lines:
    line = line[:-1]
    current_word = (line,)
    settings.PROFANITIES_LIST += current_word
text_file.close()