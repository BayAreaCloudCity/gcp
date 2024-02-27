from datetime import datetime


class Simulation:
    __simulation_start_time: datetime
    __simulation_end_time: datetime
    __real_start_time: datetime
    __speed: int

    def __init__(self, simulation_start_time: datetime, simulation_end_time: datetime, real_start_time: datetime, speed: int):
        self.__simulation_start_time = simulation_start_time
        self.__simulation_end_time = simulation_end_time
        self.__real_start_time = real_start_time
        self.__speed = speed

    def is_before_simulation(self, time: datetime):
        return self.get_simulation_time(time) < self.__simulation_start_time

    def is_after_simulation(self, time: datetime):
        return self.get_simulation_time(time) > self.__simulation_end_time

    def get_simulation_time(self, time: datetime):
        return self.__simulation_start_time + (time - self.__real_start_time) * self.__speed
