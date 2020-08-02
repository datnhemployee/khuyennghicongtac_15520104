
from tkinter import Label, Canvas, PhotoImage, LEFT, Frame
from components.scrollable_screen import ScrollableScreen
from components.button import Button
from components.project_card import ProjectCard
from utils.file import PRIOR_IMAGE, TEST_IMAGE, ICON_WARNING, ICON_ADD
from utils.image import RBGAImage
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, BLACK, GREY, ORANGE
from utils.font import TYPE_TITLE_SCREEN, TITLE_SCREEN, HEADER_1, BODY, HEADER_2, BUTTON
from utils.dimension import PADDING, SCROLL_BAR_WIDTH
from controllers.main import controller
# from models.algorithm import Algorithm


class Home(ScrollableScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

    def _init_database(self):
        from controllers.main import controller
        controller.get_all_projects()

    def _screenWillShow(self, **kwargs):
        super()._screenWillShow(**kwargs)
        self._init_database()
        self.update_list_project()

    def _init_components(self):
        """
            Khởi tạo các thành phần trên màn hình
        """
        background_color = self.get_background()

        self.type_title = Label(self.container, text="ĐỀ TÀI",
                                # borderwidth=1,
                                # relief="solid"
                                )
        self.type_title.config(font=TYPE_TITLE_SCREEN,
                               background=background_color,
                               foreground=DARK_BLUE)

        self.title = Label(
            self.container, text="KHUYẾN NGHỊ CỘNG TÁC DỰA TRÊN TIẾP CẬN HỌC SÂU")
        self.title.config(font=TITLE_SCREEN,
                          background=background_color,
                          foreground=DARK_BLUE)

        self.header_about = Label(
            self.container, text="Giới thiệu")
        self.header_about.config(font=HEADER_1,
                                 background=background_color,
                                 foreground=BLUE)
        self._init_about_tab()

        self.label_project = Label(
            self.container, text="Dự án")
        self.label_project.config(font=HEADER_1,
                                  background=background_color,
                                  foreground=BLUE)

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
            self.button_add, text="Thêm dự án")
        self.button_add_title.config(font=BUTTON,
                                     background=background_color,
                                     foreground=BLACK)
        """
            button ADD - Animations & logic
        """

        self.button_add.bind("<Button-1>", self.navigate_Add)
        self.icon_add.bind(
            "<Button-1>", self.navigate_Add)
        self.button_add_title.bind(
            "<Button-1>", self.navigate_Add)

        self.button_add.bind(
            "<Enter>", self._shade_button_add)
        self.button_add.bind(
            "<Leave>", self._light_button_add)

        """
            list algorithms: Danh sách phương pháp
        """
        self._init_list_project()

    """
    Child Components
    """

    def _init_about_tab(self):
        background_color = self.get_background()

        about_tab_width = self.app.width - PADDING * 2 - SCROLL_BAR_WIDTH
        about_tab_height = int(self.app.height / 3)
        self.about_tab = Frame(
            self.container,
        )
        self.about_tab.config(
            height=about_tab_height,
            width=about_tab_width,
            background=background_color
        )

        self.container.grid_rowconfigure(3, minsize=about_tab_height, )

        """
            Problem button: Bài toán khuyến nghị cộng tác
        """
        self.DELIMINATOR = PADDING
        about_problem_button_width = int(
            (about_tab_width / 3) - self.DELIMINATOR * 3)

        self.about_problem_button = Frame(self.about_tab)
        self.about_problem_button.config(
            height=about_tab_height,
            width=about_problem_button_width,
            background=background_color
        )

        problem_content_width = int(
            about_problem_button_width - PADDING * 2)
        self.about_tab.grid_rowconfigure(
            0, minsize=about_tab_height, )
        self.about_tab.grid_columnconfigure(
            0, minsize=problem_content_width, )
        self.about_tab.grid_columnconfigure(
            1, minsize=problem_content_width, )
        self.about_tab.grid_columnconfigure(
            2, minsize=problem_content_width, )

        self.about_problem_button.grid_propagate(False)

        self.type_about_problem = Label(
            self.about_problem_button, text="BÀI TOÁN")
        self.type_about_problem.config(font=BODY,
                                       background=background_color,
                                       foreground=DARK_BLUE)

        self.title_about_problem = Label(
            self.about_problem_button, text="Khuyến nghị cộng tác")
        self.title_about_problem.config(font=HEADER_2,
                                        background=background_color,
                                        foreground=DARK_BLUE)

        self.description_about_problem = Label(
            self.about_problem_button,
            text="Input: \n+ U: tập nghiên cứu viên, \n+ P: tập bài báo" +
            "\nOutput: Với mỗi nghiên cứu viên u," +
            "\nkhuyến nghị topK nghiên cứu viên cho u."
        )
        self.description_about_problem.config(
            font=BODY,
            background=background_color,
            foreground=BLACK,
            wraplength=problem_content_width,
            justify="left"
        )

        """
            Thêm logic & animation vào Problem button
        """
        self.about_problem_button.bind(
            "<Button-1>", self.navigate_About_Problem)
        self.type_about_problem.bind("<Button-1>", self.navigate_About_Problem)
        self.title_about_problem.bind(
            "<Button-1>", self.navigate_About_Problem)
        self.description_about_problem.bind(
            "<Button-1>", self.navigate_About_Problem)
        self.about_problem_button.bind(
            "<Enter>", self._shade_about_problem_button)
        self.about_problem_button.bind(
            "<Leave>", self._light_about_problem_button)

        """
            Instruction button: Hướng dẫn sử dụng
        """
        self.tabInstruction = Frame(self.about_tab)
        self.tabInstruction.config(
            height=about_tab_height,
            width=about_problem_button_width,
            background=background_color
        )

        self.tabInstruction.grid_propagate(False)

        self.instruction_title = Label(
            self.tabInstruction, text="Hướng dẫn sử dụng")
        self.instruction_title.config(font=HEADER_2,
                                      background=background_color,
                                      foreground=DARK_BLUE)

        self.instruction_description = Label(
            self.tabInstruction,
            text="Vui lòng xem chi tiết trong tệp pdf ",
            justify="left"
        )
        self.instruction_description.config(font=BODY,
                                            background=background_color,
                                            foreground=BLACK,
                                            wraplengt=problem_content_width,
                                            )

        self.btnInstruction = Button(
            self.tabInstruction,
            width=int(about_problem_button_width / 2),
            height=BUTTON[1] + PADDING * 2,
            text="Mở PDF",
            enable=True,
            onClick=self.openInstruction
        )
        """
            General button: Giới thiệu chung
        """
        self.tabGeneral = Frame(self.about_tab)
        self.tabGeneral.config(
            height=about_tab_height,
            width=about_problem_button_width,
            background=background_color
        )

        self.tabGeneral.grid_propagate(False)

        self.general_title = Label(
            self.tabGeneral, text="Giới thiệu chung")
        self.general_title.config(font=HEADER_2,
                                  background=background_color,
                                  foreground=DARK_BLUE)

        self.general_description = Label(
            self.tabGeneral,
            text="GVHD: TS.Huỳnh Ngọc Tín" +
            "\nNhóm thực hiện: 15520104 – Nguyễn Hữu Đạt" +
            "\nVui lòng xem chi tiết bản PDF",
            justify="left"
        )
        self.general_description.config(font=BODY,
                                        background=background_color,
                                        foreground=BLACK,
                                        wraplengt=problem_content_width,
                                        )

        self.btnGeneral = Button(
            self.tabGeneral,
            width=int(about_problem_button_width / 2),
            height=BUTTON[1] + PADDING * 2,
            text="Mở PDF",
            enable=True,
            onClick=self.openReport
        )

    def _init_list_project(self):
        """
        Khởi tạo danh sách phương pháp thực nghiệm đánh giá
        """
        project_card_width = self.app.width - 2 * PADDING - SCROLL_BAR_WIDTH
        project_card_height = self.app.height / 3
        self.project_cards = [
            ProjectCard(
                self.container,
                idx=idx,
                onClick=self.navigate_Project,
                height=project_card_height,
                width=project_card_width,
                background=self.get_background(),
                project=project,
            ) for (idx, project) in enumerate(controller.database.projects)
        ]

    """
    Navigations
    """

    def navigate_About_Problem(self, event, **kwargs):
        self.app.navigate(context="About", title="Problem")

    def navigate_PriorGraph(self, event, **kwargs):
        self.app.navigate("PriorGraph")

    def navigate_TestGraph(self, event, **kwargs):
        print("Di chuyển đến màn hình TestGraph")

    def navigate_Add(self, event, **kwargs):
        print("Di chuyển đến màn hình AddProject")
        kwargs["context"] = "AddProject"
        self.app.navigate(**kwargs)

    def navigate_Project(self, **kwargs):
        kwargs["context"] = "Project"
        print("Di chuyển đến màn hình Project", )

        self.app.navigate(**kwargs)

    """
    Logic
    """

    def openInstruction(self):
        controller.openInstruction()

    def openReport(self):
        controller.openReport()

    def update_list_project(self):
        self._init_list_project()
        self._show()

    """
    Animations
    """

    def _shade_about_problem_button(self,  event, **kwargs):
        self.about_problem_button.config(background=GREY)
        self.title_about_problem.config(background=GREY)
        self.type_about_problem.config(background=GREY)
        self.description_about_problem.config(background=GREY)

    def _light_about_problem_button(self,  event, **kwargs):
        light_color = self.get_background()
        self.about_problem_button.config(background=light_color)
        self.title_about_problem.config(background=light_color)
        self.type_about_problem.config(background=light_color)
        self.description_about_problem.config(background=light_color)

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

    def _show_type_title(self):
        # self.title.pack(side="left")
        self.type_title.grid(row=0, column=0, sticky="nw",
                             pady=(PADDING, 0),  padx=(PADDING, 0))

    def _show_title(self):
        self.title.grid(row=1, column=0, sticky="nw",
                        padx=(PADDING, 0))

    def _show_header_about(self):
        self.header_about.grid(row=2, column=0, sticky="nw",
                               pady=(PADDING, 0), padx=(PADDING, 0))

    def _show_about_tab(self):
        self.about_tab.grid(row=3, column=0, sticky="nw",
                            pady=(PADDING, 0), padx=(PADDING, 0))

    def _show_label_project(self):
        self.label_project.grid(row=4, column=0, sticky="nw",
                                pady=(PADDING, 0), padx=(PADDING, 0))

    def _show_about_problem_button(self):
        self.about_problem_button.grid(
            row=0, column=0, sticky="nw", padx=(PADDING, PADDING))
        self.type_about_problem.grid(
            row=0, column=0, sticky="nw", padx=(PADDING, PADDING))
        self.title_about_problem.grid(
            row=1, column=0, sticky="nw", padx=(PADDING, PADDING))
        self.description_about_problem.grid(
            row=2, column=0, sticky="nw", padx=(PADDING, PADDING), pady=(PADDING, 0))

    def _show_instruction_button(self):
        self.tabInstruction.grid(
            row=0, column=1, sticky="nw", padx=(PADDING, PADDING))
        self.instruction_title.grid(
            row=0, column=0, sticky="nw", padx=(PADDING, PADDING))
        self.instruction_description.grid(
            row=1, column=0, sticky="nw", padx=(PADDING, PADDING), pady=(PADDING, 0))
        self.btnInstruction.grid(
            row=2, column=0, sticky="nw", padx=(PADDING, PADDING), pady=(PADDING, 0))
        self.btnInstruction.show_components()

    def _show_general_button(self):
        self.tabGeneral.grid(
            row=0, column=2, sticky="nw", padx=(PADDING, PADDING))
        self.general_title.grid(
            row=0, column=0, sticky="nw", padx=(PADDING, PADDING))
        self.general_description.grid(
            row=1, column=0, sticky="nw", padx=(PADDING, PADDING), pady=(PADDING, 0))
        self.btnGeneral.grid(
            row=2, column=0, sticky="nw", padx=(PADDING, PADDING), pady=(PADDING, 0))
        self.btnGeneral.show_components()

    def _show_button_add(self):
        self.button_add.grid(row=8, column=0, sticky="nw",
                             pady=(PADDING * 2, PADDING * 2), padx=(PADDING, 0))
        self.icon_add.grid(row=1, column=0, sticky="nw", padx=(PADDING, 0))
        self.button_add_title.grid(
            row=1, column=1, sticky="nw", padx=(PADDING, 0))

    def _show_project_cards(self):
        for (idx, project_card) in enumerate(self.project_cards):
            project_card.grid(row=9 + idx, column=0, sticky="nw",
                              pady=(PADDING, 0), padx=(PADDING, 0))
            project_card.show()

    def _show(self, **kwargs):
        self._show_type_title()
        self._show_title()

        self._show_header_about()
        self._show_about_tab()
        self._show_about_problem_button()
        self._show_instruction_button()
        self._show_general_button()

        self._show_label_project()

        self._show_button_add()
        self._show_project_cards()
        # self._show_button_priorGraph()
        # self._show_button_run()
        # self._show_button_test()
