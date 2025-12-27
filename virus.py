"""
Virus Spread Simulation Module

This module simulates the spread of a virus through a population over time.
It tracks health statuses (Susceptible, Infected, Recovered, Vaccinated, Dead)
and provides functionality for running simulations, analyzing multiple trials,
and visualizing results.

Key Components:
    - Person: Represents an individual in the population
    - Simulation: Manages the simulation execution and state tracking
    - Visualize: Handles visualization of simulation results
    - CLI Commands: simulate, analyze, and visualize commands via Typer
"""

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
import numpy as np

app = typer.Typer()

DEFAULT_POPULATION = 1000
DEFAULT_DAYS = 50
DEFAULT_INFECTED_INITIAL = 10
MAX_NEXPOSURES: int = 21

SIMULATE_FILE = 'simulate.csv'
ANALYZE_FILE = 'analyze.csv'

class HS(int, Enum):
    """
    Health Status enumeration.
    
    Represents the possible health states of a person in the simulation.
    
    Attributes:
        SUSCEPTIBLE: Person can be infected (value: 0)
        RECOVERED: Person has recovered from infection (value: -1)
        VACCINATED: Person is vaccinated and protected (value: -2)
        DEAD: Person has died from infection (value: -3)
        INFECTED: Person is currently infected (value: 1)
    """
    SUSCEPTIBLE = 0
    RECOVERED = -1
    VACCINATED = -2
    DEAD = -3
    INFECTED = 1 

HealthStatus = HS | int

class Simulation:
    """
    Manages the virus spread simulation.
    
    This class initializes a population, tracks health status changes over time,
    and provides methods to run simulations and calculate statistics.
    
    Attributes:
        vaccinated: Number of vaccinated individuals in the population
        _infected: Number of initially infected individuals
        _population: List of Person objects representing the population
    """
    
    def __init__(self, population: int, infected: int, vaccinated: int):
        """
        Initialize a simulation with a population.
        
        Args:
            population: Total number of individuals in the population
            infected: Number of initially infected individuals
            vaccinated: Number of vaccinated individuals
            
        Note:
            The remaining individuals (population - infected - vaccinated)
            will be initialized as susceptible.
        """
        self.vaccinated = vaccinated
        self._infected = infected
        self._total_population = population  # Store for accurate status tracking
        # using list comprehnsion and splat operator to generate list of person objects for population 
        # with varying healthstatuses
        self._population: List[Person] = [*(Person(health_status=HS.INFECTED, sick_days = 1) for _ in range(infected)), *(Person(health_status=HS.VACCINATED, sick_days = 0) for _ in range(vaccinated)), *(Person(transmission_rate=random.random()) for _ in range(population - (infected + vaccinated)))]    
        random.shuffle(self.population)

    @property
    def population(self) -> int:
        """
        Get the population list.
        
        Returns:
            List of Person objects representing the population
        """
        return self._population 
    
    @population.setter
    def population(self, population: int):
        """
        Set the population list.
        
        Args:
            population: List of Person objects
            
        Raises:
            ValueError: If population is negative
        """
        if population < 0:
            raise ValueError("population cannot be a negative number")
        self._population = population 

    @property
    def days(self) -> int:
        """
        Get the number of simulation days.
        
        Returns:
            Number of days for the simulation
        """
        return self._days
    
    @days.setter
    def days(self, days: int):
        """
        Set the number of simulation days.
        
        Args:
            days: Number of days for the simulation
            
        Raises:
            ValueError: If days is negative
        """
        if days < 0:
            raise ValueError("days cannot be a negative number")
        self._days = days
    
    @property
    def infected(self) -> int:
        """
        Get the number of infected individuals.
        
        Returns:
            Number of currently infected individuals
        """
        return self._infected
    
    @infected.setter
    def infected(self, infected: int):
        """
        Set the number of infected individuals.
        
        Args:
            infected: Number of infected individuals
            
        Raises:
            ValueError: If infected count is negative
        """
        if infected < 0:
            raise ValueError("counted of infected individuals can not be a negative number")
        self._infected = infected

    def write_values_to_file(self, df: pd.DataFrame, filename: str):
        """
        Write simulation results to a CSV file.
        
        Args:
            df: DataFrame containing simulation data
            filename: Name of the output CSV file
        """
        df.to_csv(filename, index = False)
    
    def health_status_dict(self) -> Counter:
        """
        Create a dictionary with initialized values for each health status category.
        
        Returns:
            Counter object with initial counts for each health status and Day
        """
        return Counter({
            'Day':0,
            HS.SUSCEPTIBLE: self._total_population - (self._infected + self.vaccinated),
            HS.INFECTED: self._infected,
            HS.RECOVERED: 0,
            HS.DEAD: 0,
            HS.VACCINATED: self.vaccinated
        })
    
    def calculate_stats(self, df: pd.DataFrame) -> tuple:
        """
        Calculate statistical measures from simulation results.
        
        Computes average infected count, average deaths, and standard deviation
        of deaths across all days in the simulation.
        
        Args:
            df: DataFrame containing daily health status counts
            
        Returns:
            Tuple containing (avg_infected, avg_deaths, deaths_stdv)
        """
        avg_infected = df[HS.INFECTED].mean()
        avg_deaths = df[HS.DEAD].mean()
        deaths_stdv = df[HS.DEAD].std()

        return avg_infected, avg_deaths, deaths_stdv
    
    def generate_statistics_dict(self) -> dict:
        """
        Generate a dictionary template for storing trial statistics.
        
        Returns:
            Dictionary with keys for trial statistics, initialized to 0
        """
        adf_dict = {
            'Trial': 0,
            'AVG_DEATHS': 0,
            'AVG_DEATH_STDV': 0,
            'AVG_INFECTED': 0,
        }

        return adf_dict
     
    def run(self, tprob: float, dprob: float, days: int) -> pd.DataFrame:
        """
        Run the simulation for a specified number of days.
        
        For each day, updates the status of each person in the population
        based on transmission and death probabilities, then records the
        daily counts of each health status.
        
        Args:
            tprob: Transmission probability (0-1) for susceptible individuals
            dprob: Death probability (0-1) for infected individuals
            days: Number of days to simulate
            
        Returns:
            DataFrame with daily counts of each health status
        """
        daily_counts = []
        status_counts: dict = self.health_status_dict()
        df = pd.DataFrame(columns = ['Day', HS.SUSCEPTIBLE, HS.INFECTED, HS.RECOVERED, HS.DEAD, HS.VACCINATED])
        for day in range(days):
            for person in self.population:
                self.update_person_status(person, status_counts, tprob, dprob)

            status_counts['Day'] = day
            df.loc[day] = status_counts
        
        return df

    def update_person_status(self, person: 'Person', status_counts: dict, tprob: float, dprob: float) -> None:
        """
        Update a person's health status based on their current state.
        
        Routes to appropriate handler based on person's current health status.
        Vaccinated and recovered individuals remain unchanged.
        
        Args:
            person: Person object to update
            status_counts: Dictionary tracking counts of each health status
            tprob: Transmission probability
            dprob: Death probability
        """
        if person.health_status == HS.SUSCEPTIBLE:
            self._handle_susceptible(person, status_counts, tprob)
        elif person.health_status == HS.INFECTED:
            self._handle_infected(person, status_counts, dprob)
        elif person.health_status == HS.VACCINATED or person.health_status == HS.RECOVERED:
            pass

    def _handle_susceptible(self, person: 'Person', status_counts: dict, tprob: float) -> None:
        """
        Handle status update for a susceptible person.
        
        Simulates random encounters with other individuals and checks if
        infection occurs based on transmission probability. Updates status
        counts if person becomes infected.
        
        Args:
            person: Susceptible person to check
            status_counts: Dictionary tracking counts of each health status
            tprob: Transmission probability
        """
        nexposures: int = random.randint(1, 8)
        other_persons_list: List[Person] = random.sample(self.population, random.randint(1, min(nexposures, len(self.population))))
        if person.catch_or_not(tprob, other_persons_list):
            person.health_status = HS.INFECTED
            person.sick_days = 1
            status_counts[HS.INFECTED] += 1; status_counts[HS.SUSCEPTIBLE] -= 1

    def _handle_infected(self, person: 'Person', status_counts: dict, dprob: float) -> None:
        """
        Handle status update for an infected person.
        
        Checks if person dies based on death probability, or if they recover
        after being sick for more than 14 days. Updates status counts accordingly.
        
        Args:
            person: Infected person to check
            status_counts: Dictionary tracking counts of each health status
            dprob: Death probability
        """
        rand_dprob = random.random()  # Random value for death probability check
        sickness_factor = random.random()  # Random factor affecting disease severity
        if person.die_or_not(dprob, rand_dprob, sickness_factor, person):
            person.health_status = HS.DEAD
            status_counts[HS.DEAD] += 1; status_counts[HS.INFECTED] -= 1
        else:
            recovery_factor = random.random()  # Random factor for recovery time calculation
            days_sick = person.calculate_adjusted_sick_days(person, recovery_factor)
            if days_sick > 14:
                person.health_status = HS.RECOVERED
                status_counts[HS.RECOVERED] += 1; status_counts[HS.INFECTED] -= 1
            else: 
                person.sick_days += 1
    
    def print_report(self, df: pd.DataFrame, tprob: float, vaccinated: int, infected: int, days: int, population_count: int) -> None:
        """
        Print a summary report of the simulation results.
        
        Displays key simulation parameters and outcomes including population
        size, probabilities, initial conditions, final counts, and case
        fatality rate.
        
        Args:
            df: DataFrame containing simulation results
            tprob: Transmission probability used
            vaccinated: Number of vaccinated individuals
            infected: Initial number of infected individuals
            days: Number of simulation days
            population_count: Total population size
        """
        print(f"Populaton: {population_count:,}")
        print(f"Vaccination Probability: {vaccinated}")
        print(f"Transmission Probability: {tprob}")
        print(f"Initial Infections: {infected:}")
        print(f"Siumulation Period: {days:}")
        print(f"Number of Recovered: {df.iloc[-1, 3]:}") 
        print(f"Number of Dead: {df.iloc[-1, 4]:}") 
        try:
            dead_value = df.iloc[-1, 4]
            recovered_value = df.iloc[-1, 3]
            fatality_rate = round(dead_value/recovered_value, 2) if recovered_value != 0 else 'N/A'
            print(f"Case Fatality Rate: {fatality_rate}")
        except IndexError:
            print("Error calculating fatality rate")
            

@dataclass(frozen = False, slots = True)
class Person:
    """
    Represents an individual person in the simulation.
    
    Each person has a health status, tracks days sick, and has an individual
    transmission rate that affects their susceptibility to infection.
    
    Attributes:
        MAX_SICK_DAYS: Maximum number of days a person can be sick before recovery (default: 14)
        health_status: Current health status (default: SUSCEPTIBLE)
        sick_days: Number of days the person has been sick (default: 0)
        transmission_rate: Individual susceptibility factor (0-1, randomly generated)
    """
    MAX_SICK_DAYS: int = 14
    health_status: HealthStatus = HS.SUSCEPTIBLE
    sick_days: int = 0
    transmission_rate: float = random.random() 

    def validate_probability(self, prob: float, name: str) -> None:
        """
        Validate that a probability value is between 0 and 1.
        
        Args:
            prob: Probability value to validate
            name: Name of the probability parameter (for error messages)
            
        Raises:
            ValueError: If probability is not between 0 and 1
        """
        if not 0 <= prob <= 1:
            raise ValueError(f"{name} must be between 0 and 1")
    
    def _check_if_infected(self, tprob: float, other_persons: List['Person']) -> bool:
        """
        Internal method to check if this person becomes infected after interacting with others.
        
        Iterates through a list of other persons and checks if any are infected.
        If an infected person is encountered and this person's transmission_rate
        is less than the transmission probability, infection occurs.
        
        Note: This method assumes tprob has already been validated. Use catch_or_not()
        for the public interface.
        
        Args:
            tprob: Transmission probability threshold (assumed to be validated)
            other_persons: List of Person objects encountered during the day
            
        Returns:
            True if person becomes infected, False otherwise
        """
        for other_person in other_persons:
            if other_person.health_status == HS.INFECTED: 
                if self.transmission_rate < tprob:
                    return True 
        return False

    def catch_or_not(self, tprob: float, other_persons: List[Self]) -> bool:
        """
        Determine if person catches the virus from interactions.
        
        Validates transmission probability and checks if infection occurs based on
        interactions with other persons.
        
        Args:
            tprob: Transmission probability (0-1)
            other_persons: List of Person objects encountered during the day
            
        Returns:
            True if person becomes infected, False otherwise
            
        Raises:
            ValueError: If tprob is not between 0 and 1
        """
        if (tprob < 0 or tprob > 1):
            raise ValueError("tprob must be between 0 and 1")
        return self._check_if_infected(tprob, other_persons)
    
    def calculate_adjusted_sick_days(self, person: 'Person', sickness_factor: float) -> float:
        """
        Calculate adjusted sick days based on a sickness factor.
        
        Adds a weighted sickness factor to the current sick days to determine
        if recovery threshold has been reached. This allows for variable recovery
        times rather than a strict 14-day limit.
        
        Args:
            person: Person object to check
            sickness_factor: Random factor (0-1) affecting recovery time
            
        Returns:
            Adjusted number of sick days (sick_days + 3.0 * sickness_factor)
            
        Raises:
            ValueError: If sickness_factor is not between 0 and 1
        """
        if (sickness_factor < 0 or sickness_factor > 1):      
            raise ValueError("sickness_factor must be between 0 and 1")
        return person.sick_days + 3.0 * sickness_factor

    def check_if_survive(self, dprob: float, rand_dprob: float, sickness_factor: float, person: 'Person') -> bool:
        """
        Check if person survives based on death probability.
        
        Compares a random death probability value against the threshold
        to determine if person dies.
        
        Args:
            dprob: Death probability threshold
            rand_dprob: Random value (0-1) used for death determination
            sickness_factor: Factor affecting disease severity (not currently used)
            person: Person object being checked
            
        Returns:
            True if person dies (rand_dprob < dprob), False if they survive
        """
        if rand_dprob < dprob:
            return True
        return False

    def die_or_not(self, dprob: float, rand_dprob: float, sickness_factor: float, person: 'Person') -> bool:
        """
        Determine if an infected person dies based on death probability.
        
        Validates all probability parameters and checks survival status.
        This method determines whether an infected individual dies or
        continues with the infection.
        
        Args:
            dprob: Death probability threshold (0-1)
            rand_dprob: Random value (0-1) for death determination
            sickness_factor: Factor affecting disease severity (0-1)
            person: Person object being evaluated
            
        Returns:
            True if person dies, False if they survive
            
        Raises:
            ValueError: If any probability parameter is not between 0 and 1
        """
        if (sickness_factor < 0 or sickness_factor > 1):      
            raise ValueError("sickness_factor must be between 0 and 1")
        if (dprob < 0 or dprob > 1):      
            raise ValueError("dprob must be between 0 and 1")
        if (rand_dprob < 0 or rand_dprob > 1):
            raise ValueError("rand_dprob must be between 0 and 1")
        
        return self.check_if_survive(dprob, rand_dprob, sickness_factor, person)

class Visualize:
    """
    Handles visualization of simulation results.
    
    Provides methods to read CSV files and generate various plots including
    time series plots and histograms comparing multiple trials.
    
    Attributes:
        dmin: Minimum deaths for filtering (currently unused)
        dmax: Maximum deaths for filtering (currently unused)
    """
    
    def __init__(self, dmin: int, dmax: int):
        """
        Initialize visualization object.
        
        Args:
            dmin: Minimum deaths threshold (currently unused)
            dmax: Maximum deaths threshold (currently unused)
        """
        # self.dmin =  dmin
        # self.dmax = dmax
        pass

    def read_file(self, filename: str) -> pd.DataFrame:
        """
        Read simulation results from a CSV file.
        
        Args:
            filename: Path to the CSV file containing simulation data
            
        Returns:
            DataFrame containing the simulation results
        """
        return pd.read_csv(filename)
    
    def generate_histogram(self, df: pd.DataFrame) -> None:
        """
        Generate a grouped bar chart comparing results across multiple trials.
        
        Creates a histogram showing average infected, average deaths, and
        average death standard deviation for each trial in the analysis.
        
        Args:
            df: DataFrame containing trial statistics with columns:
                AVG_INFECTED, AVG_DEATHS, AVG_DEATH_STDV
        """
        # plt.hist(round(df['AVG_DEATHS']))
        # plt.xlabel('Deaths')
        # plt.ylabel('Frequency')
        # plt.title('Deaths per Trial')
        # plt.show()
    
        # generate set of health_statuses
        # column_list = df.columns.tolist()
        column_list = ['AVG_INFECTED', 'AVG_DEATHS', 'AVG_DEATH_STDV']
        # print(column_list)
        # create dict of trial results (each row in df)
        # print(trials_dict)
        # trials_dict = {i: values for i, values in enumerate(df.to_numpy())}
        # ['AVG_SUSCEPTIBLE','AVG_INFECTED', 'AVG_RECOVERED', 'AVG_DEATHS', 'STDV', 'AVG_VACCINATED']
        df_row_values = df.loc[range(len(df))].values.tolist()
        print(df_row_values)
        trials_dict = {i + 1: values for i, values in enumerate(df_row_values)}
        # print(trials_dict)

        # get number of trials
        # trial_count = len(df)
        width = 0.05
        # multiplier = 0
        x = np.arange(len(column_list))

        fig, ax = plt.subplots(figsize = (12, 6)) #layout = 'constrained')

        # for trial, values in trials_dict.items():
        for i, (trial, values) in enumerate(trials_dict.items()):
            offset = width * i
            rects = ax.bar(x + offset, values, width, label = f'Trial {trial}')
            ax.bar_label(rects, padding = 3, rotation = 90)
            # multiplier += 1
        
        ax.set_ylabel('Count')
        ax.set_title(f'Results by Health Status and Trial ({DEFAULT_POPULATION} Persons Population)')
        ax.set_xticks(x + width * (len(trials_dict) - 1) / 2)
        # ax.legend(loc = 'upper left', ncols = trial_count)
        ax.set_xticklabels(column_list, rotation = 0)
        # ax.set_ylim(0, 1000)
        ax.legend()

        plt.tight_layout()
        plt.show() 
    
    def plot(self, df: pd.DataFrame) -> None:
        """
        Generate a time series plot of health status counts over days.
        
        Creates a line plot showing how the number of susceptible, infected,
        recovered, and dead individuals changes over the course of the simulation.
        Saves the plot as 'virus_simulation.png' and displays it.
        
        Args:
            df: DataFrame containing daily health status counts with columns:
                Day, SUSCEPTIBLE, INFECTED, RECOVERED, DEAD
        """
        plt.figure(figsize=(10, 6))
        plt.plot(df['Day'], df[HS.SUSCEPTIBLE], label='Susceptible', color='blue')
        plt.plot(df['Day'], df[HS.INFECTED], label='Infected', color='red')
        plt.plot(df['Day'], df[HS.RECOVERED], label='Recovered', color='green')
        plt.plot(df['Day'], df[HS.DEAD], label='Dead', color='black')

        plt.title('Virus Spread Simulation Over Time')
        plt.xlabel('Days')
        plt.ylabel('Number of People')
        plt.legend()
        plt.grid(True)

        plt.savefig('virus_simulation.png')
        plt.show() 
    
@app.command()
def visualize(
    # dmin: Annotated[int, typer.Argument()],
    #         dmax: Annotated[int, typer.Argument()],
            input_file: Annotated[str, typer.Argument()]):
    """
    CLI command to visualize analysis results.
    
    Reads a CSV file containing trial statistics and generates a histogram
    comparing results across multiple trials.
    
    Args:
        input_file: Path to CSV file containing analysis results (typically from analyze command)
    """
    vis = Visualize(0, 0)  # dmin and dmax currently unused
    df = vis.read_file(input_file)
    vis.generate_histogram(df)

@app.command()
def analyze(nsimulations: Annotated[int, typer.Argument],
            vprob: Annotated[float, typer.Argument()],
            tprob: Annotated[float, typer.Argument()] = 0.05, 
            dprob: Annotated[float, typer.Argument()] = 0.05,
            days: Annotated[int, typer.Argument()] = DEFAULT_DAYS,
            infected: Annotated[int, typer.Argument()] = DEFAULT_INFECTED_INITIAL,
            population_count: Annotated[int, typer.Argument()] = DEFAULT_POPULATION,
            output_file: Annotated[str, typer.Argument()] = ANALYZE_FILE):
    """
    CLI command to run multiple simulations and analyze results.
    
    Executes the specified number of simulation trials with the same parameters
    and calculates average statistics (infected, deaths, standard deviation)
    across all trials. Results are saved to a CSV file.
    
    Args:
        nsimulations: Number of simulation trials to run
        vprob: Vaccination probability (fraction of population vaccinated)
        tprob: Transmission probability (default: 0.05)
        dprob: Death probability for infected individuals (default: 0.05)
        days: Number of days to simulate (default: 50)
        infected: Initial number of infected individuals (default: 10)
        population_count: Total population size (default: 1000)
        output_file: Name of output CSV file (default: 'analyze.csv')
    """ 
    vaccinated: int = int(vprob * population_count)
    # adf = pd.DataFrame(columns = ['AVG_SUSCEPTIBLE', 'AVG_INFECTED', 'AVG_RECOVERED', 'AVG_DEATHS', 'AVG_DEATH_STDV', 'AVG_VACCINATED'])
    adf = pd.DataFrame(columns = ['AVG_INFECTED', 'AVG_DEATHS', 'AVG_DEATH_STDV'])
    for trial in range(nsimulations):
        print(f"trial number {trial + 1} in progress...")
        sim = Simulation(population_count, infected, vaccinated) 
        adf_dict = sim.generate_statistics_dict()
        df = sim.run(tprob, dprob, days)
        # adf_dict['AVG_SUSCEPTIBLE'], adf_dict['AVG_INFECTED'], adf_dict['AVG_RECOVERED'], adf_dict['AVG_DEATHS'], adf_dict['AVG_STDV'], adf_dict['AVG_VACCINATED'] = sim.calculate_stats(df)
        adf_dict['AVG_INFECTED'], adf_dict['AVG_DEATHS'], adf_dict['AVG_DEATH_STDV'] = sim.calculate_stats(df)
        adf_dict['Trial'] = trial
        adf.loc[trial + 1] = adf_dict
    print(adf)
    sim.write_values_to_file(adf, output_file)

@app.command()
def simulate(vprob: Annotated[float, typer.Argument()],
            tprob: Annotated[float, typer.Argument()] = 0.5, 
            dprob: Annotated[float, typer.Argument()] = 0.5,
            infected: Annotated[int, typer.Argument()] = DEFAULT_INFECTED_INITIAL,
            days: Annotated[int, typer.Argument()] = DEFAULT_DAYS,
            population_count: Annotated[int, typer.Argument()] = DEFAULT_POPULATION,
            output_file: Annotated[str, typer.Argument()] = SIMULATE_FILE):
    """
    CLI command to run a single virus spread simulation.
    
    Executes one simulation trial with the specified parameters, tracks health
    status changes over time, and outputs results to a CSV file. Also prints
    a summary report to the console.
    
    Args:
        vprob: Vaccination probability (fraction of population vaccinated)
        tprob: Transmission probability (default: 0.5)
        dprob: Death probability for infected individuals (default: 0.5)
        infected: Initial number of infected individuals (default: 10)
        days: Number of days to simulate (default: 50)
        population_count: Total population size (default: 1000)
        output_file: Name of output CSV file (default: 'simulate.csv')
    """ 
    vaccinated: int = int(vprob * population_count)
    sim = Simulation(population_count, infected, vaccinated)
    df = sim.run(tprob, dprob, days)
    sim.write_values_to_file(df, output_file)
    sim.print_report(df, tprob, vaccinated, infected, days, population_count)

if __name__ == "__main__":
    app()