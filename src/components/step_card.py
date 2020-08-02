from tkinter import Frame, Canvas, Label
from PIL import Image, ImageTk
from utils.dimension import PADDING
from utils.image import RBGAImage
from utils.color import DARK_BLUE, BLUE, LIGHT_BLUE, WHITE, BLACK, GREY
from utils.font import BODY, HEADER_2, TYPE_HEADER_2, BUTTON
from utils.file import PRIOR_IMAGE as default_icon
from models.step import Step
from components.button import Button
from components.input import Input


class StepCard(Frame):
    def __init__(self,
                 parent,
                 idx: int,
                 height: int,
                 width: int,
                 background: str,
                 step: Step,
                 editable=False,
                 onClick_Result=None,
                 is_finished=None):
        super().__init__(master=parent)
        self.idx = idx

        self.height = height
        self.width = width
        self.background = background

        self.step = step

        self.editable = editable
        self.onClick_Result = onClick_Result
        self.is_finished = is_finished

        self._init_components()

    def _init_components(self):
        """
          Khởi tạo các thành phần trong train card
        """
        background_color = self.background

        self.icon_size = int(self.height)
        self.content_width = self.width - self.icon_size - PADDING

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

        self.icon_step = Canvas(
            self,
        )
        self.icon_step.config(
            height=self.icon_size,
            width=self.icon_size,
            background=background_color,
            highlightthickness=0
        )

        self.image = RBGAImage(
            default_icon, size=self.icon_size)

        self.icon_step.create_image(
            0, 0, image=self.image, anchor="nw")

        """
        Content
        """
        self.container_content = Frame(self)
        self.container_content.config(
            width=self.content_width,
            height=self.icon_size,
            background=background_color
        )

        self.container_content.grid_propagate(False)
        self.container_content.grid_rowconfigure(0, weight=1)
        self.container_content.grid_rowconfigure(7, weight=1)

        self._init_content()

        """
          Animations: None
        """

    def _get_enable(self, key, val):
        if (self.editable == True):
            if (key == val):
                return False
            return True
        return False

    def _init_content(self):
        wrap_text_length = self.content_width
        button_width = int(self.content_width / 3)
        button_height = BUTTON[1] + PADDING * 2

        input_height = BODY[1] + PADDING * 2

        self.label_name = Label(self.container_content)
        self.label_name.config(
            text=self.step.name,
            justify="left",
            font=HEADER_2,
            background=self.background,
            foreground=DARK_BLUE,
            wraplengt=wrap_text_length,
        )

        self.label_input = Label(self.container_content)
        self.label_input.config(
            text="INPUT",
            justify="left",
            font=TYPE_HEADER_2,
            background=self.background,
            foreground=DARK_BLUE,
            wraplengt=wrap_text_length,
        )

        self.container_setting_input = Frame(self.container_content)
        self.container_setting_input.config(
            background=self.background,
        )

        self.list_input_settings = [
            Input(self.container_setting_input,
                  width=int(self.content_width / len(self.step.inputs.keys())),
                  height=input_height,
                  title=key,
                  val=self.step.inputs[key],
                  enabel=self._get_enable(self.step.inputs[key], key),
                  #   enabel=self.editable,
                  ) for key in self.step.inputs.keys()
        ]

        self.label_output = Label(self.container_content)
        self.label_output.config(
            text="OUTPUT",
            justify="left",
            font=TYPE_HEADER_2,
            background=self.background,
            foreground=DARK_BLUE,
            wraplengt=wrap_text_length,
        )

        self.label_output_result = Label(self.container_content)
        self.label_output_result.config(
            text=self.step.to_str_output(),
            justify="left",
            font=TYPE_HEADER_2,
            background=self.background,
            foreground=DARK_BLUE,
            wraplengt=wrap_text_length,
        )

        # is_finished = False
        # if (self.is_finished is not None):
        #     is_finished = self.is_finished()
        # self.button_result = Button(
        #     self.container_content,
        #     button_width,
        #     button_height,
        #     text="Kết quả",
        #     enable=is_finished)

    """
        Logic
    """

    def get_dict_values(self):
        result = {}
        for _input in self.list_input_settings:
            result[_input.get_title()] = _input.get_val()
        return result
    """
        Animations
    """

    """
        Hiển thị
    """

    def _show_content(self):
        self.label_name.grid(row=1, column=0, sticky="nw")
        self.label_input.grid(row=2, column=0, sticky="nw")
        self.container_setting_input.grid(row=3, column=0, sticky="nw")
        for (idx, _input_setting) in enumerate(self.list_input_settings):
            _input_setting.grid(row=0, column=idx, sticky="nw")
            _input_setting.show_components()

        self.label_output.grid(row=4, column=0, sticky="nw")
        self.label_output_result.grid(row=5, column=0, sticky="nw")
        # self.button_result.grid(row=6, column=0, sticky="nw")
        # self.button_result.show_components()

    def show_components(self):
        """
          Private: Hiển thị thẻ
        """
        # self.label.grid(row=1, column=0, sticky="nw",)
        self.icon_step.grid(row=1, column=1, sticky="nw",)
        self.container_content.grid(row=1, column=2, sticky="nw",)

        """
          Private: Hiển thị content
        """
        self._show_content()

    # def onClick(self, event, **kwargs):
