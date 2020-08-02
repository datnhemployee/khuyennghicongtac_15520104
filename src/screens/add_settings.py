from components.scrollable_screen import ScrollableScreen
from components.button import Button
from components.step_card import StepCard
from components.valuation_tag import ValuationTag
from components.button_back import ButtonBack
from components.warning_line import WarningLine
from tkinter import Label, Frame, Canvas
from utils.font import TITLE_SCREEN, TYPE_TITLE_SCREEN, HEADER_2, BUTTON, BODY
from utils.color import DARK_BLUE, BLUE, GREY, DARK_GREY, GREY, BLACK, LIGHT_BLUE, WHITE, ORANGE
from utils.dimension import PADDING, SCROLL_BAR_WIDTH
from utils.image import RBGAImage

from models.step import Step
from models.node2vec import Node2vec

from controllers.main import controller


class AddSettings(ScrollableScreen):
    """
    Navigate via AlgorithmCard.onClick
    """

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.algorithm = None
        self.err = None
        self.step_list = []

    def _init_components(self):
        background_color = self.get_background()
        self.designable_width = self.app.width - PADDING * 2 - SCROLL_BAR_WIDTH
        self.label_train_width = int(self.designable_width / 3)
        self.button_width = (self.label_train_width / 2) - PADDING * 2
        self.train_bar_height = HEADER_2[1] + PADDING * 2
        button_back_size = PADDING * 3

        self.button_back = ButtonBack(
            self.container,
            size=button_back_size,
            onClick=self.navigate_AddAlgorithms
        )

        self.label_algorithm_name = Label(self.container)
        self.label_algorithm_name.config(
            font=TITLE_SCREEN,
            background=background_color,
            foreground=DARK_BLUE
        )

        self.button_ok = Button(self.container, text="Thêm mới", width=self.button_width,
                                height=self.train_bar_height, enable=True, onClick=self.add_algorithm)

        self.button_configuration = Button(self.container, text="Cấu hình máy", width=self.button_width,
                                           height=self.train_bar_height, enable=True, onClick=None)

        self.warning_line_ok = WarningLine(self.container,)
        self.warning_line_configuration = WarningLine(
            self.container, text="Vui long kiểm tra hoặc tùy chỉnh thông số mặc định dựa trên cấu hình của máy")

    def _init_steps_list(self,):
        """
        Khởi tạo danh sách bước theo từng thuật toán
        """
        background = self.get_background()
        self.node2vec_step_card_height = self.app.height / 3
        algorithm = self.algorithm

        self.step_list = algorithm.get_step_list()

        self.step_card_list = [
            StepCard(
                parent=self.container,
                idx=idx,
                height=self.node2vec_step_card_height,
                width=self.designable_width,
                background=background,
                step=step,
                editable=True
            ) for (idx, step) in enumerate(self.step_list)
        ]

    """
    Logics
    """

    def add_algorithm(self,):
        try:
            self.update_algorithm_settings()
            controller.add_algorithm(self.algorithm)
            self.app.navigate("Project", project=controller.project)
        except ValueError as err:
            print("err", err.args)
            self._show_err(err)

    def update_algorithm_settings(self):
        if (self.algorithm is not None):
            for step_card in self.step_card_list:
                settings = step_card.get_dict_values()
                print("setting", settings)
                for key in settings.keys():
                    self.algorithm.set_setting(key, settings[key])

    """
    Navigations
    """

    def navigate_AddAlgorithms(self):
        self.app.navigate(context="AddAlgorithm")

    """
    Show
    """

    def _show_steps_list(self,):
        """
        Hiển thị danh sách từng bước
        """
        for (idx, stepcard) in enumerate(self.step_card_list):
            stepcard.grid(row=(2 + idx), column=0, sticky="nw")
            stepcard.show_components()

    def get_algorithm(self, **kwargs):
        algorithm = kwargs.get("algorithm", None)
        if (algorithm is None):
            raise ValueError("Không tìm thấy thuật toán...")

        return (algorithm, )

    def _update_label_algorithm_name(self):
        self.label_algorithm_name.config(
            text=self.algorithm.name
        )

    def _show_button_back(self):
        next_row = 0
        self.button_back.grid(row=next_row, column=0, sticky="nw")
        self.button_back.show_components()

    def _show_label_algorithm_name(self):
        next_row = 1
        self.label_algorithm_name.grid(
            row=next_row, column=0, sticky="nw", pady=(0, PADDING),  padx=(PADDING, 0))

    def _show_err(self, err: ValueError):
        self.err = err
        self.warning_line_ok.grid_forget()
        self.warning_line_ok.destroy()
        self.warning_line_ok = WarningLine(self.container,)
        self.warning_line_ok.setText(err.args)

        next_row = len(self.step_list) + 3
        print(len(self.step_list))

        self.warning_line_ok.grid(
            row=next_row, column=0, sticky="nw", pady=(0, PADDING),  padx=(PADDING, 0))
        self.warning_line_ok.show_components()

    def _show_button_ok(self):
        next_row = len(self.step_list) + 4
        self.button_ok.grid(
            row=next_row, column=0, sticky="nw", pady=(0, PADDING),  padx=(PADDING, 0))
        self.button_ok.show_components()

    def _show_warning_configuration(self):
        next_row = len(self.step_list) + 5
        self.warning_line_configuration.grid(
            row=next_row, column=0, sticky="nw", pady=(0, PADDING),  padx=(PADDING, 0))
        self.warning_line_configuration.show_components()

    def _show_button_configuration(self):
        next_row = len(self.step_list) + 6
        self.button_configuration.grid(
            row=next_row, column=0, sticky="nw", pady=(0, PADDING),  padx=(PADDING, 0))
        self.button_configuration.show_components()

    def _screenWillShow(self, **kwargs):
        super()._screenWillShow(**kwargs)
        try:
            (algorithm,) = self.get_algorithm(**kwargs)
            self.algorithm = algorithm
        except ValueError as err:
            self._show_err(err)

    def _show(self, **kwargs):
        if (self.err is not None):
            return None
        self._show_button_back()
        self._update_label_algorithm_name()
        self._show_label_algorithm_name()

        self._init_steps_list()
        self._show_steps_list()

        self._show_button_ok()
        self._show_warning_configuration()
        self._show_button_configuration()
