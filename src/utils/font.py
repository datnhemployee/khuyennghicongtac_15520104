default_font_size = 20


def get_font_size(font_size_design=14) -> int:
    font_size_design = int(float(font_size_design) * 20.0/28.0)
    return font_size_design


TIMES_NEW_ROMAN = "Times New Roman"
CALIBRI = "Calibri"
SEGOE_UI_LIGHT = "Segoe UI Light"
font = SEGOE_UI_LIGHT

LOGO = (font, get_font_size(54), "bold")
TYPE_TITLE_SCREEN = (font, get_font_size(16))
TITLE_SCREEN = (font, get_font_size(36), "bold")
HEADER_1 = (font, get_font_size(36), "bold")
TYPE_HEADER_2 = (font, get_font_size(14))
HEADER_2 = (font, get_font_size(24))
BODY = (font, get_font_size(24))
BODY_BOLD = (font, get_font_size(24), "bold")
BUTTON = (font, get_font_size(24))
