from tkinter import Frame, Canvas, Label
from PIL import Image, ImageTk
from utils.dimension import PADDING
from utils.image import FlexibleImage
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, WHITE, BLACK, GREY
from utils.font import BODY, HEADER_2, TYPE_HEADER_2, BUTTON
from models.algorithm import Algorithm
from components.button import Button
from components.input import Input


class AlgorithmCard(Frame):
    def __init__(self,
                 parent,
                 idx: int,
                 height: int,
                 width: int,
                 background: str,
                 algorithm: Algorithm,
                 onClick=None,
                 onClick_Detail=None,
                 onClick_Setting=None,
                 ):
        super().__init__(master=parent)
        self.idx = idx

        self.height = height
        self.width = width
        self.background = background

        self.algorithm = algorithm

        self.onClick = onClick
        self.onClick_Detail = onClick_Detail
        self.onClick_Setting = onClick_Setting

        self._init_components()

    def _init_components(self):
        """
          Khởi tạo các thành phần trong train card
        """
        background_color = self.background

        self.icon_size = int(self.height - PADDING * 2)
        self.button_height = BODY[1] + PADDING * 2
        self.button_width = int(
            (self.width - self.icon_size) / 4) - PADDING * 2
        self.content_width = self.width - self.icon_size - self.button_width - PADDING * 2

        self.config(
            height=self.height,
            width=self.width,
            background=self.background,
            # borderwidth=1,
            # relief="solid"
        )

        self.grid_propagate(False)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.icon_algorithm = Canvas(
            self,
        )
        self.icon_algorithm.config(
            height=self.icon_size,
            width=self.icon_size,
            background=background_color,
            highlightthickness=0
        )

        self.image = FlexibleImage(
            self.algorithm.get_icon_path(), width=self.icon_size)

        self.icon_algorithm.create_image(
            0, 0, image=self.image, anchor="nw")

        """
        Content
        """
        self.container_content = Frame(self)
        self.container_content.config(
            width=self.content_width,
            height=self.icon_size,
            background=background_color
        )

        self.container_content.grid_rowconfigure(0, weight=1)
        self.container_content.grid_rowconfigure(4, weight=1)
        self.container_content.grid_propagate(False)

        self._init_content()

        """
        Buttons
        """
        self.container_buttons = Frame(self)
        self.container_buttons.config(
            width=self.button_width,
            height=self.icon_size,
            background=background_color
        )

        self.container_buttons.grid_rowconfigure(0, weight=1)
        self.container_buttons.grid_rowconfigure(3, weight=1)
        self.container_buttons.grid_propagate(False)

        has_settings = len(self.algorithm.setting.keys()) > 0
        self.button_setting = None
        if (has_settings == True):
            self.button_setting = Button(self.container_buttons, width=self.button_width,
                                         height=self.button_height, text="Cài đặt", enable=True, onClick=self._onClick_Setting)

        self.add_onClick()
        """
          Animations: None
        """
        self.bind("<Enter>", self._shade)
        self.bind("<Leave>", self._light)

    def _init_content(self):
        wrap_text_length = self.content_width

        self.label_name = Label(self.container_content)
        self.label_name.config(
            text=self.algorithm.name,
            justify="left",
            font=HEADER_2,
            background=self.background,
            foreground=DARK_BLUE,
            wraplengt=wrap_text_length,
        )

        self.label_description = Label(self.container_content)
        self.label_description.config(
            text=self.algorithm.descriptions,
            justify="left",
            font=TYPE_HEADER_2,
            background=self.background,
            foreground=DARK_BLUE,
            wraplengt=wrap_text_length,
        )

        settings = "Cài đặt (mặc định):"
        if (len(self.algorithm.setting.keys()) != 0):
            for key in self.algorithm.setting.keys():
                settings += "\n+ {0}={1}".format(key,
                                                 self.algorithm.setting[key])
        else:
            settings += "Không có"

        self.label_settings = Label(self.container_content)
        self.label_settings.config(
            text=settings,
            justify="left",
            font=TYPE_HEADER_2,
            background=self.background,
            foreground=DARK_BLUE,
            wraplengt=wrap_text_length,
        )

    """
        Logic
    """

    def add_onClick(self):
        self.bind("<Button-1>", self._onClick)
        self.icon_algorithm.bind("<Button-1>", self._onClick)

        self.container_content.bind("<Button-1>", self._onClick)
        self.label_name.bind("<Button-1>", self._onClick)
        self.label_description.bind("<Button-1>", self._onClick)
        self.label_settings.bind("<Button-1>", self._onClick)

        self.container_buttons.bind("<Button-1>", self._onClick)

    def _onClick(self, event, **kw):
        if(self.onClick is not None):
            self.onClick(self.algorithm)

    def _onClick_Setting(self,):
        if(self.onClick_Setting is not None):
            self.onClick_Setting(self.algorithm)
    """
        Animations
    """

    def _shade(self, event, **kw):
        self.config(background=GREY)
        self.icon_algorithm.config(background=GREY)
        self.container_content.config(background=GREY)
        self.container_buttons.config(background=GREY)
        self.label_name.config(background=GREY)
        self.label_description.config(background=GREY)
        self.label_settings.config(background=GREY)

    def _light(self, event, **kw):
        background = self.background
        self.config(background=background)
        self.icon_algorithm.config(background=background)
        self.container_content.config(background=background)
        self.container_buttons.config(background=background)
        self.label_name.config(background=background)
        self.label_description.config(background=background)
        self.label_settings.config(background=background)

    """
        Hiển thị
    """

    def _show_content(self):
        self.label_name.grid(row=1, column=0, sticky="nw")
        self.label_description.grid(row=2, column=0, sticky="nw")
        self.label_settings.grid(row=3, column=0, sticky="nw")

    def show_components(self):
        """
          Private: Hiển thị thẻ
        """
        self.icon_algorithm.grid(
            row=1, column=1, sticky="nw", padx=(PADDING, PADDING))
        self.container_content.grid(row=1, column=2, sticky="nw",)

        """
          Private: Hiển thị content
        """
        self._show_content()

        """
          Private: Hiển thị button
        """
        self.container_buttons.grid(
            row=1, column=3, sticky="nw", padx=(0, PADDING))

        if (self.button_setting is not None):
            self.button_setting.grid(
                row=2, column=0, sticky="nw", pady=(PADDING, PADDING), padx=(0, PADDING))
            self.button_setting.show_components()

    # def onClick(self, event, **kwargs):
