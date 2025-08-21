import random
from music_converter import *
from initial_population import *
from score_utils import *
from constraints import * #TODO obrisati kasnije
from fitness import *
from selection import *
from crossover import *
from mutation import *

def main():
    num_generation = 40
    population_size = 40

    broj = 5
    korpus_cist = get_bach_corpus(broj)
    korpus = get_clean_harmony(korpus_cist)

    sopran = get_soprano(korpus)
    sopran_chrom = soprano_to_chromosome(sopran)

    beat_strengths = get_beat_strengths(sopran)
    detected_key = sopran.analyze('key')
    
    # --- Prva generacija ---
    population = generate_initial_population(sopran_chrom, detected_key, population_size)
    fitnesses = get_population_fitness(
        population, sopran_chrom, detected_key, beat_strengths, generation_idx=0
    )
    # formatiranje za print
    fitnesses_rounded = [round(f, 1) for f in fitnesses]
    print(fitnesses_rounded)
    print("---")

    # --- Sledeće generacije ---
    for gen_idx in range(1, num_generation - 1):
        fitnesses = get_population_fitness(
            population, sopran_chrom, detected_key, beat_strengths, generation_idx=gen_idx
        )
        population = select_new_population(population, fitnesses)
        fitnesses_after_selection = get_population_fitness(
            population, sopran_chrom, detected_key, beat_strengths, generation_idx=gen_idx
        )
        # formatiranje za print
        fitnesses_after_selection_rounded = [round(f, 1) for f in fitnesses_after_selection]
        print(fitnesses_after_selection_rounded)
        print("---")
        random.shuffle(population)
        population = do_crossover(population)
        population = mutate_population(population, detected_key)

    # --- Završna generacija ---
    print("kraj")
    fitnesses = get_population_fitness(
        population, sopran_chrom, detected_key, beat_strengths, generation_idx=num_generation - 1
    )
    population = select_new_population(population, fitnesses)
    print("~~~")
    fitnesses_after_selection = get_population_fitness(
        population, sopran_chrom, detected_key, beat_strengths, generation_idx=num_generation - 1
    )
    # formatiranje za print
    fitnesses_after_selection_rounded = [round(f, 1) for f in fitnesses_after_selection]
    print(fitnesses_after_selection_rounded)
    
    # --- Najbolja jedinka ---
    best_fitness_genereted = build_full_score(sopran, population[0], detected_key)
    best_fitness_genereted.show()


if __name__ == "__main__":
    main()
