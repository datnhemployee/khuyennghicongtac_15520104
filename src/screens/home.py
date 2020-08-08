
from utils.image import FlexibleImage
from utils.dimension import PADDING, SCROLL_BAR_WIDTH
from utils.font import LOGO, BUTTON, BODY_BOLD, BODY
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, BLACK, GREY, ORANGE, WHITE
from utils.file import ICON_RESEARCHER, ICON_SWITCHER_OFF, ICON_SWITCHER_ON
from utils.image import RBGAImage

from controllers.main import controller
from controllers.excution import excute

from tkinter import Label, Canvas, LEFT, Frame, Scrollbar
from components.screen import Screen
from components.button_icon import ButtonIcon
from components.card_author import CardAuthor

max_by_row = 2


class Home(Screen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

    def _before_init_components(self):
        self.author_id = None
        self.status_switcher = False

        width_icon_switch = BUTTON[1] * 3 + PADDING * 2
        height_icon_switch = BUTTON[1] + PADDING * 2

        size_default_icon_switch = {
            "width": width_icon_switch,
            "height": height_icon_switch
        }
        self.icon_switch_off = RBGAImage(
            ICON_SWITCHER_OFF,
            **size_default_icon_switch
        )

        self.icon_switch_on = RBGAImage(
            ICON_SWITCHER_ON,
            **size_default_icon_switch
        )

    def _init_components(self):
        background_color = self.get_background()
        scrollbar_width = SCROLL_BAR_WIDTH
        height_buttons = BUTTON[1] + PADDING * 2
        width_buttons = BUTTON[1] + PADDING * 2

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

        self.frame_buttons = Frame(self,)
        self.frame_buttons.config(
            background=background_color
        )

        self.button_filter = ButtonIcon(
            self.frame_buttons, height_buttons, ICON_RESEARCHER, "Recommendations of:\nNone", on_click=self.navigate_queries)

        self.label_result = Label(
            self)
        self.label_result.config(
            text="RESULT",
            font=BODY_BOLD,
            background=background_color,
            foreground=BLACK,
            anchor="nw"
        )

        self.label_let_see_result = Label(
            self)
        self.label_let_see_result.config(
            text="Let me see the result",
            font=BODY,
            background=background_color,
            foreground=BLACK,
            anchor="nw"
        )

        self.label_switcher = Label(
            self)
        self.label_switcher.config(
            image=self.icon_switch_off,
            font=BODY,
            background=background_color,
            anchor="nw"
        )

        """
        ScrollView result     
        """
        self.canvas_result = Canvas(self,
                                    highlightthickness=1,
                                    )
        self.frame_result = Frame(self.canvas_result,
                                  highlightthickness=1,
                                  #    borderwidth=1,
                                  #    relief="solid",
                                  )
        self.canvas_result.config(
            background=WHITE,
            highlightthickness=0,
        )
        self.frame_result.config(
            background=WHITE,
            highlightthickness=0,
        )

        self.scrollbar_result = Scrollbar(
            self,
            orient="vertical",
            width=scrollbar_width,
            command=self.canvas_result.yview
        )
        self.canvas_result.config(
            yscrollcommand=self.scrollbar_result.set,
        )

        self.canvas_result.create_window(
            (0, 0), window=self.frame_result, anchor="nw",)

        self.frame_result.bind("<Configure>", self._onFrameConfigure)

        self.list_card_recommendation = None

        self.label_switcher.bind("<Button-1>", self._on_click_switcher)

    def navigate_queries(self, ):
        self.app.navigate(context="Queries")

    def _on_click_switcher(self, ev, **kw):
        self.status_switcher = not self.status_switcher
        if (self.status_switcher == True):
            self.label_switcher.config(
                image=self.icon_switch_on,
            )
        else:
            self.label_switcher.config(
                image=self.icon_switch_off,
            )
        if (self.list_card_recommendation is not None):
            for card in self.list_card_recommendation:
                card.show_valuation(enable=self.status_switcher)

    def _onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas_result.config(
            scrollregion=self.canvas_result.bbox("all"))

    def _callback_update_list_card_recommendation(self, **kw):
        recommendations = kw.get("recommendations", None)
        if (recommendations is not None):
            if (self.list_card_recommendation is not None):
                for card in self.list_card_recommendation:
                    card.grid_forget()
                    card.destroy()

            self.list_card_recommendation = [
                CardAuthor(self.frame_result, recommendation)
                for recommendation in recommendations
            ]
            return self._show_list_card_recommendation()
        return self._show_empty_list()

    def _on_error_update_list_card_recommendation(self, err: ValueError):
        self._show_empty_list()

    def _update_list_card_recommendation(self, **kw):
        author_id = kw.get("author_id", None)
        if (author_id is None):
            return self._show_empty_list()
        excute(
            task=controller.get_list_recommendations,
            args={
                "author_id": author_id
            },
            callback=self._callback_update_list_card_recommendation,
            on_error=self._on_error_update_list_card_recommendation,
        )

    def _show_empty_list(self):
        return

    def _show_list_card_recommendation(self):
        for (idx, card) in enumerate(self.list_card_recommendation):
            # rowIdx = int(idx / max_by_row)
            rowIdx = int(idx)
            # colIdx = idx % max_by_row
            colIdx = 0
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

    def _callback_update_button_filter(self, **kw):
        author = kw.get("author", None)
        if (author is not None):
            self.button_filter.set_text(
                "Recommendations of: \n{0}".format(author.name))

    def _on_error_update_button_filter(self, err: ValueError):
        return

    def _update_button_filter(self, **kw):
        author_id = kw.get("author_id", None)
        if (author_id is None):
            return self._on_error_update_button_filter(ValueError(""))
        excute(
            task=controller.get_author,
            args={
                "author_id": author_id
            },
            callback=self._callback_update_button_filter,
            on_error=self._on_error_update_button_filter
        )

    def _screenWillShow(self, **kwargs):
        super()._screenWillShow(**kwargs)

        self._update_list_card_recommendation(**kwargs)
        self._update_button_filter(**kwargs)
        self.status_switcher = True
        self._on_click_switcher(None)

    def _show(self, **kw):

        rowIdx_button_filter = 0

        colIdx_button_filter = 0

        default_grid = {
            "row": rowIdx_button_filter,
            "sticky": "nw",
            "padx": (PADDING, PADDING)
        }

        self.label_logo.pack(side="top", fill="both", expand=False)
        self.label_queries.pack(side="top", fill="both",
                                expand=False, padx=(PADDING, PADDING))

        self.frame_buttons.pack(side="top", fill="both", expand=False)
        self.button_filter.grid(
            column=colIdx_button_filter,
            **default_grid)
        self.button_filter.show_components()

        self.label_result.pack(side="top", fill="both",
                               expand=False, padx=(PADDING, PADDING))
        self.label_let_see_result.pack(side="top", fill="both",
                                       expand=False, padx=(PADDING, PADDING))
        self.label_switcher.pack(side="top", fill="both",
                                 expand=False, padx=(PADDING, PADDING))

        self.canvas_result.pack(side="left", fill="both", expand=True)
        self.scrollbar_result.pack(side="right", fill="y")
