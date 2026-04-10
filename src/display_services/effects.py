from src.display_services.effects_boss import EffectsBossMixin
from src.display_services.effects_cartoon import EffectsCartoonMixin
from src.display_services.effects_core import EffectsCoreMixin
from src.display_services.effects_particles import EffectsParticlesMixin
from src.display_services.effects_score import EffectsScoreMixin
from src.display_services.effects_special import EffectsSpecialMixin
from src.display_services.effects_victory import EffectsVictoryMixin


class DisplayEffectsService(
    EffectsScoreMixin,
    EffectsVictoryMixin,
    EffectsSpecialMixin,
    EffectsBossMixin,
    EffectsCartoonMixin,
    EffectsParticlesMixin,
    EffectsCoreMixin,
):
    LITTLE_FROG_SOUND_MAXTIME_MS = 420
    LARGE_FROG_SOUND_MAXTIME_MS = 520

    def __init__(self, display):
        self.display = display
        self._surface_cache = {}
