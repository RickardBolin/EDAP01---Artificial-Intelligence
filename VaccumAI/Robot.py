import numpy as np
import random


class Robot:

    def __init__(self, room):
        self.room = room
        self.pos = [np.random.randint(0, room.shape[0]), np.random.randint(0, room.shape[1])]
        # Directions: 1 = Up, 2 = Right, 3 = Down, 4 = Left
        self.dir = self.pick_random_valid_dir()

    def move(self):

        if np.random.uniform() > 0.7 or not self.valid_dir(self.dir, self.pos):
            self.dir = self.pick_random_valid_dir()
        if self.dir == 0:
            self.pos[1] += 1
        if self.dir == 1:
            self.pos[0] += 1
        if self.dir == 2:
            self.pos[1] -= 1
        if self.dir == 3:
            self.pos[0] -= 1
        return [self.pos[0], self.pos[1]]

    def pick_random_valid_dir(self):
        # 0 = Up, 1 = Right, 2 = Down, 3 = Left
        dirs = [0, 1, 2, 3]
        while True:
            random_dir = random.choice(dirs)
            if self.valid_dir(random_dir, self.pos):
                return random_dir
            else:
                dirs.remove(random_dir)

    def valid_dir(self, dir, pos):
        if dir == 0 and pos[1] == self.room.shape[1] - 1:
            return False
        if dir == 1 and pos[0] == self.room.shape[0] - 1:
            return False
        if dir == 2 and pos[1] == 0:
            return False
        if dir == 3 and pos[0] == 0:
            return False
        return True

