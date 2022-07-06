from ast import operator

from numpy import power
from population import Population
import random
import copy
from numpy import linspace
from numpy.random import rand

def sample(cdf):
    n = len(cdf)
    x = rand()
    if x < cdf[0]:
        return 1
    low = 0
    high = n - 1
    while high - low > 1:
        mid = (low + high) >> 1 
        if x > cdf[mid]:
            low = mid
        else:
            high = mid
    return high + 1

class NSGA2Utils:

    def __init__(self, problem, num_of_individuals=100,
                 num_of_tour_particips=2, power_law=False, crossover_prob=0.9):

        self.problem = problem
        self.num_of_individuals = num_of_individuals
        self.num_of_tour_particips = num_of_tour_particips
        self.n = problem.n
        self.power_law = None
        if power_law:
            n = self.n
            dist = (linspace(1, n//2, n//2) ** (- 1.5)).cumsum()
            dist /= dist[-1]
            self.power_law = dist
        self.crossover_prob = crossover_prob

    def create_initial_population(self):
        population = Population()
        for _ in range(self.num_of_individuals):
            individual = self.problem.generate_individual()
            self.problem.calculate_objectives(individual)
            population.append(individual)
        return population

    def fast_nondominated_sort(self, population):
        population.fronts = [[]]
        for individual in population:
            individual.domination_count = 0
            individual.dominated_solutions = []
            for other_individual in population:
                if individual.dominates(other_individual):
                    individual.dominated_solutions.append(other_individual)
                elif other_individual.dominates(individual):
                    individual.domination_count += 1
            if individual.domination_count == 0:
                individual.rank = 0
                population.fronts[0].append(individual)
        i = 0
        while len(population.fronts[i]) > 0:
            temp = []
            for individual in population.fronts[i]:
                for other_individual in individual.dominated_solutions:
                    other_individual.domination_count -= 1
                    if other_individual.domination_count == 0:
                        other_individual.rank = i+1
                        temp.append(other_individual)
            i = i+1
            population.fronts.append(temp)
        
    def calculate_crowding_distance(self, front):
        if len(front) > 0:
            solutions_num = len(front)
            for individual in front:
                individual.crowding_distance = 0

            for m in range(len(front[0].objectives)):
                random.shuffle(front)
                front.sort(key=lambda individual: individual.objectives[m])
                front[0].crowding_distance = float("inf")
                front[solutions_num-1].crowding_distance = float("inf")
                m_values = [individual.objectives[m] for individual in front]
                scale = max(m_values) - min(m_values)
                if scale == 0: scale = 1
                for i in range(1, solutions_num-1):
                    front[i].crowding_distance += (float(front[i+1].objectives[m] - front[i-1].objectives[m]))/scale

    def crowding_operator(self, individual, other_individual):
        if (individual.rank < other_individual.rank) or \
            ((individual.rank == other_individual.rank) and (individual.crowding_distance > other_individual.crowding_distance)):
            return 1
        else:
            return -1

    def create_children(self, population):
        children = []
        while len(children) < len(population):
            parent1 = self.__tournament(population)
            parent2 = self.__tournament(population)
            if self.crossover_prob > 0:
                while parent2 is parent1:
                    parent2 = self.__tournament(population)
            child1 = copy.deepcopy(parent1)
            child2 = copy.deepcopy(parent2)
            if self.crossover_prob > 0 and self.__choose_with_prob(self.crossover_prob):
                child1, child2 = self.__crossover(child1, child2)
            self.__mutate(child1)
            self.__mutate(child2)
            self.problem.calculate_objectives(child1)
            self.problem.calculate_objectives(child2)
            children.append(child1)
            children.append(child2)
        return children

    def __crossover(self, individual1, individual2):
        child1 = self.problem.generate_individual()
        child2 = self.problem.generate_individual()
        for i in range(self.n):
            if self.__choose_with_prob(0.5):
                child1.features[i] = individual1.features[i]
                child2.features[i] = individual2.features[i]
            else:
                child1.features[i] = individual2.features[i]
                child2.features[i] = individual1.features[i]
        return child1, child2


    def __mutate(self, child):
        prob = float(1)/self.n
        if (self.power_law is not None):
            prob = float(sample(self.power_law))/self.n
        for gene in range(self.n):
            if self.__choose_with_prob(prob):
                child.features[gene] = 1 - child.features[gene]

                
    def __tournament(self, population):
        participants = random.sample(population.population, self.num_of_tour_particips)
        best = None
        for participant in participants:
            if best is None or (self.crowding_operator(participant, best) == 1):
                best = participant

        return best

    def __choose_with_prob(self, prob):
        if random.random() <= prob:
            return True
        return False
