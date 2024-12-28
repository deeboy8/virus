from enum import Enum
from typing import List
# from typing import Self
from dataclasses import dataclass
import random
import typer
from typing_extensions import Annotated
import sys
import pandas as pd
import matplotlib.pyplot as plt
from pydantic import BaseModel, Field

app = typer.Typer()

DEFAULT_POPULATION = 10
DEFAULT_DAYS = 10
DEFAULT_INFECTED_INITIAL = 2
MAX_NEXPOSURES: int = 21

class HS(int, Enum):
    SUSCEPTIBLE = 0
    RECOVERED = -1
    VACCINATED = -2
    DEAD = -3
    INFECTED = 1 

HealthStatus = HS | int

class Simulation:
    def __init__(self, population: int,
                 infected: int,
                 population_count: int):
        self._population = population # should not be touched directly
        # self._days = days
        self._infected = infected
        self.population_count = population_count

        # self.nvaccinated = vprob * population_count
        # generate a list of Person objects
        self._population: List[Person] = [Person(health_status=HS.INFECTED, sick_days = 1) for _ in range(infected)] + [Person(transmission_rate=random.random()) for _ in range(population_count - infected)]      
        random.shuffle(self.population)

    @property
    def population(self) -> int:
        '''The population property'''
        return self._population 
    
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
        self_days = days
    
    @property
    def infected(self) -> int:
        '''The infected property'''
        return self._days
    
    @days.setter
    def infected(self, infected: int):
        if infected < 0:
            raise ValueError("counted of infected individuals can not be a negative number")
        self._infected = infected
    
    # function to aggregate results from one day of analysis
    # consists of health statuses as keys and counts as values
    # def aggregate_health_status_counts() -> dict: #TODO: should this be a global fx or class fx
    #     # status_counts = {
    #     #     'Day':0,
    #     #     HS.SUSCEPTIBLE: 0,
    #     #     HS.INFECTED: 0,
    #     #     HS.RECOVERED: 0,
    #     #     HS.DEAD: 0,
    #     #     HS.VACCINATED: 0
    #     # }

    #     # for person in population:
    #     #     status_counts[person.health_status] += 1

    #     return status_counts

    # #TODO: method to count values for each state at end of each day
    # def d():
    #     pass

    def write_status_counts_to_file(self, df: pd.DataFrame, filename: str): 
        df.to_csv(filename, index = False)

    def plot(df: pd.DataFrame):
        # Create the plot
        plt.figure(figsize=(10, 6))
        plt.plot(df['Day'], df[HS.SUSCEPTIBLE], label='Susceptible', color='blue')
        plt.plot(df['Day'], df[HS.INFECTED], label='Infected', color='red')
        plt.plot(df['Day'], df[HS.RECOVERED], label='Recovered', color='green')
        plt.plot(df['Day'], df[HS.DEAD], label='Dead', color='black')

        # Customize the plot
        plt.title('Virus Spread Simulation Over Time')
        plt.xlabel('Days')
        plt.ylabel('Number of People')
        plt.legend()
        plt.grid(True)

        # Save and show the plot
        plt.savefig('virus_simulation.png')
        plt.show() 
    
    def run(self, tprob: float, dprob: float, days: int, population: List['Person']): 
        daily_counts= []
        # create dictionary for updating health statuses
        status_counts = {
            'Day':0,
            HS.SUSCEPTIBLE: 0,
            HS.INFECTED: 0,
            HS.RECOVERED: 0,
            HS.DEAD: 0,
            HS.VACCINATED: 0
        }
        # health_status_dict = self.aggregate_health_status_counts() # create empty dataframe
        # create dataframe to hold values
        df = pd.DataFrame(columns = ['Day', HS.SUSCEPTIBLE, HS.INFECTED, HS.RECOVERED, HS.DEAD, HS.VACCINATED])
        for day in days:
            for person in population: # check each persons status on each day
                if person.health_status == HS.SUSCEPTIBLE:
                    nexposures: int = random.randint(1, 8) # randomly generate int to simulate number of exposures Person objects encounters each day
                    other_persons_list: List[Person] = random.sample(population, random.randint(1, min(nexposures, len(population)))) 
                    if person.catch_or_not(tprob, other_persons_list):
                        person.health_status = HS.INFECTED
                        person.sick_days = 1
                        status_counts[HS.INFECTED] += 1
                elif person.health_status == HS.INFECTED:
                    if person.die_or_not(dprob, random.random(), random.random(), person):
                        person.health_status = HS.DEAD
                        status_counts[HS.DEAD] += 1
                    else:
                        days_sick = person.num_sick_days_greater_than_max_sick_days(person, random.random())
                        if days_sick > 14:
                            person.health_status = HS.RECOVERED
                            status_counts[HS.RECOVERED] += 1
                        else: 
                            person.sick_days += 1
                elif person.health_status == HS.RECOVERED:
                    continue

            status_counts['Day'] = day
            df.loc[day] = status_counts
        print(df)
        return df
    
    # def compile_each_days_health_status_counts(df, day):
    #     # aggregate each days count of health statuses
    #     # returns a dict of health statuses and counts for the day
    #     daily_counts = Simulation.aggregate_health_status_counts(population) 
        daily_counts['Day'] = day
    #     # # add each days aggregated counts to dataframe df
    #     df.loc[day] = daily_counts

    


# @dataclass
class Person(BaseModel):
    MAX_SICK_DAYS: int = 14
    
    # def __init__(self, health_status: HealthStatus = HealthStatus.SUSCEPTIBLE, sick_days: int = 0):
    #     self.health_status: HealthStatus = health_status
    #     self.sick_days: int = 0 #num of days person is sick
    health_status: HealthStatus = HS.SUSCEPTIBLE
    # sick_days: int = 0
    sick_days: int = Field(0, gt=0, le=1)
    transmission_rate: float = random.random() #being treated as a class var -> getting hit once and setting all 12/4

    def check_if_infected(self, tprob: float, other_persons: List['Person']) -> bool:
        # iterate over list of random people to simulate interacting with individuals throughout day
        for other_person in other_persons:
            if other_person.health_status == HS.INFECTED: 
                # if Person.transmission_rate < tprob:
                if self.transmission_rate < tprob:
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
        # parameter argument validation
        if (sickness_factor < 0 or sickness_factor > 1):      
            raise ValueError("sickness_factor must be between 0 and 1")
        if (dprob < 0 or dprob > 1):      
            raise ValueError("dprob must be between 0 and 1")
        if (rand_dprob < 0 or rand_dprob > 1):
            raise ValueError("rand_dprob must be between 0 and 1")
        # if len(population) == 0:
        #     raise IndexError("empty range for population")
        return self.check_if_survive(dprob, rand_dprob, sickness_factor, person)

@app.command()
def visualize():
    pass

@app.command()
def analyze(days: Annotated[int, typer.Argument()],
            nsimulations: Annotated[int, typer.Argument],
            tprob: Annotated[float, typer.Argument()] = 0.5, 
            dprob: Annotated[float, typer.Argument()] = 0.5): # concerned with writing down the avg deaths for each trial run
    # adf = df of columns with avg, stdv
    # for i in nsimulations
        # sim = Simulate(...) -> creating instance of the class
        # df = sim.run(...)
        # avg, stdv = sim.calculate_stats(df)
        # adf.append(avg, stdv)
    
    # adf.save_csv(filename)
    #_______________________________
    # create df
    # run simulate n times using
        # run a single simulation over a specific number of days
        # determine statistical analysis for each 100 day simulation: avg., stdf
        # update df for this specific simulation
    # return df
    pass

'''simulate will run a single simulation'''
@app.command()
def simulate(tprob: Annotated[float, typer.Argument()] = 0.5, 
             dprob: Annotated[float, typer.Argument()] = 0.5,
             infected: Annotated[int, typer.Argument()] = DEFAULT_INFECTED_INITIAL,
             days: Annotated[int, typer.Argument()] = DEFAULT_DAYS,
             population_count: Annotated[int, typer.Argument()] = DEFAULT_POPULATION): 
    sim = Simulation(population_count, infected)
    df = sim.run(tprob, dprob, days)
    # df.save_csv(filename)
   
    # create empty dataframe
    # df = pd.DataFrame(columns = ['Day', HS.SUSCEPTIBLE, HS.INFECTED, HS.RECOVERED, HS.DEAD, HS.VACCINATED])
    # # run a single simulation 
    # for day in days:
    #     single_simulation = Simulation.run(tprob, dprob)
    #     Simulation.compile_each_days_health_status_counts(df, day)
    # # Simulation.write_status_counts_to_file(df, 'simulation_n1',)

    # return df
    

# set up population list 
# def main(vprob: Annotated[float, typer.Argument()] = 0.5,
#          population_count: Annotated[int, typer.Argument()] = DEFAULT_POPULATION, 
#          infected: Annotated[int, typer.Argument()] = DEFAULT_INFECTED_INITIAL,
#          days: Annotated[int, typer.Argument()] = DEFAULT_DAYS): 
    
#     nvaccinated = vprob * population_count
#     # generate list of Person objects
#     # a count based on the CL value passed are intialized to a health status of infected 
#     population: List[Person] = [Person(health_status=HS.INFECTED, sick_days = 1) for _ in range(infected)] + [Person(transmission_rate=random.random()) for _ in range(population_count - infected)]      
#     # p = Person(sick_days = 15)
#     random.shuffle(population)


if __name__ == "__main__":
    app()
    # typer.run(main)

'''
To Do:
    - pydantic
    - unit tests


inputs/outputs:
    - program 1
        - input: tprob, dprob, vprob, pop count, infected, days
        - output: .csv file
    - program 2
        - input: number of trials
        - output: csv file for each trial run, csv file with statistical analysis: std. dev.
    - program 3
        - dmin dmax input_file output_file
        - output file

- make three apps sub-commands
    - use typer sub commands

To do:
    - read pydantic
    - property based testing (pbt)
    - 
'''