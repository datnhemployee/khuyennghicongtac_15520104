from tkinter import Frame, Canvas, Scrollbar
from components.screen import Screen
from utils.color import WHITE
from utils.dimension import SCROLL_BAR_WIDTH


class ScrollableScreen(Screen):
    def __init__(self, parent, app):
        super().__init__(parent=parent, app=app)

    def _init_scrollframe(self):
        self.canvas = Canvas(self,)
        self.container = Frame(self.canvas,
                               #    borderwidth=1,
                               #    relief="solid"
                               )
        self.canvas.config(background=WHITE)
        self.container.config(background=WHITE)

        scrollbar_width = SCROLL_BAR_WIDTH
        self.scrollbar = Scrollbar(self, orient="vertical", width=scrollbar_width,
                                   command=self.canvas.yview)
        self.update_idletasks()
        self.canvas.configure(
            width=self.app.width - scrollbar_width,
            height=self.app.height,
            yscrollcommand=self.scrollbar.set,
        )

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.container, anchor="nw",)

        self.container.bind("<Configure>", self._onFrameConfigure)

    def _before_init_components(self):
        """
          Hàm phụ trợ trước khi khởi tạo màn hình
        """
        self._init_scrollframe()

    def _onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _init_components(self):
        """
          sử dụng `self.container` để vẽ
        """
