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

1) Because of our decision to use multiprogramming to simulate our model clocks through subprocesses, this program cannot be run across different machines. We chose to simulate through a single machine.
    -  More specifically, the queue module implements multi-producer, multi-consumer queues. The Queue class in this module implements all the required locking semantics, and the multiprocessing queues are sent between processes by serializing its objects through pipes. The choice simplifies programming while still accurately reflecting the results of our model clock system.
2) A limitation of the `Queue` class is that, on some Unix machines (including our own), the `.qsize()` method that returns the size of the queue is not able to be implemented. This doesn't effect the results of the experiment in any meaningful way, it jus tmeans we can't precisely view the sizes of the queues.

# Engineering Notebook

First, we'll discuss an analysis of our testing results. In the `logs` folder, there are several iterations of test logs. They are named according to the experiment number and machine number. **Experiments 1-5** are set according to the initial specs, with each scenario running for at least 90 seconds. **Experiment 6** varies the upper limit of a potential clock cycle to 20 seconds, creating a much wider variety in system clock rates. **Experiment 7** changes the likelihood of an internal event happening to just 25%, as the range of potential outcomes upon taking a message from the queue is now 1-4 (with only 4 being an internal event).

## Findings
In the first five experiments, we noticed a few common patterns:
- **Logging**: Obviously, the frequency of events in the logs vary by clock times, as the slowest model clock has fewest events, the fastest has the most events.
- **Local Clock**: Similarly as expected, the slowest clock exhibits large jumps in its local clock time as a result of frequent events by the fastest clock. The fastest clock sees an increment of 1 for each event in its log, whereas slower clocks see significant jumps. 
- **Message Queues**: The messages queues of the slower clocks can grow very quickly, leaving the slower clocks to more often be recieving messages than taking the chance of sending messages or having internal events. This can be most clearly seen when we increment the range of different clock speeds in experiment 6. In that case, the slowest clock is slowest by a lot, and it is therefore always receiving messages. Also, when the likelihood of an internal event is low (experiment 7) this further exacerbates the problem because faster clocks are always sending messages. As a result, slower clocks cannot keep up and they are always recieving messages with growing queue sizes. This is true even with smaller variations of clock times. For example, in *Experiment 7*, Machine 1 has a clock speed of 3, while Machines 0 and 2 have clock speeds of 1. However, Machine 1 can never keep up (as evident by its log).
- **Noticeable Behaviors**: It appears through our experimentation that if two machines have the same clock speed, then the luck of one can put it in control for longer periods of time. For example, in experiment 7, where we decrease the likelihood of internal events, if one clock does not send a message due to chance, then the other clock with the same speed will be recieving that round, making it more likely that the other clock will keep sending messages. Thus, momentum carries weight, especially when it is less likely for an internal event to occur. 


## Engineering Decisions
1) The first major decision we made was to use the `multiprogramming` library. We chose to use this to simplify communication between our programs through the `Queue` class. This allows us to observe the accurate results of the experiments without handling socket logic. We also considered reusing aspects of our `grpc` chat bot for a simplified communication channel, but this would require having an app state system in place rather than direct communication between the processes. In the end, `multiprogramming` seemed to be the simplest solution for our goals of observing results of different model clocks. 
2) Unfortunately, this decision led to some unforeseen complications in other changes we'd like to make, like gracefully exiting the program or being able to view the queue size on our development systems. However, these were not breaking to the overall project specifications. 
3) To execute the model clock logic, we decided to have each virtual machine run through it's work on a single step, contained in the `.step()` function of the `VirtualMachine` class. Each `VirtualMachine` process has a set clock. The `run()` function of the `VirtualMachine` just contains calls for it to `step()`, i.e. run the logic of the system, and then `sleep()` for its pre-defined clock time. We considered doing this in other ways (having this all be in one function, or having the `VirtualMachine` be it's own program entirely), but this implementation seemed cleanest and most logical to us. 


