import random
from music21 import *
from music_converter import midi_to_chromosom

RANGES = [(53, 74), (48, 69), (41, 62)]

#F - d1
#c - a1
#f - d2

def generate_initial_population(soprano: list, key: key.Key):
    population = []

    num_population = 1

    for i in range(num_population):
        population.append(generate_one(soprano, key))

    return population



def generate_one(soprano: list, key: key.Key):
    one = []
    for i in range(len(soprano)):
        moment = []
        for j in range(3):
            down_range = midi_to_chromosom(RANGES[j][0], key)[0]
            up_range = midi_to_chromosom(RANGES[j][1], key)[0]
            first_num = random.randint(down_range, up_range)
            second_num = 0
            moment.append([first_num, second_num])

        one.append(moment)

    return one


