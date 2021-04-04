import subprocess
import multiprocessing as mp
import signal
from time import sleep
from tqdm import tqdm

# pause_event = mp.Event()

def initializer():
    # ignore SIGINT so that the main process can kill pool workers
    signal.signal(signal.SIGINT, signal.SIG_IGN)

# Runs a single gfan process with inp_str via stdin
def run(inp_str):
    # inp_str, flag = inp
    # pause_event.wait()
    p1 = subprocess.Popen(('echo', inp_str), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(('gfan_resultantfan', '--projection', '--vectorinput'), stdin=p1.stdout, stdout=subprocess.PIPE)
    try:
        out, err = p2.communicate()
        out = out.decode().split('F_VECTOR\n')[1].split('\n')[0]

        # resultant f-vector is reversed
        out = out.split(' ')
        out.reverse()
        out = tuple([int(o) for o in out][:-1])
        # if flag:
        #     print('%s\n%s\n' % (inp_str, out))
    except IndexError:
        print('%s not a hypersurface' % inp_str)
        out = 'invalid'

    return (inp_str, out)

def multi_run(pool, inputs, chunks=1):
    # parallelize
    # inputs = [(i, print_output) for i in inputs]
    results = []
    # pause_event = mp.Event()
    try:
        for result in tqdm(pool.imap_unordered(run, inputs, chunks), total=len(inputs)):
            # print('sleeping')
            # sleep(1)
            # pause_event.set()
            results.append(result)
    except KeyboardInterrupt:
        print('C-c received, cancelling...')
        pool.terminate()
        pool.join()

    print('done with %d inputs' % len(results))
    return results
