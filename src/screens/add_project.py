from tkinter import Label, Canvas, PhotoImage, LEFT, Frame
from components.scrollable_screen import ScrollableScreen
from components.input import Input
from components.button import Button
from components.button_back import ButtonBack
from components.warning_line import WarningLine
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, BLACK, GREY, ORANGE, WHITE
from utils.font import TYPE_TITLE_SCREEN, TITLE_SCREEN, HEADER_1, BODY, HEADER_2, BUTTON
from utils.dimension import PADDING, SCROLL_BAR_WIDTH
# from models.algorithm import Algorithm
from controllers.main import controller


class AddProject(ScrollableScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

    def _init_components(self):
        background_color = self.get_background()
        designable_width = self.app.width - PADDING * 2
        input_width = int(designable_width / 2)
        input_height = BODY[1] + PADDING * 2
        button_back_size = input_height

        self.button_back = ButtonBack(
            self.container,
            size=button_back_size,
            onClick=self.navigate_Home
            # borderwidth=0,
            # relief="solid"
        )

        self.label_screenName = Label(
            self.container, text="Thêm dự án")
        self.label_screenName.config(font=TITLE_SCREEN,
                                     background=background_color,
                                     foreground=DARK_BLUE)

        self.input_name = Input(
            self.container, width=input_width, height=input_height, title="Tên dự án", val="Tên dự án", enabel=True)

        self.label_prior = Label(
            self.container, text="Huấn luyện")
        self.label_prior.config(font=HEADER_1,
                                background=background_color,
                                foreground=BLUE)

        self.input_prior_start = Input(
            self.container, width=input_width, height=input_height, title="Năm bắt đầu", val="2014", enabel=True)
        self.input_prior_end = Input(
            self.container, width=input_width, height=input_height, title="Năm kết thúc", val="2015", enabel=True)

        self.label_test = Label(
            self.container, text="Đánh giá")
        self.label_test.config(font=HEADER_1,
                               background=background_color,
                               foreground=BLUE)

        self.input_test_start = Input(
            self.container, width=input_width, height=input_height, title="Năm bắt đầu", val="2016", enabel=True)
        self.input_test_end = Input(
            self.container, width=input_width, height=input_height, title="Năm kết thúc", val="2016", enabel=True)

        self.button_save = Button(
            self.container, width=int(designable_width / 2), height=input_height, text="Khởi tạo", enable=True, onClick=self.onClick_save)

        self.warning_line = WarningLine(
            self.container, icon_size=input_height, text="")

    def onClick_save(self,):
        self.hide_warning()
        self.setBtnSave(False)
        controller.add_project(
            name=self.input_name.get_val(),
            prior_start=self.input_prior_start.get_val(),
            prior_end=self.input_prior_end.get_val(),
            test_start=self.input_test_start.get_val(),
            test_end=self.input_test_end.get_val(),
            callback=self.navigate_Home,
            on_error=self.show_warning
        )

    def hide_warning(self, ):
        self.warning_line.setText("")

    def show_warning(self, err: ValueError):
        self.warning_line.setText(err.args)
        self.setBtnSave(True)

    def navigate_Home(self, **kw):
        self.app.navigate("Home")
        self.setBtnSave(True)

    def setBtnSave(self, enabel=True):
        self.button_save.setEnable(enabel)
        if (enabel == True):
            self.button_save.setText("Khởi tạo")
        else:
            self.button_save.setText("Đợi")

    def _show(self):

        default_grid = {
            "column": 0,
            "sticky": "nw",
            "padx": (PADDING, 0),
            "pady": (PADDING, PADDING)
        }
        rowIdx_btnBack = 0
        rowIdx_lblScreenName = 1
        rowIdx_input_name = 2
        rowIdx_label_prior = 3
        rowIdx_input_prior_start = 4
        rowIdx_input_prior_end = 5
        rowIdx_label_test = 6
        rowIdx_input_test_start = 7
        rowIdx_input_test_end = 8
        rowIdx_warning_line = 9
        rowIdx_button_save = 10

        self.button_back.grid(
            row=rowIdx_btnBack,
            **default_grid
        )
        self.button_back.show_components()

        self.label_screenName.grid(
            row=rowIdx_lblScreenName,
            **default_grid
        )

        self.input_name.grid(
            row=rowIdx_input_name,
            **default_grid
        )
        self.input_name.show_components()

        self.label_prior.grid(
            row=rowIdx_label_prior,
            **default_grid
        )

        self.input_prior_start.grid(
            row=rowIdx_input_prior_start,
            **default_grid
        )
        self.input_prior_start.show_components()

        self.input_prior_end.grid(
            row=rowIdx_input_prior_end,
            **default_grid
        )
        self.input_prior_end.show_components()

        self.label_test.grid(
            row=rowIdx_label_test,
            **default_grid
        )

        self.input_test_start.grid(
            row=rowIdx_input_test_start,
            **default_grid
        )
        self.input_test_start.show_components()

        self.input_test_end.grid(
            row=rowIdx_input_test_end,
            **default_grid
        )
        self.input_test_end.show_components()

        self.warning_line.grid(
            row=rowIdx_warning_line,
            **default_grid
        )
        self.warning_line.show_components()

        self.button_save.grid(
            row=rowIdx_button_save,
            **default_grid
        )
        self.button_save.show_components()
