import time
import random
import math
from numba import jit, autojit

### REMOVE @jit DECORATORS TO MAKE THIS WORK

# prepare data ********************************************************************************************************

people = [('Seymour', 'BOS'),
          ('Franny', 'DAL'),
          ('Zooey', 'CAK'),
          ('Walt', 'MIA'),
          ('Buddy', 'ORD'),
          ('Les', 'OMA')]

destination = 'LGA'  # LaGuardia Airport in New York


flights = {}
for line in file('schedule.txt'):
    origin, dest, depart, arrive, price = line.strip().split(',')
    flights.setdefault((origin, dest), [])

    # add details
    flights[(origin, dest)].append((depart, arrive, int(price)))


# helper functions ****************************************************************************************************


def get_minutes(t):  # how many minutes into the day a given time is
    x = time.strptime(t, '%H:%M')
    return x[3]*60 + x[4]


def print_schedule(r):
    for d in range(0, len(r), 2):
        name = people[math.trunc(d/2.)][0]
        origin = people[math.trunc(d/2.)][1]
        out = flights[(origin, destination)][r[d]]
        ret = flights[(destination, origin)][r[d+1]]
        print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (name, origin, out[0], out[1], out[2],
                                                                    ret[0], ret[1], ret[2])


# cost function *******************************************************************************************************

def schedule_cost(solution):
    """ The cost function depends on a few parameters:
    Total cost of the trip,
    Total time spent at airport waiting for members of the family, $1 per minute
    Total flight time, $0.50 per minute on the plane
    If the car is returned later in the day than when it was rented, add $50 """

    total_price = 0
    latest_arrival = 0
    earliest_departure = 24 * 60 # times are minutes from the beginning of the day
    earliest_departure_outbound = earliest_departure
    total_wait = 0
    for d in xrange(len(solution) / 2): # d iterates as index of people
        # get the inbound and outbound flights
        origin = people[d][1]
        outbound_flight = flights[(origin, destination)][int(solution[2*d])]
        return_flight = flights[(destination, origin)][int(solution[2*d+1])]

        # increase total flight prices
        total_price += outbound_flight[2]
        total_price += return_flight[2]

        # track the latest arrival and earliest departure
        if latest_arrival < get_minutes(outbound_flight[1]):
            latest_arrival = get_minutes(outbound_flight[1])
        if earliest_departure > get_minutes(return_flight[0]):
            earliest_departure = get_minutes(return_flight[0])

        # also track the earliest departure for the outbound flight
        if earliest_departure > get_minutes(outbound_flight[0]):
            earliest_departure = get_minutes(outbound_flight[0])

    for d in xrange(len(solution) / 2):  # d iterates as index of people
        # get the inbound and outbound flights
        origin = people[d][1]
        outbound_flight = flights[(origin, destination)][int(solution[2 * d])]
        return_flight = flights[(destination, origin)][int(solution[2 * d + 1])]

        # every person must wait at the airport until the last person arrives
        # they also must arrive at the same time and wait for their flights
        total_wait += latest_arrival - get_minutes(outbound_flight[1])
        total_wait += get_minutes(return_flight[0]) - earliest_departure

    # does this solution require an extra day of car rental? Add $50 if so.
    if latest_arrival < earliest_departure:
        total_price += 50

    flight_time = 0
    for d in xrange(len(solution) / 2):  # add penalty for total flight time
        outbound_flight = flights[(origin, destination)][int(solution[2 * d])]
        return_flight = flights[(destination, origin)][int(solution[2 * d + 1])]

        flight_time += (get_minutes(outbound_flight[1]) - get_minutes(outbound_flight[0]))
        flight_time += (get_minutes(return_flight[1]) - get_minutes(return_flight[0]))

    # if anyone has to be at the airport before 8:00am we penalize that solution by $20
    sabahin_korunde_kalkma_cezasi = 0
    penalty_time = 480  # 08:00
    if earliest_departure < penalty_time:
        sabahin_korunde_kalkma_cezasi += 20
    if earliest_departure_outbound < penalty_time:
        sabahin_korunde_kalkma_cezasi += 20

    return total_price + total_wait + flight_time * 0.5 + sabahin_korunde_kalkma_cezasi


def random_point(domain):
    return [random.randint(k[0], k[1]) for k in domain]


# optimization algorithms *********************************************************************************************

def random_optimize(domain, costf):
    """
    :param domain: Lower and upper bounds for each element, as a list of tuples.
    :param costf: The cost function to be used.
    :return: Returns the best guess.
    """

    best = 9e10  # make sure this is more than most random guesses and is an unacceptable result
    bestr = None
    for i in range(10000):
        # create a random solution, get the cost
        # r = [random.randint(domain[k][0], domain[k][1]) for k in range(len(domain))]
        r = [random.randint(k[0], k[1]) for k in domain]
        cost = costf(r)

        if cost < best:
            best = cost
            bestr = r
    return bestr


def hill_climb(domain, costf):
    solution = [random.randint(k[0], k[1]) for k in domain]  # create random solution

    iter_count = 0
    while 1:  # main loop
        iter_count += 1

        neighbors = []  # create the list of neighboring solutions
        for j in range(len(domain)):
            if solution[j] > domain[j][0]:
                neighbors.append(solution[0:j] + [solution[j]-1] + solution[j+1:])
            if solution[j] < domain[j][1]:
                neighbors.append(solution[0:j] + [solution[j]+1] + solution[j+1:])

        neighbors.append(solution)
        current = costf(solution)
        # see what the best solution amongst the neighbors and current point is
        best_cost, solution = min([(costf(k), k) for k in neighbors], key=lambda e: e[0])
        if best_cost == current:
            break

    # print 'Hill Climbing iterations: %s' % iter_count
    return solution


def multiple_hill_climb(domain, costf, iters):
    """ Hill Climb from different starting points iters times, report the best result. """

    solutions = []
    for k in xrange(iters):
        this_sol = hill_climb(domain, costf)
        solutions.append((costf(this_sol), this_sol))

    return min(solutions)[1]


def simulated_annealing(domain, costf, T=10000., cool=0.9999, step=1):
    vec = random_point(domain)  # start from a random solution

    while T > 0.1:
        index = random.randint(0, len(domain)-1)  # choose a random index do change
        direction = step * (-1)**random.randint(0, 1)  # choose a random direction * stepsize

        new_vec = vec[:]  # make a new list with the index value shifted by direction
        new_vec[index] += direction

        if new_vec[index] < domain[index][0]:  # if the new vector is outside the domain, put it back
            new_vec[index] = domain[index][0]
        if new_vec[index] > domain[index][1]:
            new_vec[index] = domain[index][1]

        old_cost = costf(vec)  # calculate the current and new costs
        new_cost = costf(new_vec)

        # is the new cost lower, or does it make the probability cutoff?
        if new_cost < old_cost:
            vec = new_vec
        else:
            p = pow(math.e, -(new_cost - old_cost) / T)
            if random.random() < p:
                vec = new_vec

        T *= cool  # decrease the temperature
    return vec


def multiple_simulated_annealing(domain, costf, iters):
    solutions = []
    for k in xrange(iters):
        this_sol = simulated_annealing(domain, costf)
        solutions.append((costf(this_sol), this_sol))

    return min(solutions)[1]


def genetic_algorithm(domain, costf, popsize=100, step=1, mutation_prob=0.3, elite_percentage=0.3, maxiter=100):
    """ popsize: size of the population
        mutation_prob: probability that a new member of the population will be a mutant rather than a crossover
        elite_percentage: the fraction of the population that will pass to the nex generation and be used as
        basis for mutation and crossover
        maxiter: number of generations to run """

    def mutate(vec):  # CAREFUL: can go out of bounds for different step sizes
        i = random.randint(0, len(vec)-1)
        if random.random() < 0.5 and vec[i] > domain[i][0]:
            return vec[0:i] + [vec[i]-step] + vec[i+1:]
        elif vec[i] < domain[i][1]:
            return vec[0:i] + [vec[i] + step] + vec[i + 1:]
        else:
            return vec

    def crossover(r1, r2):
        i = random.randint(1, len(domain)-2)
        return r1[0:i] + r2[i:]

    pop = []  # build the initial population
    for i in xrange(popsize):
        pop.append(random_point(domain))

    elite_count = int(elite_percentage * popsize)

    for i in xrange(maxiter):  # main loop
        #print 'pop: ' + str(pop)
        scores = [(costf(v), v) for v in pop]
        scores.sort()
        ranked_vectors = [v for (s, v) in scores]

        pop = ranked_vectors[0:elite_count]  # start by preserving the elite

        while len(pop) < popsize:  # add mutated and crossovered forms of the winners
            if random.random() < mutation_prob:
                c = random.randint(0, elite_count)
                pop.append(mutate(ranked_vectors[c]))
            else:
                c1 = random.randint(0, elite_count)
                c2 = random.randint(0, elite_count)
                pop.append(crossover(ranked_vectors[c1], ranked_vectors[c2]))

        #print scores[0][0]  # current best score
    return scores[0][1]




















