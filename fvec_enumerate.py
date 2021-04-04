#!/usr/bin/python3
import argparse
import fvec_runner as fvr
import fvec_util as util
import time
import itertools
import multiprocessing as mp
from os import cpu_count
from tqdm import tqdm
from operator import add
from ast import literal_eval

# START_INDEX = 49287
START_INDEX = 0

class ConfigurationValidator():
    def __init__(self, cfg, fstr):
        self.fstr = fstr
        self.cfg = cfg

    def process_config(self, exps_str):
        exps = list(literal_eval(self.fstr.replace('{', '').replace('}', '') % exps_str)) # hack, but should work assuming nice input
        return self.fstr % exps_str if util.check_valid(exps, self.cfg) else None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Enumerate systems of polynomials and calculate the resultant f-vectors')
    parser.add_argument('-r', '--drange', help='Monomial degree range, inclusive', nargs=2, type=int, default=[0, 5])
    parser.add_argument('-f', '--fstr', help='Configuration of system as a (properly formatted) format string', default='{((0,0),(0,1),(1,0)),((0,0),(%d,%d),(%d,%d)),((0,0),(%d,%d),(%d,%d))}')
    parser.add_argument('-p', '--procs', help='Number of concurrent processes; if omitted, uses all available CPU cores', type=int, default=-1)
    parser.add_argument('-c', '--count', help='Number of iterations to perform; if omitted, performs all possible computations based on degree range', type=int, default=-1)
    parser.add_argument('-o', '--output', help='Name of output file', type=str, default=None)
    parser.add_argument('-s', '--start', help='Starting offset for the iterator', type=int, default=START_INDEX)
parser.add_argument('-l', '--latex', help='Format unique f-vectors for TeX', action='store_true')

    args = parser.parse_args()

    # calculate the configuration i.e. [3,3,3] for the default
    cfg = util.parse_configuration(args.fstr)

    # use cmd arg num iterations if specified, otherwise do all of them
    num_slots = fstr.count('%')
    num_iterations = args.count if args.count > 0 else (args.drange[1]-args.drange[0] + 1) ** num_slots

    # start timer
    t0 = time.time()
    count = 0
    input_it = itertools.product(range(args.drange[0], args.drange[1] + 1), repeat=num_slots)
    inputs = []

    print('Preparing input')
    # note: too large of chunksize deadlocks the pool for unknown reasons
    chunksize = max(1, int((num_iterations - args.start)/cpu_count() / 100))
    configs = itertools.islice(input_it, args.start, args.start + num_iterations)
    cfg_processor = ConfigurationValidator(cfg, fstr)

    with mp.Pool() as proc_pool:
        for out in tqdm(proc_pool.imap_unordered(cfg_processor.process_config, configs, chunksize), total=num_iterations - args.start):
            if out is not None:
                inputs.append(out)

    # create new pool
    if args.procs > 0:
        pool = mp.Pool(args.procs, initializer=fvr.initializer)
    else:
        pool = mp.Pool(initializer=fvr.initializer)

    print('Calculating f-vectors')
    # todo: experiment with different chunk sizes
    results = fvr.multi_run(pool, inputs, print_output=False, chunks=1)
    dt = time.time() - t0
    pool.close()

    # print the output/write to file
    if args.output is None:
        util.print_results(results, dt=dt, tex=args.latex)
    else:
        util.print_results(results, filename=args.output, dt=dt, tex=args.latex)
