"""
Unit tests for the Person class.

Tests cover initialization, validation, infection mechanics,
death/survival logic, and recovery calculations.
"""

import pytest
from virus import Person, HS
import random


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
        person = Person(health_status=HS.VACCINATED, sick_days=0)
        assert person.health_status == HS.VACCINATED
        assert person.sick_days == 0
    
    def test_transmission_rate_range(self):
        """Test that transmission_rate is always between 0 and 1."""
        for _ in range(100):  # Test multiple random generations
            person = Person()
            assert 0 <= person.transmission_rate <= 1


class TestValidateProbability:
    """Test the validate_probability method."""
    
    def test_valid_probability_zero(self):
        """Test that probability 0 is valid."""
        person = Person()
        person.validate_probability(0.0, "test_prob")  # Should not raise
    
    def test_valid_probability_one(self):
        """Test that probability 1 is valid."""
        person = Person()
        person.validate_probability(1.0, "test_prob")  # Should not raise
    
    def test_valid_probability_middle(self):
        """Test that probability 0.5 is valid."""
        person = Person()
        person.validate_probability(0.5, "test_prob")  # Should not raise
    
    def test_invalid_probability_negative(self):
        """Test that negative probability raises ValueError."""
        person = Person()
        with pytest.raises(ValueError, match="must be between 0 and 1"):
            person.validate_probability(-0.1, "test_prob")
    
    def test_invalid_probability_greater_than_one(self):
        """Test that probability > 1 raises ValueError."""
        person = Person()
        with pytest.raises(ValueError, match="must be between 0 and 1"):
            person.validate_probability(1.5, "test_prob")


class TestCalculateAdjustedSickDays:
    """Test the calculate_adjusted_sick_days method."""
    
    def test_zero_sickness_factor(self):
        """Test with sickness_factor = 0 (minimum adjustment)."""
        person = Person(sick_days=10)
        adjusted = person.calculate_adjusted_sick_days(person, 0.0)
        assert adjusted == 10.0  # 10 + 3.0 * 0 = 10
    
    def test_one_sickness_factor(self):
        """Test with sickness_factor = 1 (maximum adjustment)."""
        person = Person(sick_days=10)
        adjusted = person.calculate_adjusted_sick_days(person, 1.0)
        assert adjusted == 13.0  # 10 + 3.0 * 1 = 13
    
    def test_middle_sickness_factor(self):
        """Test with sickness_factor = 0.5."""
        person = Person(sick_days=10)
        adjusted = person.calculate_adjusted_sick_days(person, 0.5)
        assert adjusted == 11.5  # 10 + 3.0 * 0.5 = 11.5
    
    def test_recovery_threshold(self):
        """Test that adjusted days can exceed MAX_SICK_DAYS for recovery check."""
        person = Person(sick_days=12)
        adjusted = person.calculate_adjusted_sick_days(person, 0.8)
        assert adjusted == 14.4  # 12 + 3.0 * 0.8 = 14.4 (> 14, triggers recovery)
    
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
        result = person.check_if_survive(dprob=0.5, rand_dprob=0.3, sickness_factor=0.5, person=person)
        assert result is True  # Dies
    
    def test_survives_when_rand_above_threshold(self):
        """Test that person survives when rand_dprob >= dprob."""
        person = Person()
        result = person.check_if_survive(dprob=0.3, rand_dprob=0.5, sickness_factor=0.5, person=person)
        assert result is False  # Survives
    
    def test_survives_when_rand_equals_threshold(self):
        """Test edge case when rand_dprob == dprob."""
        person = Person()
        result = person.check_if_survive(dprob=0.5, rand_dprob=0.5, sickness_factor=0.5, person=person)
        assert result is False  # Survives (not strictly less than)
    
    def test_zero_death_probability(self):
        """Test that zero death probability means always survives."""
        person = Person()
        result = person.check_if_survive(dprob=0.0, rand_dprob=0.0, sickness_factor=0.5, person=person)
        assert result is False  # Survives
    
    def test_one_death_probability(self):
        """Test that death probability of 1.0 with low rand_dprob means dies."""
        person = Person()
        result = person.check_if_survive(dprob=1.0, rand_dprob=0.5, sickness_factor=0.5, person=person)
        assert result is True  # Dies


class TestInfectionLogic:
    """Test infection mechanics using existing test_catch_or_not.py tests."""
    
    def test_transmission_rate_zero_always_infects(self):
        """Test that transmission_rate=0 means always gets infected (if tprob > 0)."""
        person = Person(transmission_rate=0.0)
        infected = Person(health_status=HS.INFECTED)
        
        result = person.catch_or_not(0.1, [infected])
        assert result is True  # 0 < 0.1, so infected
    
    def test_transmission_rate_one_never_infects(self):
        """Test that transmission_rate=1.0 means never gets infected (unless tprob=1)."""
        person = Person(transmission_rate=1.0)
        infected = Person(health_status=HS.INFECTED)
        
        result = person.catch_or_not(0.9, [infected])
        assert result is False  # 1.0 not < 0.9, so not infected
    
    def test_transmission_rate_one_infects_at_max_tprob(self):
        """Test edge case: transmission_rate=1.0, tprob=1.0."""
        person = Person(transmission_rate=1.0)
        infected = Person(health_status=HS.INFECTED)
        
        result = person.catch_or_not(1.0, [infected])
        assert result is False  # 1.0 not < 1.0, so not infected (edge case)


class TestRecoveryLogic:
    """Test recovery threshold calculations."""
    
    def test_just_below_recovery_threshold(self):
        """Test person with 13 sick days (just below 14)."""
        person = Person(sick_days=13)
        # With sickness_factor < 0.33, adjusted will be < 14
        adjusted = person.calculate_adjusted_sick_days(person, 0.3)
        assert adjusted == 13.9  # 13 + 3.0 * 0.3 = 13.9 (< 14, no recovery yet)
    
    def test_just_above_recovery_threshold(self):
        """Test person with 13 sick days crossing threshold."""
        person = Person(sick_days=13)
        # With sickness_factor > 0.33, adjusted will be > 14
        adjusted = person.calculate_adjusted_sick_days(person, 0.4)
        assert adjusted == 14.2  # 13 + 3.0 * 0.4 = 14.2 (> 14, triggers recovery)
    
    def test_at_max_sick_days(self):
        """Test person at exactly MAX_SICK_DAYS."""
        person = Person(sick_days=14)
        # Any positive sickness_factor pushes over threshold
        adjusted = person.calculate_adjusted_sick_days(person, 0.1)
        assert adjusted == 14.3  # 14 + 3.0 * 0.1 = 14.3 (> 14, triggers recovery)

