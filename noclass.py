#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import time
from array import array
from random import Random
from math import (
    exp,
)
from data import (
    LookupInstance,
)
from performance import (
    timeit,
    cprofile,
    Profiler,
)

TOTAL_NB_QUBITS = 512
DIFF_RANGE = 65
RND_SEED = 7186
N_SWEEPS = 1000

print 'Random Seed: ', RND_SEED


# @profile
def run(problem_id, given_temps):
    time_to_solution = time.time()
    # initialization of loop variables:
    add, sub = 0, 0
    random = Random(RND_SEED).random
    randrange = Random(RND_SEED).randrange
    choice = Random(1234).choice
    instance = LookupInstance(id=problem_id, nb_sg=420)
    # instance = LookupInstance(id=0, nb_sg=420)
    J = instance.J
    n_sweeps = N_SWEEPS
    cost = None
    possible_values = (-1, 1)
    # generate_temperatures ******************
    # temperatures = [2, 1, .5]
    temperatures = given_temps
    # ****************************************

    # get_accept_probs() *****************
    accept_probs = tuple(tuple(exp(d / T)
                               for d in xrange(-DIFF_RANGE, 0)) for T in temperatures)
    # ************************************
    # print 'Time to config: ', time.time() - time_to_solution
    # while cost != instance.min_cost:
    for i in xrange(5):
        #: Init variables for annealing
        solution = [choice(possible_values) for i in xrange(TOTAL_NB_QUBITS)]
        cost = instance.get_cost

        #: Run the annealing process
        cost = cost(solution)
        for T_i, T in enumerate(temperatures):
            start = time.time()
            for sweep in xrange(n_sweeps):
                swaps = [randrange(0, TOTAL_NB_QUBITS)
                         for i in xrange(TOTAL_NB_QUBITS)]
                for swap in swaps:
                    # update_solution ****************************
                    # sub = sum([value * solution[j] for j, value in J[swap]])
                    # sub *= solution[swap]
                    solution[swap] *= -1
                    add = sum([value * solution[j] for j, value in J[swap]])
                    add *= solution[swap]
                    # ********************************************
                    diff = 2 * add
                    if diff >= 0 or random() < accept_probs[T_i][diff]:
                        cost -= diff
                        if cost <= instance.min_cost:
                            break
                    else:
                        solution[swap] *= -1
                if cost <= instance.min_cost:
                    break
            # print T, ': ', 'Current best: ', cost, '/', instance.min_cost
            # print 'timing', time.time() - start
            if cost <= instance.min_cost:
                break
        if cost == instance.min_cost:
            break
    end = time.time() - time_to_solution

    print 'Time to solution: ', end
    return end

from multiprocessing import Pool


def drange(start, stop, step):
    res = []
    r = start
    while r < stop:
        res.append(r)
        r += step
    return res


def explore(temp):
    # ids = xrange(0, 500, 50)
    ids = [0, 100]
    times = [run(i, temp) for i in ids]
    return sum(times)/len(times)


if __name__ == '__main__':
    temps = [
        [2, 1, .5],
        [2, 1, .75, .5],
        [3, 2, 1, .5],
        [3, 2.5, 2, 1, .5],
        [2, 1.5, 1, .5],
        [3, 2, 1.5, 1, .5],
        [4, 3, 2, 1.5, 1, .5],
        [5, 4, 3, 2, 1.5, 1, .5],
        [3.2, 2.7, 2, 1.5, 1, .5],
        drange(.5, 3, .1)[::-1],
        drange(.5, 3, .2)[::-1],
        drange(.5, 3, .25)[::-1],
        drange(.5, 3, .33)[::-1],
        drange(.5, 3, .4)[::-1],
        drange(.5, 3, .5)[::-1],
    ]
    pool = Pool(processes=7)
    results = pool.map(explore, temps)
    for i, r in enumerate(results):
        print 'Entry: ', i, ', average: ', r

# To improve:
# - To find diff: if sol[i] == sol[j] -> add J[i, j] else substract.
# - Manually calculate the exp probs
# - change so that diff = new - old
# - Replace sum with for loop -> About the same, slightly slower
# - Find best configurations and temperatures
