import random
from simulation.cars.car import Car


class HumanCar(Car):
    def __init__(
        self,
        *args,
        color=1,
        reaction_time=0.4,
        reaction_time_jitter=0.0,
        brake_deceleration=5.0,
        follow_gain=2.0,
        **kwargs,
    ):
        super().__init__(*args, color=color, **kwargs)
        self._preferred_acceleration = self.acceleration
        self.brake_deceleration = brake_deceleration
        self.follow_gain = follow_gain
        if reaction_time_jitter > 0:
            self._effective_reaction_time = max(
                0.05,
                reaction_time + random.uniform(-reaction_time_jitter, reaction_time_jitter),
            )
        else:
            self._effective_reaction_time = reaction_time
        self._history = []

    def _desired_acceleration(self, road_length, others):
        others = others or []
        max_a = self._preferred_acceleration if self._preferred_acceleration > 0 else 3.0
        if self.max_speed is not None and self.speed >= self.max_speed:
            cruise_a = 0.0
        else:
            cruise_a = self._preferred_acceleration
        lead = None
        for other in others:
            if other is self or other.lane != self.lane:
                continue
            if other.position > self.position and (lead is None or other.position < lead.position):
                lead = other
        if lead is None:
            return cruise_a
        gap = lead.back - self.front
        th = max(self.time_headway, 0.3)
        desired_speed = min(
            self.max_speed if self.max_speed is not None else 100.0,
            max(0.0, (gap - self.length * 0.5) / th),
        )
        desired_a = (desired_speed - self.speed) * self.follow_gain
        return max(-self.brake_deceleration, min(max_a, desired_a))

    def update(self, dt, road_length, others=None, sim_time=0.0):
        desired_a = self._desired_acceleration(road_length, others)
        self._history.append((sim_time, desired_a))
        cutoff = sim_time - self._effective_reaction_time - 0.5
        self._history = [(t, a) for t, a in self._history if t >= cutoff]
        target_t = sim_time - self._effective_reaction_time
        if not self._history:
            self.acceleration = desired_a
        elif target_t <= self._history[0][0]:
            self.acceleration = self._history[0][1]
        elif target_t >= self._history[-1][0]:
            self.acceleration = self._history[-1][1]
        else:
            for i in range(len(self._history) - 1):
                t_lo, a_lo = self._history[i]
                t_hi, a_hi = self._history[i + 1]
                if t_lo <= target_t <= t_hi:
                    alpha = (target_t - t_lo) / (t_hi - t_lo) if t_hi > t_lo else 1.0
                    self.acceleration = a_lo + alpha * (a_hi - a_lo)
                    break
        super().update(dt, road_length, others, sim_time)
