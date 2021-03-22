#!/usr/bin/python3
import sys
import argparse
import random
import time
import gfan_runner as gfr
import multiprocessing as mp

parser = argparse.ArgumentParser(description='Generate system of polynomials and calculate the resultant f-vector')
parser.add_argument('-r', '--drange', help='Degree range, inclusive', nargs=2, type=int, default=[0, 5])
parser.add_argument('-v', '--num-vars', help='Number of variables', type=int, default=2)
parser.add_argument('-f', '--config', help='Configuration of system', type=int, nargs='+', default=[3, 3, 3])
parser.add_argument('-c', '--count', help='Number of systems to generate', type=int, default=1)
parser.add_argument('-p', '--procs', help='Max number of concurrent processes', type=int, default=-1)

args = parser.parse_args()

# build format string for gfan
fmt = '{' 
for i in range(len(args.config)):
    if i > 0:
        fmt += ','

    tup = '(' + ','.join(('%d',) * args.num_vars) + ')'
    fmt += '(' + ','.join((tup,) * args.config[i]) + ')'
fmt += '}'

inputs = []

t0 = time.time()
# generate the inputs
for it in range(args.count):
    # check for degenerate case of 3 collinear points
    exps = []
    for i in range(len(args.config)):
        new_poly = [tuple([0] * args.num_vars)] * args.config[i] 
        while len(set(new_poly)) <= 1: # ensures no degenerate cases
            # build new list pointwise
            for i in range(args.config[i]):
                new_poly[i] = tuple([random.randint(args.drange[0], args.drange[1]) for j in range(args.num_vars)])

        exps.extend(new_poly)

    # convert list of tuples to list
    exps_list = []
    for i in range(len(exps)):
        exps_list.extend(list(exps[i]))

    inputs.append(fmt % tuple(exps_list))
# end for loop

if args.procs > 0:
    pool = mp.Pool(args.procs, initializer=gfr.initializer)
else:
    pool = mp.Pool()

results = gfr.GfanRunner().multi_run(pool, inputs)
dt = time.time() - t0

# sort output by f_0
unique_f_vecs = sorted(list(set([r[1] for r in results])), key=lambda x: x[0], reverse=False)

# print the output
for vec, out in results:
    print(vec)
    print(out)
    print('')

print('Unique f-vectors: ')
for fv in unique_f_vecs:
    print(fv)

print('Time: %f for %d results' % (dt, len(results)))
print('Average time: %f per item' % (dt / len(results)))
