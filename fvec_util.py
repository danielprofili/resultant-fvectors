from math import log
from datetime import timedelta

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
def print_results(results, unique=True, filename=None, dt=None):
    if unique:
        # find unique f-vectors and sort by f0 (first entry - number of vertices)
        unique_f_vecs = sorted(list(set([r[1] for r in results])), key=lambda x: x[0], reverse=False)

    if filename is None:
        print('Configurations:')
        for vec, out in results:
            print(vec)
            print(out)
            print('')

        if unique:
            print('Unique f-vectors:')
            for fv in unique_f_vecs:
                print(fv)
                print('concave: %s' % str(is_concave(fv)))
                print('log concave: %s\n' % str(is_log_concave(fv)))

        if dt is not None:
            print('Time: %s for %d results' % (str(timedelta(seconds=int(dt))), len(results)))
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
                    f.write('%s\n' % str(fv))
                    f.write('concave: %s\n' % str(is_concave(fv)))
                    f.write('log concave: %s\n\n' % str(is_log_concave(fv)))

            if dt is not None:
                f.write('Time: %s for %d results\n' % (str(timedelta(seconds=int(dt))), len(results)))
                f.write('Average time: %f s per item\n' % (dt / len(results)))
