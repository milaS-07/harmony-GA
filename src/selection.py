import random

def select_new_population(population: list, fitnesses: list):
    pop_size = len(population)
    num_elite = max(1, int(len(population) * 0.1))
    
    sorted_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i], reverse=True)
    
    elite_indices = sorted_indices[:num_elite]
    elite_individuals = [population[i] for i in elite_indices]
    
    remaining_indices = sorted_indices[num_elite:]
    remaining_population = [population[i] for i in remaining_indices]
    remaining_fitnesses = [fitnesses[i] for i in remaining_indices]
    
    total_fitness = sum(remaining_fitnesses)
    probabilities = [f / total_fitness for f in remaining_fitnesses]

    num_to_select = pop_size - num_elite
    selected_individuals = []

    for _ in range(num_to_select):
        r = random.random()
        cumulative = 0
        for i, p in enumerate(probabilities):
            cumulative += p
            if r <= cumulative:
                selected_individuals.append(remaining_population[i])
                break

    new_population = elite_individuals + selected_individuals
    return new_population
    