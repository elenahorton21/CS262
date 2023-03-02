import threading
import queue
import random

# General idea, this program can create as many processes as we need 
# through the multiprocessing library running worker threads that define the main function

# the queue is shared by all the processes, includes messages for each thread

class myThread (threading.Thread):
    def __init__(self, id, queues, my_queue):
      threading.Thread.__init__(self)
      self.id = id
      self.queues = queues
      self.my_queue = my_queue

    def add_to_queue(self, queueID, message):
        self.queues[queueID].put(message)


    def run(self):              
      print("Starting " + str(self.id))
      print("Exiting " + str(self.id))




def run():
    first_q = queue.Queue()
    second_q = queue.Queue()
    third_q = queue.Queue()
    queues = [first_q, second_q, third_q]
    clocktime = random.randint(1, 6)
    print(clocktime)

    # Create three "model clock" processes
    p1 = myThread(1, queues, 0)
    p2 = myThread(2, queues, 1)
    p3 = myThread(3, queues, 2)

    p1.start()
    p2.start()
    p3.start()

    p1.add_to_queue(2, "hi!")
    p2. add_to_queue(1, "what's up? ")

    for i in range(0, len(queues)):
        q = queues[i]
        if not q.empty():
            msg = q.get()
            print(str(i) + ": " + msg)


if __name__ == '__main__':
    run()
