from PIL import Image, ImageTk


def RBGAImage(path, size=None, width=None, height=None):
    img = Image.open(path)

    if (size is not None):
        img = img.resize((size, size), Image.ANTIALIAS)
    elif (width is not None and height is not None):
        img = img.resize((width, height), Image.ANTIALIAS)
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
