import threading
import queue
import random

# General idea, threading library creates "processes" that are each running our logical clock module

# the queue is shared by all the processes, includes messages for each thread

class myThread (threading.Thread):
    def __init__(self, id, queues, my_queue, clock):
      threading.Thread.__init__(self)
      self.id = id
      self.queues = queues
      self.my_queue = my_queue
      self.clock = clock

    def add_to_queue(self, queueID, message):
        self.queues[queueID].put(message)


    def run(self):  

    # add all the logic here for handling what to do on each clock tick             
      print("Starting " + str(self.id))
      print("Exiting " + str(self.id))




def run():
    first_q = queue.Queue()
    second_q = queue.Queue()
    third_q = queue.Queue()
    queues = [first_q, second_q, third_q]
    clocktime = random.randint(1, 6)
    print(clocktime)

    # Create three "model clock" processes, note their ID in the queues list
    p1 = myThread(1, queues, 0)
    p2 = myThread(2, queues, 1)
    p3 = myThread(3, queues, 2)

    p1.start()
    p2.start()
    p3.start()


    # testing functionality of the queues across processes --> working!
    p1.add_to_queue(2, "hi!")
    p2.add_to_queue(1, "what's up? ")

    for i in range(0, len(queues)):
        q = queues[i]
        if not q.empty():
            msg = q.get()
            print(str(i) + ": " + msg)


if __name__ == '__main__':
    run()
