import random

def select_new_population(population: list, fitnesses: list):
    pop_size = len(population)
    num_elite = max(1, int(pop_size * 0.1))

    sorted_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
    elite_indices = sorted_indices[:num_elite]
    elite_individuals = [population[i] for i in elite_indices]

    remaining_fitnesses = normalize_fitness(fitnesses)
    total_fitness = sum(remaining_fitnesses)
    if total_fitness == 0:
        probabilities = [1 / len(remaining_fitnesses)] * len(remaining_fitnesses)
    else:
        probabilities = [f / total_fitness for f in remaining_fitnesses]

    num_to_select = pop_size - num_elite
    selected_individuals = []
    for _ in range(num_to_select):
        r = random.random()
        cumulative = 0
        for i, p in enumerate(probabilities):
            cumulative += p
            if r <= cumulative:
                selected_individuals.append(population[i])
                break

    return elite_individuals + selected_individuals



def normalize_fitness(fitnesses, offset=1.0):
    f_min = min(fitnesses)
    return [f - f_min + offset for f in fitnesses]

