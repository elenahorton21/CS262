from multiprocessing import Process, Queue
import random
import time

# General idea, threading library creates "processes" that are each running our logical clock module

# the queue is shared by all the processes, includes messages for each thread

class VirtualMachine(Process):
    def __init__(self, id, queues, **kwargs):
        """
        id (int): The id of the machine (1, 2, or 3).
        queues ()
        """
        super().__init__(**kwargs)
        self.id = id
        self.queues = queues
        self.clock_speed = 60 / random.randint(1, 6)
        print("Process " + str(self.id) + " has a clock time of " + str(self.clock_speed))

    def add_to_queue(self, queueID, message):
        self.queues[queueID].put(message)
    
    def get_from_queue(self):
        my_queue = self.queues[self.id]
        if not my_queue.empty():
            return my_queue.get()
        else:
            return "Nothing in queue"


    def run(self):  

    # add all the logic here for handling what to do on each clock tick             
        print("Starting " + str(self.id))

    # On each clock cycle, if there is a message in the message queue for the machine
    #  (remember, the queue is not running at the same cycle speed) the virtual machine 
    # should take one message off the queue, update the local logical clock, and write in the log that it received a message,
    # the global time (gotten from the system), the length of the message queue, and the logical clock time.

    # to do: create a global clock and local clock to update on each cycle
    # add message sending logic (based on random integers)

        time.sleep(self.clock_speed)
        msg = self.get_from_queue()
        print(msg)


if __name__ == '__main__':
    first_q = Queue()
    second_q = Queue()
    third_q = Queue()
    queues = [first_q, second_q, third_q]


    # Create three "model clock" processes, note their ID in the queues list
    p1 = VirtualMachine(0, queues)
    p2 = VirtualMachine(1, queues)
    p3 = VirtualMachine(2, queues)

    p1.start()
    p1.join()
    p2.start()
    p2.join()
    p3.start()
    p3.join()
    
    # testing functionality of the queues across processes --> working!
    p1.add_to_queue(2, "hi!")
    p2.add_to_queue(1, "what's up? ")
    p3.add_to_queue(0, "hello from p3!")

    # for i in range(0, len(queues)):
    #     q = queues[i]
    #     if not q.empty():
    #         msg = q.get()
    #         print(str(i) + ": " + msg)