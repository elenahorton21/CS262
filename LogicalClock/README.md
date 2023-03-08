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
- The primary data structure that we use for our system is the `Queue` libary, which allows to multiple processes to share a single queue through locking. 
- Our system is run through a simulated through a single main program, which creates three sub processes using the `multiprogramming` library. 

# Testing

For details on our experiments, please see the `Engineering Notebook` section below.

- TODO add testing instructions

# Limitations

1) Because of our decision to use multiprogramming to simulate our model clocks through subprocesses, this program cannot be run across different machines. 
2) A limitation of the `Queue` class is that, on some Unix machines (including our own), the `.qsize()` method that returns the size of the queue is not able to be implemented. This doesn't effect the results of the experiment in any meaningful way, it jus tmeans we can't precisely view the sizes of the queues.

# Engineering Notebook

First, we'll discuss an analysis of our testing results. In the `logs` folder, there are several iterations of test logs. They are named according to the experiment number and machine number. **Experiments 1-5** are set according to the initial specs, with each scenario running for at least 90 seconds. **Experiment 6** varies the upper limit of a potential clock cycle to 20 seconds, creating a much wider variety in system clock rates. **Experiment 7** changes the likelihood of an internal event happening to just 25%, as the range of potential outcomes upon taking a message from the queue is now 1-4 (with only 4 being an internal event).

## Findings
In the first five experiments, we noticed a few common patterns:
- **Logging**: Obviously, the frequency of events in the logs vary by clock times, as the slowest model clock has fewest events, the fastest has the most events.
- **Local Clock**: Similarly as expected, the slowest clock exhibits large jumps in its local clock time as a result of frequent events by the fastest clock. The fastest clock sees an increment of 1 for each event in its log, whereas slower clocks see significant jumps. 
- **Message Queues**: The messages queues of the slower clocks can grow very quickly, leaving the slower clocks to more often be recieving messages than taking the chance of sending messages or having internal events. This can be most clearly seen when we increment the range of different clock speeds in experiment 6. In that case, the slowest clock is slowest by a lot, and it is therefore always receiving messages. Also, when the likelihood of an internal event is low (experiment 7) this further exacerbates the problem because faster clocks are always sending messages. As a result, slower clocks cannot keep up and they are always recieving messages with growing queue sizes. This is true even with smaller variations of clock times. For example, in *Experiment 7*, Machine 1 has a clock speed of 3, while Machines 0 and 2 have clock speeds of 1. However, Machine 1 can never keep up (as evident by its log).



