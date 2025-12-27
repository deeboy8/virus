"""
Unit tests for the Simulation class - Core integration tests.

Tests cover initialization, state management, and simulation execution.
Private methods (_handle_susceptible, _handle_infected) are tested indirectly through run().
"""

import pytest
from virus import Simulation, Person, HS
import pandas as pd


class TestSimulationInitialization:
    """Test Simulation object creation and population setup."""
    
    def test_basic_initialization(self):
        """Test that Simulation initializes with correct parameters."""
        sim = Simulation(population=100, infected=10, vaccinated=20)
        assert sim.vaccinated == 20
        assert sim._infected == 10
        assert sim._total_population == 100
        assert len(sim.population) == 100
    
    def test_population_distribution(self):
        """Test that population has correct distribution of health statuses."""
        sim = Simulation(population=100, infected=10, vaccinated=20)
        
        infected_count = sum(1 for p in sim.population if p.health_status == HS.INFECTED)
        vaccinated_count = sum(1 for p in sim.population if p.health_status == HS.VACCINATED)
        susceptible_count = sum(1 for p in sim.population if p.health_status == HS.SUSCEPTIBLE)
        
        assert infected_count == 10
        assert vaccinated_count == 20
        assert susceptible_count == 70
    
    def test_all_vaccinated_population(self):
        """Test simulation with 100% vaccination."""
        sim = Simulation(population=50, infected=0, vaccinated=50)
        vaccinated_count = sum(1 for p in sim.population if p.health_status == HS.VACCINATED)
        assert vaccinated_count == 50
    
    def test_all_infected_population(self):
        """Test simulation with 100% infected."""
        sim = Simulation(population=30, infected=30, vaccinated=0)
        infected_count = sum(1 for p in sim.population if p.health_status == HS.INFECTED)
        assert infected_count == 30
    
    def test_small_population(self):
        """Test simulation with very small population."""
        sim = Simulation(population=5, infected=2, vaccinated=1)
        assert len(sim.population) == 5


class TestHealthStatusDict:
    """Test health_status_dict method - verifies bug fix."""
    
    def test_correct_counts_with_custom_population(self):
        """Test that bug fix works: uses actual population, not constants."""
        sim = Simulation(population=500, infected=50, vaccinated=100)
        status_dict = sim.health_status_dict()
        
        # Bug was using DEFAULT_POPULATION (1000) instead of actual 500
        assert status_dict[HS.SUSCEPTIBLE] == 350  # 500 - 50 - 100
        assert status_dict[HS.INFECTED] == 50
        assert status_dict[HS.VACCINATED] == 100
    
    def test_initial_recovered_and_dead_are_zero(self):
        """Test that simulation starts with zero recovered and dead."""
        sim = Simulation(population=100, infected=10, vaccinated=20)
        status_dict = sim.health_status_dict()
        
        assert status_dict[HS.RECOVERED] == 0
        assert status_dict[HS.DEAD] == 0
        assert status_dict['Day'] == 0
    
    def test_all_vaccinated_counts(self):
        """Test status dict with 100% vaccinated population."""
        sim = Simulation(population=50, infected=0, vaccinated=50)
        status_dict = sim.health_status_dict()
        
        assert status_dict[HS.SUSCEPTIBLE] == 0
        assert status_dict[HS.INFECTED] == 0
        assert status_dict[HS.VACCINATED] == 50


class TestCalculateStats:
    """Test the calculate_stats method."""
    
    def test_returns_tuple_of_three(self, sample_dataframe):
        """Test that calculate_stats returns a 3-element tuple."""
        sim = Simulation(population=10, infected=1, vaccinated=0)
        result = sim.calculate_stats(sample_dataframe)
        
        assert isinstance(result, tuple)
        assert len(result) == 3
    
    def test_calculates_correct_means(self, sample_dataframe):
        """Test that statistics are calculated correctly."""
        sim = Simulation(population=10, infected=1, vaccinated=0)
        avg_infected, avg_deaths, deaths_stdv = sim.calculate_stats(sample_dataframe)
        
        # sample_dataframe has INFECTED = [10, 15, 18, 20, 15]
        assert avg_infected == 15.6
        # sample_dataframe has DEAD = [0, 0, 0, 0, 2]
        assert avg_deaths == 0.4


class TestSimulationRun:
    """Test the run method - core simulation loop (tests private methods indirectly)."""
    
    def test_returns_dataframe_with_correct_structure(self):
        """Test that run() returns DataFrame with expected columns."""
        sim = Simulation(population=10, infected=2, vaccinated=2)
        df = sim.run(tprob=0.1, dprob=0.1, days=5)
        
        assert isinstance(df, pd.DataFrame)
        expected_cols = ['Day', HS.SUSCEPTIBLE, HS.INFECTED, HS.RECOVERED, HS.DEAD, HS.VACCINATED]
        assert all(col in df.columns for col in expected_cols)
    
    def test_dataframe_has_correct_number_of_rows(self):
        """Test that DataFrame has one row per simulation day."""
        sim = Simulation(population=10, infected=2, vaccinated=2)
        days = 7
        df = sim.run(tprob=0.1, dprob=0.1, days=days)
        assert len(df) == days
    
    def test_day_column_increments_correctly(self):
        """Test that Day column increments from 0."""
        sim = Simulation(population=10, infected=2, vaccinated=2)
        df = sim.run(tprob=0.1, dprob=0.1, days=5)
        assert list(df['Day']) == [0, 1, 2, 3, 4]
    
    def test_zero_transmission_prevents_spread(self):
        """Test that tprob=0 prevents all new infections (tests _handle_susceptible indirectly)."""
        sim = Simulation(population=20, infected=2, vaccinated=0)
        df = sim.run(tprob=0.0, dprob=0.0, days=5)
        
        # Susceptible count should never decrease with tprob=0
        initial_susceptible = df[HS.SUSCEPTIBLE].iloc[0]
        assert all(df[HS.SUSCEPTIBLE] == initial_susceptible)
    
    def test_all_vaccinated_no_infections_possible(self):
        """Test that vaccinated population never gets infected."""
        sim = Simulation(population=20, infected=0, vaccinated=20)
        df = sim.run(tprob=1.0, dprob=0.1, days=10)
        
        # No infections should ever occur
        assert all(df[HS.INFECTED] == 0)
        assert all(df[HS.VACCINATED] == 20)
    
    def test_conservation_of_population(self):
        """Test that total population remains constant (tests all state transitions)."""
        sim = Simulation(population=50, infected=5, vaccinated=10)
        df = sim.run(tprob=0.3, dprob=0.1, days=15)
        
        # Sum of all statuses should always equal total population
        for _, row in df.iterrows():
            total = (row[HS.SUSCEPTIBLE] + row[HS.INFECTED] + 
                    row[HS.RECOVERED] + row[HS.DEAD] + row[HS.VACCINATED])
            assert total == 50
    
    def test_zero_infected_stays_zero(self):
        """Test that with no initial infections, no spread occurs."""
        sim = Simulation(population=20, infected=0, vaccinated=0)
        df = sim.run(tprob=0.5, dprob=0.1, days=10)
        
        # No infections possible without initial infected
        assert all(df[HS.INFECTED] == 0)
    
    def test_single_person_simulation(self):
        """Test edge case: simulation with population of 1."""
        sim = Simulation(population=1, infected=1, vaccinated=0)
        df = sim.run(tprob=0.1, dprob=0.1, days=5)
        
        assert len(df) == 5
        assert len(sim.population) == 1
    
    def test_one_day_simulation(self):
        """Test edge case: simulation with just 1 day."""
        sim = Simulation(population=10, infected=2, vaccinated=2)
        df = sim.run(tprob=0.1, dprob=0.1, days=1)
        
        assert len(df) == 1
        assert df.loc[0, 'Day'] == 0
    
    def test_infected_can_die_or_recover(self):
        """Test that infected population changes over time (tests _handle_infected indirectly)."""
        sim = Simulation(population=20, infected=20, vaccinated=0)
        df = sim.run(tprob=0.0, dprob=0.2, days=20)
        
        # With all infected, some should die or recover over 20 days
        final_infected = df[HS.INFECTED].iloc[-1]
        final_dead = df[HS.DEAD].iloc[-1]
        final_recovered = df[HS.RECOVERED].iloc[-1]
        
        # At least some state change should occur
        assert (final_dead + final_recovered) > 0
