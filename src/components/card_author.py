from tkinter import Frame, Label, StringVar
from PIL import Image, ImageTk

from utils.font import TITLE_SCREEN, BODY, BUTTON
from utils.file import ICON_RESEARCHER
from utils.color import GREY, DARK_GREY, BLACK, WHITE, BLUE
from utils.dimension import PADDING, BORDER_WITH
from utils.image import RBGAImage

from models.author import Author


class CardAuthor(Frame):
    def __init__(self, parent,  author: Author, clickable=False, on_click=None):
        super().__init__(master=parent)
        self.author = author
        self.clickable = clickable
        self.on_click = on_click

        self._init_components()

    def get_default_background(self):
        return WHITE

    def get_foreground(self):
        return BLUE

    def _init_components(self, ):
        """
          Khởi tạo các thành phần trên nút
        """
        icon_size = (BUTTON[1] + PADDING * 2) * 3

        self.config(
            background=self.get_default_background(),
        )

        self.icon_researcher = RBGAImage(
            ICON_RESEARCHER, size=icon_size)

        self.label_icon = Label(self, image=self.icon_researcher)
        self.label_icon.config(
            background=self.get_default_background(),
            highlightthickness=0
        )

        self.frame_content = Frame(self)
        self.frame_content.config(
            background=self.get_default_background()
        )

        self.label_name = Label(self.frame_content)
        self.label_name.config(
            text=self.author.name,
            font=TITLE_SCREEN,
            background=self.get_default_background(),
            foreground=self.get_foreground(),
            anchor="nw",
            justify="left",
            wraplengt=200
            # highlightthickness=BORDER_WITH,
            # highlightbackground=DARK_GREY,
        )

        text_similarity = None
        if (self.author.similarity is not None):
            text_similarity = "Similarity: %.2f" % self.author.similarity

        self.label_similarity = Label(self.frame_content)
        self.label_similarity.config(
            text=text_similarity,
            font=BODY,
            background=self.get_default_background(),
            foreground=self.get_foreground(),
            anchor="nw",
            justify="left"
            # highlightthickness=BORDER_WITH,
            # highlightbackground=DARK_GREY,
        )

        self._add_logic()
        self._add_animations()

    def _add_logic(self):
        if(self.clickable == True):
            self.bind("<Button-1>", self._on_click)
            self.label_similarity.bind("<Button-1>", self._on_click)
            self.label_icon.bind("<Button-1>", self._on_click)
            self.label_name.bind("<Button-1>", self._on_click)
            self.frame_content.bind("<Button-1>", self._on_click)

    def _on_enter(self, event, **kw):
        if(self.clickable == True):
            color = GREY
            self.config(background=color)
            self.label_similarity.config(background=color)
            self.label_icon.config(background=color)
            self.label_name.config(background=color)
            self.frame_content.config(background=color)

    def _on_leave(self, event, **kw):
        if(self.clickable == True):
            color = self.get_default_background()
            self.config(background=color)
            self.label_similarity.config(background=color)
            self.label_icon.config(background=color)
            self.label_name.config(background=color)
            self.frame_content.config(background=color)

    def _add_animations(self):
        if(self.clickable == True):
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)

    def _on_click(self, event, **kw):
        if(self.on_click is not None):
            self.on_click(self.author)

    def show_components(self, ):
        """
          Khởi tạo các thành phần trên nút
        """
        colIdx_left = 0
        colIdx_label_icon = 1
        colIdx_content = 2
        colIdx_right = colIdx_content + 1

        rowIdx_header = 0
        rowIdx_frame_content = 1
        rowIdx_footer = rowIdx_frame_content + 1

        rowIdx_name = 1
        rowIdx_collaborations = 2
        rowIdx_works = 3

        self.grid_columnconfigure(colIdx_left, weight=1)
        self.grid_columnconfigure(colIdx_right, weight=1)

        self.grid_rowconfigure(rowIdx_header, weight=1)
        self.grid_rowconfigure(rowIdx_footer, weight=1)

        grid_default = {
            "sticky": "news",
            "pady": (0, PADDING),
            "padx": (PADDING, PADDING),
        }

        # self.label_text.pack(fill="both", expand=1)
        self.label_icon.grid(row=rowIdx_frame_content,
                             column=colIdx_label_icon,
                             **grid_default
                             )
        self.frame_content.grid(row=rowIdx_frame_content,
                                column=colIdx_content,
                                **grid_default
                                )
        self.label_name.grid(row=rowIdx_name,
                             column=0,
                             **grid_default
                             )
        self.label_similarity.grid(row=rowIdx_collaborations,
                                   column=0,
                                   **grid_default
                                   )
