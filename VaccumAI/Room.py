import random
import numpy as np
from Robot import Robot
from Sensor import Sensor


class Room:

    def __init__(self, height, width):
        self.room = np.zeros(shape=(height, width))
        self.robot = Robot(self.room)
        self.sensor = Sensor()

    def out_of_bounds(self, new_pos):
        if 0 <= new_pos[0] < self.room.shape[0]:
            if 0 <= new_pos[1] < self.room.shape[1]:
                return False
        return True

    def choose_random_neighbor(self):
        [x, y] = self.robot.pos
        new_x, new_y = 0, 0
        while new_x == 0 and new_y == 0:
            new_x = random.choice(range(-1, 2))
            new_y = random.choice(range(-1, 2))
        new_pos = [x+new_x, y+new_y]
        if self.out_of_bounds(new_pos):
            return None
        else:
            return new_pos

    def choose_random_second_neighbor(self):
        [x, y] = self.robot.pos
        [new_x, new_y] = [0, 0]
        while new_x == 0 and new_y == 0:
            new_x = random.choice(range(-2, 3))
            new_y = random.choice(range(-2, 3))
        new_pos = [x + new_x, y + new_y]
        if self.out_of_bounds(new_pos):
            return None
        else:
            return new_pos
