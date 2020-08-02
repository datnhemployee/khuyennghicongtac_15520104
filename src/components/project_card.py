from tkinter import Frame, Canvas, Label
from PIL import Image, ImageTk
from utils.dimension import PADDING
from utils.image import RBGAImage
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, WHITE, BLACK, GREY
from utils.font import BODY, HEADER_2
from models.project import Project


class ProjectCard(Frame):
    def __init__(self, parent, idx: int, onClick, height: int, width: int, background: str, project: Project, ):
        super().__init__(master=parent)
        self.config(background=WHITE)
        self.idx = idx

        self.height = height
        self.width = width
        self.background = background

        self.project = project

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
        )

        """
        Content
        """
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_propagate(False)

        self._init_content()

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
        wrap_text_length = self.width

        project_name = self.project.name
        prior_database = "Tập huấn luyện: {0}-{1}".format(
            self.project.get_prior_start(),
            self.project.get_prior_end(),
        )
        test_database = "Tập đánh giá: {0}-{1}".format(
            self.project.get_test_start(),
            self.project.get_test_end(),
        )
        if (self.project.get_test_end() == self.project.get_test_start()):
            test_database = "Tập đánh giá: {0}".format(
                self.project.get_test_start(),
            )

        self.label_name = Label(self)
        self.label_name.config(
            text=project_name,
            justify="left",
            font=HEADER_2,
            background=self.background,
            foreground=DARK_BLUE,
            wraplengt=wrap_text_length,
        )

        self.label_setting = Label(self)
        self.label_setting.config(
            text=prior_database,
            justify="left",
            font=BODY,
            background=self.background,
            foreground=BLACK,
            wraplengt=wrap_text_length,
        )

        self.label_description = Label(self)
        self.label_description.config(
            text=test_database,
            justify="left",
            font=BODY,
            background=self.background,
            foreground=BLACK,
            wraplengt=wrap_text_length,
        )

    """
        Logic
    """

    def _add_OnClick(self):
        self.bind("<Button-1>", self._onClick)
        self.label_name.bind("<Button-1>", self._onClick)
        self.label_description.bind("<Button-1>", self._onClick)
        self.label_setting.bind("<Button-1>", self._onClick)

    """
        Animations
    """

    def _shade(self, event, **kwargs):
        self.config(background=GREY)
        self.label_name.config(background=GREY)
        self.label_description.config(background=GREY)
        self.label_setting.config(background=GREY)

    def _light(self, event, **kwargs):
        light_color = self.background
        self.config(background=light_color)
        self.label_name.config(background=light_color)
        self.label_description.config(background=light_color)
        self.label_setting.config(background=light_color)

    """
        Hiển thị
    """

    def _show_content(self):
        self.label_name.grid(row=1, column=0, sticky="nw")
        self.label_setting.grid(row=2, column=0, sticky="nw")
        self.label_description.grid(row=3, column=0, sticky="nw")

    def _show(self):
        """
          Private: Hiển thị thẻ
        """

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
        self.onClick(project=self.project, idx=self.idx)
