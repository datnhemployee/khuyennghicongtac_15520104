from tkinter import Frame, Label, StringVar
from PIL import Image, ImageTk
from utils.font import BUTTON
from utils.color import GREY, DARK_GREY, BLACK
from utils.dimension import PADDING, BORDER_WITH


class Button(Frame):
    def __init__(self, parent, width: int, height: int, text="button", enable=False, onClick=None):
        super().__init__(master=parent)
        self.__txt__ = StringVar(value=text,)
        self.width = width
        self.height = height
        self.__enable__ = enable
        self.onClick = onClick

        self._init_components()

    def get_background(self):
        return DARK_GREY

    def _init_components(self, ):
        """
          Khởi tạo các thành phần trên nút
        """
        background = GREY
        if (self.__enable__ == True):
            background = DARK_GREY

        self.config(
            width=self.width,
            height=self.height,
            background=background
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_propagate(False)

        foreground = DARK_GREY
        if (self.__enable__ == True):
            foreground = BLACK

        self.label_text = Label(self)
        self.label_text.config(
            textvariable=self.__txt__,
            font=BUTTON,
            background=background,
            foreground=foreground,
            # highlightthickness=BORDER_WITH,
            # highlightbackground=DARK_GREY,
        )

        self._add_animations()
        if (self.onClick is not None):
            self.bind("<Button-1>", self._onClick)
            self.label_text.bind("<Button-1>", self._onClick)

    def setText(self, text: str):
        self.__txt__.set(text)

    def setEnable(self, val: bool):
        self.__enable__ = val

        if (self.__enable__ == False):
            self.label_text.config(
                background=GREY,
                foreground=DARK_GREY,
            )
            self.config(
                background=GREY
            )
            return
        self.label_text.config(
            background=DARK_GREY,
            foreground=BLACK,
        )
        self.config(
            background=DARK_GREY
        )

    def _add_animations(self):
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event, **kwargs):
        if(self.__enable__ == True):
            self.config(
                highlightthickness=1,
                highlightbackground=BLACK,
            )

    def _on_leave(self, event, **kwargs):
        self.config(
            highlightthickness=0,
        )

    def _onClick(self, event, **kwargs):
        if(self.__enable__ == True):
            self.onClick()

    def show_components(self, ):
        """
          Khởi tạo các thành phần trên nút
        """
        # self.label_text.pack(fill="both", expand=1)
        self.label_text.grid(row=1, column=1, sticky="news")
