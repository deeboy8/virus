from enum import Enum
from typing import List
from dataclasses import dataclass
import random
import typer
from typing_extensions import Annotated
import sys

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
    #TODO: solution: DS => list of list with elements consisting of num days infected, status, etc?

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
    
    def catch_or_not(self, tprob: float, status: List, nexposure: int, other_person: int, other_person_tprob: float) -> int: # neposure, other_person, other_person_tprob randomly generated
        if tprob < 0 or tprob > 1:
            raise ValueError("tprob must be between 0 and 1")
        if len(status) == 0:
            raise IndexError("empty range for status")
        # iterate to simulate person interacting with nexposure number of people each day
        for i in range(nexposure):
            if status[other_person][1] > 0: 
                # person is now infected by other_person if other_person_tprob < tprob
                if other_person_tprob < tprob:
                    return HealthStatus.INFECTED, 1
        # return is_susceptible value for the day if not infected from random interactions for the day 
        return HealthStatus.SUSCEPTIBLE

    # checks if individual stays sick, dies or gets better
    def die_or_not(self, dprob: float, rand_dprob: float, sickness_factor: float, sick_days: int, person: int, status: List):
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
            if status[person][0] > sick_days_randomization:
                print("recovered")
                return HealthStatus.RECOVERED
            else:
                print("still sick") 
                return status[person][0] + 1
         
def main(tprob: Annotated[float, typer.Argument()], dprob: Annotated[float, typer.Argument()], vprob: Annotated[float, typer.Argument()],
                population_count: Annotated[int, typer.Argument()] = DEFAULT_POPULATION, infected: Annotated[int, typer.Argument()] = DEFAULT_INFECTED_INITIAL,
                days: Annotated[int, typer.Argument()] = DEFAULT_DAYS):
    columns = 2
    nvaccinated = vprob * population_count
    # 2d list: two columns to hold length of infection (days), current_status (see Enum class above)
    status = [[0] * columns for i in range(20)] #population_count] # [status, days_infected]
    status_new = None
    # nested loop to iterate for each day with inner loop iterating over each individual determining if gets sick, dies, or ramains the same
    for day in range(days): # iterate over each day
        for person in range(len(status)): # iterate each person
            # person = Person()
            # # for production use: nexpsure: random.randint(20), other_person: random.randint(population_count), other_person_tprob: random.random()
            # person.catch_or_not(tprob, status, 11, 17, 0.4)
            # person.die_or_not(0.15, 0.45, 0.07, person.MAX_SICK_DAYS, 5, status) # rand_dprob: random.random(), sickeness_factor: random.ran
            if status[person][0] == HealthStatus.SUSCEPTIBLE:
                status_new[person][0], status_new[person][1] = Person.catch_or_not(tprob, status, random.randint(20), random.randint(population_count), random.random())
            elif status[person][0] == HealthStatus.INFECTED:
                status_new[person][0], status_new[person][1] = Person.die_or_not(dprob, random.random(), random.random(), Person.MAX_SICK_DAYS, status[person], status)
    if __name__ == "__main__":
        typer.run(main)


# if status is infected, must accoutn for status[0] as heathastatus.infected and status[1] which will be num days infected