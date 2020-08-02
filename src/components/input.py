from tkinter import Frame, Label, Entry

from utils.color import BLACK, GREY, DARK_GREY, WHITE
from utils.font import BODY
from utils.dimension import PADDING


class Input(Frame):
    def __init__(self, parent, width: int, height: int, title: str, val, enabel=True):
        super().__init__(master=parent,)
        self._init_components(width, height, title, val, enabel)

    def _init_components(self, width, height, title, val, enabel):
        component_width = int(width / 2)
        wrap_text_length = component_width
        self.config(
            width=width,
            height=height,
            background=WHITE
        )
        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        # self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(3, weight=1)

        self.label = Label(self)
        self.label.config(
            text=title,
            justify="left",
            font=BODY,
            background=WHITE,
            foreground=BLACK,
            wraplengt=wrap_text_length,
        )

        status_entry = "normal"
        if (enabel == False):
            status_entry = "readonly"

        background_entry = WHITE
        if (enabel == False):
            background_entry = GREY

        foreground_entry = BLACK
        if (enabel == False):
            foreground_entry = DARK_GREY

        self.entry = Entry(self)
        self.entry.insert(0, val)
        self.entry.config(
            justify="center",
            font=BODY,
            background=background_entry,
            foreground=foreground_entry,
            state=status_entry,
            width=min([BODY[1], component_width])
        )

    def get_val(self) -> str:
        return self.entry.get()

    def get_title(self):
        return self.label["text"]

    def show_components(self):
        self.label.grid(row=0, column=0, sticky="nw")
        self.entry.grid(row=0, column=1, sticky="nw")
