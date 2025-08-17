import random
from music21 import *
from music_converter import chromosome_to_midi
from constraints import RANGES

def mutate_population(population: list, key: key.Key):
    mutation_rate = 0.01

    new_population = []

    for chromosome in population:
        new_chromosome = []
        for moment in chromosome:
            new_moment = []

            for i, voice in enumerate(moment):
                tone, alteration = voice

                if random.random() < mutation_rate:
                    shift = random.choice([-2, -1, 1, 2])
                    low, high = RANGES[i]

                    if low <= chromosome_to_midi([tone + shift, alteration], key) <= high:
                        tone += shift
                new_moment.append([tone, alteration])
            new_chromosome.append(new_moment)
        new_population.append(new_chromosome)

    return new_population
