# Overview
This folder contains our logical clock model code.

# Installation
To set up your environment to run our code:
1) Run `pip install -r requirements.txt` from this folder. 
2) Adjust any configuration values you'd like to in `config.py`. `MAX_CLOCK_RANGE` defines the random interval of clock rates chosen by a process. The default is a choice between 1 and 6. But changing this value to 10 would change that interval to random between 1 and 10. Similarly, `MAX_PROBABILITY` is the range for interval events. The default is 10 by the specs, but decreasing this to 6 would decrease the probability of an internal event happening from 7/10 to 1/2. This cannot be less than 3. 
2) Run `python3 main.py` from this folder.

# Usage

This model clock experiment can be run simply by calling `python3 main.py` from this folder. The resulting outputs will be automatically written to the files `machine0.txt`, `machine1.txt`, and `machine2.txt`. 

# Structure

The structure of our system is pretty simple:
- `main.py` contains the core module, which runs three virtual machines according to the assignment specifications. Each virtual machine "model clock" writes to its own log files. All log files are contained in the `logs` directory. 
- The primary data structure that we use for our system is the Queue libary, which allows to multiple processes to share a single queue through locking. 
- Our system is run through a simulated through a single main program, which creates three sub processes using the `multiprogramming` library. 

# Testing

For details on our experiments, please see the `Engineering Notebook` section below.

- TODO add testing instructions

# Limitations

1) Because of our decision to use multiprogramming to simulate our model clocks through subprocesses, this program cannot be run across different machines. 
2) A limitation of the `Queue` class is that, on some Unix machines (including our own), the `.qsize()` method that returns the size of the queue is not able to be implemented. This doesn't effect the results of the experiment in any meaningful way, it jus tmeans we can't precisely view the sizes of the queues.

# Engineering Notebook


