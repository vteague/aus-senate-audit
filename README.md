# Overview

The ``aus-senate-audit`` is a command-line tool for auditing the reported outcome of the Australian Senate Election. The  intention of this tool is two-fold. First, it provides a platform for researchers to run simulated audits on electronic  representations of paper ballots from the Australian Senate Election. Second, it provides a platform for election officials  to use when auditing the paper ballots of the Australian Senate Election.

``aus-senate-audit`` uses the Bayesian audit, a post-election, ballot-polling audit developed by [Rivest and Shen (2012)](https://www.usenix.org/system/files/conference/evtwote12/rivest_bayes_rev_073112.pdf). This software, however, can be extended to support any post-election, ballot-polling audit.

# Getting Started

You can download the ``aus-senate-audit`` command-line tool with the following command.

```
$ pip3 install aus-senate-audit
```

You can upgrade your installment of the ``aus-senate-audit`` package to the latest version with the following command.

```
$ pip3 install --upgrade aus-senate-audit
```

Once you have installed the package, you can see its usage with the following command.

```
$ aus-senate-audit --help
 usage: aus-senate-audit [-h] [-s SEED] [--num-ballots NUM_BALLOTS]
                        [--num-candidates NUM_CANDIDATES]
                        [--state {ACT,NSW,NT,QLD,SA,TAS,VIC,WA}]
                        [--selected-ballots SELECTED_BALLOTS] [--data DATA]
                        [--max-ballots MAX_BALLOTS]
                        [-f UNPOPULAR_FREQUENCY_THRESHOLD]
                        [--sample-increment-size SAMPLE_INCREMENT_SIZE]
                        MODE

positional arguments:
  MODE                  The mode in which to run the audit.

optional arguments:
  -h, --help            show this help message and exit
  -s SEED, --seed SEED  The starting value of the random number generator.
  --num-ballots NUM_BALLOTS
                        The number of ballots cast for a simulated senate
                        election.
  --num-candidates NUM_CANDIDATES
                        The number of candidates for a simulated senate
                        election.
  --state {ACT,NSW,NT,QLD,SA,TAS,VIC,WA}
                        The abbreviation of the state name to run the senate
                        election audit for.
  --selected-ballots SELECTED_BALLOTS
                        The path to the CSV file containing the selected
                        ballots data.
  --data DATA           The path to all Australian senate election data.
  --max-ballots MAX_BALLOTS
                        The maximum number of ballots to check for a real
                        senate election audit.
  -f UNPOPULAR_FREQUENCY_THRESHOLD, --unpopular-frequency-threshold UNPOPULAR_FREQUENCY_THRESHOLD
                        The minimum frequency of trials in a single audit
                        stage a candidate must be elected in order for the
                        candidate to be deemed unpopular (only applied on the
                        last audit stage).
  --sample-increment-size SAMPLE_INCREMENT_SIZE
                        The number of ballots to add to the growing sample
                        during this audit stage.
```

This package is distributed by the Python Package Index (PyPI) [here](https://pypi.python.org/pypi/aus-senate-audit).

# Running an Audit

The ``aus-senate-audit`` can be run in three different modes.

## Simulation Mode

Simulation mode runs a simulated audit on fake Australian Senate Election data using Borda Count as the social choice function. This differs from the social choice function used by the actual Australian Senate Election, [single transferable vote (STV)](https://en.wikipedia.org/wiki/Single_transferable_vote).

Simulation mode is indicated by the first (and only) positional argument set as ``simulation``, as shown below.

```
aus-senate-audit simulation --seed SEED --num-candidates NUM_CANDIDATES --num-ballots NUM_BALLOTS
```

The ``SEED`` option specifies the starting value of the random number generator (RNG) used by the audit to generate all randomness (defaults to 1). The ``NUM_CANDIDATES`` option is the number of candidates in the simulated election (defaults to 100). The ``NUM_BALLOTS`` option is the number of cast ballots in the simulated election (defaults to 1000000).

## Quick Mode

Quick mode runs a Bayesian audit on real Australian Senate Election data using STV as the social choice function. This mode simulates a "real" Australian Senate Election audit by inspecting electronic representations of paper ballots.

Quick mode is indicated by the first positional argument set as ``quick``, as shown below.

```
aus-senate-audit quick --seed SEED --state STATE --data DATA
```

As before, the ``SEED`` option specifies the starting value of the RNG used by the audit to generate all randomness (defaults to 1). The ``STATE`` option is the abbreviated name of the Australian state to run the audit for (e.g. ``TAS``). The ``DATA`` option is the file path to all Australian Senate Election data (see [Getting Australian Senate Election Data](#getting-australian-senate-election-data) for details).

## Real Mode

Real mode runs a Bayesian audit on real Australian Senate Election data using STV as the social choice function. Unlike quick mode, however, real mode requires user interaction. This interaction occurs in two repeating steps.

First, a user must provide the software with the Australian Senate Election data, as shown below. Note the first positional argument is set as ``real``.

```
aus-senate-audit real --seed SEED --state STATE --data DATA
```

As before, the ``SEED`` option specifies the starting value of the RNG used by the audit to generate all randomness (defaults to 1). The ``STATE`` option is the abbreviated name of the Australian state to run the audit for (e.g. ``TAS``). The ``DATA`` option is the file path to all Australian Senate Election data (see [Getting Australian Senate Election Data](#getting-australian-senate-election-data) for details).

This command generates a CSV file named ``selected_ballots.csv``. This file contains a random sample of ballots from the Australian Senate Election without the preferences marked on the ballot. The auditor must use the information in the file (i.e. location of the paper ballot) to retrieve the paper ballot and enter its preferences into the missing entry in the CSV file.

For example, suppose a line in the ``selected_ballots.csv`` file appears as

```
Denison,POSTAL 3,311,19,42,
```

The user would retrieve the paper ballot corresponding to the given information and add the preferences read from that paper ballot to the ``selected_ballots.csv``, as shown below.

```
Denison,POSTAL 3,311,19,42,",1,2,3,,6,,,,4,,,5,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
```

Once the user has filled in every row in the ``selected_ballots.csv``, they are ready for the second step, started with the command below.

```
aus-senate-audit real --seed SEED --state STATE --selected-ballots SELECTED_BALLOTS_FILE --data DATA
```

As before, the ``SEED`` option specifies the starting value of the RNG used by the audit to generate all randomness (defaults to 1). The ``STATE`` option is the abbreviated name of the Australian state to run the audit for (e.g. ``TAS``). The ``SELECTED_BALLOTS_FILE`` option is the path to the selected ballots file. The ``DATA`` option is the file path to all Australian Senate Election data (see [Getting Australian Senate Election Data](#getting-australian-senate-election-data) for details).

This command runs one stage of the Bayesian audit on the sample of paper ballots audited thus far.

The user continues these two steps in succession until the audit terminates with one of the two messages below.

```
Audit has looked at all ballots. Done.
```

```
Stopping because audit confirmed outcome:
   (28081, 28083, 28085, 28345, 28346, 28348, 28350, 28871, 28873, 28874, 28876, 28877)
 Total number of ballots examined: 6116
```

# Getting Australian Senate Election Data

The Australian Senate Election data can be retrieved by downloading the ``data.tar.gz`` file at the top-level of this repository.

This can be done in one of two ways:

(Directions to come soon...)
