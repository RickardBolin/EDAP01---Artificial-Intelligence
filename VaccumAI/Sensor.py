import numpy as np


class Sensor:
    def __init__(self):
        self.pL = 0.1
        self.pLs1 = 0.05
        self.pLs2 = 0.025

    def measure_location(self, room):
        x = np.random.uniform()
        if x < self.pL:
            return room.robot.pos
        elif x < self.pL + self.pLs1 * 8:
            return room.choose_random_neighbor()
        elif x < self.pL + self.pLs1 * 8 + self.pLs2 * 16:
            return room.choose_random_second_neighbor()
        else:
            return None
