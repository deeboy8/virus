"""
Shared pytest fixtures for virus simulation tests.

This module provides reusable test fixtures to avoid duplication
and ensure consistent test data across test files.
"""

import pytest
from virus import Person, HS, Simulation
import pandas as pd


# Person fixtures
@pytest.fixture
def susceptible_person():
    """Return a susceptible person with fixed transmission rate for predictable testing."""
    person = Person(health_status=HS.SUSCEPTIBLE, transmission_rate=0.5)
    return person


@pytest.fixture
def infected_person():
    """Return an infected person with 1 sick day."""
    return Person(health_status=HS.INFECTED, sick_days=1, transmission_rate=0.5)


@pytest.fixture
def vaccinated_person():
    """Return a vaccinated person."""
    return Person(health_status=HS.VACCINATED, sick_days=0, transmission_rate=0.5)


@pytest.fixture
def recovered_person():
    """Return a recovered person."""
    return Person(health_status=HS.RECOVERED, sick_days=0, transmission_rate=0.5)


@pytest.fixture
def dead_person():
    """Return a dead person."""
    return Person(health_status=HS.DEAD, sick_days=0, transmission_rate=0.5)


# Simulation fixtures
@pytest.fixture
def simple_simulation():
    """Return a small 10-person simulation for fast testing."""
    return Simulation(population=10, infected=2, vaccinated=2)


@pytest.fixture
def all_vaccinated_simulation():
    """Return a simulation where everyone is vaccinated."""
    return Simulation(population=10, infected=0, vaccinated=10)


@pytest.fixture
def all_infected_simulation():
    """Return a simulation where everyone is infected."""
    return Simulation(population=10, infected=10, vaccinated=0)


@pytest.fixture
def sample_dataframe():
    """Return a sample simulation result DataFrame for testing stats."""
    data = {
        'Day': [0, 1, 2, 3, 4],
        HS.SUSCEPTIBLE: [90, 85, 80, 75, 70],
        HS.INFECTED: [10, 15, 18, 20, 15],
        HS.RECOVERED: [0, 0, 2, 5, 13],
        HS.DEAD: [0, 0, 0, 0, 2],
        HS.VACCINATED: [0, 0, 0, 0, 0]
    }
    return pd.DataFrame(data)

