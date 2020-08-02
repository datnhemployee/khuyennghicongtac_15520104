from tkinter import Label, Canvas, PhotoImage, LEFT, Frame
from components.scrollable_screen import ScrollableScreen
from components.button_back import ButtonBack
from components.algorithm_card import AlgorithmCard
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, BLACK, GREY, ORANGE, WHITE
from utils.font import TYPE_TITLE_SCREEN, TITLE_SCREEN, HEADER_1, BODY, HEADER_2, BUTTON
from utils.dimension import PADDING, SCROLL_BAR_WIDTH
# from models.algorithm import Algorithm
from controllers.main import controller
from controllers.excution import excute
# algorithms
from models.node2vec import Node2vec
from models.common_neighbor import CommonNeighbor
from models.jaccard import Jaccard
from models.adamic import Adamic
from models.content_based import ContentBased


class AddAlgorithm(ScrollableScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

    def _before_init_components(self):
        super()._before_init_components()

        self.list_algorithms = []

    def _init_components(self):
        background_color = self.get_background()
        button_back_size = PADDING * 3

        self.button_back = ButtonBack(
            self.container,
            size=button_back_size,
            onClick=self.navigate_Home
        )

        self.label_screenName = Label(
            self.container, text="Thêm phương pháp")
        self.label_screenName.config(font=TITLE_SCREEN,
                                     background=background_color,
                                     foreground=DARK_BLUE)

    def _init_list_algorithm_cards(self):
        background_color = self.get_background()
        designable_width = self.app.width - PADDING * 2
        algorithm_card_height = int(self.app.height / 3)

        self.list_algorithm_cards = [
            AlgorithmCard(self.container,
                          idx=idx,
                          height=algorithm_card_height,
                          width=designable_width,
                          background=background_color,
                          algorithm=algorithm,
                          onClick=self.add_algorithm,
                          onClick_Detail=None,
                          onClick_Setting=self.navigate_AddSettings,
                          ) for (idx, algorithm) in enumerate(self.list_algorithms)]

    def navigate_Home(self, **kw):
        self.app.navigate("Project", project=controller.project)

    def add_algorithm(self, algorithm):
        controller.add_algorithm(algorithm)
        self.app.navigate("Project", project=controller.project)

    def navigate_AddSettings(self, algorithm):
        self.app.navigate(context="AddSettings", algorithm=algorithm)

    def _show_list_algorithm_cards(self):
        for (idx, algorithm_card) in enumerate(self.list_algorithm_cards):
            algorithm_card.grid(row=2 + idx, column=0, sticky="nw")
            algorithm_card.show_components()

    def _screenWillShow(self, **kwargs):
        super()._screenWillShow(**kwargs)
        self.list_algorithms = [
            Node2vec(),
            CommonNeighbor(),
            Jaccard(),
            Adamic(),
            ContentBased()
        ]
        self._init_list_algorithm_cards()

    def _show(self, **kw):

        self.button_back.grid(row=0, column=0, sticky="nw")
        self.button_back.show_components()

        self.label_screenName.grid(
            row=1, column=0, sticky="nw")

        self._show_list_algorithm_cards()
