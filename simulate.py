from enum import Enum
from typing import List

class HealthStatus(Enum):
    SUSCEPTIBLE = 0,
    RECOVERED = -1,
    VACCINATED = -2,
    DEAD = -3,
    INFECTED = 4 #TODO: ????? CHALLENGE: NOT JUST A STATE BUT A COUNT AKA # DAYS USER IS INFECTED -> how get around this! representing state and count
'''
OOP: about relationships between things; IS-A and HAS-A as test to apply to relationship
    - example: IS-A (done via inheritance)
        is a simulation a halth status? No!
         - SO SIMULATE SHOULD NOT INHERIT FROM HEALTHSTATUS
    - example: HAS-A (via encapsulation: represented by variables inside a class)
        moved constants into constructor 
        siumulation uses encapsulation!!!! it HAS-A population

inheritance: 
'''

DEFAULT_POPULATION = 10000 #if user doesn't supply, then use this 

class Simulation: # changed simulation from simulate
    '''this makes Simulate class singularly focused; hard coding values vs user passing in'''
    def __init__(self, population: int = DEFAULT_POPULATION):
        self._population = population # make all instance vars private, and properites to access them
    DAYS = 100
    INFECTED_INITIAL = 100

    @property
    def _population(self) -> int:
        return self._population
    
    '''get to control how it gets changed vs ther caller'''
    @_population.setter
    def _population(self, population: int): #setters typicaly dont return anything
        if population < 0:
            # Exception:
                #enter code for exception
            pass
                
        self._population = population 


    # determine if a SINGLE SUSCEPTIBLE individual becomes infected
    # simulate random number of encounters 
    def catch_or_not(self, tprob: int, npeople: int, status: List) -> int:
        # generate random num of people for exposure
        # generate n_exposure = arbitrary count of exposures individual encountered)
        # iterate over n_exposures
            # create other_person (via rand gen) = random person from 10k list (?)
            # check if other_person sick by comp against tprob
        # if value > 1, person on first day of sickness (add to new_status/day_end)
        # return is_sus if no encounters result in infection
        pass
    
    # TODO: checks if individual stays sick, dies or gets better
    def die_or_not(self, dprob: int, sick_days: int, person: int, npeople: int, status: List):
        pass 

 #example 1: no properties
    new_sim = Simulate(500)
    new_sim.population = -1 #accessing memory and changing

#xample 2
    new_sim.set_population(-1) #using a function call

class Person:
    def __init__(self, health_status: HealthStatus = HealthStatus.SUSCEPTIBLE):
        self._health_status = health_status

        #ASSIGNMENT: using prop decorator, write the getters and setters for health_status 
        #think about: what other prop or actions need to be defined for these classes
        #unit tests