def do_crossover(selected_population: list):
    new_population = []
    pop_size = len(selected_population)

    if pop_size % 2 != 0:
        last_individual = selected_population[-1]
        selected_population = selected_population[:-1]
    else:
        last_individual = None

    for i in range(0, len(selected_population), 2):
        parent1 = selected_population[i]
        parent2 = selected_population[i+1]

        length = len(parent1)
        crossover_point = length // 2 

        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]

        new_population.extend([child1, child2])

    if last_individual:
        new_population.append(last_individual)

    return new_population