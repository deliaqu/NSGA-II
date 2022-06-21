from numpy import power
from utils import NSGA2Utils
from population import Population
import random

class Evolution:

    def __init__(self, problem, num_of_individuals, num_of_tour_particips, power_law, crossover_prob, goal=[], output_population_dynamics=False):
        self.utils = NSGA2Utils(problem, num_of_individuals, num_of_tour_particips, power_law, crossover_prob)
        self.population = None
        self.num_of_individuals = num_of_individuals
        self.power_law = power_law
        self.goal = goal
        self.output_population_dynamics = output_population_dynamics
        self.population_dynamics = []
        self.successful_parents = []

    def stop(self, population):
        if not population: return False
        covered = set()
        for ind in population:
            covered.add(tuple(ind.objectives))
        for target in self.goal:
            if target not in covered:
                return False
        return True

    def calculate_population_dynamics(self):
        nums = [0 for i in range(self.utils.n+1)]
        features = [ind.features for ind in self.population]
        for fea in features:
            num_one = fea.count(1)
            nums[num_one] += 1
        self.population_dynamics.append(nums)
    
    def found_all_ones(self):
        for ind in self.population:
            if 0 not in ind.features:
                return True
        return False

    def evolve(self):
        self.population = self.utils.create_initial_population()
        self.utils.fast_nondominated_sort(self.population)
        for front in self.population.fronts:
            self.utils.calculate_crowding_distance(front)
        children, successful_parents = self.utils.create_children(self.population, self.output_population_dynamics)
        returned_population = None
        generation = 0
        if self.output_population_dynamics and not self.found_all_ones():
            successful_parents = [(pair) + (generation,) for pair in successful_parents]
            self.successful_parents.extend(successful_parents)

        stop, missing = self.stop(returned_population)
        while not stop:
            if self.output_population_dynamics and generation % 500 == 0:
                self.calculate_population_dynamics()
            self.population.extend(children)
            self.utils.fast_nondominated_sort(self.population)
            new_population = Population()
            front_num = 0
            generation += 1
            while len(new_population) < self.num_of_individuals and len(new_population) + len(self.population.fronts[front_num]) <= self.num_of_individuals:
                self.utils.calculate_crowding_distance(self.population.fronts[front_num])
                new_population.extend(self.population.fronts[front_num])
                front_num += 1
            self.utils.calculate_crowding_distance(self.population.fronts[front_num])
            ranked_by_dis = dict()
            for ind in self.population.fronts[front_num]:
                dis = ind.crowding_distance
                if dis in ranked_by_dis: ranked_by_dis[dis].append(ind)
                else: ranked_by_dis[dis] = [ind]
            ranked_by_dis = sorted(ranked_by_dis.items(), reverse=True)
            index = 0
            while len(new_population) < self.num_of_individuals and len(new_population) + len(ranked_by_dis[index][1]) <= self.num_of_individuals:
                new_population.extend(ranked_by_dis[index][1])
                index += 1
            ran = random.sample(ranked_by_dis[index][1], self.num_of_individuals-len(new_population))
            new_population.extend(ran)
            returned_population = self.population
            self.population = new_population
            self.utils.fast_nondominated_sort(self.population)
            for front in self.population.fronts:
                self.utils.calculate_crowding_distance(front)
            children, successful_parents = self.utils.create_children(self.population, self.output_population_dynamics)
            if self.output_population_dynamics and not self.found_all_ones():
                successful_parents = [(pair) + (generation,) for pair in successful_parents]
                self.successful_parents.extend(successful_parents)
            stop = self.stop(returned_population)
        print(generation)
        return returned_population, generation, self.population_dynamics, self.successful_parents
