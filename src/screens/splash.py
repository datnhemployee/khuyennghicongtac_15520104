
from utils.image import RBGAImage
from utils.dimension import PADDING, SCROLL_BAR_WIDTH
from utils.font import LOGO, BODY
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, BLACK, GREY, ORANGE, WHITE
from utils.file import ICON_APP

from controllers.main import controller
from controllers.excution import excute

from tkinter import Label, Canvas, LEFT, Frame, StringVar
from components.screen import Screen


class Splash(Screen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

    def _before_init_components(self):
        super()._before_init_components()

        self.lstImages = []
        self.designableWidth = self.app.width - PADDING * 2 - SCROLL_BAR_WIDTH

    def _init_components(self):
        background_color = self.get_background()
        icon_size = int(self.designableWidth / 5)

        self.config(
            width=self.app.width,
            height=self.app.height,
            background=background_color
        )
        self.grid_propagate(False)

        self.label_title = Label(self)
        self.label_title.config(
            text="weCoNet",
            font=LOGO,
            background=background_color,
            foreground=BLUE
        )

        self.icon_app = RBGAImage(
            ICON_APP, size=icon_size)

        self.canvas_icon_app = Label(self, image=self.icon_app)
        self.canvas_icon_app.config(
            background=background_color,
            highlightthickness=0
        )

        self.label_status = Label(self)
        self.label_status.config(
            text="We are setting up. Enjoy yourself.",
            font=BODY,
            background=background_color,
            foreground=BLUE
        )

    def init(self):
        status = False
        try:
            status = controller.isConnect()
        except ValueError as e:
            self.label_status.config(
                text=e.args
            )
        if (status == False):
            self.label_status.config(
                text="No data found. We are creating new one, please wait."
            )
            try:
                controller.initNew()
            except:
                self.label_status.config(
                    text="No connection found. try again."
                )
        controller.update_algorithm()
        self.app.navigate(context="Home")
        return {}

    def _screenDidShow(self, **kwargs):
        super()._screenDidShow(**kwargs)
        excute(task=self.init)

    def _show(self, **kw):

        rowIdx_blank_header = 0

        rowIdx_label_title = 1
        rowIdx_canvas_icon_app = 2
        rowIdx_label_status = 3

        rowIdx_blank_footer = rowIdx_label_status + 1

        colIdx_blank_left = 0
        colIdx_blank_right = 2
        colIdx_blank_center = 1

        default_grid = {
            "column": colIdx_blank_center,
            "sticky": "news",
            "padx": (PADDING, PADDING)
        }

        self.grid_rowconfigure(index=colIdx_blank_left, weight=1)
        self.grid_rowconfigure(index=colIdx_blank_right, weight=1)

        self.grid_columnconfigure(index=rowIdx_blank_header, weight=1)
        self.grid_columnconfigure(index=rowIdx_blank_footer, weight=1)

        self.label_title.grid(
            row=rowIdx_label_title,
            **default_grid
        )
        self.canvas_icon_app.grid(
            row=rowIdx_canvas_icon_app,
            **default_grid
        )
        self.label_status.grid(
            row=rowIdx_label_status,
            **default_grid
        )
