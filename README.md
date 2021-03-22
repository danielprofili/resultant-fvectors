# resultant-fvectors

Useful scripts to compute huge numbers of f-vectors of resultant polytopes as efficiently as possible, either by uniformly sampling exponent vectors or enumerating all possible exponents in a certain range.

## Requirements

Python 3.9.2, `tqdm`

## Usage

The main entry points are `fvec_random.py` and `fvec_enumerate.py`; their commandline args are described in the source code and by using `--help`.

## Background
See https://danielprofili.github.io/research.html for some background theory.

## Credits

The tropical resultant computations are done using [Gfan](https://users-math.au.dk/jensen/software/gfan/gfan.html) by Anders Jensen
