"""
TODO: Is using sleep to mimic the clock cycles okay?
TODO: Maybe add a better way to stop program.
"""
from multiprocessing import Process, Queue
import random
import time
from datetime import datetime


config = {
    "MAX_CLOCK_RANGE": 6,
    "MAX_PROBABILITY": 4,
    "INCLUDE_QUEUE_SIZE": False,
}


class VirtualMachine(Process):
    """
    Simulates a virtual machine with a random clock rate. Each instance
    is a process, and `multiprocessing.Queue` is used to communicate between 
    virtual machines. The clock rate is simulated by modifying the process's 
    `run()` method to sleep for some amount of time between calls to `step()`,
    which represents the work done in one clock cycle.
    """
    def __init__(self, id, queues, **kwargs):
        """
        id (int): The id of the machine (1, 2, or 3).
        queues (List[multiprocessing.Queue]): A queue for each VirtualMachine.
        """
        super().__init__(**kwargs)
        self.id = id
        self.queues = queues
        self.clock_rate = random.randint(1, config["MAX_CLOCK_RANGE"]) # The number of clock ticks per minute
        self.lclock = 0 # Initial value of logical clock 
        self.lclock_increment = 1 # Logical clock increment
        self.log_file_path = f"logs/machine{id}.txt" # Logging file
        
        # Specify the IDs of the other machines and their order
        self.other_ids = [0, 1, 2]
        self.other_ids.remove(id)

        print("Process " + str(self.id) + " has a clock rate of " + str(self.clock_rate))   
        self.write_to_log("Process " + str(self.id) + " has a clock rate of " + str(self.clock_rate) + '\n\n') 

    @property
    def empty_queue(self):
        """Returns True if the machine's message queue is empty."""
        return self.queues[self.id].empty()
    
    @property
    def system_time(self):
        """The current system time in string format."""
        now = datetime.now()
        return now.strftime("%H:%M:%S")
    
    def send_message(self, machine_id, message):
        """
        Send a message to the specified machine by putting a message in its queue.
        
        Args:
            machine_id (int): The ID of the machine to send a message to.
            message (str): The message content.

        Returns:
            None
        """
        self.queues[machine_id].put(message)
    
    def pop_message(self):
        """
        Get the first message in the queue.
        
        Args:
            None

        Returns:
            str: The content of the first message in the queue.

        Raises:
            queue.Empty: If no item is available in the queue.
        """
        my_queue = self.queues[self.id]
        return my_queue.get()

    def update_lclock(self, recv_clock=None):
        """
        Update the machine's logical clock. If a message was received, the local clock is set to the 
        max of the received clock value and the local clock value, plus the logical clock increment. 
        Otherwise, increment by the standard increment (1).

        Args:
            Optional[int]: An optional argument for a logical clock time from another machine.
        
        Returns:
            None
        """
        if recv_clock:
            self.lclock = max(self.lclock, recv_clock)
            
        self.lclock += self.lclock_increment

    def write_to_log(self, message):
        """
        Write the message to the machine's log.
        
        Args:
            message (str): The content to write.
        
        Returns:
            None
        """
        with open(self.log_file_path, "a") as f:
            f.write(message)

    def step(self):
        """
        Defines the operations performed in one clock cycle. If the machine has 
        queued messages, consume the first message in the queue, update the local logical
        clock, and log the event. Otherwise, generate a random number and either send a message,
        or simulate an internal event.
        """
        # If there are no message in the queue, use random number to determine action
        if self.empty_queue:
            action = random.randint(1, config["MAX_PROBABILITY"])
            # If the random number is 1 or 2, send a message to the corresponding machine
            if action in [1, 2]:
                recp_id = self.other_ids[action-1]
                message = str(self.lclock)
                self.send_message(recp_id, message)
                # Update logical clock after sending message
                self.update_lclock()
                # Log 
                self.write_to_log(f"Sent message:'{message}'\t System time: {self.system_time}\t Logical clock time: {self.lclock}\n")
            # If the random number is 3, send a message to both other machines
            elif action == 3:
                for id in self.other_ids:
                    message = str(self.lclock)
                    self.send_message(id, message)
                self.update_lclock()
                self.write_to_log(f"Sent message:'{message}'\t System time: {self.system_time}\t Logical clock time: {self.lclock}\n")
            # Otherwise, simulate an internal event
            else:
                self.update_lclock()
                self.write_to_log(f"Internal event\t System time: {self.system_time}\t Logical clock time: {self.lclock}\n")
        # If there are messages in the queue, consume the first message
        else:
            msg = self.pop_message()
            self.update_lclock(int(msg))
            # With `multiprocessing.Queue`, we cannot call `qsize()` on certain machines, e.g. MacOS.
            base_log_msg = f"Received message\t System time: {self.system_time}\t Logical clock time: {self.lclock}"
            if config["INCLUDE_QUEUE_SIZE"]:
                queue_size = self.queues[self.id].qsize()
                base_log_msg += f"\t Queue size: {queue_size}"
            self.write_to_log(base_log_msg + "\n")     

    def run(self):
        """
        Run loop that simulates a virtual machine running `step()` every clock tick. This is called with `VirtualMachine.start()`,
        and `time.sleep` is used to control the amount of time between clock ticks, which should be 60s/`self.clock_rate`.
        """
        while True:
            self.step()
            time.sleep(60/self.clock_rate)


def clear_logs():
    """Clear all the log files."""
    for i in range(3):
        open(f'logs/machine{i}.txt', 'w').close()


def main():
     # Clear logs before running
    clear_logs()

    # Initialize queues
    first_q = Queue()
    second_q = Queue()
    third_q = Queue()
    queues = [first_q, second_q, third_q]

    # Create three "model clock" processes, note their IDs in the queues list
    p1 = VirtualMachine(0, queues)
    p2 = VirtualMachine(1, queues)
    p3 = VirtualMachine(2, queues)

    # Start all virtual machine processes
    p1.start()
    p2.start()
    p3.start()

    # Will run indefinitely until the user exits the program.`join()` ensures that the child processes are killed when the parent 
    # process ends.
    p1.join()
    p2.join()
    p3.join()


if __name__ == '__main__':
    main()

