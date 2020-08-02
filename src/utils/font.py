default_font_size = 20


def get_font_Size(font_size_design=14) -> int:
    font_size_design = int(float(font_size_design) * 20.0/28.0)
    return font_size_design


TYPE_TITLE_SCREEN = ("Times New Roman", get_font_Size(16))
TITLE_SCREEN = ("Times New Roman", get_font_Size(28), "bold")
HEADER_1 = ("Times New Roman", get_font_Size(28), "bold")
TYPE_HEADER_2 = ("Times New Roman", get_font_Size(14))
HEADER_2 = ("Times New Roman", get_font_Size(24))
BODY = ("Times New Roman", get_font_Size(14))
BODY_BOLD = ("Times New Roman", get_font_Size(14), "bold")
BUTTON = ("Times New Roman", get_font_Size(18))
