import os
import json
from constraints import *
from music_converter import combine_voices

func_map = {
    0: "I",
    1: "II",
    2: "III",
    3: "IV",
    4: "V",
    5: "VI",
    6: "VII",
}

inversion_map = {
    1: "",
    2: "6",
    3: "64"
}

LOG_DIR = "logs"

if os.path.exists(LOG_DIR):
    import shutil
    shutil.rmtree(LOG_DIR)

os.makedirs(LOG_DIR, exist_ok=True)

def save_generation_log(generation_idx: int, population_data: list):
    log_data = []

    for ind in population_data:
        fitness_formatted = round(ind["fitness"], 1)
        breakdown_formatted = {k: round(v, 1) for k, v in ind["breakdown"].items()}

        log_ind = {
            "individual_index": ind["individual_index"],
            "chromosome": str(ind["chromosome"]),
            "chords_formatted": str(ind["chords_formatted"]),
            "fitness": fitness_formatted,
            "breakdown": breakdown_formatted
        }
        log_data.append(log_ind)

    file_path = os.path.join(LOG_DIR, f"generation_{generation_idx}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2)



def get_population_fitness(population: list, soprano: list, key: key.Key, beat_strengths: list, generation_idx: int):
    population_log = []
    for ind_idx, ind in enumerate(population):
        fitness, breakdown, chords_formatted = get_individual_fitness(
            ind, soprano, key, beat_strengths
        )

        population_log.append({
            "individual_index": ind_idx,
            "chromosome": ind,
            "fitness": fitness,
            "breakdown": breakdown,
            "chords_formatted": chords_formatted
        })

    save_generation_log(generation_idx, population_log)

    return [ind["fitness"] for ind in population_log]

def get_individual_fitness(individual: list, soprano: list, key: key.Key, beat_strengths: list):
    fitness = 0
    breakdown = {}

    voices_combined = combine_voices(soprano, individual)
    is_minor = key.mode == 'minor'

    breakdown['voice_range'] = check_voice_range(individual, key)
    fitness += breakdown['voice_range']

    breakdown['voice_crossing'] = check_voice_crossing(voices_combined)
    fitness += breakdown['voice_crossing']

    breakdown['voice_overlap'] = check_voice_overlap(voices_combined)
    fitness += breakdown['voice_overlap']

    breakdown['monotone_motion'] = check_monotone_motion(voices_combined)
    fitness += breakdown['monotone_motion']

    breakdown['voice_spacing'] = check_voice_spacing(voices_combined)
    fitness += breakdown['voice_spacing']

    breakdown['parallel_intervals'] = check_parallel_intervals(voices_combined)
    fitness += breakdown['parallel_intervals']

    score, chords = check_if_chords_exist(voices_combined, is_minor)
    breakdown['chords'] = score
    fitness += score

    breakdown['starting_chord'] = check_starting_chord(chords[0])
    fitness += breakdown['starting_chord']

    breakdown['function_transfer'] = check_function_transfer(chords, beat_strengths)
    fitness += breakdown['function_transfer']

    breakdown['final_cadence'] = check_final_cadence(chords)
    fitness += breakdown['final_cadence']

    breakdown['no_forbidden_intervals'] = check_if_allowed_intervals(individual, key)
    fitness += breakdown['no_forbidden_intervals']

    breakdown['double_jump_dissonance'] = check_if_violates_double_jump_dissonance(individual, key)
    fitness += breakdown['double_jump_dissonance']

    breakdown['forbidden_progression'] = check_forbidden_chord_progression(chords, beat_strengths)
    fitness += breakdown['forbidden_progression']

    breakdown['fifth_sixth_progression'] = check_if_right_fifth_sixth_tone_progression(chords, voices_combined)
    fitness += breakdown['fifth_sixth_progression']

    breakdown['chord_frequency'] = check_chord_frequency(chords)
    fitness += breakdown['chord_frequency']

    chords_formatted = [
        f"{func_map[chord[0]]}{inversion_map[chord[1]]}" if chord is not None else "None"
        for chord in chords
    ]

    return fitness, breakdown, chords_formatted