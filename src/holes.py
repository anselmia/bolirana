class Hole:
    def __init__(self, type, value, pin, text, position1, position2=None):
        self.type = type
        self.value = value
        self.pin = pin
        self.text = text
        self.position = position1
        self.position2 = position2
