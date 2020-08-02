from tkinter import Frame, Label
from utils.font import BODY
from utils.dimension import PADDING


class ValuationTag(Frame):
    def __init__(self, parent, icon_size, text, color, background):
        super().__init__(master=parent, )
        self._init_components(icon_size, text, color, background)

    def _init_components(self, icon_size, text, color, background):
        self.config(
            background=background
        )

        self.rec = Frame(self)
        self.rec.config(
            height=icon_size,
            width=icon_size,
            background=color
        )

        self.rec.grid_propagate(False)

        self.tag = Label(
            self, text=text)
        self.tag.config(font=BODY,
                        background=background,
                        foreground=color)

    def show_components(self, ):
        self.rec.grid(row=0, column=0, sticky="nw", padx=(PADDING, 0))
        self.tag.grid(row=0, column=1, sticky="nw")
