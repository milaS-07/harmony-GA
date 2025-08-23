import random
from music21 import *
from music_converter import chromosome_to_midi, midi_to_chromosome
from constraints import RANGES, get_tone
from initial_population import right_voice_ranges, right_voice_spacing, check_if_triad, no_voice_overlap

def mutate_population(population: list, soprano: list, key: key.Key):
    mutation_rate = 0.1

    new_population = []

    is_minor = key.mode == 'minor'

    for chromosome in population:
        new_chromosome = chromosome.copy()

        if random.random() < mutation_rate:
            idx = random.randint(0, len(chromosome) - 2)
            new_moment = []

            soprano_midi = chromosome_to_midi(soprano[idx], key)
            upper_limit = soprano_midi

            for j, (low, high) in enumerate(RANGES):
                voice_high = min(high, upper_limit)
                voice_low = low

                down_chrom = midi_to_chromosome(voice_low, key)[0]
                up_chrom = midi_to_chromosome(voice_high, key)[0]

                alteration = 0

                while True:
                    if down_chrom >= up_chrom:
                        upper_limit = chromosome_to_midi([down_chrom, alteration], key)
                        new_moment.append([down_chrom, alteration])
                        break

                    tone = random.randint(down_chrom, up_chrom)
                    alteration = 0
                    if is_minor and get_tone([tone, 0])[0] == 6:
                        alteration = 1

                    if right_voice_ranges(tone, alteration, upper_limit, key) and \
                       (random.random() < 0.15 or right_voice_spacing(new_moment, tone, soprano[idx])) and \
                       (idx == len(soprano) - 1 or random.random() < 0.002 or check_if_triad(soprano[idx], new_moment + [[tone, alteration]], key)) and \
                       (idx == 0 or no_voice_overlap(tone, alteration, chromosome[idx-1], j + 1, idx, soprano)):
                        upper_limit = chromosome_to_midi([tone, alteration], key)
                        new_moment.append([tone, alteration])
                        break

            new_chromosome[idx] = new_moment

        new_population.append(new_chromosome)

    return new_population
