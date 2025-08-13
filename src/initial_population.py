import random
from music21 import *
from music_converter import midi_to_chromosome, chromosome_to_midi
from constraints import RANGES



def generate_initial_population(soprano: list, key: key.Key):
    population = []

    num_population = 1

    for i in range(num_population):
        population.append(generate_individual(soprano, key))

    return population



def generate_individual(soprano: list, key: key.Key):
    individual = []
    for i in range(len(soprano)):
        moment = []
        soprano_midi = chromosome_to_midi(soprano[i], key)

        upper_limit = soprano_midi

        for (low, high) in RANGES:
            voice_high = min(high, upper_limit)
            voice_low = low

            down_chrom = midi_to_chromosome(voice_low, key)[0]
            up_chrom = midi_to_chromosome(voice_high, key)[0]

            second_num = 0
            while True:
                first_num = random.randint(down_chrom, up_chrom)
                if chromosome_to_midi([first_num, second_num], key) <= upper_limit:
                    moment.append([first_num, second_num])
                    upper_limit = chromosome_to_midi([first_num, second_num], key)
                    break

        individual.append(moment)

    return individual


