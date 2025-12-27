"""
Unit tests for the Person class - Core functionality only.

Tests cover initialization, validation, survival logic, and recovery calculations.
Infection mechanics are tested separately in test_catch_or_not.py.
"""

import pytest
from virus import Person, HS


class TestPersonInitialization:
    """Test Person object creation and default values."""
    
    def test_default_initialization(self):
        """Test that Person initializes with correct defaults."""
        person = Person()
        assert person.health_status == HS.SUSCEPTIBLE
        assert person.sick_days == 0
        assert person.MAX_SICK_DAYS == 14
        assert 0 <= person.transmission_rate <= 1
    
    def test_infected_initialization(self):
        """Test creating an infected person."""
        person = Person(health_status=HS.INFECTED, sick_days=5)
        assert person.health_status == HS.INFECTED
        assert person.sick_days == 5
    
    def test_vaccinated_initialization(self):
        """Test creating a vaccinated person."""
        person = Person(health_status=HS.VACCINATED)
        assert person.health_status == HS.VACCINATED
    
    def test_transmission_rate_range(self):
        """Test that transmission_rate is always between 0 and 1."""
        for _ in range(20):  # Test multiple random generations
            person = Person()
            assert 0 <= person.transmission_rate <= 1


class TestValidateProbability:
    """Test the validate_probability method."""
    
    def test_valid_probability_extremes(self):
        """Test that probabilities 0 and 1 are valid."""
        person = Person()
        person.validate_probability(0.0, "test")  # Should not raise
        person.validate_probability(1.0, "test")  # Should not raise
    
    def test_valid_probability_middle(self):
        """Test that probability 0.5 is valid."""
        person = Person()
        person.validate_probability(0.5, "test")  # Should not raise
    
    def test_invalid_probability_negative(self):
        """Test that negative probability raises ValueError."""
        person = Person()
        with pytest.raises(ValueError, match="must be between 0 and 1"):
            person.validate_probability(-0.1, "test")
    
    def test_invalid_probability_greater_than_one(self):
        """Test that probability > 1 raises ValueError."""
        person = Person()
        with pytest.raises(ValueError, match="must be between 0 and 1"):
            person.validate_probability(1.5, "test")


class TestCalculateAdjustedSickDays:
    """Test the calculate_adjusted_sick_days method."""
    
    def test_zero_sickness_factor(self):
        """Test with sickness_factor = 0 (minimum adjustment)."""
        person = Person(sick_days=10)
        adjusted = person.calculate_adjusted_sick_days(person, 0.0)
        assert adjusted == 10.0
    
    def test_one_sickness_factor(self):
        """Test with sickness_factor = 1 (maximum adjustment)."""
        person = Person(sick_days=10)
        adjusted = person.calculate_adjusted_sick_days(person, 1.0)
        assert adjusted == 13.0  # 10 + 3.0 * 1
    
    def test_recovery_threshold_crossing(self):
        """Test that adjusted days can exceed MAX_SICK_DAYS for recovery check."""
        person = Person(sick_days=13)
        adjusted = person.calculate_adjusted_sick_days(person, 0.5)
        assert adjusted == 14.5  # 13 + 3.0 * 0.5 = 14.5 (> 14, triggers recovery)
    
    def test_invalid_sickness_factor_negative(self):
        """Test that negative sickness_factor raises ValueError."""
        person = Person(sick_days=10)
        with pytest.raises(ValueError, match="must be between 0 and 1"):
            person.calculate_adjusted_sick_days(person, -0.1)
    
    def test_invalid_sickness_factor_too_large(self):
        """Test that sickness_factor > 1 raises ValueError."""
        person = Person(sick_days=10)
        with pytest.raises(ValueError, match="must be between 0 and 1"):
            person.calculate_adjusted_sick_days(person, 1.2)


class TestCheckIfSurvive:
    """Test the check_if_survive method."""
    
    def test_dies_when_rand_below_threshold(self):
        """Test that person dies when rand_dprob < dprob."""
        person = Person()
        result = person.check_if_survive(dprob=0.5, rand_dprob=0.3, 
                                        sickness_factor=0.5, person=person)
        assert result is True  # Dies
    
    def test_survives_when_rand_above_threshold(self):
        """Test that person survives when rand_dprob >= dprob."""
        person = Person()
        result = person.check_if_survive(dprob=0.3, rand_dprob=0.5,
                                        sickness_factor=0.5, person=person)
        assert result is False  # Survives
    
    def test_edge_case_equal_values(self):
        """Test edge case when rand_dprob == dprob (should survive)."""
        person = Person()
        result = person.check_if_survive(dprob=0.5, rand_dprob=0.5,
                                        sickness_factor=0.5, person=person)
        assert result is False  # Survives (not strictly less than)
