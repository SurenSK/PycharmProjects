import math

from PIL import Image
import bisect

# RobertHeaton chars = " .\'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
chars = " `^\",:;I!li~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*MW&8%B@$#"
# chars2 is ordered by measured character brightness
# chars2_vals is the average brightness of regions composed solely of this character
# measured with photoshop, size 8 characters, pure black background, pure white text
chars2_chars = "  `^:,~-;!|*)(_\\/\"{}[?+]vi1clr0o&jutIJzxYCwa8L$nZkOhfbdXUqp%mQ@#BMW"
chars2_lums = [0, 5, 11, 11, 12, 14, 14, 16, 16, 16, 16, 17, 17, 18, 20,
               20, 20, 21, 21, 22, 23, 24, 25, 25, 25, 27, 27, 28,
               29, 30, 30, 31, 31, 32, 32, 33, 34, 34, 35, 36, 36,
               36, 36, 36, 36, 37, 37, 39, 39, 39, 40, 40, 41, 41,
               42, 43, 43, 46, 46, 46, 47, 49, 53, 54, 54, 55, 57]
charset2 = (chars2_chars, chars2_lums)
chars2_reversed = "WM#B@Qm%pqUXdbfhOkZn$L8awCYxzJItuj&o0rlc1iv]+?[}{\"/\\_()*|!;-~,:^`. "
# chars3 is order by measured brightness without characters of equal brightness
# chars3_chars = "  `'^,~*)/{}[?+iclr&utIzx$knhbdXqmQ@BMW"
chars3_chars = " `'^,~*)/{}[?+iclr&utIzx$knhbdXqmQ#BMW"
chars3_lums = [3, 8, 9, 11, 12, 14, 16, 17, 20, 21, 22, 23, 24, 25,
               27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39,
               39, 40, 41, 42, 43, 46, 47, 49, 53, 54, 55, 57]
charset3 = (chars3_chars, chars3_lums)
# aspectRatio ~= 750/900 with 2 characters per pixel ~= 0.415 ~= Need to widen image by 2.4x


def list_im_info(image: Image) -> None:
    print("width", image.width)
    print("height", image.height)
    print("#pixels", image.width * image.height)
    print("type", image.format)


def get_raw_data(path: str) -> list:
    global im
    im = Image.open(path)
    data = im.getdata()
    return data


def raw_to_luminance(data: list, invert: bool, alpha: bool, mode: str) -> list:
    # Data: From im.getdata(), _invert: T/F, alpha: Ignore T/F, mode: formula used

    # lum_list = [round((0.2126 * pixel[0] + 0.7152 * pixel[1] + 0.0722 * pixel[2]), 4) for pixel in data]
    # lum_list = [abs((_invert * 255) - pixel) for pixel in lum_list]
    lum_list = []
    for pixel in data:
        lum = -1
        r, g, b = pixel[0], pixel[1], pixel[2]
        a = 1 if len(pixel) == 3 else pixel[3]/255

        if mode == "luminance":
            lum = round((0.2126*r + 0.7152*g + 0.0722*b), 4)
        elif mode == "lightness":
            lum = round((max(r+g+b)+min(r+g+b))/2, 4)
        elif mode == "average":
            lum = round((r+g+b)/3, 4)
        elif mode == "norm":
            lum = round(((r**2+g**2+b**2)**0.5)/3, 4)
        elif mode == "r":
            lum = r
        elif mode == "g":
            lum = g
        elif mode == "b":
            lum = b
        elif mode == "max":
            lum = max(r, g, b)
        elif mode == "min":
            lum = min(r, g, b)

        lum = lum*a if alpha is True else lum
        lum = 255-lum if invert is True else lum

        lum_list.append(lum)
    return lum_list


def data_to_chars_simple(data: list, _charset) -> list:
    step_size = 255 / (len(_charset[0])-1)

    index_list = []
    index_list[:] = [int(i / step_size) for i in data]
    char_list = []
    char_list[:] = [_charset[0][i]*2 for i in index_list]

    return char_list


def data_to_chars_dithered(data: list, _charset) -> list:
    ref_chars = _charset[0]
    ref_vals = _charset[1]
    ref_vals[:] = [(val * (255 / max(ref_vals))) for val in ref_vals]
    chars_arr = [[0 for x in range(len(data[0]))] for y in range(len(data))]
    err_arr = [[0 for x in range(len(data[0]))] for y in range(len(data))]

    for x in range(0, len(data[0])):
        for y in range(0, len(data)):
            index = bisect.bisect_left(ref_vals, min(data[y][x],255))
            error = data[y][x] - ref_vals[index]
            if abs(data[y][x] - ref_vals[max(index - 1, 0)]) < abs(error):
                index -= 1
                error = data[y][x] - ref_vals[index]
            err_arr[y][x] = '', int(error)
            if x < (len(data[0])-1):
                data[y][x+1] = data[y][x+1] + error*7/16
            if x > 0 and y < (len(data)-1):
                data[y+1][x-1] = data[y+1][x-1] + error*3/16
            if y < (len(data)-1):
                data[y+1][x] = data[y+1][x] + error*5/16
            if x < (len(data[0])-1) and y < (len(data)-1):
                data[y+1][x+1] = data[y+1][x+1] + error*1/16
            # chars_arr[y][x] = ref_chars[index]+str(int(data[y][x]))
            chars_arr[y][x] = ref_chars[index]*2

    # output_2d_img(err_arr,' ')
    # output_2d_img(data,' ')
    return chars_arr


def list_to_2d(data_flat: list, height: int, width: int) -> list:
    array_2d = []
    for x in range(0, height):
        row = []
        for y in range(0, width):
            row.append(data_flat[(x * width) + y])
        array_2d.append(row)
    return array_2d


def output_2d_img(array: list, end_char: str) -> None:
    for row in array:
        for elem in row:
            print(elem, end=end_char)
        print()


def list_char_freqs(array: list) -> None:
    for c in charset[0]:
        print(c+c, sum(row.count(c+c) for row in array))


def pr_red(skk): print("\033[91m {}\033[00m" .format(skk))


img_path = "face3.jpg"
charset = charset3
invert_img = False
use_alpha = False
luminance_mode = "luminance"

rawData = get_raw_data(img_path)
lumData = raw_to_luminance(rawData, invert_img, use_alpha, luminance_mode)
data2d = list_to_2d(lumData, im.height, im.width)
final_image = data_to_chars_dithered(data2d, charset)

# image_simple = data_to_chars_simple(lumData, charset)
# output_2d_img(list_to_2d(image_simple, im.height, im.width), '')
# list_char_freqs(final_image)

# output_2d_img(final_image, '')
pr_red("test")
