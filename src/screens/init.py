
from utils.image import FlexibleImage
from utils.dimension import PADDING, SCROLL_BAR_WIDTH
from utils.font import TYPE_TITLE_SCREEN, TITLE_SCREEN, HEADER_1, BODY, HEADER_2, BUTTON
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, BLACK, GREY, ORANGE, WHITE

from controllers.main import controller

from tkinter import Label, Canvas, PhotoImage, LEFT, Frame, StringVar
from components.scrollable_screen import ScrollableScreen
from components.warning_line import WarningLine
from components.button import Button


class Init(ScrollableScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

    def _before_init_components(self):
        super()._before_init_components()

        self.lstImages = []
        self.title = StringVar(value="")
        self.designableWidth = self.app.width - PADDING * 2 - SCROLL_BAR_WIDTH

    def _init_components(self):
        background_color = self.get_background()
        btnWidth = self.designableWidth / 5
        btnHeight = BUTTON[1] + PADDING * 2

        self.label_screenName = Label(
            self.container)
        self.label_screenName.config(
            text="KHỞI TẠO CƠ SỞ DỮ LIỆU",
            font=TITLE_SCREEN,
            background=background_color,
            foreground=DARK_BLUE)

        self.wl_status = WarningLine(
            self.container, text="Đang kiểm tra cơ sở dữ liệu.")

        self.btn_init = Button(
            self.container,
            width=btnWidth,
            height=btnHeight,
            text="Đợi",
            enable=False,
            onClick=self.init)

    def navigate_Home(self, **kw):
        self.app.navigate("Home",)

    def setWLStatus(self, status: str):
        self.wl_status.setText(status)

    def setBtnInit(self, status: bool):
        if (status == False):
            self.btn_init.setEnable(status)
            self.btn_init.setText("Đợi")
            return
        self.btn_init.setEnable(status)
        self.btn_init.setText("Khởi tạo")

    def cb_init(self, **kw):
        self.navigate_Home()
        self.setBtnInit(True)

    def onError_init(self, err: ValueError):
        self.wl_status.setText(err.args)
        self.setBtnInit(True)

    def init(self):
        self.setBtnInit(False)
        controller.init(
            callback=self.cb_init,
            on_error=self.onError_init
        )

    def cb_isInit(self, **kw):
        status = kw.get("status", False)
        if (status == True):
            self.navigate_Home()
            return

        self.setWLStatus(
            "Không tìm thấy cơ sở dữ liệu. Vui lòng khởi tạo để sang màn hình chính.")
        self.setBtnInit(True)

    def onError_isInit(self, err: ValueError):
        self.wl_status.setText(err.args)

    def chkStatus(self):
        controller.isInit(callback=self.cb_isInit,
                          on_error=self.onError_isInit)

    def _screenWillShow(self, **kwargs):
        super()._screenWillShow(**kwargs)

        self.chkStatus()

    def _show(self, **kw):

        rowIdx_label_screenName = 0
        rowIdx_wl_status = 1
        rowIdx_btn_init = 2

        default_grid = {
            "column": 0,
            "sticky": "nw",
            "padx": (PADDING, PADDING),
            "pady": (PADDING, PADDING),
        }

        self.label_screenName.grid(
            row=rowIdx_label_screenName,
            **default_grid
        )

        self.wl_status.grid(
            row=rowIdx_wl_status,
            **default_grid
        )
        self.wl_status.show_components()

        self.btn_init.grid(
            row=rowIdx_btn_init,
            **default_grid
        )
        self.btn_init.show_components()
