from individual import Individual
import random

class Problem:

    def __init__(self, n, k, objectives):
        self.n = n
        self.k = k
        self.objectives = objectives

    def generate_individual(self):
        individual = Individual()
        individual.features = [random.randint(0, 1) for _ in range(self.n)]
        return individual

    def calculate_objectives(self, individual):
        individual.objectives = [f(individual.features, self.n, self.k) for f in self.objectives]
