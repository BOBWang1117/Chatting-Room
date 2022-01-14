import cv2
from PIL import Image  # 批量对一批图片更改大小

img_list = ["headshot/1_origenal.png", "headshot/2_origenal.png", "headshot/3_origenal.jpg",
            "headshot/4_origenal.png", "headshot/5_origenal.jpg", "headshot/default.jpeg"]  # 图片名称列表
img_list = ["headshot/4.jpeg", "headshot/5.jpg"]

path = 'headshot/'  # 图片所在目录
i = 4
for imgs in img_list:
    img = Image.open(imgs)  # 读取图片
    img = img.resize((40, 40))  # 重置大小 （长，宽）
    if imgs.endswith('.png'):
        img.save(path + str(i) + "_smaller.png")
    elif imgs.endswith('.jpeg'):
        img.save(path + str(i) + "_smaller.jpeg")
    elif imgs.endswith('.jpg'):
        img.save(path + str(i) + "_smaller.jpg")
    i += 1