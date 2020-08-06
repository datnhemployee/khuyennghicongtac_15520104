from tkinter import Frame, Label, StringVar
from PIL import Image, ImageTk

from utils.font import BODY_BOLD
from utils.color import GREY, DARK_GREY, BLACK, WHITE, BLUE
from utils.dimension import PADDING, BORDER_WITH
from utils.image import RBGAImage


class ButtonIcon(Frame):
    def __init__(self, parent, icon_size: int, icon_path: str, text="button", on_click=None):
        super().__init__(master=parent)
        self.__txt__ = text
        self.__icon_size__ = icon_size
        self.__icon_path__ = icon_path
        self.__on_click__ = on_click

        self._init_components()

    def get_default_background(self):
        return WHITE

    def get_foreground(self):
        return BLUE

    def set_text(self, val):
        self.label_text.config(
            text=val)

    def get_text(self, val):
        return self.label_text.cget("text")

    def _init_components(self, ):
        """
          Khởi tạo các thành phần trên nút
        """

        self.config(
            background=self.get_default_background()
        )

        self.icon_button = RBGAImage(
            self.__icon_path__, size=self.__icon_size__)

        self.label_icon = Label(self, image=self.icon_button)
        self.label_icon.config(
            background=self.get_default_background(),
            highlightthickness=0
        )

        self.label_text = Label(self)
        self.label_text.config(
            text=self.__txt__,
            font=BODY_BOLD,
            background=self.get_default_background(),
            foreground=self.get_foreground(),
            anchor="nw",
            justify="left"
            # highlightthickness=BORDER_WITH,
            # highlightbackground=DARK_GREY,
        )

        self._add_animations()
        if (self.__on_click__ is not None):
            self.bind("<Button-1>", self._on_click)
            self.label_text.bind("<Button-1>", self._on_click)

    def _add_animations(self):
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def set_background(self, color):
        self.config(
            background=color
        )
        self.label_text.config(
            background=color
        )
        self.label_icon.config(
            background=color
        )

    def _on_enter(self, event, **kwargs):
        self.set_background(GREY)

    def _on_leave(self, event, **kwargs):
        self.set_background(self.get_default_background())

    def _on_click(self, event, **kwargs):
        self.__on_click__()

    def show_components(self, ):
        """
          Khởi tạo các thành phần trên nút
        """
        colIdx_left = 0
        colIdx_label_icon = 1
        colIdx_label_text = 2
        colIdx_right = colIdx_label_text + 1

        rowIdx_header = 0
        rowIdx_content = 1
        rowIdx_footer = rowIdx_content + 1

        self.grid_columnconfigure(colIdx_left, weight=1)
        self.grid_columnconfigure(colIdx_right, weight=1)

        self.grid_rowconfigure(rowIdx_header, weight=1)
        self.grid_rowconfigure(rowIdx_footer, weight=1)

        grid_default = {
            "sticky": "news",
            "pady": (PADDING, PADDING),
            "padx": (PADDING, PADDING),
        }

        # self.label_text.pack(fill="both", expand=1)
        self.label_icon.grid(row=rowIdx_content,
                             column=colIdx_label_icon,
                             **grid_default
                             )
        self.label_text.grid(row=rowIdx_content,
                             column=colIdx_label_text,
                             **grid_default
                             )
