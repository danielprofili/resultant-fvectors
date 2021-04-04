#!/bin/python
from math import log
# from datetime import timedelta
import datetime
import re
import traceback
import sys
from ast import literal_eval

NUM_TEX_COLS = 4

def parse_configuration(fstr):
    cfg = []
    fstr = fstr.replace(' ', '')
    # for m in [m for m in re.finditer('\(\(.*?\)\)', fstr)]:
    for m in re.finditer('\(\(.*?\)\)', fstr):
        cfg.append(len(re.findall('\(.*?\)', m.group(0))))

    return cfg

# Returns true if vec is concave (i.e. f_i*2 >= f_{i-1} + f_{i+1})
def is_concave(vec):
    # if not all(isinstance(el, int) for el in vec):
    if isinstance(vec, str):
        return False

    for i in range(1, len(vec) - 1):
        if vec[i] * 2 < vec[i-1] + vec[i + 1]:
            return False

    return True

def is_log_concave(vec):
    if not all(isinstance(v, int) for v in vec):
        return False
    result = is_concave([log(v) for v in vec])
    if not result:
        print('!!!!!!!')
        input('press to continue')

    return result
    # return is_concave([log(v) for v in vec])

# check if cfg is a valid point configuration
def check_valid(exps, cfg):
    # first: check for repeated points
    for i in range(len(exps)):
        if len(set(exps[i])) < cfg[i]:
            return False

        if len(exps[i]) == 3:
            # check for collinear points (removes all 3d cases I think?)
            p0, p1, p2 = exps[i]
            x1, y1 = p1[0] - p0[0], p1[1] - p0[1]
            x2, y2 = p2[0] - p0[0], p2[1] - p0[0]
            # integers so don't worry about tolerance
            if abs(x1 * y2 - x2 * y1) == 0:
                return False

    # check for parallel edges
    val = False




    return not val

# prints results of a computation
#    - unique (bool): whether to compute and print the set of unique
#     vectors
#    - filename (str): path of file to write (or none if no file output)
#    - dt: elapsed time
#    - tex: (bool) whether or not to format unique f-vectors as TeX table
def print_results(results, app=None, unique=True, filename=None, dt=None, tex=False):
    try:
        if unique:
            # find unique f-vectors and sort by f0 (first entry - number of vertices)
            unique_f_vecs = get_unique_fvecs(results) 

        if filename is None:
            print('Configurations:')
            for vec, out in results:
                print(vec)
                print(out)
                print('')

            if unique:
                print('Unique f-vectors:')
                for fv in unique_f_vecs:
                    if fv != 'invalid':
                        print(fv)
                        print('concave: %s' % str(is_concave(fv)))
                        print('log concave: %s\n' % str(is_log_concave(fv)))

            if dt is not None:
                print('Time: %s for %d results' % (str(datetime.timedelta(seconds=int(dt))), len(results)))
                print('Average time: %f s per item' % (dt / len(results)))
        else:
            with open(filename, 'w') as f:
                f.write('Configurations:\n')
                for vec, out in results:
                    f.write('%s\n' % str(vec))
                    f.write('%s\n\n' % str(out))

                if unique:
                    f.write('Unique f-vectors:\n')
                    for fv in unique_f_vecs:
                        if fv != 'invalid':
                            f.write('%s\n' % str(fv))
                            f.write('concave: %s\n' % str(is_concave(fv)))
                            f.write('log concave: %s\n\n' % str(is_log_concave(fv)))

                    if tex:
                        f.write(tex_table(unique_f_vecs))

                if dt is not None:
                    f.write('Time: %s for %d results\n' % (str(datetime.timedelta(seconds=int(dt))), len(results)))
                    f.write('Average time: %f s per item\n' % (dt / len(results)))
    except Exception as e:
        if not dump:
            # print('Caught exception %s, dumping to file' % str(e))
            print(traceback.format_exc())
        else:
            # print('Caught exception ' + e)
            print(traceback.format_exc())
                    
    finally:
        # always dump - that way f-vector sets can be more easily merged after
        if app is None:
            dump_fname = filename if filename is not None else str(datetime.datetime.now()).replace(' ', '_')
        else:
            dump_fname = app
        with open('%s.out' % dump_fname, 'a') as f:
            for r in results:
                f.write('%s\n' % str(r))

# Get set of unique f vectors and sort by f_0
def get_unique_fvecs(results):
    return sorted(list(set([r[1] for r in results])), key=lambda x: x[0] if (len(x) > 0 and all(isinstance(x[0], int) for e in x)) else 0, reverse=False)

def tex_table(unique_f_vecs):
    to_write = ''
    to_write += ('\\begin{table}[h]\\centering\n\\begin{tabular}{|%s|}\n\n' % (' '.join(['c'] * NUM_TEX_COLS)))
    count = 0
    for fv in unique_f_vecs:
        # fv = unique_f_vecs[i]
        if fv != 'invalid':
            entry = str(fv)
            if not is_concave(fv):
                entry += '^{*}'
            if not is_log_concave(fv):
                entry += '^{\dagger}'

            to_write += ('$%s$' % entry)
            if count % 4 == 3:
                # newline in the table
                to_write += (' \\\\ \n')
            elif count < len(unique_f_vecs) - 1:
                to_write += (' & ') # separator

            count += 1

    # end table
    to_write += ('\n\\end{tabular}\n\\end{table}\n\n')

    return to_write
    

# Utility to merge raw output files
if __name__ == '__main__':
    # merge dump files from commandline
    # usage: ./fvec_util.py <input 1> <input 2> ...
    results = []
    for i in range(1, len(sys.argv)):
        with open(sys.argv[i], 'r') as f:
            results.extend([list(literal_eval(line)) for line in f])

    unq = get_unique_fvecs(results)
    print(tex_table(unq))
