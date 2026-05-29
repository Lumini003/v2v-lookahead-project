from simulation.cars.human_car import HumanCar

ROAD_LENGTH = 1000
NUM_CARS = 8
SPACING = 28
START = 60
DECEL_DURATION = 3.0
ACCEL_DURATION = 3.0

# Lead decelerates then accelerates; followers slow then speed up with delay (human-like)
human_platoon = [
    HumanCar(
        START + i * SPACING,
        0,
        speed=40,
        acceleration=-2.5 if i == NUM_CARS - 1 else 2.0,
        max_speed=45,
        reaction_time=0.45,
        time_headway=0.35,
        brake_deceleration=6,
        follow_gain=2.0,
    )
    for i in range(NUM_CARS)
]


def setup(sim, t):
    sim.road(length=ROAD_LENGTH, lanes=1)
    lead = human_platoon[NUM_CARS - 1]
    if t < DECEL_DURATION:
        lead._preferred_acceleration = -2.5
    elif t < DECEL_DURATION + ACCEL_DURATION:
        lead._preferred_acceleration = 2.0
    else:
        lead._preferred_acceleration = 0.0
    if t < 0.05:
        for car in human_platoon:
            sim.add_car(car)


def reset():
    for i, car in enumerate(human_platoon):
        car.position = START + i * SPACING
        car.speed = 40
        car.acceleration = -2.5 if i == NUM_CARS - 1 else 2.0
        car._preferred_acceleration = -2.5 if i == NUM_CARS - 1 else 2.0
        car._history = []
