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
- TODO: add details on our code structure

# Testing

TODO add testing instructions

# Limitations

TODO: Add details on multiprocessing and configurations

# Engineering Notebook

TODO: Add findings from experiments
