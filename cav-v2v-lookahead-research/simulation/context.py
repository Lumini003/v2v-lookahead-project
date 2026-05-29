class ScenarioContext:
    def __init__(self):
        self.road_length = 500
        self.num_lanes = 2
        self._pending = []

    def road(self, length, lanes):
        self.road_length = length
        self.num_lanes = lanes

    def add_car(self, car):
        self._pending.append(car)
