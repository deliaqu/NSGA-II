class Individual(object):

    def __init__(self):
        self.rank = None
        self.crowding_distance = None
        self.domination_count = None
        self.dominated_solutions = None
        self.features = None
        self.objectives = None

    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.features == other.features
        return False

    def weakly_dominates(self, other_individual):
        assert len(self.objectives) == len(other_individual.objectives)
        for index, obj in enumerate(self.objectives):
            if obj < other_individual.objectives[index]:
                return False
        return True

    def dominates(self, other_individual):
        assert len(self.objectives) == len(other_individual.objectives)
        strict = False
        for index, obj in enumerate(self.objectives):
            if obj < other_individual.objectives[index]:
                return False
            if not strict and obj > other_individual.objectives[index]:
                strict = True
        return strict

