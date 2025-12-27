"""
Unit tests for the Simulation class.

Tests cover simulation initialization, population management,
state tracking, and simulation execution.
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
        
        # Count actual health statuses
        infected_count = sum(1 for p in sim.population if p.health_status == HS.INFECTED)
        vaccinated_count = sum(1 for p in sim.population if p.health_status == HS.VACCINATED)
        susceptible_count = sum(1 for p in sim.population if p.health_status == HS.SUSCEPTIBLE)
        
        assert infected_count == 10
        assert vaccinated_count == 20
        assert susceptible_count == 70  # 100 - 10 - 20
    
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
    
    def test_infected_have_sick_days(self):
        """Test that infected persons start with sick_days = 1."""
        sim = Simulation(population=20, infected=5, vaccinated=0)
        
        infected_people = [p for p in sim.population if p.health_status == HS.INFECTED]
        assert all(p.sick_days == 1 for p in infected_people)


class TestHealthStatusDict:
    """Test the health_status_dict method (bug fix verification)."""
    
    def test_correct_initial_counts_standard(self):
        """Test that initial status counts match actual population."""
        sim = Simulation(population=100, infected=10, vaccinated=20)
        status_dict = sim.health_status_dict()
        
        assert status_dict[HS.SUSCEPTIBLE] == 70  # 100 - 10 - 20
        assert status_dict[HS.INFECTED] == 10
        assert status_dict[HS.VACCINATED] == 20
        assert status_dict[HS.RECOVERED] == 0
        assert status_dict[HS.DEAD] == 0
        assert status_dict['Day'] == 0
    
    def test_correct_initial_counts_custom(self):
        """Test with non-default population sizes (bug fix verification)."""
        sim = Simulation(population=500, infected=50, vaccinated=100)
        status_dict = sim.health_status_dict()
        
        # This was the bug - it used DEFAULT_POPULATION (1000) instead of 500
        assert status_dict[HS.SUSCEPTIBLE] == 350  # 500 - 50 - 100
        assert status_dict[HS.INFECTED] == 50
        assert status_dict[HS.VACCINATED] == 100
    
    def test_all_vaccinated_counts(self):
        """Test status dict with 100% vaccinated."""
        sim = Simulation(population=50, infected=0, vaccinated=50)
        status_dict = sim.health_status_dict()
        
        assert status_dict[HS.SUSCEPTIBLE] == 0
        assert status_dict[HS.INFECTED] == 0
        assert status_dict[HS.VACCINATED] == 50


class TestCalculateStats:
    """Test the calculate_stats method."""
    
    def test_basic_stats_calculation(self, sample_dataframe):
        """Test that stats are calculated correctly."""
        sim = Simulation(population=10, infected=1, vaccinated=0)
        avg_infected, avg_deaths, deaths_stdv = sim.calculate_stats(sample_dataframe)
        
        # From sample_dataframe: INFECTED = [10, 15, 18, 20, 15]
        assert avg_infected == 15.6  # Mean of INFECTED column
        # DEAD = [0, 0, 0, 0, 2]
        assert avg_deaths == 0.4  # Mean of DEAD column
        assert deaths_stdv == pytest.approx(0.8944, rel=0.01)  # Std of DEAD column
    
    def test_returns_tuple(self, sample_dataframe):
        """Test that calculate_stats returns a tuple."""
        sim = Simulation(population=10, infected=1, vaccinated=0)
        result = sim.calculate_stats(sample_dataframe)
        
        assert isinstance(result, tuple)
        assert len(result) == 3


class TestGenerateStatisticsDict:
    """Test the generate_statistics_dict method."""
    
    def test_dict_structure(self):
        """Test that statistics dict has correct structure."""
        sim = Simulation(population=10, infected=1, vaccinated=0)
        stats_dict = sim.generate_statistics_dict()
        
        assert 'Trial' in stats_dict
        assert 'AVG_DEATHS' in stats_dict
        assert 'AVG_DEATH_STDV' in stats_dict
        assert 'AVG_INFECTED' in stats_dict
    
    def test_dict_initial_values(self):
        """Test that statistics dict initializes to zeros."""
        sim = Simulation(population=10, infected=1, vaccinated=0)
        stats_dict = sim.generate_statistics_dict()
        
        assert stats_dict['Trial'] == 0
        assert stats_dict['AVG_DEATHS'] == 0
        assert stats_dict['AVG_DEATH_STDV'] == 0
        assert stats_dict['AVG_INFECTED'] == 0


class TestSimulationRun:
    """Test the run method - core simulation loop."""
    
    def test_run_returns_dataframe(self):
        """Test that run() returns a DataFrame."""
        sim = Simulation(population=10, infected=2, vaccinated=2)
        df = sim.run(tprob=0.1, dprob=0.1, days=5)
        
        assert isinstance(df, pd.DataFrame)
    
    def test_dataframe_structure(self):
        """Test that DataFrame has correct columns."""
        sim = Simulation(population=10, infected=2, vaccinated=2)
        df = sim.run(tprob=0.1, dprob=0.1, days=5)
        
        expected_columns = ['Day', HS.SUSCEPTIBLE, HS.INFECTED, HS.RECOVERED, HS.DEAD, HS.VACCINATED]
        assert all(col in df.columns for col in expected_columns)
    
    def test_dataframe_row_count(self):
        """Test that DataFrame has one row per day."""
        sim = Simulation(population=10, infected=2, vaccinated=2)
        days = 7
        df = sim.run(tprob=0.1, dprob=0.1, days=days)
        
        assert len(df) == days
    
    def test_zero_transmission_no_spread(self):
        """Test that tprob=0 prevents all transmission."""
        sim = Simulation(population=20, infected=2, vaccinated=0)
        df = sim.run(tprob=0.0, dprob=0.0, days=5)
        
        # With tprob=0, no new infections should occur
        # Initial infected should stay infected (no deaths with dprob=0)
        assert df[HS.INFECTED].iloc[0] == 2
        assert df[HS.SUSCEPTIBLE].iloc[0] == 18
    
    def test_all_vaccinated_no_infections(self):
        """Test that vaccinated population doesn't get infected."""
        sim = Simulation(population=20, infected=0, vaccinated=20)
        df = sim.run(tprob=1.0, dprob=0.1, days=10)
        
        # No one should ever become infected
        assert all(df[HS.INFECTED] == 0)
        assert all(df[HS.VACCINATED] == 20)
    
    def test_conservation_of_population(self):
        """Test that total population remains constant throughout simulation."""
        sim = Simulation(population=50, infected=5, vaccinated=10)
        df = sim.run(tprob=0.3, dprob=0.1, days=20)
        
        # Sum of all statuses should always equal total population
        for _, row in df.iterrows():
            total = (row[HS.SUSCEPTIBLE] + row[HS.INFECTED] + 
                    row[HS.RECOVERED] + row[HS.DEAD] + row[HS.VACCINATED])
            assert total == 50
    
    def test_day_column_increments(self):
        """Test that Day column increments correctly."""
        sim = Simulation(population=10, infected=2, vaccinated=2)
        df = sim.run(tprob=0.1, dprob=0.1, days=5)
        
        assert list(df['Day']) == [0, 1, 2, 3, 4]


class TestUpdatePersonStatus:
    """Test the update_person_status method."""
    
    def test_routes_susceptible_person(self):
        """Test that susceptible person is routed to _handle_susceptible."""
        sim = Simulation(population=10, infected=1, vaccinated=0)
        person = Person(health_status=HS.SUSCEPTIBLE)
        status_counts = sim.health_status_dict()
        
        # Should not raise error
        sim.update_person_status(person, status_counts, tprob=0.1, dprob=0.1)
    
    def test_routes_infected_person(self):
        """Test that infected person is routed to _handle_infected."""
        sim = Simulation(population=10, infected=1, vaccinated=0)
        person = Person(health_status=HS.INFECTED, sick_days=5)
        status_counts = sim.health_status_dict()
        
        # Should not raise error
        sim.update_person_status(person, status_counts, tprob=0.1, dprob=0.1)
    
    def test_vaccinated_person_unchanged(self):
        """Test that vaccinated person's status doesn't change."""
        sim = Simulation(population=10, infected=1, vaccinated=0)
        person = Person(health_status=HS.VACCINATED)
        status_counts = sim.health_status_dict()
        
        sim.update_person_status(person, status_counts, tprob=1.0, dprob=1.0)
        assert person.health_status == HS.VACCINATED
    
    def test_recovered_person_unchanged(self):
        """Test that recovered person's status doesn't change."""
        sim = Simulation(population=10, infected=1, vaccinated=0)
        person = Person(health_status=HS.RECOVERED)
        status_counts = sim.health_status_dict()
        
        sim.update_person_status(person, status_counts, tprob=1.0, dprob=1.0)
        assert person.health_status == HS.RECOVERED


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_single_person_simulation(self):
        """Test simulation with population of 1."""
        sim = Simulation(population=1, infected=1, vaccinated=0)
        df = sim.run(tprob=0.1, dprob=0.1, days=5)
        
        assert len(df) == 5
        assert len(sim.population) == 1
    
    def test_zero_infected_stays_zero(self):
        """Test that with no initial infections and no transmission, infections stay zero."""
        sim = Simulation(population=20, infected=0, vaccinated=0)
        df = sim.run(tprob=0.5, dprob=0.1, days=10)
        
        # No initial infections means no spread possible
        assert all(df[HS.INFECTED] == 0)
    
    def test_one_day_simulation(self):
        """Test simulation with just 1 day."""
        sim = Simulation(population=10, infected=2, vaccinated=2)
        df = sim.run(tprob=0.1, dprob=0.1, days=1)
        
        assert len(df) == 1
        assert df.loc[0, 'Day'] == 0

