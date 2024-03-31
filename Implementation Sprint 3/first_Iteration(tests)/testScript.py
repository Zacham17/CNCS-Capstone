# This was my first test script to practice reading a file and searching for keywords
from termcolor import colored, cprint

keywords=['Zachary','Gary']

for line in open('testfile1.txt'):
   for k in keywords:
      if k in line:
          print(colored("Related line found: ", 'green'), line)
