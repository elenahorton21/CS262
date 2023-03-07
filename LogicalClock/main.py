"""
TODO: May want a better logging method.
TODO: Is using sleep to mimic the clock cycles okay?
TODO: Maybe add a better way to stop program.
"""
from multiprocessing import Process, Queue
import random
import time
from datetime import datetime
import logging

class VirtualMachine(Process):
    def __init__(self, id, queues, **kwargs):
        """
        id (int): The id of the machine (1, 2, or 3).
        queues (List[multiprocessing.Queue])
        """
        super().__init__(**kwargs)
        self.id = id
        self.queues = queues
        self.clock_rate = random.randint(1,6)
        self.lclock = 0 # Value of logical clock 
        self.lclock_increment = 1 # Logical clock increment
        self.log_file_path = f"logs/machine{id}.txt" # Logging file
        print("Process " + str(self.id) + " has a clock rate of " + str(self.clock_rate))   
        self.write_to_log("Process " + str(self.id) + " has a clock rate of " + str(self.clock_rate) + '\n\n') 

        # TODO: Using this to specify which machine to send a message for 1 and 2, respectively.
        self.other_ids = [0, 1, 2]
        self.other_ids.remove(id)

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
        """Send a message to the specified machine by putting a message in its queue."""
        self.queues[machine_id].put(message)
    
    def pop_message(self):
        """Get the first message in the queue."""
        my_queue = self.queues[self.id]
        return my_queue.get()


    def update_lclock(self, recv_clock=None):
        """
        Update the machine's logical clock. If a message was received, the local clock is set to the 
        max of the received clock value and the local clock value. Otherwise, increment
        by the standard increment (1).
        """
        if recv_clock:
            self.lclock = max(self.lclock, recv_clock)
        else:
            self.lclock += self.lclock_increment

    def write_to_log(self, message):
        """Write the message to the machine's log."""
        with open(self.log_file_path, "a") as f:
            f.write(message)

    def step(self):
        """
        Operations for one clock cycle.
        
        Instructions: On each clock cycle, if there is a message in the message queue for the machine
        (remember, the queue is not running at the same cycle speed) the virtual machine 
        should take one message off the queue, update the local logical clock, and write in the log that it received a message,
        the global time (gotten from the system), the length of the message queue, and the logical clock time.
        
        TODO: Refactor duplicate code.
        TODO: Logging the right information.
        TODO: Should we update the logical clock twice when the value is 3?
        """
        # If there are no message in the queue, use random number to
        # determine action.
        if self.empty_queue:
            action = random.randint(1, 10)
            if action == 1:
                recp_id = self.other_ids[0]
                message = str(self.lclock)
                self.send_message(recp_id, message)
                # Update logical clock after sending message
                self.update_lclock()
                # Log 
                self.write_to_log(f"Sent message:'{message}'\t System time: {self.system_time}\t Logical clock time: {self.lclock}\n")
            elif action == 2:
                recp_id = self.other_ids[1]
                message = str(self.lclock)
                self.send_message(recp_id, message)
                self.update_lclock()
                self.write_to_log(f"Sent message:'{message}'\t System time: {self.system_time}\t Logical clock time: {self.lclock}\n")
            elif action == 3:
                for id in self.other_ids:
                    message = str(self.lclock)
                    self.send_message(id, message)
                self.update_lclock()
                # Should we log once for each message?
                self.write_to_log(f"Sent message:'{message}'\t System time: {self.system_time}\t Logical clock time: {self.lclock}\n")
            else:
                # Treat as internal event
                self.update_lclock()
                self.write_to_log(f"Internal event\t System time: {self.system_time}\t Logical clock time: {self.lclock}\n")
        else:
            msg = self.pop_message()
            self.update_lclock(int(msg))
            self.write_to_log(f"Received message\t System time: {self.system_time}\t Logical clock time: {self.lclock}\n")     


    def run(self):
        """
        Run loop called by `Process.start()`.

        TODO: We could make this actually be 60 seconds by timing the 
        execution time for `self.step()`. This probably isn't necessary.
        """

        self.step()
        time.sleep(self.clock_rate)


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

    # Create three "model clock" processes, note their ID in the queues list
    p1 = VirtualMachine(0, queues)
    p2 = VirtualMachine(1, queues)
    p3 = VirtualMachine(2, queues)

    # start all model clock processes
    p1.start()
    p2.start()
    p3.start()

    # will run indefinitely until the user exits the program
   
    p1.join()
    p2.join()
    p3.join()


if __name__ == '__main__':
    main()

