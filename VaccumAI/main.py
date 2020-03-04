from Model import Model
from Room import Room
import matplotlib.pyplot as plt


def calc_error(room, guessed_position):
    return abs(room.robot.pos[0] - guessed_position[0]) + abs(room.robot.pos[1] - guessed_position[1])


def main():

    ROOM_HEIGHT = 6
    ROOM_WIDTH = 6

    room = Room(ROOM_HEIGHT, ROOM_WIDTH)
    model = Model(room)

    nbr_of_moves = 0
    correct_guesses = 0
    total_error = 0
    real_positions = []
    guessed_positions = []
    guess_pos = [0, 0]
    for i in range(300):

        nbr_of_moves += 1
        room.room[room.robot.pos[0], room.robot.pos[1]] = 0
        pos = room.robot.move()
        room.room[pos[0], pos[1]] = 1
        real_positions.append(pos)

        room.room[guess_pos[0], guess_pos[1]] = 0
        guess_pos = model.guess_move()
        room.room[guess_pos[0], guess_pos[1]] = 2
        guessed_positions.append(guess_pos)

        #plot_map(room.room)

        if guessed_positions[-1] == pos:
            correct_guesses += 1
        error = calc_error(room, guessed_positions[-1])
        total_error += error

    print("Average error: " + str(total_error / nbr_of_moves))
    print("Accuracy: " + str(correct_guesses / nbr_of_moves))


def plot_map(room):
    plt.figure(figsize=(6, 6))
    plt.pcolor(room, cmap='magma', edgecolors='k', linewidths=3)
    plt.show()


if __name__ == "__main__":
    main()
