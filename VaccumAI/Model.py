# Inspiration from https://github.com/jalil-M, mainly in the construction of the transition matrix
import numpy as np


class Model:

    def __init__(self, room):
        self.room = room
        self.h = self.room.room.shape[0]
        self.w = self.room.room.shape[1]
        # Build the transition matrix
        self.T = self.build_T()
        # Build the O-matrix that is used when the sensor fails to report a position
        self.O_no_sensor_reading = self.build_O_no_sensor_reading()
        # Initialize f with equal probability for all states
        self.f = np.ones(shape=(self.h * self.w * 4, 1)) / (self.h * self.w * 4)

    def guess_move(self):
        sensor_reading = self.room.sensor.measure_location(self.room)
        self.f = self.calc_new_f(sensor_reading)
        return self.find_most_probable_position()

    def build_T(self):
        S = self.h * self.w * 4
        T = np.zeros(shape=(S, S))

        for r in range(self.h):
            for c in range(self.w):
                for dir in range(4):
                    current_state = r * self.w * 4 + c * 4 + dir
                    possible_transitions = self.find_possible_transitions(r, c, dir)
                    for (valid_new_x, valid_new_y, valid_new_dir), prob in possible_transitions:
                        next_state = valid_new_x * self.w * 4 + valid_new_y * 4 + valid_new_dir
                        T[current_state, next_state] = prob
        return T

    def out_of_bounds(self, new_pos):
        if -1 < new_pos[0] < self.h:
            if -1 < new_pos[1] < self.w:
                return False
        return True

    def find_possible_transitions(self, x, y, dir):
        # List all possible neighbors
        neighbors = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y)]

        # Keep track of if we can continue walking in the same direction as before or not
        same_dir_possible = True
        new_x, new_y = neighbors[dir]
        if self.out_of_bounds((new_x, new_y)):
            same_dir_possible = False

        d = -1
        transitions = []
        for new_x, new_y in neighbors:
            d += 1
            if self.out_of_bounds((new_x, new_y)):
                continue
            else:
                if d == dir:
                    transitions.append(((new_x, new_y, d), 0.7))
                else:
                    if same_dir_possible:
                        # If we could move in the same direction but changed anyway:
                        prob = 0.3
                    else:
                        # If we had to change direction:
                        prob = 1.0
                    transitions.append(((new_x, new_y, d), prob))

        # Adjust probabilities when we know how many transitions are possible
        transitions_correct_probs = []
        if same_dir_possible:
            for pos, prob in transitions:
                if prob != 0.7:
                    # If we change direction randomly, give all other transitions equal probability
                    transitions_correct_probs.append((pos, prob/(len(transitions)-1)))
                else:
                    transitions_correct_probs.append((pos, prob))
        else:
            # If we hit a wall, give all transitions equal probability
            for pos, prob in transitions:
                transitions_correct_probs.append((pos, prob / len(transitions)))

        return transitions_correct_probs

    def build_O(self, sensor_reading):
        if sensor_reading is None:
            return self.O_no_sensor_reading
        S = self.h * self.w * 4
        O = np.array(np.zeros(shape=(S, S)))

        # Probability of 0.1 for the sensed coordinate
        idx = sensor_reading[0] * 4 * self.w + sensor_reading[1] * 4
        for i in range(4):
            O[idx + i, idx + i] = 0.1

        # Probability of 0.05 for the neighbors of the sensed coordinate
        possible_neighbors = self.find_possible_neighbors(sensor_reading[0], sensor_reading[1])
        for neighbor_x, neighbor_y in possible_neighbors:
            idx = neighbor_x * self.w * 4 + neighbor_y * 4
            for i in range(4):
                O[idx + i, idx + i] = 0.05

        # Probability of 0.025 for the second neighbors of the sensed coordinate
        possible_second_neighbors = self.find_possible_second_neighbors(sensor_reading[0], sensor_reading[1])
        for neighbor_x, neighbor_y in possible_second_neighbors:
            idx = neighbor_x * self.w * 4 + neighbor_y * 4
            for i in range(4):
                O[idx + i, idx + i] = 0.025

        # Returned normalized O to compensate for "missed probabilities" when being close to edges etc.
        return O/np.sum(O)

    def build_O_no_sensor_reading(self):

        nb_tiles = self.w * self.h
        p_corner = 4/nb_tiles
        p_next_to_corner = 8/nb_tiles
        p_edge = np.max([0.0, (2*(self.w - 4) + 2*(self.h - 4)) / nb_tiles])
        p_inner_edge = np.max([0.0, (2*(self.w - 4) + 2*(self.h - 4)) / nb_tiles])
        p_center = np.max([0.0, (self.w - 4) * (self.h - 4) / nb_tiles])

        # Probability of being in a corner on the edge when getting no reading:
        p_no_reading_given_edge_corner = 0.625
        # Probability of being on the edge, next to a corner when getting no reading:
        p_no_reading_given_edge_next_to_corner = 0.5
        # Probability of being on the edge, away from a corner when getting no reading:
        p_no_reading_given_edge = 0.425
        # Probability of being in a corner on the "inner edge" when getting no reading:
        p_no_reading_given_inner_edge_corner = 0.325
        # Probability of being on the inner edge, away from a corner when getting no reading:
        p_no_reading_given_inner_edge = 0.225
        # Probability of being somewhere in the center when getting no reading:
        p_no_reading_given_center = 0.1

        # Bayes theorem: P(A|B) = P(B|A)*P(A)/P(B)  ->  P(B|A) = P(B)*P(A|B)/P(A)
        # where A = No reading.
        # Probability of getting "No reading" does not matter since it is just going to
        # be a normalizing constant that we can normalize away anyway. We still include
        # the "p_no_reading" in the calculations for completions sake, but it is set to
        # the obviously incorrect value of 1.
        p_no_reading = 1

        p_edge_corner_given_no_reading = p_corner*p_no_reading_given_edge_corner/p_no_reading
        p_edge_next_to_corner_given_no_reading = p_next_to_corner*p_no_reading_given_edge_next_to_corner/p_no_reading
        p_edge_given_no_reading = p_edge*p_no_reading_given_edge/p_no_reading
        p_inner_edge_corner_given_no_reading = p_corner*p_no_reading_given_inner_edge_corner/p_no_reading
        p_inner_edge_given_no_reading = p_inner_edge*p_no_reading_given_inner_edge/p_no_reading
        p_center_given_no_reading = p_center*p_no_reading_given_center/p_no_reading

        # Build O after calculating all probabilities
        S = self.h * self.w * 4

        # All center tiles
        O = np.diag(np.diag(np.ones(shape=(S, S))*p_center_given_no_reading / ((self.w - 4) * (self.h - 4))))

        # Inner edges
        for r in range(self.h):
            if r == self.h - 2 or r == 1:
                for c in range(2, self.w - 2):
                    idx = r * self.w * 4 + c * 4
                    for i in range(4):
                        O[idx + i, idx + i] = p_inner_edge_given_no_reading / (2*(self.w - 4) + 2*(self.h - 4))
            elif r != 0 or r != self.h - 1:
                for c in [1, self.w - 2]:
                    idx = r * self.w * 4 + c * 4
                    for i in range(4):
                        O[idx + i, idx + i] = p_inner_edge_given_no_reading / (2*(self.w - 4) + 2*(self.h - 4))

        # Outer edges
        for r in range(self.h):
            if r == self.h - 1 or r == 0:
                for c in range(2, self.w - 2):
                    idx = r * self.w * 4 + c * 4
                    for i in range(4):
                        O[idx + i, idx + i] = p_edge_given_no_reading / (2*(self.w - 4) + 2*(self.h - 4))

            elif r != 1 or r != self.h - 2:
                for c in [0, self.w - 1]:
                    idx = r * self.w * 4 + c * 4
                    for i in range(4):
                        O[idx + i, idx + i] = p_edge_given_no_reading / (2*(self.w - 4) + 2*(self.h - 4))

        # Edge Corners
        outer_corners = [(0, 0), (0, self.w - 1), (self.h - 1, 0), (self.h - 1, self.w - 1)]
        for corner_x, corner_y in outer_corners:
            idx = corner_x * self.w * 4 + corner_y * 4
            for i in range(4):
                O[idx + i, idx + i] = p_edge_corner_given_no_reading / 4

        # Next to outer corners
        next_to_outer_corners = [(0, 1), (1, 0), (0, self.w - 2), (1, self.w - 1), (self.h - 2, 0),
                                 (self.h - 1, 1), (self.h - 2, self.w - 1), (self.h - 1, self.w - 2)]
        for corner_x, corner_y in next_to_outer_corners:
            idx = corner_x * self.w * 4 + corner_y * 4
            for i in range(4):
                O[idx + i, idx + i] = p_edge_next_to_corner_given_no_reading / 8

        # Inner edge corners
        inner_corners = [(1, 1), (1, self.w - 2), (self.h - 2, 1), (self.h - 2, self.w - 2)]
        for corner_x, corner_y in inner_corners:
            idx = corner_x * self.w * 4 + corner_y * 4
            for i in range(4):
                O[idx + i, idx + i] = p_inner_edge_corner_given_no_reading / 4

        # Return normalized O to compensate for the incorrect "p_no_reading"-value
        return O/np.sum(O)

    def find_possible_neighbors(self, x, y):
        possible_neighbors = []
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if not (dx == 0 and dy == 0):
                    if not self.out_of_bounds([x+dx, y+dy]):
                        possible_neighbors.append([x+dx, y+dy])
        return possible_neighbors

    def find_possible_second_neighbors(self, x, y):
        possible_second_neighbors = []
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if not (dx == 0 and dy == 0):
                    if not self.out_of_bounds([x+dx, y+dy]):
                        possible_second_neighbors.append([x+dx, y+dy])
        return possible_second_neighbors

    def calc_new_f(self, sensor_reading):
        new_f = self.build_O(sensor_reading).dot(np.transpose(self.T)).dot(self.f)
        # Return normalized new_f to compensate for not having a normalizing constant alpha included
        return new_f/np.sum(new_f)

    def find_most_probable_position(self):
        idx_of_highest_prob = np.argmax(self.f)
        # Since we do not really care about the direction at this point, convert to only position in room
        x = (idx_of_highest_prob // 4) // self.w
        y = (idx_of_highest_prob // 4) % self.w
        return [x, y]
