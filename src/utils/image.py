from PIL import Image, ImageTk


def RBGAImage(path, size=None,):
    if (size == None):
        raise "RBGAImage: Lỗi resize hình ảnh."
    img = Image.open(path).resize((size, size), Image.ANTIALIAS)
    img = img.convert("RGBA")
    # print("mode", img.mode)
    return ImageTk.PhotoImage(img)


def FlexibleImage(path, width: int = None, height: int = None):
    img = Image.open(path)
    (imgWidth, imgHeight) = img.size

    ratio = imgWidth * 1.0/imgHeight
    _width = width
    _height = int(_width * 1.0/ratio)
    if (height is not None):
        _height = height
        _width = int(_width * ratio)

    img = Image.open(path).resize((_width, _height), Image.ANTIALIAS)
    img = img.convert("RGBA")
    # print("mode", img.mode)
    return ImageTk.PhotoImage(img)
