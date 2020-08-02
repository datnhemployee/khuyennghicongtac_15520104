from tkinter import Frame, Label, Canvas, StringVar
from utils.font import BODY
from utils.color import ORANGE, WHITE
from utils.dimension import PADDING
from utils.image import RBGAImage
from utils.file import ICON_WARNING


class WarningLine(Frame):
    def __init__(self, parent, text="", icon_size=BODY[1]+PADDING*2, color=ORANGE, background=WHITE, ):
        super().__init__(master=parent, )
        self.__txt__ = StringVar("")

        self._init_components(icon_size, text, color, background)

    def _init_components(self, icon_size, text, color, background):
        self.config(
            background=background
        )

        self.icon_warning = Canvas(
            self,
        )

        self.icon_warning.config(
            height=icon_size,
            width=icon_size,
            background=background,
            highlightthickness=0
        )

        self.figure = RBGAImage(
            ICON_WARNING, size=icon_size)

        self.icon_warning.create_image(
            0, 0, image=self.figure, anchor="nw")

        self.content = Label(
            self,)
        self.content.config(
            textvariable=self.__txt__,
            font=BODY,
            background=background,
            foreground=color)

    def setText(self, text: str):
        self.__txt__.set(text)
        self.show_components()

    def getText(self, ):
        return self.__txt__.get()

    def show_components(self, ):
        if (self.__txt__.get() != ""):
            self.icon_warning.grid_forget()
            self.content.grid_forget()

            self.icon_warning.grid(
                row=0, column=0, sticky="nw", padx=(PADDING, 0))
            self.content.grid(row=0, column=1, sticky="nw")
