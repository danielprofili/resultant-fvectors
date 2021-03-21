import subprocess
import multiprocessing as mp
import signal
from tqdm import tqdm

def initializer():
    # ignore SIGINT so that the main process can kill pool workers
    signal.signal(signal.SIGINT, signal.SIG_IGN)

# pbar = tqdm(delay=10)
# results = []
# class GfanRunner():
# Runs a single gfan process with inp_str via stdin
def run(inp):
    inp_str, q, flag = inp
    # inp_str, flag = inp
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

    # q.put((inp_str, out))
    # q.task_done()
    # results.append((inp_str, out))
    # print(results)
    # update progress bar
    # pbar.update(1)
    return (inp_str, out)

def multi_run(pool, inputs, print_output=False, chunks=100):
    # parallelize
    # inputs = [(i, fmt) for i in inputs]
    # print(inputs)
    # input()
    # results = self.pool.map(self.__run_wrapper__, inputs)
    q = mp.Manager().Queue()
    inputs = [(i, q, print_output) for i in inputs]
    # pbar.total = len(inputs)
    # inputs = [(i, print_output) for i in inputs]
    # results = pool.map_async(self.run, inputs, chunks)
    results = []
    try:
        # results = pool.map_async(self.run, inputs, chunks)
        # results = pool.map(run, inputs, chunks)
        for result in tqdm(pool.imap_unordered(run, inputs, chunks), total=len(inputs)):
            results.append(result)

    except KeyboardInterrupt:
        print('C-c received, cancelling...')
        # pool.close()
        pool.terminate()
        pool.join()

    # probably not great
    # while not results.ready():
    #     pass

    # print('done with %d inputs' % q.qsize())
    print('done with %d inputs' % len(results))
    # ensure all processes have exited properly
    # q.join()

    # process the queue into a nicer format
    # q_data = []

    # class Drainer(object):
    #     def __init__(self, q):
    #         self.q = q
    #     def __iter__(self):
    #         while True:
    #             try:
    #                 yield self.q.get_nowait()
    #             except Exception:
    #                 break

    # for result in Drainer(q):
    #     q_data.append(result)

    # return q_data
    # return results.get()
    return results
