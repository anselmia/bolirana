from zeroconf import ServiceBrowser, Zeroconf


class MDNSListener:
    def __init__(self):
        self.zeroconf = Zeroconf()
        self.listener = ServiceBrowser(self.zeroconf, "_http._tcp.local.", self)

    def remove_service(self, zeroconf, type, name):
        print(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            print(f"Service {name} added, service info: {info}")

    def read_holes(self):
        return 0

    def next(self):
        return False
