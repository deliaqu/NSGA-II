from absl import app
from absl import flags

from problem import Problem
from evolution import Evolution

FLAGS = flags.FLAGS

flags.DEFINE_integer('n', 30, '') 
flags.DEFINE_integer('k', 3, '')
flags.DEFINE_integer('population_coefficient', 4, '')
flags.DEFINE_boolean('power_law', False, '')
flags.DEFINE_float('crossover_prob', 0, '')


def f1(x, n, k):
    num_one = x.count(1)
    if num_one <= n-k or num_one == n:
        return k + num_one
    return n - num_one

def f2(x, n, k):
    num_zero = x.count(0)
    if num_zero <= n-k or num_zero == n:
        return k + num_zero
    return n - num_zero

def optima(n, k):
    optima = [(k, n+k), (n+k, k)]
    x = k
    while x <= n-k:
        optima.append((x+k, k+n-x))
        x += 1
    return optima

def main(argv):
    n = FLAGS.n
    k = FLAGS.k
    num_of_individuals = FLAGS.population_coefficient * (n - 2*k + 3)
    problem = Problem(n=n, k=k, objectives=[f1, f2])
    opt = optima(n,k)
    evo = Evolution(problem, num_of_individuals, num_of_tour_particips=2, 
                    power_law=FLAGS.power_law, crossover_prob=FLAGS.crossover_prob,
                    goal=opt, output_population_dynamics=FLAGS.output_population_dynamics)
    generation = evo.evolve()

    filename = '{}_{}_{}'.format(n, k, FLAGS.population_coefficient)
    if FLAGS.power_law:
        filename += '_power_law'
    if FLAGS.crossover_prob > 0:
        filename += '_crossover_{}'.format(FLAGS.crossover_prob)
    filename += '.xlsx'

    with open(filename, 'a') as output:
        output.write(str(generation))
        output.write('\n')


if __name__ == '__main__':
  app.run(main)