
from utils.image import FlexibleImage
from utils.dimension import PADDING, SCROLL_BAR_WIDTH
from utils.font import LOGO, BUTTON, BODY_BOLD
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, BLACK, GREY, ORANGE, WHITE
from utils.file import ICON_RESEARCHER, ICON_CHART

from controllers.main import controller
from controllers.excution import excute

from tkinter import Label, Canvas, LEFT, Frame, Scrollbar
from components.screen import Screen
from components.button_back import ButtonBack
from components.button_icon import ButtonIcon
from components.card_author import CardAuthor
from components.button import Button

max_by_row = 2


class Queries(Screen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

    def _init_components(self):
        background_color = self.get_background()
        scrollbar_width = SCROLL_BAR_WIDTH
        height_buttons = BUTTON[1] + PADDING * 2
        width_buttons = BUTTON[1] + PADDING * 2

        self.button_back = ButtonBack(
            self, size=height_buttons, onClick=self.navigate_home)

        self.label_logo = Label(
            self)
        self.label_logo.config(
            text="weCoNet",
            font=LOGO,
            background=background_color,
            foreground=BLUE,
        )

        self.label_queries = Label(
            self)
        self.label_queries.config(
            text="QUERIES",
            font=BODY_BOLD,
            background=background_color,
            foreground=BLACK,
            anchor="nw"
        )

        """
        ScrollView result     
        """
        self.canvas_queries = Canvas(self,
                                     highlightthickness=1,
                                     )
        self.frame_queries = Frame(self.canvas_queries,
                                   highlightthickness=1,
                                   #    borderwidth=1,
                                   #    relief="solid",
                                   )
        self.canvas_queries.config(
            background=WHITE,
            highlightthickness=0,
        )
        self.frame_queries.config(
            background=WHITE,
            highlightthickness=0,
        )

        self.scrollbar_queries = Scrollbar(
            self,
            orient="vertical",
            width=scrollbar_width,
            command=self.canvas_queries.yview
        )
        self.canvas_queries.config(
            yscrollcommand=self.scrollbar_queries.set,
        )

        self.canvas_queries.create_window(
            (0, 0), window=self.frame_queries, anchor="nw",)

        self.frame_queries.bind("<Configure>", self._onFrameConfigure)

        self.list_card_recommendation = None

        self.button_add = Button(self, self.app.width - PADDING * 2,
                                 height=height_buttons, text="See more ...", enable=True, onClick=self._on_click_see_more)

    def navigate_home(self):
        self.app.navigate(context="Home")

    def _on_click_see_more(self):
        controller.current += controller.delta
        self._update_list_card_queries()

    def _onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas_queries.config(
            scrollregion=self.canvas_queries.bbox("all"))

    def _callback_update_list_card_queries(self, **kw):
        authors = kw.get("authors", None)
        if (authors is not None):
            self.list_card_recommendation = [
                CardAuthor(self.frame_queries, author,
                           clickable=True, on_click=self._on_click_card)
                for author in authors
            ]
            return self._show_list_card_queries()
        return self._show_empty_list()

    def _on_click_card(self, *args, **kw):
        author = args[0]
        print("author", author)
        if (author is not None):
            self.app.navigate(context="Home", author_id=author._id)

    def _on_error_update_list_card_queries(self, err: ValueError):
        self._show_empty_list()

    def _update_list_card_queries(self, **kw):
        excute(
            task=controller.get_list_author,
            callback=self._callback_update_list_card_queries,
            on_error=self._on_error_update_list_card_queries,
        )

    def _show_empty_list(self):
        return

    def _show_list_card_queries(self):
        for (idx, card) in enumerate(self.list_card_recommendation):
            rowIdx = int(idx / max_by_row)
            colIdx = idx % max_by_row
            card.grid(
                row=rowIdx,
                column=colIdx,
                padx=(PADDING, PADDING),
                pady=(PADDING, PADDING),
                sticky="nw"
            )
            card.show_components()

        # self.frame_result.config(
        #     background=self.get_background()
        # )

    def _screenWillShow(self, **kwargs):
        super()._screenWillShow(**kwargs)

        self._update_list_card_queries(**kwargs)

    def _show(self, **kw):

        rowIdx_button_filter = 0

        colIdx_button_filter = 0

        default_grid = {
            "row": rowIdx_button_filter,
            "sticky": "nw",
            "padx": (PADDING, PADDING)
        }

        self.button_back.pack(side="top", expand=False, anchor="nw")
        self.button_back.show_components()

        self.label_logo.pack(side="top", fill="both", expand=False)
        self.label_queries.pack(side="top", fill="both",
                                expand=False, padx=(PADDING, PADDING))
        self.button_add.pack(side="top", fill="x", expand=False, padx=(
            PADDING, PADDING), pady=(PADDING, PADDING),)
        self.button_add.show_components()

        self.canvas_queries.pack(side="left", fill="both", expand=True)
        self.scrollbar_queries.pack(side="right", fill="y")
