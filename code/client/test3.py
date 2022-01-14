from PIL import ImageFont

from QDialog import TipUi

fontfile = 'Consolas.ttf'
font = ImageFont.truetype(fontfile, 12)
text = "hello"
width, height = font.getsize(text)
# print(height, width)

# segment = ['Alice', 'Bob', "A", 'Charlie', 'Bob', 'Dave']
# line_width = 0
# content_show = ""
# for i in range(len(segment)):
#     width, height = font.getsize(segment[0] + " ")
#     if line_width + width < 101:
#         line_width += width
#         content_show = content_show + segment[0] + " "
#     else:
#         line_width = width
#         content_show = content_show + "/n" + segment[0] + " "
#     segment.remove(segment[0])
# print(content_show)

# import subprocess
# calcProc = subprocess.Popen('C:/Windows/System32/rundll32.exe C:/Windows/system32/shimgvw.dll C:/Users/DELL/Desktop/1637570371528.jpeg')
# print(calcProc.poll())
# print(calcProc.wait())
# print(calcProc.poll())

import os

# os.system('start IMG/cache/1637570371528.jpeg')

pic_name = "resize_aa.jpeg"



if pic_name[0:7:1] == "resize_":
    new_name = pic_name.split("resize_", 1)[1]
    if os.path.isfile("IMG/cache/" + new_name):
        pic_name = "IMG/cache/" + new_name
        os.system('start ' + pic_name)
        exit(0)
    else:
        print("pic doesn't exist! 1")
        TipUi.show_tip("Picture doesn't exist!")
        exit(0)
else:
    if os.path.isfile("IMG/cache/" + pic_name):
        pic_name = "IMG/cache/" + pic_name
        os.system('start ' + pic_name)
        exit(0)
    else:
        print("pic doesn't exist! 2")
        TipUi.show_tip("Picture doesn't exist!")
