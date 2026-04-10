from src.display_services.effects_boss import EffectsBossMixin
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
    EffectsParticlesMixin,
    EffectsCoreMixin,
):
    LITTLE_FROG_SOUND_MAXTIME_MS = 1450
    LARGE_FROG_SOUND_MAXTIME_MS = 1750

    def __init__(self, display):
        self.display = display
