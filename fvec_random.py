#!/usr/bin/python3
import sys
import argparse
import random
import time
import fvec_runner as fvr
import fvec_util as util
import multiprocessing as mp
from ast import literal_eval
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Generate system of polynomials and calculate the resultant f-vector')

parser.add_argument('-r', '--drange', help='Degree range, inclusive', nargs=2, type=int, default=[0, 5])
parser.add_argument('-v', '--num-vars', help='Number of variables', type=int, default=2)
parser.add_argument('-c', '--count', help='Number of systems to generate', type=int, default=1)
parser.add_argument('-p', '--procs', help='Max number of concurrent processes', type=int, default=-1)
parser.add_argument('-o', '--output', help='Name of output file', type=str, default=None)
parser.add_argument('-a', '--append', help='Name of append file', type=str, default=None)
parser.add_argument('-l', '--latex', help='Format unique f-vectors for TeX', action='store_true')

cfg_grp = parser.add_mutually_exclusive_group(required=True)
cfg_grp.add_argument('-g', '--config', help='Configuration of system', type=int, nargs='+')
cfg_grp.add_argument('-f', '--fstr', help='Configuration of system as a (properly formatted) format string')
cfg_grp.add_argument('-i', '--input', help='Input file from a program crash', default=None)

args = parser.parse_args()

if args.input is None:
    # build format string for gfan
    if args.fstr is None:
        # config specified
        config = args.config
        fmt = '{' 
        for i in range(len(config)):
            if i > 0:
                fmt += ','

            tup = '(' + ','.join(('%d',) * args.num_vars) + ')'
            fmt += '(' + ','.join((tup,) * config[i]) + ')'
        fmt += '}'
    else:
        # config not specified
        fmt = args.fstr
        config = util.parse_configuration(fmt)

    inputs = []

    t0 = time.time()
    # generate the inputs
    print('Generating %d inputs' % args.count)
    for it in tqdm(range(args.count)):
        # check for degenerate case of 3 collinear points
        exps = []
        for i in range(len(args.config)):
            new_poly = [tuple([0] * args.num_vars)] * config[i] 
            while len(set(new_poly)) <= 1: # ensures no degenerate cases
            # while not util.check_valid(new_poly, config) or new_poly in exps:
                # build new list pointwise
                for i in range(config[i]):
                    new_poly[i] = tuple([random.randint(args.drange[0], args.drange[1]) for j in range(args.num_vars)])

            exps.extend(new_poly)

        # convert list of tuples to list
        exps_list = []
        for i in range(len(exps)):
            exps_list.extend(list(exps[i]))

        inputs.append(fmt % tuple(exps_list))
    # end for loop

    if args.procs > 0:
        pool = mp.Pool(args.procs, initializer=fvr.initializer)
    else:
        pool = mp.Pool()

    results = fvr.multi_run(pool, inputs)
    dt = time.time() - t0

    if args.output is None:
        util.print_results(results, dt=dt, tex=args.latex, app=args.append)
    else:
        util.print_results(results, filename=args.output, dt=dt, tex=args.latex, app=args.append)

else:
    # load results from dump file
    with open(args.input, 'r') as f:
        # for line in f:
        #     print(line)
        #     input()
        results = [list(literal_eval(line)) for line in f]

    if args.output is None:
        util.print_results(results, dump=True, tex=args.latex)
    else:
        util.print_results(results, dump=True, filename=args.output, tex=args.latex)
