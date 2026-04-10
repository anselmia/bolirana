from src.display_services.ui_common import UICommonMixin
from src.display_services.ui_game import UIGameMixin
from src.display_services.ui_menu import UIMenuMixin
from src.display_services.ui_scene import UISceneMixin


class DisplayUIService(UIMenuMixin, UIGameMixin, UISceneMixin, UICommonMixin):
    def __init__(self, display):
        self.display = display
