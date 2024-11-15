from enum import Enum
from typing import List
from dataclasses import dataclass
import random

#notes:
    # think about individual classes as actions and prop.
    # #what are the internal tings I need to worry about like getters and setters

'''
OOP: about relationships between things; IS-A and HAS-A as test to apply to relationship
    - example: IS-A (done via inheritance)
        is a simulation a halth status? No!
         - SO SIMULATE SHOULD NOT INHERIT FROM HEALTHSTATUS
    - example: HAS-A (via encapsulation: represented by variables inside a class)
        moved constants into constructor 
        siumulation uses encapsulation!!!! it HAS-A population
'''

DEFAULT_POPULATION = 10000 
DEFAULT_DAYS = 100
DEFAULT_INFECTED_INITIAL = 100
MAX_NEXPOSURES: int = 21

class HealthStatus(Enum):
    SUSCEPTIBLE = 0,
    RECOVERED = -1,
    VACCINATED = -2,
    DEAD = -3,
    INFECTED = 4 #TODO: ????? CHALLENGE: NOT JUST A STATE BUT A COUNT AKA # DAYS USER IS INFECTED -> how get around this!

class Simulation:
    def __init__(self, population: int = DEFAULT_POPULATION, days: int = DEFAULT_DAYS, 
                 infected: int = DEFAULT_INFECTED_INITIAL):
        self._population = population #should not be touched directly
        self._days = days
        self._infected = infected

    status: int = []
    new_status: int = []
    '''creating a public prop onto private data'''

    @property
    def population(self) -> int:
        '''The population property'''
        return self.population 
    
    @population.setter
    def population(self, population: int):
        if population < 0:
            raise ValueError("population can not be a negative number")
        self._population = population 

    @property
    def days(self) -> int:
        '''The days property'''
        return self._days
    
    @days.setter
    def days(self, days: int):
        if days < 0:
            raise ValueError("days can not be a negative number")
        self.days = days
    
    @property
    def infected(self) -> int:
        '''The infected property'''
        return self._days
    
    @days.setter
    def infected(self, infected: int):
        if infected < 0:
            raise ValueError("counted of infected individuals can not be a negative number")
        self.infected = infected
    
    #TODO: do we want this
    def write_to_file():
        pass

# @dataclass
class Person:
    MAX_SICK_DAYS: int = 14
    
    def __init__(self, health_status: HealthStatus = HealthStatus.SUSCEPTIBLE, sick_days: int = 0):
        self.health_status: HealthStatus = health_status
        self.sick_days: int = 0 #num of days person is sick
    # health_status: HealthStatus
    # sick_days: int 
    
    def catch_or_not(self, tprob: float, status: List, nexposure: int, other_person: int, other_person_tprob: float) -> int: 
        if tprob < 0 or tprob > 1:
            raise ValueError("tprob must be between 0 and 1")
        if len(status) == 0:
            raise IndexError("empty range for status")
        # iterate to simulate person interacting with nexposure number of people each day
        for i in range(nexposure):
            if status[other_person] > 0: 
                # person is now infected by other_person if other_person_tprob < tprob
                if other_person_tprob < tprob:
                    return 1
        # return is_susceptible value for the day if not infected from random interactions for the day 
        return HealthStatus.SUSCEPTIBLE

    # checks if individual stays sick, dies or gets better
    def die_or_not(self, dprob: float, sick_days: int, person: int, status: List, rand_dprob: float, sickness_factor: float):
        if (dprob < 0 or dprob > 1):      
            raise ValueError("dprob must be between 0 and 1")
        if (rand_dprob < 0 or rand_dprob > 1):
            raise ValueError("rand_dprob must be between 0 and 1")
        if len(status) == 0:
            raise IndexError("empty range for status")
        if rand_dprob < dprob:
            print("died")
            return HealthStatus.DEAD
        else:
            # else must check if recovers or remains sick
            sick_days_randomization = sick_days + 3.0 * sickness_factor
            if status[person] > sick_days_randomization:
                print("recovered")
                return HealthStatus.RECOVERED
            else:
                print("still sick")
                return status[person] + 1
         

def main():
    # CLA: tprob, dprob, days_to_assess, population_count = DEFAULT_POPULATION, percent_initially_infected
    # status = [0] * population count 
    # new_status = [] # rename to status on each iteration loop 
    status = [0, 1, 0, 3, 2, 2, 0, 1, 0, 3, 2, 2] 
    person = Person()
    person.catch_or_not(0.5, status)
    person.die_or_not(0.15, person.MAX_SICK_DAYS, 6, status)

if __name__ == "__main__":
    main()