import math

from PIL import Image


def get_im_info(image: Image) -> None:
    print("width", image.width)
    print("height", image.height)
    print("#pixels", image.width * image.height)


def output_2d(array) -> None:
    for row in array:
        for elem in row:
            print(elem, end='')
        print()


def output_list(flat_arr, height, width) -> None:
    array = []
    for x in range(0, height):
        temp = []
        for y in range(0, width):
            temp.append(flat_arr[(x * width) + y])
        array.append(temp)
    output_2d(array)


chars = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"

path1 = "ascii-pineapple.jpg"
path2 = "red.jpg"
path3 = "orange.png"
path4 = "blackwhite.png"
path5 = "test.jpg"

im = Image.open(path5)
px = im.load()
rgbPixels = im.getdata()

avgPixels = []
for pixel in rgbPixels:
    avgPixels.append(int((pixel[0]+pixel[1]+pixel[2]))/3)

charList = []
for i in range(len(avgPixels)):
    charList.append(chars[int(((avgPixels[i] * len(chars)) // 256))])

output_list(charList, im.height, im.width)