from enum import Enum
from typing import List, Annotated
from dataclasses import dataclass
import random
import pandas as pd
from typing_extensions import Self
import sys
import typer
import matplotlib.pyplot as plt
import csv
from collections import Counter

app = typer.Typer()

DEFAULT_POPULATION = 100
DEFAULT_DAYS = 10
DEFAULT_INFECTED_INITIAL = 10
MAX_NEXPOSURES: int = 21

SIMULATE_FILE = 'simulate.csv'
ANALYZE_FILE = 'analyze.csv'

class HS(int, Enum):
    SUSCEPTIBLE = 0
    RECOVERED = -1
    VACCINATED = -2
    DEAD = -3
    INFECTED = 1 

HealthStatus = HS | int

# class Analyze:
    # function to import 

class Simulation:
    def __init__(self, population: int, infected: int, vaccinated: int):
        self.vaccinated = vaccinated
        self._infected = infected
        # generate a list of Person objects
        # self._population: List[Person] = [Person(health_status=HS.INFECTED, sick_days = 1) for _ in range(infected)] + [Person(health_status=HS.VACCINATED, sick_days = 0) for _ in range(vaccinated)]+ [Person(transmission_rate=random.random()) for _ in range(population - (infected + vaccinated))]    
        # using list comprehnsion and splat operator to generate list of person objects for population
        self._population: List[Person] = [*(Person(health_status=HS.INFECTED, sick_days = 1) for _ in range(infected)), *(Person(health_status=HS.VACCINATED, sick_days = 0) for _ in range(vaccinated)), *(Person(transmission_rate=random.random()) for _ in range(population - (infected + vaccinated)))]    
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
        return self._infected
    
    @infected.setter
    def infected(self, infected: int):
        if infected < 0:
            raise ValueError("counted of infected individuals can not be a negative number")
        self._infected = infected

    def write_values_to_file(self, df: pd.DataFrame, filename: str): 
        df.to_csv(filename, index = False)
    
    # dict with initalized values for each health status catagory
    def health_status_dict(self) -> Counter: #dict:
        # status_counts = {
        return Counter({
            'Day':0,
            HS.SUSCEPTIBLE: DEFAULT_POPULATION - (DEFAULT_INFECTED_INITIAL + self.vaccinated),
            HS.INFECTED: DEFAULT_INFECTED_INITIAL,
            HS.RECOVERED: 0,
            HS.DEAD: 0,
            HS.VACCINATED: self.vaccinated
        })

        # return status_counts
    
    def calculate_stats(self, df: pd.DataFrame) -> float: 
        # take avg of all rows in column 1
        avg = df[HS.DEAD].mean()
        stdv = df[HS.DEAD].std()
        return avg, stdv
    
    def generate_statistics_dict(self):
        adf_dict = {
            'Trial': 0,
            'AVG_DEATHS': 0,
            'STDV': 0
        }

        return adf_dict
     
    def run(self, tprob: float, dprob: float, days: int): #TODO: how do we incorporate vaccinated 
        daily_counts = []
        status_counts: dict = self.health_status_dict()
        df = pd.DataFrame(columns = ['Day', HS.SUSCEPTIBLE, HS.INFECTED, HS.RECOVERED, HS.DEAD, HS.VACCINATED])
        for day in range(days):
            for person in self.population: # check each persons status on each day
                self.update_person_status(person, status_counts, tprob, dprob)

            status_counts['Day'] = day
            df.loc[day] = status_counts
        
        return df

    def update_person_status(self, person: Person, status_counts: dict, tprob: float, dprob: float) -> None:
        if person.health_status == HS.SUSCEPTIBLE:
            self._handle_susceptible(person, status_counts, tprob)
        elif person.health_status == HS.INFECTED:
            self._handle_infected(person, status_counts, dprob)

    def _handle_susceptible(self, person: Person, status_counts: dict, tprob: float) -> None:
        nexposures: int = random.randint(1, 8) # randomly generate int to simulate number of exposures Person objects encounters each day
        other_persons_list: List[Person] = random.sample(self.population, random.randint(1, min(nexposures, len(self.population)))) #TODO: check for accuracy -> why min
        if person.catch_or_not(tprob, other_persons_list):
            person.health_status = HS.INFECTED
            person.sick_days = 1
            status_counts[HS.INFECTED] += 1; status_counts[HS.SUSCEPTIBLE] -= 1

    def _handle_infected(self, person: Person, status_counts: dict, dprob: float) -> None:
        if person.die_or_not(dprob, random.random(), random.random(), person):
            person.health_status = HS.DEAD
            status_counts[HS.DEAD] += 1; status_counts[HS.INFECTED] -= 1
        else:
            days_sick = person.num_sick_days_greater_than_max_sick_days(person, random.random())
            if days_sick > 14:
                person.health_status = HS.RECOVERED
                status_counts[HS.RECOVERED] += 1; status_counts[HS.INFECTED] -= 1
            else: 
                person.sick_days += 1
    
    def print_report(self, df: pd.DataFrame, tprob: float, vaccinated: int, infected: int, days: int, population_count: int) -> None:
        print(f"Populaton: {population_count:,}")
        print(f"Vaccination Probability: {vaccinated:.2%}")
        print(f"Transmission Probability: {tprob:.2%}")
        print(f"Initial Infections: {infected:,}")
        print(f"Siumulation Period: {days:,}")
        print(f"Number of Recovered: {df.iloc[8, 3]:,}") 
        print(f"Number of Dead: {df.iloc[8, 4]:,}") 
        # try to calculate CFR but if zero recover will print error
        try:
            dead_value = df.iloc[8, 4] #TODO: UNIT TEST
            recovered_value = df.iloc[8, 2].max() #TODO: UNIT TEST
            fatality_rate = round(dead_value/recovered_value, 2) if recovered_value != 0 else 'N/A'
            print(f"Case Fatality Rate: {fatality_rate:,}") #TODO: as dprob increases, rate of recovery descreases and thus end up with divide by zero
        except IndexError:
            print("DivideByZero error") #TODO: should this be printed to a log like fprintf or snprintf?
            

@dataclass(frozen = True, slots = True)
class Person:
    MAX_SICK_DAYS: int = 14
    health_status: HealthStatus = HS.SUSCEPTIBLE
    sick_days: int = 0
    transmission_rate: float = random.random() 

    def validate_probability(self, prob: float, name: str) -> None: 
        if not 0 <= prob <= 1:
            raise ValueError(f"{name} must be between 0 and 1")
    
    def check_if_infected(self, tprob: float, other_persons: List['Person']) -> bool:
        if (tprob < 0 and tprob > 1):
            raise ValueError("tprob must be between 0 and 1")
        # if self.validate_probability(tprob, tprob): #TODO: ask DG -> recc by Cody
        #     pass
        # iterate over list of random people to simulate interacting with individuals throughout day
        for other_person in other_persons:
            if other_person.health_status == HS.INFECTED: 
                if self.transmission_rate < tprob:
                    return True
                
        return False

    def catch_or_not(self, tprob: float, other_persons: List[Self]) -> bool: 
        if (tprob < 0 and tprob > 1):
            raise ValueError("tprob must be between 0 and 1")
        return self.check_if_infected(tprob, other_persons)
    
    def num_sick_days_greater_than_max_sick_days(self, person: 'Person', sickness_factor: float) -> int:
        if (sickness_factor < 0 or sickness_factor > 1):      
            raise ValueError("sickness_factor must be between 0 and 1")
        return person.sick_days + 3.0 * sickness_factor

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
        
        return self.check_if_survive(dprob, rand_dprob, sickness_factor, person)

class Visualize: #TODO: should this be a class or just global functions
    def __init__(self, dmin: int, dmax: int):
        self.dmin = dmin
        self.dmax = dmax

    # read CSV file into pandas df
    def read_file(self, filename: str):
        return pd.read_csv(filename)
    
    # generate historgram using matplotlib
    def generate_histogram(self, df: pd.DataFrame):
        plt.hist(df['AVG_DEATHS'])
        plt.xlabel('Deaths')
        plt.ylabel('Frequency')
        plt.title('Deaths per Trial')
        plt.show()
    
    def plot(self, df: pd.DataFrame): #TODO: cody suggested moving this here but i dont ever create a Vis. object in the sim commd
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
    
@app.command()
def visualize(dmin: Annotated[int, typer.Argument()],
            dmax: Annotated[int, typer.Argument()],
            input_file: Annotated[str, typer.Argument()]):
    # create a visualize object
    vis = Visualize(dmin, dmax)
    df = vis.read_file(input_file)
    vis.generate_histogram(df)

def calculate_vaccinated(vprob: float, population_count: int) -> int:
    return int(vprob * population_count)

# execute n number of simulations
@app.command()
def analyze(nsimulations: Annotated[int, typer.Argument],
            tprob: Annotated[float, typer.Argument()] = 0.05, 
            dprob: Annotated[float, typer.Argument()] = 0.05,
            vprob: Annotated[float, typer.Argument()] = 0.0,
            days: Annotated[int, typer.Argument()] = DEFAULT_DAYS,
            infected: Annotated[int, typer.Argument()] = DEFAULT_INFECTED_INITIAL,
            population_count: Annotated[int, typer.Argument()] = DEFAULT_POPULATION,
            output_file: Annotated[str, typer.Argument()] = ANALYZE_FILE): 
    vaccinated: int = calculate_vaccinated(vprob, population_count) #TODO: lambda function
    adf = pd.DataFrame(columns = ['AVG_DEATHS', 'STDV'])
    for trial in range(nsimulations):
        print(f"trial number {trial + 1} in progress...")
        sim = Simulation(population_count, infected, vaccinated) 
        adf_dict = sim.generate_statistics_dict()
        df = sim.run(tprob, dprob, days)
        adf_dict['AVG_DEATHS'], adf_dict['STDV'] = sim.calculate_stats(df)
        adf_dict['Trial'] = trial
        adf.loc[trial + 1] = adf_dict
    sim.write_values_to_file(adf, output_file)

# run a single simulation
@app.command()
def simulate(tprob: Annotated[float, typer.Argument()] = 0.5, 
             dprob: Annotated[float, typer.Argument()] = 0.5,
             vprob: Annotated[float, typer.Argument()] = 0.5,
             infected: Annotated[int, typer.Argument()] = DEFAULT_INFECTED_INITIAL,
             days: Annotated[int, typer.Argument()] = DEFAULT_DAYS,
             population_count: Annotated[int, typer.Argument()] = DEFAULT_POPULATION,
             output_file: Annotated[str, typer.Argument()] = SIMULATE_FILE): 
    vaccinated: int = calculate_vaccinated(vprob, population_count) #TODO: lambda function
    sim = Simulation(population_count, infected, vaccinated)
    df = sim.run(tprob, dprob, days)
    sim.write_values_to_file(df, output_file)
    sim.print_report(df, tprob, vaccinated, infected, days, population_count)

if __name__ == "__main__":
    app()

#Me: RECOVERED is not getting changing in values. If infected is going to zero then they should be counted as recovered. Only sus, infected, and dead or changing. Not even vacc changing with adding values.
    #problem: vaccinated prob with instantiation of list of person objects, recovered must be with run() logic

'''
To do:
    - update readme.md (CHECK)
    - re-configure code based on Cody results
    - update unit tests based on newly created fxs from above
    - complete analyze and proper hist plotting
'''