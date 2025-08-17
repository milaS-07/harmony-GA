import random

def select_new_population(population: list, fitnesses: list):
    pop_size = len(population)
    num_elite = max(1, int(pop_size * 0.1))

    sorted_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
    
    elite_indices = sorted_indices[:num_elite]
    elite_individuals = [population[i] for i in elite_indices]

    remaining_indices = sorted_indices[num_elite:]
    remaining_population = [population[i] for i in remaining_indices]
    remaining_fitnesses = [fitnesses[i] for i in remaining_indices]

    
    num_to_select = pop_size - num_elite
    min_fitness = min(remaining_fitnesses, default=0)
    if min_fitness < 0:
        remaining_fitnesses = [f - min_fitness + 1 for f in remaining_fitnesses]

    total_fitness = sum(remaining_fitnesses)
    if total_fitness == 0:
        probabilities = [1 / len(remaining_fitnesses)] * len(remaining_fitnesses)
    else:
        probabilities = [f / total_fitness for f in remaining_fitnesses]

    selected_individuals = []
    for _ in range(num_to_select):
        r = random.random()
        cumulative = 0
        for i, p in enumerate(probabilities):
            cumulative += p
            if r <= cumulative:
                selected_individuals.append(remaining_population[i])
                break

    return elite_individuals + selected_individuals
