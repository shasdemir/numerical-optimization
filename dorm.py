import random
import math
import operator


dorms = ['Zeus', 'Athena', 'Hercules', 'Bacchus', 'Pluto']  # dorms, each have 2 places

preferences = [('Toby', ('Bacchus', 'Hercules')),
               ('Steve', ('Zeus', 'Pluto')),
               ('Andrea', ('Athena', 'Zeus')),
               ('Sarah', ('Zeus', 'Pluto')),
               ('Dave', ('Athena', 'Bacchus')),
               ('Jeff', ('Hercules', 'Pluto')),
               ('Fred', ('Pluto', 'Athena')),
               ('Suzie', ('Bacchus', 'Hercules')),
               ('Laura', ('Bacchus', 'Hercules')),
               ('Neil', ('Hercules', 'Athena'))]

domain = [(0, i) for i in range(len(dorms)*2-1, -1, -1)]


def print_solution(vec):
    slots = []
    for k in range(len(dorms)):  # create two slots for each dorm
        slots += [k, k]

    for k in range(len(vec)):  # loop over each student's assignment
        x = int(vec[k])

        dorm = dorms[slots[x]]  # choose the slot from the remaining ones

        print preferences[k][0], dorm  # show the student and the assigned dorm

        del slots[x]  # remove this slot


def dorm_cost(vec):
    cost = 0
    slots = []
    for k in range(len(dorms)):  # create two slots for each dorm
        slots += [k, k]

    for k in range(len(vec)):  # loop over each student
        x = int(vec[k])
        dorm = dorms[slots[x]]
        pref = preferences[k][1]

        # first choice costs 0, second choice costs 1, not on the list costs 3
        if pref[0] == dorm:
            cost += 0
        elif pref[1] == dorm:
            cost += 1
        else:
            cost+= 3

        del slots[x]  # remove the selected slot

    return cost