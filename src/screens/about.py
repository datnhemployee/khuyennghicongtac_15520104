
from utils.image import FlexibleImage
from utils.dimension import PADDING, SCROLL_BAR_WIDTH
from utils.font import TYPE_TITLE_SCREEN, TITLE_SCREEN, HEADER_1, BODY, HEADER_2, BUTTON
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, BLACK, GREY, ORANGE, WHITE

from controllers.main import controller

from tkinter import Label, Canvas, PhotoImage, LEFT, Frame, StringVar
from components.scrollable_screen import ScrollableScreen
from components.button_back import ButtonBack


class About(ScrollableScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

    def _before_init_components(self):
        super()._before_init_components()

        self.lstImages = []
        self.title = StringVar("")
        self.designableWidth = self.app.width - PADDING * 2 - SCROLL_BAR_WIDTH

    def _init_components(self):
        background_color = self.get_background()
        button_back_size = PADDING * 3

        self.button_back = ButtonBack(
            self.container,
            size=button_back_size,
            onClick=self.navigate_Home
        )

        self.label_screenName = Label(
            self.container)
        self.label_screenName.config(
            textvariable=self.title,
            font=TITLE_SCREEN,
            background=background_color,
            foreground=DARK_BLUE)

        self.lstCanvas = None

    def navigate_Home(self, **kw):
        self.app.navigate("Home",)

    def _initLstCanvas(self):
        if (self.lstCanvas is not None):
            for cv in self.lstCanvas:
                cv.grid_forget()
                cv.destroy()

        self.lstCanvas = []

        for img in self.lstImages:
            cv = Canvas(
                self.container,
                # borderwidth=0,
                # relief="solid"
            )
            cv.config(
                width=img.width(),
                height=img.height(),
                background=self.get_background(),
                highlightthickness=0
            )

            cv.create_image(
                0, 0, image=img, anchor="nw")

            self.lstCanvas.append(cv)

    def setTitle(self, title: str):
        if (title == "Problem"):
            self.title.set("Bài toán khuyến nghị cộng tác")
        else:
            raise ValueError("Không tìm thấy dữ liệu về màn hình tương ứng.")

    def setLstImages(self, title: str):

        from utils.file import PROBLEM_IMAGE
        if (title == "Problem"):
            self.lstImages = [PROBLEM_IMAGE]
        else:
            raise ValueError("Không tìm thấy dữ liệu về màn hình tương ứng.")

        i = 0
        while(i < len(self.lstImages)):
            self.lstImages[i] = FlexibleImage(
                self.lstImages[i], width=self.designableWidth)
            i += 1

    def _screenWillShow(self, **kwargs):
        super()._screenWillShow(**kwargs)

        title = kwargs.get("title", None)

        self.setTitle(title)
        self.setLstImages(title)

        self._initLstCanvas()

    def _show(self, **kw):

        rowIdx_button_back = 0
        rowIdx_label_screenName = 1
        rowIdx_default_img = 2

        default_grid = {
            "column": 0,
            "sticky": "nw",
            "padx": (PADDING, PADDING)
        }

        self.button_back.grid(
            row=rowIdx_button_back,
            **default_grid
        )
        self.button_back.show_components()

        self.label_screenName.grid(
            row=rowIdx_label_screenName,
            **default_grid
        )
        for (idx, cv) in enumerate(self.lstCanvas):
            cv.grid(
                row=rowIdx_default_img + idx,
                **default_grid
            )
