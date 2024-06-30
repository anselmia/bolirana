from src.mdns import MDNSListener


class Hole:
    def __init__(self, type, value, pin):
        self.type = type
        self.value = value
        self.pin = pin

    def read_holes(holes):
        pin_activated = MDNSListener.read_holes()
        hole = next((hole for hole in holes if pin_activated in hole.pin), None)
        return hole
