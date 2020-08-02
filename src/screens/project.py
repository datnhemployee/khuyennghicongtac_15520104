
from tkinter import Label, Button, Canvas, PhotoImage, LEFT, Frame
from components.scrollable_screen import ScrollableScreen
from components.train_card import TrainCard
from components.warning_line import WarningLine
from components.button_back import ButtonBack
from utils.file import PRIOR_IMAGE, TEST_IMAGE, ICON_WARNING, ICON_ADD
from utils.image import RBGAImage
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, BLACK, GREY, ORANGE
from utils.font import TYPE_TITLE_SCREEN, TITLE_SCREEN, HEADER_1, BODY, HEADER_2, BUTTON
from utils.dimension import PADDING, SCROLL_BAR_WIDTH
from controllers.main import controller
# from models.algorithm import Algorithm


class Project(ScrollableScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

    def _before_init_components(self):
        """
          Hàm phụ trợ trước khi khởi tạo màn hình
        """
        self._init_scrollframe()
        # self.states = {
        #     "val": [
        #         2,
        #         5,
        #         6,
        #         7,
        #         8,
        #         15
        #     ],
        #     "training": None,
        #     "algorithms": [
        #         Algorithm(
        #             name="Node2vecA",
        #             descriptions="",
        #             setting={
        #                 "l": 80,
        #                 "p": 1,
        #                 "q": 1,
        #             },
        #             valuations={}
        #         ),
        #         Algorithm(
        #             name="Node2vecB",
        #             descriptions="",
        #             setting={
        #                 "l": 80,
        #                 "p": 0.5,
        #                 "q": 1,
        #             },
        #             valuations={
        #                 "precision": 0.35,
        #                 "recall": 0.35,
        #                 "fmeasure": 0.7,
        #             }
        #         ),
        #     ]
        # }

    def _init_components(self):
        """
            Khởi tạo các thành phần trên màn hình
        """
        background_color = self.get_background()

        button_back_size = PADDING * 3

        self.button_back = ButtonBack(
            self.container,
            size=button_back_size,
            onClick=self.navigate_Home
        )

        self.type_title = Label(self.container, text="DỰ ÁN",
                                # borderwidth=1,
                                # relief="solid"
                                )
        self.type_title.config(font=TYPE_TITLE_SCREEN,
                               background=background_color,
                               foreground=DARK_BLUE)

        self.title = Label(
            self.container, )
        self.title.config(font=TITLE_SCREEN,
                          background=background_color,
                          foreground=DARK_BLUE)

        self.header_database = Label(
            self.container, text="Tập dữ liệu")
        self.header_database.config(font=HEADER_1,
                                    background=background_color,
                                    foreground=BLUE)
        self._init_database_tab()

        self.header_experiments = Label(
            self.container, text="Thực nghiệm, đánh giá")
        self.header_experiments.config(font=HEADER_1,
                                       background=background_color,
                                       foreground=BLUE)
        self._init_experiments_tab()

        """
            button ADD: Thêm phương pháp
        """
        icon_add_size = int(PADDING * 4)
        button_add_width = self.app.width - SCROLL_BAR_WIDTH - PADDING * 2
        button_add_height = icon_add_size + PADDING * 2
        self.button_add = Frame(
            self.container, )
        self.button_add.config(
            height=button_add_height,
            width=button_add_width,
            background=background_color
        )

        self.button_add.grid_propagate(False)
        self.button_add.grid_rowconfigure(0, weight=1)
        self.button_add.grid_rowconfigure(2, weight=1)

        self.icon_add = Canvas(
            self.button_add,
            # borderwidth=0,
            # relief="solid"
        )
        self.icon_add.config(
            height=icon_add_size,
            width=icon_add_size,
            background=background_color,
            highlightthickness=0
        )

        self.icon_add_image = RBGAImage(
            ICON_ADD, size=icon_add_size)

        self.icon_add.create_image(
            0, 0, image=self.icon_add_image, anchor="nw")

        self.button_add_title = Label(
            self.button_add, text="Thêm phương pháp")
        self.button_add_title.config(font=BUTTON,
                                     background=background_color,
                                     foreground=BLACK)
        """
            button ADD - Animations & logic
        """
        self.button_add.bind("<Button-1>", self.navigate_AddAlgorithm)
        self.icon_add.bind(
            "<Button-1>", self.navigate_AddAlgorithm)
        self.button_add_title.bind(
            "<Button-1>", self.navigate_AddAlgorithm)

        # self.button_add.bind("<Button-1>", self._add_algorithm_Node2vec)
        # self.icon_add.bind(
        #     "<Button-1>", self._add_algorithm_Node2vec)
        # self.button_add_title.bind(
        #     "<Button-1>", self._add_algorithm_Node2vec)

        self.button_add.bind(
            "<Enter>", self._shade_button_add)
        self.button_add.bind(
            "<Leave>", self._light_button_add)

        """
            list algorithms: Danh sách phương pháp
        """
        self._init_list_algorithms()

        self.warning_line = None

        self.button_back_row = self.get_row_idx()
        self.type_title_row = self.get_next_row_idx()
        self.title_row = self.get_next_row_idx()
        self.header_database_row = self.get_next_row_idx()
        self.database_tab_row = self.get_next_row_idx()
        self.header_experiments_row = self.get_next_row_idx()
        self.experiments_bar_row = self.get_next_row_idx()
        self.button_add_row = self.get_next_row_idx()

    """
    Child Components
    """

    def _init_database_tab(self):
        """
        Tab Database Button: Tập huấn luyện và tập test
        """
        background_color = self.get_background()

        database_tab_width = self.app.width - PADDING * 2 - SCROLL_BAR_WIDTH
        database_tab_height = int(self.app.height / 2)
        self.database_tab = Frame(
            self.container,
            # borderwidth=1,
            # relief="solid"
        )
        self.database_tab.config(
            height=database_tab_height,
            width=database_tab_width,
            background=background_color
        )

        """
        Prior Database Button: Di chuyển đến màn hình tập huấn luyện
        """
        database_button_width = int(
            (database_tab_width / 2) - PADDING * 2)

        self.prior_database_button = Frame(self.database_tab)
        self.prior_database_button.config(
            height=database_tab_height,
            width=database_button_width,
            background=background_color
        )

        self.database_tab.grid_rowconfigure(
            0, minsize=database_tab_height, )
        self.database_tab.grid_columnconfigure(
            0, minsize=database_button_width, )
        self.database_tab.grid_columnconfigure(
            1, minsize=database_button_width, )

        self.prior_database_button.grid_propagate(False)

        """
        Prior Database Icon: Icon mạng huấn luyện
        """
        prior_database_image_container_width = int(
            database_button_width / 3)

        self.prior_database_image_container = Frame(
            self.prior_database_button,
        )
        self.prior_database_image_container.config(
            height=database_tab_height,
            width=prior_database_image_container_width,
            background=background_color
        )

        self.prior_database_image_container.grid_propagate(False)
        self.prior_database_image_container.grid_rowconfigure(0, weight=1)
        self.prior_database_image_container.grid_rowconfigure(2, weight=1)

        prior_database_image_size = int(
            prior_database_image_container_width - PADDING)

        self.prior_database_image = Canvas(
            self.prior_database_image_container,
            # borderwidth=0,
            # relief="solid"
        )
        self.prior_database_image.config(
            height=prior_database_image_size,
            width=prior_database_image_size,
            background=background_color,
            highlightthickness=0
        )

        self.prior_database_image_icon = RBGAImage(
            PRIOR_IMAGE, size=prior_database_image_size)

        self.prior_database_image.create_image(
            0, 0, image=self.prior_database_image_icon, anchor="nw")

        """
        Prior Database Content: Nội dung tập huấn luyện
        """
        prior_database_content_container_width = int(
            database_button_width - prior_database_image_container_width - PADDING)

        self.prior_database_content_container = Frame(
            self.prior_database_button,)
        self.prior_database_content_container.config(
            height=database_tab_height,
            width=prior_database_content_container_width,
            background=background_color
        )

        self.prior_database_content_container.grid_propagate(False)
        self.prior_database_content_container.grid_rowconfigure(0, weight=1)
        self.prior_database_content_container.grid_rowconfigure(3, weight=1)

        self.prior_database_title = Label(
            self.prior_database_content_container, text="Tập huấn luyện")
        self.prior_database_title.config(font=HEADER_2,
                                         background=background_color,
                                         foreground=DARK_BLUE)

        self.prior_database_description = Label(
            self.prior_database_content_container,
            justify="left"
        )
        self.prior_database_description.config(font=BODY,
                                               background=background_color,
                                               foreground=BLACK,
                                               wraplengt=prior_database_content_container_width,
                                               )

        """
        Test Database Button: Di chuyển đến màn hình tập huấn luyện
        """
        self.test_database_button = Frame(self.database_tab)
        self.test_database_button.config(
            height=database_tab_height,
            width=database_button_width,
            background=background_color
        )

        self.test_database_button.grid_propagate(False)

        """
        Test Database Icon: Icon tập đánh giá
        """

        self.test_database_image_container = Frame(
            self.test_database_button,
        )
        self.test_database_image_container.config(
            height=database_tab_height,
            width=prior_database_image_container_width,
            background=background_color
        )

        self.test_database_image_container.grid_propagate(False)
        self.test_database_image_container.grid_rowconfigure(0, weight=1)
        self.test_database_image_container.grid_rowconfigure(2, weight=1)

        self.test_database_image = Canvas(
            self.test_database_image_container,
            # borderwidth=0,
            # relief="solid"
        )
        self.test_database_image.config(
            height=prior_database_image_size,
            width=prior_database_image_size,
            background=background_color,
            highlightthickness=0
        )

        self.test_database_image_icon = RBGAImage(
            TEST_IMAGE, size=prior_database_image_size)

        self.test_database_image.create_image(
            0, 0, image=self.test_database_image_icon, anchor="nw")

        """
        Test Database Content: Nội dung tập đánh giá
        """

        self.test_database_content_container = Frame(
            self.test_database_button,)
        self.test_database_content_container.config(
            height=database_tab_height,
            width=prior_database_content_container_width,
            background=background_color
        )

        self.test_database_content_container.grid_propagate(False)
        self.test_database_content_container.grid_rowconfigure(0, weight=1)
        self.test_database_content_container.grid_rowconfigure(3, weight=1)

        self.test_database_title = Label(
            self.test_database_content_container, text="Tập đánh giá")
        self.test_database_title.config(font=HEADER_2,
                                        background=background_color,
                                        foreground=DARK_BLUE)

        self.test_database_description = Label(
            self.test_database_content_container,
            justify="left"
        )
        self.test_database_description.config(font=BODY,
                                              background=background_color,
                                              foreground=BLACK,
                                              wraplengt=prior_database_content_container_width,
                                              )

    def _init_experiments_tab(self):
        """
        Tab Experiments Icons Bar: Thanh giải thích kí hiệu
        """
        background_color = self.get_background()

        experiments_bar_width = self.app.width - PADDING * 2 - SCROLL_BAR_WIDTH
        experiments_bar_height = PADDING * 2
        self.experiments_bar = Frame(
            self.container,
        )
        self.experiments_bar.config(
            height=experiments_bar_height,
            width=experiments_bar_width,
            background=background_color
        )

        """
        Precision Icons: Kí hiệu Precision
        """

        icon_width = experiments_bar_height
        self.precision_rec = Frame(self.experiments_bar)
        self.precision_rec.config(
            height=icon_width,
            width=icon_width,
            background=DARK_BLUE
        )

        self.precision_rec.grid_propagate(False)

        self.presicion_tag = Label(
            self.experiments_bar, text="Precision")
        self.presicion_tag.config(font=BODY,
                                  background=background_color,
                                  foreground=DARK_BLUE)

        """
        Recall Icons: Kí hiệu Recall
        """

        self.recall_rec = Frame(self.experiments_bar)
        self.recall_rec.config(
            height=icon_width,
            width=icon_width,
            background=BLUE
        )

        self.recall_rec.grid_propagate(False)

        self.recall_tag = Label(
            self.experiments_bar, text="Recall")
        self.recall_tag.config(font=BODY,
                               background=background_color,
                               foreground=BLUE)

        """
        F-measure Icons: Kí hiệu F-measure
        """

        self.fmeasure_rec = Frame(self.experiments_bar)
        self.fmeasure_rec.config(
            height=icon_width,
            width=icon_width,
            background=LIGHT_BLUE
        )

        self.fmeasure_rec.grid_propagate(False)

        self.fmeasure_tag = Label(
            self.experiments_bar, text="F-measure")
        self.fmeasure_tag.config(font=BODY,
                                 background=background_color,
                                 foreground=LIGHT_BLUE)

    def _init_list_algorithms(self):
        """
        Khởi tạo danh sách phương pháp thực nghiệm đánh giá
        """
        train_card_width = self.app.width - 2 * PADDING - SCROLL_BAR_WIDTH
        train_card_height = self.app.height / 3
        self.train_cards = [
            TrainCard(
                self.container,
                idx=idx,
                onClick=self.navigate_Experiment,
                height=train_card_height,
                width=train_card_width,
                background=self.get_background(),
                algo=controller.mapAlgorithm(algo),
            ) for (idx, algo) in enumerate(controller.project.algorithms)
        ]

    """
    Navigations
    """

    def navigate_AddAlgorithm(self, event, **kwargs):
        print("Di chuyển đến màn hình AddAlgorithm")
        kwargs["context"] = "AddAlgorithm"
        self.app.navigate(**kwargs)

    def navigate_Experiment(self, **kwargs):
        print("Di chuyển đến màn hình Experiment")
        kwargs["context"] = "Experiments"
        self.app.navigate(**kwargs)

    def navigate_Home(self, ):
        print("Di chuyển đến màn hình Home")
        self.app.navigate(context="Home")

    """
    Logic
    """

    def get_project(self, project):
        controller.get_project(project.uid)

    def update_title(self,):
        project = controller.project
        self.title.grid_forget()
        self.title.config(text=project.name)

    def update_tab_database(self, ):
        project = controller.project
        num_prior_author = project.get_prior_num_author()
        num_prior_paper = project.get_prior_num_paper()
        num_prior_connection = project.get_prior_num_connection()

        num_test_graph_author = project.get_test_graph_num_author()
        num_test_graph_paper = project.get_test_graph_num_paper()
        num_test_graph_connection = project.get_test_graph_num_connection()

        prior_start = project.get_prior_start()
        prior_end = project.get_prior_end()

        text_prior = """
            Gồm {num_author} nghiên cứu viên với điều kiện:
            1. Là tác giả ít nhất 1 bài báo {prior_start}-{prior_end}.
            2. Bài báo đó có ít nhất 1 đồng tác giả.
            
            Xây dựng mạng huấn luyện:
                CoNet_1=(U_1,Co_1).
            Trong đó:
            + |U_1|: {num_author} nghiên cứu viên.
            + {num_paper} bài báo.
            + |Co_1|: {num_connection} liên kết""".format(
            prior_start=prior_start,
            prior_end=prior_end,
            num_author=num_prior_author,
            num_paper=num_prior_paper,
            num_connection=num_prior_connection,
        ).replace("{", "").replace("}", "")

        self.prior_database_description.config(text=text_prior)

        test_start = project.get_test_start()
        test_end = project.get_test_end()

        test_year = "{test_start}-{test_end}".format(
            test_start=test_start, test_end=test_end)
        if (test_start == test_end):
            test_year = "{test_start}".format(
                test_start=test_start,)

        text_test = """
            Gồm {num_graph_author} nghiên cứu viên với điều kiện:
            1. Từ tập huấn luyện.
            2. Là tác giả ít nhất 1 bài báo {test_year}.
            3. Mỗi bài báo có ít nhất 1 đồng tác giả.

            Xây dựng mạng đánh giá:
                CoNet_2=(U_2,Co_2)
            Trong đó:
            + |U_2|: {num_graph_author} nghiên cứu viên.
            (U_2 là tập con của U_1)
            + {num_graph_paper} bài báo.
            + |Co_2|: {num_graph_connection} liên kết (thực sự)""".format(
            num_graph_author=num_test_graph_author,
            num_graph_paper=num_test_graph_paper,
            num_graph_connection=num_test_graph_connection,
            test_year=test_year,
        ).replace("{", "").replace("}", "")

        self.test_database_description.config(text=text_test)

    def update_list_algorithms(self, ):
        self._init_list_algorithms()

    # def _add_algorithm_Node2vec(self, event, **kwargs):
    #     from models.node2vec import Node2vec
    #     algorithm = Node2vec(controller.next_id, p=0.5)
    #     controller.save(algorithm, self.update_list_algorithms)

    # def cb_end(self,):
    #     controller.training = -1
    #     self.update_list_algorithms()

    # def on_error(self, err: Exception):
    #     controller.training = -1
    #     print("error", err)
    #     self.update_list_algorithms()

    # def train_card_onClick(self, algorithm, idx):
    #     controller.train(algorithm, cb_check=self.update_list_algorithms,
    #                      cb_end=self.cb_end, on_error=self.on_error)

    # def do_stuff_task(self, **kwargs):
    #     import time
    #     idx = kwargs.get("idx", None)
    #     oldVal = (self.states["val"])[idx]
    #     print("do_stuff_task", kwargs)
    #     time.sleep(2)
    #     return {
    #         "has_error": False,
    #         "val": {
    #             "oldVal": (self.states["val"])[idx],
    #             "idx": idx,
    #         }
    #     }

    # def do_stuff_callback(self, **kwargs):
    #     has_error = kwargs.get("has_error", True)
    #     print("do_stuff_callback", kwargs)
    #     if (has_error != True):
    #         result = kwargs.get("val")
    #         oldVal = result.get("oldVal")
    #         idx = result.get("idx")
    #         (self.states["val"])[idx] = oldVal + 1
    #         self.train_cards[idx].update_label(val=(self.states["val"])[idx])
    #         print("do", (self.states["val"])[idx])

    # def do_stuff(self, **kwargs):
    #     from controllers.excution import excute
    #     kwargs["task"] = self.do_stuff_task
    #     kwargs["callback"] = self.do_stuff_callback
    #     excute(kwargs)

    """
    Animations
    """

    def _shade_prior_database_button(self,  event, **kwargs):
        self.prior_database_button.config(background=GREY)
        self.prior_database_image_container.config(background=GREY)
        self.prior_database_image.config(background=GREY)
        self.prior_database_content_container.config(background=GREY)
        self.prior_database_title.config(background=GREY)
        self.prior_database_description.config(background=GREY)

    def _light_prior_database_button(self,  event, **kwargs):
        light_color = self.get_background()
        self.prior_database_button.config(background=light_color)
        self.prior_database_image_container.config(background=light_color)
        self.prior_database_image.config(background=light_color)
        self.prior_database_content_container.config(background=light_color)
        self.prior_database_title.config(background=light_color)
        self.prior_database_description.config(background=light_color)

    def _shade_test_database_button(self,  event, **kwargs):
        self.test_database_button.config(background=GREY)
        self.test_database_image_container.config(background=GREY)
        self.test_database_image.config(background=GREY)
        self.test_database_content_container.config(background=GREY)
        self.test_database_title.config(background=GREY)
        self.test_database_description.config(background=GREY)

    def _light_test_database_button(self,  event, **kwargs):
        light_color = self.get_background()
        self.test_database_button.config(background=light_color)
        self.test_database_image_container.config(background=light_color)
        self.test_database_image.config(background=light_color)
        self.test_database_content_container.config(background=light_color)
        self.test_database_title.config(background=light_color)
        self.test_database_description.config(background=light_color)

    def _shade_button_add(self,  event, **kwargs):
        self.button_add.config(background=GREY)
        self.icon_add.config(background=GREY)
        self.button_add_title.config(background=GREY)

    def _light_button_add(self,  event, **kwargs):
        light_color = self.get_background()
        self.button_add.config(background=light_color)
        self.icon_add.config(background=light_color)
        self.button_add_title.config(background=light_color)

    """
    Hiển thị components
    """

    def _show_button_back(self):
        self.button_back.grid(row=self.button_back_row, column=0, sticky="nw",)
        self.button_back.show_components()

    def _show_type_title(self):
        self.type_title.grid(row=self.type_title_row, column=0, sticky="nw",
                             pady=(PADDING, 0),  padx=(PADDING, 0))

    def _show_title(self):
        self.title.grid(row=self.title_row, column=0, sticky="nw",
                        padx=(PADDING, 0))

    def _show_header_database(self):
        self.header_database.grid(row=self.header_database_row, column=0, sticky="nw",
                                  pady=(PADDING, 0), padx=(PADDING, 0))

    def _show_database_tab(self):
        self.database_tab.grid(row=self.database_tab_row, column=0, sticky="nw",
                               pady=(PADDING, 0), padx=(PADDING, 0))

    def _show_header_experiments(self):
        self.header_experiments.grid(row=self.header_experiments_row, column=0, sticky="nw",
                                     pady=(PADDING, 0), padx=(PADDING, 0))

    def _show_prior_database_button(self):
        self.prior_database_button.grid(
            row=0, column=0, sticky="nw", padx=(PADDING, 0))
        self.prior_database_image_container.grid(
            row=0, column=0, sticky="nw", padx=(PADDING, 0))
        self.prior_database_image.grid(
            row=1, column=0, sticky="nw")

        self.prior_database_content_container.grid(
            row=0, column=1, sticky="nw", padx=(PADDING, 0))
        self.prior_database_title.grid(
            row=1, column=0, sticky="nw", )
        self.prior_database_description.grid(
            row=2, column=0, sticky="nw", )

    def _show_test_database_button(self):
        self.test_database_button.grid(
            row=0, column=1, sticky="nw", padx=(PADDING, 0))
        self.test_database_image_container.grid(
            row=0, column=0, sticky="nw", padx=(PADDING, 0))
        self.test_database_image.grid(
            row=1, column=0, sticky="nw")

        self.test_database_content_container.grid(
            row=0, column=1, sticky="nw", padx=(PADDING, 0))
        self.test_database_title.grid(
            row=1, column=0, sticky="nw", )
        self.test_database_description.grid(
            row=2, column=0, sticky="nw", )

    def _show_experiments_bar(self):
        self.experiments_bar.grid(
            row=self.experiments_bar_row, column=0, sticky="nw", pady=(PADDING, PADDING), padx=(PADDING, PADDING))
        self.precision_rec.grid(
            row=0, column=0, sticky="nw", padx=(PADDING, 0))
        self.presicion_tag.grid(
            row=0, column=1, sticky="nw", padx=(PADDING, PADDING))

        self.recall_rec.grid(
            row=0, column=2, sticky="nw", padx=(PADDING * 2, 0))
        self.recall_tag.grid(
            row=0, column=3, sticky="nw", padx=(PADDING, PADDING))

        self.fmeasure_rec.grid(
            row=0, column=4, sticky="nw", padx=(PADDING * 2, 0))
        self.fmeasure_tag.grid(
            row=0, column=5, sticky="nw", padx=(PADDING, PADDING))

    def _show_button_add(self):
        self.button_add.grid(row=self.button_add_row, column=0, sticky="nw",
                             pady=(PADDING * 2, PADDING * 2), padx=(PADDING, 0))
        self.icon_add.grid(row=1, column=0, sticky="nw", padx=(PADDING, 0))
        self.button_add_title.grid(
            row=1, column=1, sticky="nw", padx=(PADDING, 0))

    def _show_train_cards(self):
        for (idx, train_card) in enumerate(self.train_cards):
            train_card.grid(row=self.button_add_row + idx + 1, column=0, sticky="nw",
                            pady=(PADDING, 0), padx=(PADDING, 0))
            train_card.show()

    def _show_warning_line(self, text):
        self.warning_line = WarningLine(self.container, text=text)
        self.warning_line.grid(row=self.button_add_row +
                               len(self.train_cards) + 1, column=0, sticky="nw")
        self.warning_line.show_components()

    def _hide_warning_line(self, ):
        if (self.warning_line is not None):
            self.warning_line.grid_forget()
            self.warning_line.destroy()

    def _show(self, **kwargs):

        project = kwargs.get("project", None)
        self._hide_warning_line()
        if (project is None):
            self._show_warning_line("Không tìm thấy dự án tương ứng.")
        else:
            # for key in kwargs.keys():
            #     print("key", key, kwargs.get(key))
            self.get_project(project)
            self.update_title()
            self.update_tab_database()
            self.update_list_algorithms()

            self._show_button_back()
            self._show_type_title()
            self._show_title()

            self._show_header_database()
            self._show_database_tab()
            self._show_prior_database_button()
            self._show_test_database_button()

            self._show_header_experiments()
            self._show_experiments_bar()
            self._show_button_add()
            self._show_train_cards()
