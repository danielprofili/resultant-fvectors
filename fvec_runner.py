import subprocess
import multiprocessing as mp
import signal
from tqdm import tqdm

def initializer():
    # ignore SIGINT so that the main process can kill pool workers
    signal.signal(signal.SIGINT, signal.SIG_IGN)

# Runs a single gfan process with inp_str via stdin
def run(inp):
    inp_str, flag = inp
    p1 = subprocess.Popen(('echo', inp_str), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(('gfan_resultantfan', '--projection', '--vectorinput'), stdin=p1.stdout, stdout=subprocess.PIPE)
    try:
        out, err = p2.communicate()
        out = out.decode().split('F_VECTOR\n')[1].split('\n')[0]

        # resultant f-vector is reversed
        out = out.split(' ')
        out.reverse()
        out = tuple([int(o) for o in out][:-1])
        if flag:
            print('%s\n%s\n' % (inp_str, out))
    except IndexError:
        print('%s not a hypersurface' % inp_str)
        out = [0, 0]

    return (inp_str, out)

def multi_run(pool, inputs, print_output=False, chunks=100):
    # parallelize
    inputs = [(i, q, print_output) for i in inputs]
    results = []
    try:
        for result in tqdm(pool.imap_unordered(run, inputs, chunks), total=len(inputs)):
            results.append(result)

    except KeyboardInterrupt:
        print('C-c received, cancelling...')
        pool.terminate()
        pool.join()


    print('done with %d inputs' % len(results))
    return results
