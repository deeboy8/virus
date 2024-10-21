from enum import Enum
from typing import List

class HealthStatus(Enum):
    SUSCEPTIBLE = 0,
    RECOVERED = -1,
    VACCINATED = -2,
    DEAD = -3,
    INFECTED = 4 #?????

class Simulate(HealthStatus):
    POPULATION = 10000
    DAYS = 100
    INFECTED_INITIAL = 100

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