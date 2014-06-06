from django.conf import settings
import os

file_location = os.path.join(settings.BASE_DIR, "badwords.txt")
text_file = open(file_location, "r")
lines = text_file.readlines()
for line in lines:
    line = line[:-1]
    current_word = (line,)
    settings.PROFANITIES_LIST += current_word
text_file.close()