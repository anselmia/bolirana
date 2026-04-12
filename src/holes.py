class Hole:
    def __init__(self, display, type, value, pin, text):
        self.type = type
        self.value = value
        self.pin = pin
        self.text = text
        self.position = display.get_hole_position(text, 1)
        self.position2 = display.get_hole_position(text, 2)
        self.bonus_active = False
        self.bonus_active_pin = None
        self.bonus_activated_at = 0.0
        self.bonus_duration = 0.0
        self.malus_active = False
        self.malus_active_pin = None
        self.malus_activated_at = 0.0
        self.malus_duration = 0.0
