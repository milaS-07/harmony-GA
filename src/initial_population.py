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

            alteration = 0

            while True:
                tone = random.randint(down_chrom, up_chrom)
                if right_voice_ranges(tone, alteration, upper_limit, key):
                    if i == 0 or no_voice_overlap(tone, alteration, individual[i-1], j + 1, i, soprano):
                        upper_limit = chromosome_to_midi([tone, alteration], key)

                        moment.append([tone, alteration])
                        break


        individual.append(moment)

    return individual

def right_voice_ranges(tone: int, alteration: int, upper_limit: int, key: key.Key):
    return chromosome_to_midi([tone, alteration], key) <= upper_limit

def no_voice_overlap(tone: int, alteration: int, last_moment: list, voice_ind: int, moment_ind: int, soprano: list): #TODO da nikad ne gresi
    whole_last_moment = [soprano[moment_ind - 1]]
    whole_last_moment.extend(last_moment)

    last_moment_tone_up = whole_last_moment[voice_ind - 1][0]
    last_moment_alteration_up = whole_last_moment[voice_ind - 1][1]

    if voice_ind == 3:
        if tone > last_moment_tone_up:
            return False
        elif tone == last_moment_tone_up:
            return alteration <= last_moment_alteration_up
        else:
            return True
    else:
        last_moment_tone_down = whole_last_moment[voice_ind + 1][0]
        last_moment_alteration_down = whole_last_moment[voice_ind + 1][1]

        if last_moment_tone_down < tone < last_moment_tone_up:
            return True
        elif last_moment_tone_down == tone:
            return last_moment_alteration_down <= alteration
        elif tone == last_moment_tone_up:
            return last_moment_alteration_up >= alteration
        else:
            return False

