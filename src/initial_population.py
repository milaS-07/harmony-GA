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

        for j, (low, high) in enumerate(RANGES):
            voice_high = min(high, upper_limit)
            voice_low = low

            down_chrom = midi_to_chromosome(voice_low, key)[0]
            up_chrom = midi_to_chromosome(voice_high, key)[0]

            alteraion = 0
            while True:
                tone = random.randint(down_chrom, up_chrom)
                if right_voice_ranges(tone, alteraion, upper_limit, key):
                    upper_limit = chromosome_to_midi([tone, alteraion], key)

                    moment.append([tone, alteraion])
                    break

        individual.append(moment)

    return individual

def right_voice_ranges(tone: int, alteration: int, upper_limit: int, key: key.Key):
    return chromosome_to_midi([tone, alteration], key) <= upper_limit

def no_voice_overlap(tone: int, alteration: int, last_moment: list, tone_ind: int, moment_ind: int, soprano: list):
    whole_last_moment = soprano[moment_ind - 1] + last_moment

    if tone_ind == 3:
        if tone > whole_last_moment[tone_ind - 1][0]:
            return False
        elif tone == whole_last_moment[tone_ind - 1][0]:
            return alteration <= whole_last_moment[tone_ind - 1]
        else:
            return True
    else:
        if whole_last_moment[tone_ind + 1] > tone > whole_last_moment[tone_ind - 1]:
            return True
        elif whole_last_moment[tone_ind + 1] == tone:
            return whole_last_moment[tone_ind + 1][1]
        elif tone == whole_last_moment[tone_ind - 1]:
        else:
            return False

