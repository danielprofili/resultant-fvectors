#!/usr/bin/python3
import argparse
import gfan_runner as gfr
import time
import itertools
import multiprocessing as mp
import re
from datetime import timedelta
from os import cpu_count
from tqdm import tqdm
from operator import add
from ast import literal_eval

# START_INDEX = 49287
START_INDEX = 0

class ConfigurationValidator():
    def __init__(self, fstr):
        self.fstr = fstr

    def process_config(self, exps_str):
        exps = list(literal_eval(self.fstr.replace('{', '').replace('}', '') % exps_str)) # hack, but should work assuming nice input
        flag = False

        # try check for degenerate cases
        for i in range(len(exps)):
            # first: check for repeated points
            if len(set(exps[i])) < cfg[i]:
                flag = True
                break

            # check for collinear points (removes all 3d cases I think?)
            p0, p1, p2 = exps[i]
            x1, y1 = p1[0] - p0[0], p1[1] - p0[1]
            x2, y2 = p2[0] - p0[0], p2[1] - p0[0]
            # integers so don't worry about tolerance
            if abs(x1 * y2 - x2 * y1) == 0:
                flag = True
                break

            # todo: check for parallel edges between triangles???
        if flag:
            return None

        return self.fstr % exps_str

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Enumerate systems of polynomials and calculate the resultant f-vector')
    parser.add_argument('-r', '--drange', help='Degree range, inclusive', nargs=2, type=int, default=[0, 5])
    parser.add_argument('-f', '--fstr', help='Configuration of system as a (properly formatted) format string', default='{((0,0),(0,1),(1,0)),((0,0),(%d,%d),(%d,%d)),((0,0),(%d,%d),(%d,%d))}')
    parser.add_argument('-p', '--procs', help='Max number of concurrent processes', type=int, default=-1)
    parser.add_argument('-c', '--count', help='Max number of iterations', type=int, default=-1)
    parser.add_argument('-o', '--output', help='Name of output file', type=str, default=None)
    parser.add_argument('-s', '--start', help='Starting offset for the iterator', type=int, default=START_INDEX)

    args = parser.parse_args()

    # calculate the configuration i.e. [3,3,3] for the default
    cfg = []
    fstr = args.fstr.replace(' ', '')
    for m in [m for m in re.finditer('\(\(.*?\)\)', fstr)]:
        cfg.append(len(re.findall('\(.*?\)', m.group(0))))

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
    chunksize = int((num_iterations - args.start)/cpu_count() / 100)
    configs = itertools.islice(input_it, args.start, args.start + num_iterations)
    cfg_processor = ConfigurationValidator(fstr)

    with mp.Pool() as proc_pool:
        for out in tqdm(proc_pool.imap_unordered(cfg_processor.process_config, configs, chunksize), total=num_iterations - args.start):
            if out is not None:
                inputs.append(out)

    # create new pool
    if args.procs > 0:
        pool = mp.Pool(args.procs, initializer=gfr.initializer)
    else:
        pool = mp.Pool(initializer=gfr.initializer)

    print('Calculating f-vectors')
    results = gfr.multi_run(pool, inputs, print_output=False, chunks=1)
    dt = time.time() - t0

    # find unique f-vectors and sort by f0 (first entry - number of vertices)
    unique_f_vecs = sorted(list(set([r[1] for r in results])), key=lambda x: x[0], reverse=False)

    # print the output/write to file
    if args.output is None:
        for vec, out in results:
            print(vec)
            print(out)
            print('')

        print('Unique f-vectors: ')
        for fv in unique_f_vecs:
            print(fv)
    else:
        with open(args.output, 'w') as f:
            f.write('Configurations\n')
            for vec, out in results:
                f.write('%s\n' % str(vec))
                f.write('%s\n\n' % str(out))

            f.write('Unique f-vectors\n')
            for fv in unique_f_vecs:
                f.write('%s\n' % str(fv))

    print('Time: %s for %d results' % (str(timedelta(seconds=int(dt))), len(results)))
    print('Average time: %f s per item' % (dt / len(results)))
