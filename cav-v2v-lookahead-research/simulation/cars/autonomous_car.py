from simulation.cars.car import Car


class AutonomousCar(Car):
    def __init__(self, *args, color=2, **kwargs):
        super().__init__(*args, color=color, **kwargs)
