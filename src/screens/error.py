
from utils.image import FlexibleImage
from utils.dimension import PADDING, SCROLL_BAR_WIDTH
from utils.font import TYPE_TITLE_SCREEN, TITLE_SCREEN, HEADER_1, BODY, HEADER_2, BUTTON
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, BLACK, GREY, ORANGE, WHITE

from controllers.main import controller

from tkinter import Label, Canvas, PhotoImage, LEFT, Frame, StringVar
from components.scrollable_screen import ScrollableScreen
from components.button_back import ButtonBack


class Error(ScrollableScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

    def _before_init_components(self):
        super()._before_init_components()

        self.lstImages = None
        self.msg = StringVar("")
        self.designableWidth = self.app.width - PADDING * 2

    def _init_components(self):
        background_color = self.get_background()
        button_back_size = PADDING * 3

        self.canvas.config(
            background=background_color
        )
        self.container.config(
            background=background_color
        )

        self.button_back = ButtonBack(
            self.container,
            size=button_back_size,
            onClick=self.navigate_Home,
        )

        self.label_screenName = Label(
            self.container)
        self.label_screenName.config(
            text="Oops !! Lỗi",
            font=TITLE_SCREEN,
            background=background_color,
            foreground=WHITE)

        default_message = "Hiện ứng dụng đã bị lỗi không thể hiển thị màn hình."
        default_message += "\n\nVui lòng liên hệ nhà phát triển để được sửa chữa sớm nhất."
        default_message += "\n\nGmail: 15520104@gm.uit.edu.vn"

        self.label_default_message = Label(
            self.container)
        self.label_default_message.config(
            text=default_message,
            font=BODY,
            background=background_color,
            foreground=WHITE,
            justify="left",
            anchor="w")

        self.label_detail_message = Label(
            self.container)
        self.label_detail_message.config(
            textvariable=self.msg,
            font=BODY,
            background=background_color,
            foreground=WHITE)

    def get_background(self):
        background = DARK_BLUE
        return background

    def navigate_Home(self, **kw):
        self.app.navigate("Home")

    def setMessage(self, msg: str):
        self.msg.set(msg)

    def _screenWillShow(self, **kwargs):
        super()._screenWillShow(**kwargs)

        message = kwargs.get("message", None)

        self.setMessage(message)

    def _show(self, **kw):

        rowIdx_button_back = 0
        rowIdx_label_screenName = 1
        rowIdx_label_default_message = 2
        rowIdx_label_detail_message = 3

        self.button_back.grid(
            row=rowIdx_button_back,
            column=0,
            sticky="nw"
        )
        self.button_back.show_components()

        self.label_screenName.grid(
            row=rowIdx_label_screenName,
            column=0,
            sticky="nw"
        )
        self.label_default_message.grid(
            row=rowIdx_label_default_message,
            column=0,
            sticky="nw"
        )
        self.label_detail_message.grid(
            row=rowIdx_label_detail_message,
            column=0,
            sticky="nw"
        )
