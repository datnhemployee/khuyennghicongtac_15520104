from tkinter import Frame, Canvas
from PIL import Image, ImageTk
from utils.color import WHITE
from utils.dimension import PADDING


class Screen(Frame):
    def __init__(self, parent, app):
        super().__init__(master=parent)
        self.app = app
        self.row_idx = 0
        self._before_init_components()
        self._init_components()
        self.config(background=WHITE)

    def get_row_idx(self):
        """
        Component nào gọi hàm này là component đầu tiên trên màn hình
        """
        return self.row_idx

    def get_next_row_idx(self):
        """
        Component đầu tiên không gọi hàm này
        """
        self.row_idx += 1
        return self.row_idx

    def get_background(self):
        return WHITE

    def _before_init_components(self):
        """
          Hàm phụ trợ trước khi khởi tạo màn hình
        """

    def _init_components(self):
        """
          Khởi tạo các thành phần trên màn hình
        """

    def inch_to_pixel(self):
        """
          Khởi tạo các thành phần trên màn hình
        """

    def pixel_to_inch(self, pixel=1) -> float:
        """
          Chuyển đổi pixel thành inch
        """
        pixel_per_inch = self.app.winfo_fpixels('1i')
        inch = pixel / pixel_per_inch
        return inch

    def back(self):
        """
          quay về màn trước (mặc định: màn hình hiện tại)
        """

    def _show(self, **kwargs):
        """
          Hiện toàn bộ thành phần trên màn hình
        """

    def _screenWillShow(self, **kwargs):
        """
          Cập nhật trước khi hiển thị
        """

    def _screenDidShow(self, **kwargs):
        """
          Cập nhật sau khi hiển thị
        """

    def update(self, **kwargs):
        """
          Cập nhật và hiện toàn bộ thành phần trên màn hình
        """
        self._screenWillShow(**kwargs)
        self._show(**kwargs)
        self._screenDidShow(**kwargs)

        self.update_idletasks()

    def create_rectangle(self, x1, y1, x2, y2, fill, alpha):

        alpha = int(alpha * 255)
        fill = self.app.winfo_rgb(fill) + (alpha,)
        image = Image.new('RGBA', (x2-x1, y2-y1), fill)
        image = ImageTk.PhotoImage(image)
        return image
