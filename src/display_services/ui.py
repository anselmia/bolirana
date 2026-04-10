from src.display_services.ui_common import UICommonMixin
from src.display_services.ui_game import UIGameMixin
from src.display_services.ui_menu import UIMenuMixin
from src.display_services.ui_scene import UISceneMixin


class DisplayUIService(UIMenuMixin, UIGameMixin, UISceneMixin, UICommonMixin):
    def __init__(self, display):
        self.display = display
        self._menu_frame_cache = {}
        self._game_frame_cache_key = None
        self._game_frame_cache_surface = None
        self._surface_cache = {}
