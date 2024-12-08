from enum import Enum
from typing import List
# from typing import Self
from dataclasses import dataclass
import random
import typer
from typing_extensions import Annotated
import sys

DEFAULT_POPULATION = 10000 
DEFAULT_DAYS = 100
DEFAULT_INFECTED_INITIAL = 100
MAX_NEXPOSURES: int = 21

class HS(int, Enum):
    SUSCEPTIBLE = 0
    RECOVERED = -1
    VACCINATED = -2
    DEAD = -3
    INFECTED = 1 

HealthStatus = HS | int

class Simulation:
    def __init__(self, population: int = DEFAULT_POPULATION, days: int = DEFAULT_DAYS, 
                 infected: int = DEFAULT_INFECTED_INITIAL):
        self._population = population # should not be touched directly
        self._days = days
        self._infected = infected

    @property
    def population(self) -> int:
        '''The population property'''
        return self.population 
    
    @population.setter
    def population(self, population: int):
        if population < 0:
            raise ValueError("population cannot be a negative number")
        self._population = population 

    @property
    def days(self) -> int:
        '''The days property'''
        return self._days
    
    @days.setter
    def days(self, days: int):
        if days < 0:
            raise ValueError("days cannot be a negative number")
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

    #TODO: method to count values for each state at end of each day
    def count_healthstatus_states():
        pass

@dataclass
class Person:
    MAX_SICK_DAYS: int = 14
    
    # def __init__(self, health_status: HealthStatus = HealthStatus.SUSCEPTIBLE, sick_days: int = 0):
    #     self.health_status: HealthStatus = health_status
    #     self.sick_days: int = 0 #num of days person is sick
    health_status: HealthStatus = HS.SUSCEPTIBLE
    sick_days: int = 0
    transmission_rate: float = random.random() #being treated as a class var -> getting hit once and setting all 12/4

    def check_if_infected(self, tprob: float, other_persons: List['Person']) -> bool:
        # iterate over list of random people to simulate interacting with individuals throughout day
        for other_person in other_persons:
            if other_person.health_status == HS.INFECTED: 
                if Person.transmission_rate < tprob:
                    return True
                
        return False

    def catch_or_not(self, tprob: float, other_persons: List['Person']) -> bool: 
        if tprob < 0 or tprob > 1:
            raise ValueError("tprob must be between 0 and 1")
        if len(other_persons) == 0:
            raise IndexError("empty range for other_persons list")
        # person_infected = self.check_if_infected(tprob, other_persons)

        # return True if person_infected else False
        # return person_infected
        return self.check_if_infected(tprob, other_persons)
    
    def num_sick_days_greater_than_max_sick_days(self, person: 'Person', sickness_factor: float) -> int:
        # sick_days_randcomization = person.sick_days + 3.0 * sickness_factor
        return person.sick_days + 3.0 * sickness_factor
        # if person.sick_days > sick_days_randomization:
            

    
    def check_if_survive(self, dprob: float, rand_dprob: float, sickness_factor: float, person: 'Person') -> bool:
        if rand_dprob < dprob:
            return True
        return False

    # checks if individual stays sick, dies or gets better
    def die_or_not(self, dprob: float, rand_dprob: float, sickness_factor: float, person: 'Person') -> bool: #, population: List) -> bool:
        if (sickness_factor < 0 or sickness_factor > 1):      
            raise ValueError("sickness_factor must be between 0 and 1")
        if (dprob < 0 or dprob > 1):      
            raise ValueError("dprob must be between 0 and 1")
        if (rand_dprob < 0 or rand_dprob > 1):
            raise ValueError("rand_dprob must be between 0 and 1")
        # if len(population) == 0:
        #     raise IndexError("empty range for population")
        return self.check_if_survive(dprob, rand_dprob, sickness_factor, person)
        
         
def main(tprob: Annotated[float, typer.Argument()] = 0.5, dprob: Annotated[float, typer.Argument()] = 0.5, vprob: Annotated[float, typer.Argument()] = 0.5,
                population_count: Annotated[int, typer.Argument()] = DEFAULT_POPULATION, infected: Annotated[int, typer.Argument()] = DEFAULT_INFECTED_INITIAL,
                days: Annotated[int, typer.Argument()] = DEFAULT_DAYS):
    nvaccinated = vprob * population_count
    # generate list of Person objects with some set to health_status.INFECTED based on infected value passed on CL
    population: List[Person] = [Person(health_status=HS.INFECTED, sick_days = 1) for _ in range(3)] + [Person(transmission_rate=random.random()) for _ in range(5)] 
    random.shuffle(population)
    for i in population:
        print(i)
    # nested loop iterating over each day
    # the inner loop iterates over each individual to determine if person gets sick, gets well, dies, or remains sick and increases day of infection by 1 day
    for day in range(days): # iterate over each day
        for person in population: # check each persons status on each day
            if person.health_status == HS.SUSCEPTIBLE:
                nexposures: int = random.randint(1, 8) # randomly generate int to simulate numer of exposures Person objects encounters for the day
                other_persons_list: List[Person] = random.sample(population, random.randint(1, min(nexposures, len(population)))) 
                if person.catch_or_not(tprob, other_persons_list):
                    person.health_status = HS.INFECTED
                    person.sick_days = 1
            elif person.health_status == HS.INFECTED:
                if person.die_or_not(dprob, random.random(), random.random(), person):
                    person.health_status = HS.DEAD
                else:
                    days_sick = person.num_sick_days_greater_than_max_sick_days(person, random.random())
                    if days_sick > 14:
                        person.health_status == HS.RECOVERED
                    else: 
                        person.sick_days += 1
            elif person.health_status == HS.RECOVERED:
                continue
            
            # write count of health_statuses to file for data collection
                # generate fx to tally up w vars and place in dict: susceptible, recovered, nvaccinated, infected and dead for each day
                    # add to a pandas dataframe for data collection
            # switch status to new_health_statuses
        
    print('________________________')
    print('\n')
    for i in population:
        print(i)

if __name__ == "__main__":
    typer.run(main)

''' 12/04
- simulate runs one simulation of n days -> prints out each day
- what will output be for virus? figure out wha capture from each to output as a whole program
    - normalize: combine into one format
- push data to dataframe as opposed to I/O
    - output to excel and look at data before matplotlib

pydantic
dataclasses- real python
'''