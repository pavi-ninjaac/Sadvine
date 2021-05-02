import logging
import threading
import time
import datetime

class Package:
    """
    A package to deliver.
    """

    def __init__(self, name):
        self.name = name
        self.worker = None
        self.delivered = False
        self.assigned = False

    def assign_worker(self, worker):
        self.worker = worker

    def mark_delivered(self):
        #if self.delivered:---> eliminated this check , all packages are assigned to only one worker so no 
        #need to check if it is already delivered or not.

        self.delivered = True


class Worker(threading.Thread):
    """
    Worker receives packages from employer and deliver them.
    """
    
    def __init__(self, name, employer):
        super().__init__()
        self.setName(name)
        self.employer = employer
        self.balance = 0
        self.packages_delivered = 0
        self.logger = get_logger(name.lower())
    
    def run(self):
        self.logger.info("Starting work")

        while True:
            package = self.employer.get_package_to_deliver()
            if not package:
                self.logger.info("No more packages to deliver")
                break
            self.deliver_package(package)
            self.employer.report_package_delivered(package)
            self.packages_delivered += 1

        self.logger.info("The work is fully done")
        return None #chaned here


    def deliver_package(self , package):
        package.assign_worker(self)
        self.logger.info(f"Package {package.name} is assigned to {package.worker}")
        self.logger.info(f"Delivering package {package.name}") 
        self.logger.info(f"Package {package.name} successfully delivered")


class Employer:
    """  Employeer hiring the workers and must deliver all the package correctly"""
    def __init__(self, packages_to_deliver):
        self.logger = get_logger("employer")
        self.packages_to_deliver = packages_to_deliver
        self.packages = [Package(f"package_{n + 1}") for n in range(packages_to_deliver)]
        self.package_start = 0
        self.balance = len(self.packages)
        self.workers = []
        self.the_lock = threading.Lock() #changed place
        

    def hire(self, name):
        self.workers.append(Worker(name, self))
        self.logger.info(f"A new worker {name} was hired")

    def get_package_to_deliver(self ): #eliminated the for loop here
        with self.the_lock:
            if self.package_start < self.packages_to_deliver:
                package = self.packages[self.package_start]
                if not package.delivered:
                    if not package.assigned:
                        package.assigned = True
                        self.package_start+=1
                        return package
        
        return None

    def report_package_delivered(self , package): #eliminated the try block here 
        self.balance -= 1
        package.mark_delivered()
        self.logger.info(f"Package {package.name} was delivered by {package.worker.name}")  

    #def get_left_to_deliver(self): #there is no need for this function anymore.

    def deliver_all_packages(self):
        
        self.logger.info(f"Starting the work with {len(self.workers)} workers")
        start_time = datetime.datetime.now()

        for worker in self.workers:
            worker.start() 

        while self.balance > 0:
            self.logger.info(f"Still {self.balance} packages to sent")

        self.logger.info("All packages delivered")

        for worker in self.workers:
            worker.join()

        work_duration = ((datetime.datetime.now() - start_time).total_seconds())
        self.logger.info(f"The work is fully done in {work_duration} seconds")
        self.logger.info(f"Employer balance: {self.balance}")
        total_deliveries_reported = 0
        for worker in self.workers:
            delivered = worker.packages_delivered
            total_deliveries_reported += delivered
            self.logger.info(f"Packages delivered by {worker.name}: {delivered}")

        self.logger.info(f"Total number of packages planned for delivery: {len(self.packages)} ")
        self.logger.info(f"Total number of packages delivered by workers: {total_deliveries_reported}")

handler = logging.FileHandler(filename='log.txt',mode = 'w+')
def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    logger.addHandler(handler)
    format_ = logging.Formatter("%(asctime)s [%(levelname)8s] %(name)s: %(message)s")
    handler.setFormatter(format_)
    
    return logger

if __name__ == '__main__':
    planet_express = Employer(10000)
    planet_express.hire("Philip")
    planet_express.hire("Leela")
    planet_express.hire("Bender")
    planet_express.hire("Amy")
    planet_express.hire("Hermes")
    planet_express.hire("Zoidberg")
    
    planet_express.deliver_all_packages()