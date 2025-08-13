from constraints import *
from music_converter import combine_voices

def get_population_fitness(population: list, soprano: list, key: key.Key):
    return [get_individual_fitness(ind, soprano, key) for ind in population]

def get_individual_fitness(individual: list, soprano: list, key: key.Key):
    fitness = 0

    voices_combined = combine_voices(soprano, individual)

    fitness += check_voice_range(individual, key)
    fitness += check_voice_crossing(voices_combined)
    fitness += check_voice_overlap(voices_combined)

    return fitness