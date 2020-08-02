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

from controllers.main import controller
from controllers.excution import excute


class Experiments(ScrollableScreen):
    """
    Navigate via TrainCard.onClick
    """

    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.error_training = None

    def update_is_trained(self, ):
        self.is_trained = controller.is_trained(algorithm=self.algorithm)

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
            onClick=self.navigate_Project
        )

        self.label_screen_title = Label(self.container)
        self.label_screen_title.config(
            text="PHƯƠNG PHÁP",
            font=TYPE_TITLE_SCREEN,
            background=background_color,
            foreground=DARK_BLUE
        )

        self.label_algorithm_name = Label(self.container)
        self.label_algorithm_name.config(
            font=TITLE_SCREEN,
            background=background_color,
            foreground=DARK_BLUE
        )

        self.train_bar = Frame(self.container)
        self.train_bar.config(
            width=self.designable_width,
            height=self.train_bar_height,
            background=background_color,
        )

        self.train_bar.grid_columnconfigure(0, minsize=self.label_train_width)
        self.train_bar.grid_columnconfigure(1, weight=1)
        self.train_bar.grid_columnconfigure(2, minsize=self.button_width)
        self.train_bar.grid_propagate(False)

        self.label_train = Label(self.train_bar)
        self.label_train.config(
            text="Huấn luyện",
            font=HEADER_2,
            background=background_color,
            foreground=BLUE,
            justify="left",

        )

        self.warning_line_training = WarningLine(self.container,)

        self.button_train = Button(self.train_bar, text="Thực hiện",
                                   width=self.button_width, height=self.train_bar_height, enable=True, onClick=self.train)

        self.bar_valuation = Frame(self.container)
        self.bar_valuation.config(
            width=self.designable_width,
            height=self.train_bar_height,
            background=background_color,
        )

        self.bar_valuation.grid_columnconfigure(
            0, minsize=self.label_train_width)
        self.bar_valuation.grid_columnconfigure(1, weight=1)
        self.bar_valuation.grid_columnconfigure(2, minsize=self.button_width)
        self.bar_valuation.grid_propagate(False)

        self.label_valuation = Label(self.bar_valuation)
        self.label_valuation.config(
            text="Đánh giá",
            font=HEADER_2,
            background=background_color,
            foreground=BLUE,
            justify="left",
        )

        self.button_valuate = Button(self.bar_valuation, text="Thực hiện", width=self.button_width,
                                     height=self.train_bar_height, enable=False, onClick=self.valuate)

        self.bar_valuation_types = Frame(self.container)
        self.bar_valuation_types.config(
            width=self.designable_width,
            height=self.train_bar_height,
            background=background_color,
        )

        valuation_types = [
            {"name": "Precision",
             "color": DARK_BLUE, },
            {"name": "Recall",
             "color": BLUE, },
            {"name": "F-measure",
             "color": LIGHT_BLUE, },
        ]
        self.tag_valuations = [
            ValuationTag(
                self.bar_valuation_types,
                self.train_bar_height,
                valuation_type["name"],
                valuation_type["color"], WHITE)
            for valuation_type in valuation_types]

        self.warning_valuation = WarningLine(
            self.container,
            icon_size=BODY[1] + PADDING * 2,
            text="Chưa hoàn tất huấn luyện nên chưa thể đánh giá",
            color=ORANGE,
            background=WHITE
        )

        self.container_bar_chart = Frame(self.container)
        self.label_precision = Label(self.container_bar_chart)
        self.bar_precision = Frame(self.container_bar_chart)
        self.label_recall = Label(self.container_bar_chart)
        self.bar_recall = Frame(self.container_bar_chart)
        self.label_fmeasure = Label(self.container_bar_chart)
        self.bar_fmeasure = Frame(self.container_bar_chart)

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
            ) for (idx, step) in enumerate(self.step_list)
        ]

    def _config_bar_chart(self, precision: float, recall: float, fmeasure: float):
        container_bar_chart_height = int(self.app.height / 3)
        bar_height = int(container_bar_chart_height / 3) - PADDING * 2
        precision_width = int(precision * self.designable_width)
        recall_width = int(recall * self.designable_width)
        fmeasure_width = int(fmeasure * self.designable_width)

        self.container_bar_chart.config(
            height=container_bar_chart_height,
            width=self.designable_width,
            background=self.get_background(),
        )
        self.container_bar_chart.grid_propagate(False)

        self.label_precision.config(
            text=precision,
            foreground=DARK_BLUE,
            background=self.get_background()
        )

        self.bar_precision.config(
            height=bar_height,
            width=precision_width,
            background=DARK_BLUE
        )
        self.bar_precision.grid_propagate(False)

        self.label_recall.config(
            text=recall,
            foreground=BLUE,
            background=self.get_background()
        )

        self.bar_recall.config(
            height=bar_height,
            width=recall_width,
            background=BLUE
        )
        self.bar_recall.grid_propagate(False)

        self.label_fmeasure.config(
            text=fmeasure,
            foreground=LIGHT_BLUE,
            background=self.get_background()
        )

        self.bar_fmeasure.config(
            height=bar_height,
            width=fmeasure_width,
            background=LIGHT_BLUE
        )
        self.bar_fmeasure.grid_propagate(False)

    def _show_button_back(self):
        self.button_back.grid(row=0, column=0, sticky="nw")
        self.button_back.show_components()

    def _show_steps_list(self,):
        """
        Hiển thị danh sách từng bước
        """
        for (idx, stepcard) in enumerate(self.step_card_list):
            stepcard.grid(row=(4 + idx), column=0, sticky="nw")
            stepcard.show_components()

    def get_algorithm(self, **kwargs):
        algorithm = kwargs.get("algorithm", None)
        idx = kwargs.get("idx", None)
        if (algorithm is None or idx is None):
            raise ValueError("Không tìm thấy thuật toán...")

        return (algorithm, idx)

    def _set_label_algorithm_name(self):
        self.label_algorithm_name.config(
            text=self.algorithm.name
        )

    def _show_label_screen_title(self):
        self.label_screen_title.grid(
            row=1, column=0, sticky="nw", pady=(PADDING, 0), padx=(PADDING, 0))

    def _show_label_algorithm_name(self):
        self.label_algorithm_name.grid(
            row=2, column=0, sticky="nw", pady=(0, PADDING),  padx=(PADDING, 0))

    def _show_button_train(self):
        self.button_train.grid(
            row=0, column=2, sticky="ne",)
        self.button_train.show_components()

    def _show_button_valuate(self):
        self.button_valuate.grid(
            row=0, column=2, sticky="ne",)
        self.button_valuate.show_components()

    def _show_train_bar(self):
        self.train_bar.grid(
            row=3, column=0, sticky="nw", pady=(PADDING, PADDING),  padx=(PADDING, PADDING))
        self.label_train.grid(
            row=0, column=0, sticky="nw",)

        self._show_button_train()

    def _show_valuation_bar(self,):
        next_row = len(self.step_list) + 4 + 1

        self.bar_valuation.grid(
            row=next_row, column=0, sticky="nw", pady=(PADDING, PADDING),  padx=(PADDING, PADDING))
        self.label_valuation.grid(
            row=0, column=0, sticky="nw",)

        if (self.is_trained == True):
            self.enable_valuate()
        else:
            self.disable_valuate()
        self._show_button_valuate()

    def _show_valuation_type_bar(self):
        next_row = len(self.step_list) + 4 + 1 + 1
        self.bar_valuation_types.grid(
            row=next_row, column=0, sticky="nw", pady=(PADDING, PADDING), padx=(PADDING, PADDING))
        for (idx, tag_valuation) in enumerate(self.tag_valuations):
            tag_valuation.grid(row=0, column=idx, sticky="nw")
            tag_valuation.show_components()

    def _show_warning_valuation(self):
        next_row = len(self.step_list) + 4 + 1 + 1 + 1
        if(self.is_trained == False):
            self.warning_valuation.grid_forget()
            self.warning_valuation.grid(
                row=next_row, column=0, sticky="nw", pady=(PADDING, PADDING), padx=(PADDING, PADDING))
            self.warning_valuation.show_components()

    def _show_warning_training(self):
        next_row = 4
        if(self.error_training is not None):
            self.warning_line_training.grid(
                row=next_row, column=0, sticky="nw", pady=(PADDING, PADDING), padx=(PADDING, PADDING))
            self.warning_line_training.show_components()

    def _hide_bar_chart(self, **kw):
        self.container_bar_chart.grid_forget()
        self.label_precision.grid_forget()
        self.bar_precision.grid_forget()

        self.label_recall.grid_forget()
        self.bar_recall.grid_forget()

        self.label_fmeasure.grid_forget()
        self.bar_fmeasure.grid_forget()

    def _show_bar_chart(self, **kw):
        # self.algorithm = controller.get_algorithm(self.algorithm._id)
        algorithm = self.algorithm
        precision = algorithm.valuations["precision"]
        recall = algorithm.valuations["recall"]
        fmeasure = algorithm.valuations["fmeasure"]
        if (precision >= 0 and recall >= 0 and fmeasure >= 0):
            next_row = len(self.step_list) + 4 + 1 + 1 + 1
            self._config_bar_chart(precision, recall, fmeasure)
            self.container_bar_chart.grid(
                row=next_row,
                column=0,
                sticky="nw",
                pady=(PADDING, PADDING),
                padx=(PADDING, PADDING)
            )
            self.label_precision.grid(row=0, column=0, sticky="nw")
            self.bar_precision.grid(row=0, column=1, sticky="nw")

            self.label_recall.grid(
                row=1, column=0, sticky="nw", pady=(PADDING, PADDING))
            self.bar_recall.grid(
                row=1, column=1, sticky="nw", pady=(PADDING, PADDING))

            self.label_fmeasure.grid(row=2, column=0, sticky="nw")
            self.bar_fmeasure.grid(row=2, column=1, sticky="nw")
        else:
            self._hide_bar_chart()

    def navigate_Project(self,):
        self.app.navigate(context="Project", project=controller.project)

    def disable_train(self):
        print("training-disable")
        self.button_train.setEnable(False)
        self.button_train.setText("Đợi")
        self._show_button_train()

    def enable_train(self):
        print("training-enable")
        self.button_train.setEnable(True)
        self.button_train.setText("Thực hiện")
        self._show_button_train()

    def disable_valuate(self):
        print("disable_valuate")
        self.button_valuate.setEnable(False)
        self.button_valuate.setText("Đợi")
        self._show_button_valuate()

    def enable_valuate(self, ):
        print("enable_valuate")
        self.button_valuate.setEnable(True)
        self.button_valuate.setText("Thực hiện")
        self._show_button_valuate()

    def train_on_error(self, error: ValueError):
        self.warn_train(error)
        self.enable_train()

    def train_callback(self, **kw):
        self.update_is_trained()
        self.enable_valuate()
        self.enable_train()

    def train(self):
        self.disable_train()
        controller.train(
            algorithm=self.algorithm, cb_end=self.train_callback, on_error=self.train_on_error)

    def valuate_callback(self, **kw):
        self._show_bar_chart()
        self.enable_valuate()

    def valuate_on_error(self, error: ValueError):
        self.warn_valuate(error)
        self.enable_valuate()

    def valuate(self):
        self.disable_valuate()
        controller.valuate(
            algorithm=self.algorithm, callback=self.valuate_callback, on_error=self.valuate_on_error)

    def warn_train(self, error: ValueError):
        self.error_training = error
        self.warning_line_training.setText(error.args)
        self._show_warning_training()

    def warn_valuate(self, error: ValueError):
        self.error_training = error
        self.warning_valuation.setText(error.args)
        self._show_warning_training()

    def _screenWillShow(self, **kwargs):
        super()._screenWillShow(**kwargs)
        (algorithm, idx) = self.get_algorithm(**kwargs)
        # print("algorithm-before-mapped", algorithm.name)
        self.algorithm = controller.mapAlgorithm(algorithm)
        # print("algorithm-mapped",  self.algorithm)

    def _show(self, **kwargs):
        self.update_is_trained()
        # print("is_trained", self.is_trained)
        self._show_button_back()
        self._show_label_screen_title()
        self._set_label_algorithm_name()
        self._show_label_algorithm_name()
        self._show_train_bar()

        self._init_steps_list()
        self._show_steps_list()

        self._show_valuation_bar()
        self._show_valuation_type_bar()
        self._show_warning_valuation()
        self._show_bar_chart()
