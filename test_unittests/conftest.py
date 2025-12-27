"""
Shared pytest fixtures for virus simulation tests.

Provides reusable Person objects, Simulation objects, and test data
to avoid duplication across test files.
"""

import pytest
import pandas as pd
from virus import Person, HS, Simulation


# ============================================================================
# Person Fixtures
# ============================================================================

@pytest.fixture
def susceptible_person():
    """Create a susceptible person for testing."""
    return Person(health_status=HS.SUSCEPTIBLE, sick_days=0)


@pytest.fixture
def infected_person():
    """Create an infected person for testing."""
    return Person(health_status=HS.INFECTED, sick_days=5)


@pytest.fixture
def vaccinated_person():
    """Create a vaccinated person for testing."""
    return Person(health_status=HS.VACCINATED, sick_days=0)


@pytest.fixture
def recovered_person():
    """Create a recovered person for testing."""
    return Person(health_status=HS.RECOVERED, sick_days=0)


@pytest.fixture
def dead_person():
    """Create a dead person for testing."""
    return Person(health_status=HS.DEAD, sick_days=10)


@pytest.fixture
def person_list():
    """Create a list of persons with various health statuses."""
    return [
        Person(health_status=HS.SUSCEPTIBLE),
        Person(health_status=HS.INFECTED, sick_days=3),
        Person(health_status=HS.VACCINATED),
        Person(health_status=HS.RECOVERED),
        Person(health_status=HS.DEAD, sick_days=14),
    ]


# ============================================================================
# Simulation Fixtures
# ============================================================================

@pytest.fixture
def simple_simulation():
    """Create a small simulation for fast testing."""
    return Simulation(population=10, infected=2, vaccinated=2)


@pytest.fixture
def all_vaccinated_simulation():
    """Create a simulation where everyone is vaccinated."""
    return Simulation(population=20, infected=0, vaccinated=20)


@pytest.fixture
def all_infected_simulation():
    """Create a simulation where everyone is infected."""
    return Simulation(population=15, infected=15, vaccinated=0)


# ============================================================================
# Data Fixtures
# ============================================================================

@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame mimicking simulation output."""
    data = {
        'Day': [0, 1, 2, 3, 4],
        HS.SUSCEPTIBLE: [80, 70, 60, 55, 50],
        HS.INFECTED: [10, 15, 18, 20, 15],
        HS.RECOVERED: [0, 5, 10, 12, 18],
        HS.DEAD: [0, 0, 0, 0, 2],
        HS.VACCINATED: [10, 10, 12, 13, 15],
    }
    return pd.DataFrame(data)
