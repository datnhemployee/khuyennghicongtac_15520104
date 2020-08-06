
from tkinter import Tk, Frame
# from screens.home import Home as HomeScreen
from screens.splash import Splash
from screens.home import Home
from screens.queries import Queries
# from screens.experiments import Experiments as ExperimentScreen
# from screens.project import Project as ProjectScreen
# from screens.add_project import AddProject as AddProjectScreen
# from screens.add_algorithms import AddAlgorithm as AddAlgorithmScreen
# from screens.add_settings import AddSettings as AddSettingsScreen
# from screens.error import Error as ErrorScreen
# from screens.about import About as AboutScreen
# from screens.init import Init as InitScreen
from components.screen import Screen
# from utils.file import A as icon_photo
# from tkinter import PhotoImage


def get_screen_name(screen: Screen) -> str:
    name = type(screen).__name__
    return name


class App(Tk):
    """
    Khởi tạo tất cả màn hình

    Tips:
    + Navigate(HomeScreen) ở trong __init__ 
    """

    def _init_all_screen(self, min_height=None, min_width=None):

        self.grid_rowconfigure(0, minsize=self.width)

        self.grid_columnconfigure(1, minsize=self.height)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.container = Frame(self)
        self.container.grid(row=0, column=1, sticky="nsew")

        self.frames = {}
        screens = (Splash, Home, Queries)
        # screens = (HomeScreen, ProjectScreen, ExperimentScreen, AboutScreen, InitScreen,
        #            AddProjectScreen, AddAlgorithmScreen, AddSettingsScreen, ErrorScreen)
        for F in screens:
            frame = F(self.container, self)
            name = get_screen_name(frame)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def set_size(self, height=None, width=None):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.width = int(screen_width * 2 / 3)
        self.height = int(screen_height * 2 / 3)

        x_coordinate = int((screen_width - self.width) / 2)
        y_coordinate = int((screen_height - self.height) / 2)

        if (height is not None and width is not None):
            self.width = width
            self.height = height
        self.geometry('{width}x{height}+{x_coordinate}+{y_coordinate}'.format(
            width=self.width, height=self.height, x_coordinate=x_coordinate, y_coordinate=y_coordinate))

        """
        Không thể resize
        """
        self.resizable(False, False)

    # def close_all(self):
    #     import matplotlib.pyplot as plt

    #     plt.close('all')
    #     self.quit()

    def __init__(self, *args, **kwargs):

        Tk.__init__(self, *args, **kwargs)

        # self.wm_protocol('WM_DELETE_WINDOW', func=self.close_all)

        self.set_size()
        self._init_all_screen()

        self.navigate("Splash")
        # self.wm_attributes('-transparentcolor', self['bg'])
        # self.tk.call('wm', 'iconphoto', self._w, PhotoImage(file=icon_photo))
        # self.iconphoto(True, PhotoImage(file=icon_photo))

    def navigate(self, context: str, **kwargs):
        try:
            frame = self.frames[context]
            frame.tkraise()
            frame.update(**kwargs)
        except ValueError as err:
            self.showError(err.args)

    def showError(self, message: str):
        context = "Error"
        frame = self.frames[context]
        frame.tkraise()
        frame.update(message=message)
