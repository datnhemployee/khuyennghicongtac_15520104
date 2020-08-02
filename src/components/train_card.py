from tkinter import Frame, Canvas, Label
from PIL import Image, ImageTk
from utils.dimension import PADDING
from utils.image import FlexibleImage
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, WHITE, BLACK, GREY
from utils.font import BODY, HEADER_2
from models.algorithm import Algorithm


class TrainCard(Frame):
    def __init__(self, parent, idx: int, height: int, width: int, background: str, algo: Algorithm, onClick=None,):
        super().__init__(master=parent)
        self.config(background=WHITE)
        self.idx = idx

        self.height = height
        self.width = width
        self.background = background

        self.algo = algo

        self.onClick = onClick

        self._init_components()

    def get_background(self):
        return WHITE

    def _init_components(self):
        """
          Khởi tạo các thành phần trong train card
        """
        background_color = self.background

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

        # self.label = Label(self)

        self.icon_size = int(self.height - PADDING * 2)
        self.icon_algorithm = Canvas(
            self,
        )

        self.icon_algorithm.config(
            height=self.icon_size,
            width=self.icon_size,
            background=background_color,
            highlightthickness=0
        )

        self.figure = FlexibleImage(
            self.algo.get_icon_path(), width=self.icon_size)

        self.icon_algorithm.create_image(
            0, 0, image=self.figure, anchor="nw")

        self.chart_size = self.icon_size
        self.content_algorithm_width = self.width - \
            self.icon_size - self.chart_size - PADDING * 2

        """
        Content
        """
        self.content_container = Frame(self)
        self.content_container.config(
            width=self.content_algorithm_width,
            height=self.icon_size,
            background=background_color
        )

        self.content_container.grid_propagate(False)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(4, weight=1)

        self._init_content()

        """
        Bar-chart
		"""

        self.bar_chart_container = Frame(self)
        self.bar_chart_container.config(
            width=self.chart_size,
            height=self.chart_size,
            background=background_color,
            # borderwidth=1,
            # relief="solid"
        )
        self._init_bar_chart()

        """
          OnClick 
        """
        self._add_OnClick()

        """
          Animations 
        """
        self.bind("<Enter>", self._shade)
        self.bind("<Leave>", self._light)

    def _init_content(self):
        self.label_name = Label(self.content_container)
        wrap_text_length = self.content_algorithm_width
        self.label_name.config(
            text=self.algo.name,
            justify="left",
            font=HEADER_2,
            background=self.background,
            foreground=DARK_BLUE,
            wraplengt=wrap_text_length,
        )

        self.label_setting = Label(self.content_container)
        self.label_setting.config(
            text=self.algo.to_str_setting(),
            justify="left",
            font=BODY,
            background=self.background,
            foreground=BLACK,
            wraplengt=wrap_text_length,
        )

        self.label_description = Label(self.content_container)
        self.label_description.config(
            text=self.algo.descriptions,
            justify="left",
            font=BODY,
            background=self.background,
            foreground=BLACK,
            wraplengt=wrap_text_length,
        )

    def _init_bar_chart(self,):
        """
          Khởi tạo bar chart
        """
        """
          Khởi tạo bar chart container
        """
        background_color = self.background

        self.figure_container = Frame(self.bar_chart_container)
        figure_size = int(self.chart_size * 2 / 3)
        self.figure_container.config(
            width=figure_size,
            height=self.chart_size,
            background=background_color,
            # borderwidth=1,
            # relief="solid"
        )
        self.figure_container.grid_columnconfigure(
            0, minsize=figure_size)

        self.figure_container.grid_propagate(False)

        valuations_container_width = int(self.chart_size - figure_size)
        self.valuations_container = Frame(self.bar_chart_container)
        self.valuations_container.config(
            width=valuations_container_width,
            height=self.chart_size,
            background=background_color,
            # borderwidth=1,
            # relief="solid"
        )

        self.valuations_container.grid_propagate(False)

        if(self.has_barchart() == False):
            self.bars = []
            self.valuation_labels = []
            return None

        """
          Khởi tạo bar chart components
        """
        valuations = ["precision", "recall", "fmeasure"]
        self.bars = [Frame(self.figure_container) for valuation in valuations]
        self.bar_height = int(self.chart_size / 3) - PADDING * 3
        for (idx, bar) in enumerate(self.bars):
            percentage = 0.0
            title = valuations[idx]
            _percentage = self.algo.get_valuation(title)
            if (_percentage > 0):
                percentage = _percentage

            bar.config(
                height=self.bar_height,
                width=int(figure_size * percentage),
                background=self.algo.get_valuation_color(title)
            )
            bar.grid_propagate(False)

        self.valuation_labels = [
            Label(self.valuations_container) for valuation in valuations]
        for (idx, label) in enumerate(self.valuation_labels):
            title = valuations[idx]
            _percentage = self.algo.get_valuation(title)

            label.config(
                text=_percentage,
                foreground=self.algo.get_valuation_color(title),
                background=self.background
            )

        """
          Animations & Logic
        """

    """
        Logic
    """

    def has_barchart(self) -> bool:
        precision = self.algo.get_valuation("precision")
        recall = self.algo.get_valuation("recall")
        fmeasure = self.algo.get_valuation("fmeasure")

        if(precision > 0 and recall > 0 and fmeasure > 0):
            return True
        return False

    def _add_OnClick(self):
        self.bind("<Button-1>", self._onClick)
        self.icon_algorithm.bind("<Button-1>", self._onClick)
        self.content_container.bind("<Button-1>", self._onClick)
        self.label_name.bind("<Button-1>", self._onClick)
        self.label_description.bind("<Button-1>", self._onClick)
        self.label_setting.bind("<Button-1>", self._onClick)
        self.bar_chart_container.bind("<Button-1>", self._onClick)
        self.figure_container.bind("<Button-1>", self._onClick)
        self.valuations_container.bind("<Button-1>", self._onClick)
        for bar in self.bars:
            bar.bind("<Button-1>", self._onClick)
        for valuation_label in self.valuation_labels:
            valuation_label.bind("<Button-1>", self._onClick)
    """
        Animations
    """

    def _shade(self, event, **kwargs):
        self.config(background=GREY)
        self.icon_algorithm.config(background=GREY)
        self.content_container.config(background=GREY)
        self.label_name.config(background=GREY)
        self.label_description.config(background=GREY)
        self.label_setting.config(background=GREY)
        self.bar_chart_container.config(background=GREY)
        self.figure_container.config(background=GREY)
        self.valuations_container.config(background=GREY)

    def _light(self, event, **kwargs):
        light_color = self.background
        self.config(background=light_color)
        self.icon_algorithm.config(background=light_color)
        self.content_container.config(background=light_color)
        self.label_name.config(background=light_color)
        self.label_description.config(background=light_color)
        self.label_setting.config(background=light_color)
        self.bar_chart_container.config(background=light_color)
        self.figure_container.config(background=light_color)
        self.valuations_container.config(background=light_color)

    """
        Hiển thị
    """

    def _show_bar_chart(self):
        """
          Private: Hiển thị barchart
        """
        self.figure_container.grid(row=0, column=0, sticky="ne",)
        self.valuations_container.grid(row=0, column=1, sticky="nw",)

        pady = (PADDING, self.bar_height)
        for (idx, bar) in enumerate(self.bars):
            bar.grid(row=idx, column=0, sticky="ne",
                     pady=pady)

        for (idx, label) in enumerate(self.valuation_labels):
            label.grid(row=idx, column=0, sticky="nw",
                       pady=pady)

    def _show_content(self):
        self.label_name.grid(row=1, column=0, sticky="nw")
        self.label_setting.grid(row=2, column=0, sticky="nw")
        self.label_description.grid(row=3, column=0, sticky="nw")

    def _show(self):
        """
          Private: Hiển thị thẻ
        """
        # self.label.grid(row=1, column=0, sticky="nw",)
        self.icon_algorithm.grid(row=1, column=1, sticky="nw",)
        self.content_container.grid(row=1, column=2, sticky="nw",)
        self.bar_chart_container.grid(row=1, column=3, sticky="nw",)
        """
          Private: Hiển thị chart
        """

        if(self.has_barchart()):
            self._show_bar_chart()

        """
          Private: Hiển thị content
        """
        self._show_content()

    def show(self, props={}):
        """
          Public: hiển thị thẻ
        """

        self._show()

    def _onClick(self, event, **kwargs):

        self.onClick(algorithm=self.algo, idx=self.idx)
