from tkinter import Label, Canvas, PhotoImage, LEFT, Frame
from components.scrollable_screen import ScrollableScreen
from components.input import Input
from components.button import Button
from utils.file import ICON_BACK
from utils.image import RBGAImage
from utils.color import BLACK, GREY, WHITE
from utils.font import TYPE_TITLE_SCREEN, TITLE_SCREEN, HEADER_1, BODY, HEADER_2, BUTTON
from utils.dimension import PADDING, SCROLL_BAR_WIDTH
# from models.algorithm import Algorithm


class ButtonBack(Frame):
    def __init__(self, parent, size, onClick=None):
        super().__init__(parent,)
        self._init_components(size)

        self.onClick = onClick

    def _init_components(self, size: int):
        icon_size = int(size / 3)
        background_color = WHITE

        self.config(
            width=size,
            height=size,
            background=background_color
        )
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_propagate(False)

        self.canvas_back = Canvas(
            self,
            # borderwidth=0,
            # relief="solid"
        )
        self.canvas_back.config(
            height=icon_size,
            width=icon_size,
            background=background_color,
            highlightthickness=0
        )

        self.icon_back = RBGAImage(
            ICON_BACK, size=icon_size)

        self.canvas_back.create_image(
            0, 0, image=self.icon_back, anchor="nw")

        self.add_animations()

        self.bind("<Button-1>", self._onClick)
        self.canvas_back.bind("<Button-1>", self._onClick)

    def add_animations(self):
        self.bind("<Enter>", self._shade)
        self.bind("<Leave>", self._light)

    def _shade(self, event, **kw):
        self.config(
            background=GREY
        )

    def _light(self, event, **kw):
        self.config(
            background=WHITE
        )

    def _onClick(self, event, **kw):
        if (self.onClick is not None):
            self.onClick()

    def show_components(self):
        self.canvas_back.grid(row=1, column=1, sticky="nw")
