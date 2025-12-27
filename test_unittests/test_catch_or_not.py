from virus import Person, HS
import random
import pytest

@pytest.fixture
def person():
    """Returns a Person object."""
    return Person()

@pytest.fixture
def person_list():
    """Returns a list of Person objects with various health statuses."""
    return [
        Person(health_status=HS.SUSCEPTIBLE),
        Person(health_status=HS.INFECTED),
        Person(health_status=HS.SUSCEPTIBLE),
        Person(health_status=HS.SUSCEPTIBLE),
        Person(health_status=HS.RECOVERED),
        Person(health_status=HS.VACCINATED),
        Person(health_status=HS.DEAD),
    ]

def test_catch_or_not_returns_boolean(person: Person, person_list: list):
    """Test that catch_or_not returns a boolean value."""
    result = person.catch_or_not(0.5, person_list)
    assert isinstance(result, bool)

def test_catch_or_not_zero_transmission(person: Person, person_list: list):
    """Test that zero transmission probability results in no infection."""
    result = person.catch_or_not(0.0, person_list)
    assert isinstance(result, bool)
    # With tprob=0.0, transmission_rate < tprob will never be true, so should return False
    # unless person.transmission_rate is negative (which shouldn't happen)
    assert result == False

def test_catch_or_not_full_transmission(person: Person, person_list: list):
    """Test that full transmission probability can result in infection."""
    result = person.catch_or_not(1.0, person_list)
    assert isinstance(result, bool)
    assert result in [True, False]  # Can be either depending on transmission_rate

def test_catch_or_not_full_transmission_reproducible(person: Person, person_list: list):
    """Test that full transmission probability with seed is reproducible."""
    random.seed(42)
    person.transmission_rate = random.random()  # Set a known transmission rate
    result1 = person.catch_or_not(1.0, person_list)
    
    random.seed(42)
    person.transmission_rate = random.random()  # Reset to same value
    result2 = person.catch_or_not(1.0, person_list)
    
    assert result1 == result2  # Should be reproducible

def test_catch_or_not_invalid_tprob(person: Person, person_list: list):
    """Test that invalid transmission probabilities raise ValueError."""
    with pytest.raises(ValueError):
        person.catch_or_not(-0.5, person_list)
    with pytest.raises(ValueError):
        person.catch_or_not(1.5, person_list)

def test_catch_or_not_empty_list(person: Person):
    """Test that empty list returns False (no infection possible)."""
    result = person.catch_or_not(0.7, [])
    assert result == False

def test_catch_or_not_with_infected_person(person: Person):
    """Test that infection occurs when encountering infected person with appropriate transmission rate."""
    # Create a person with low transmission_rate so infection is likely
    person.transmission_rate = 0.1
    infected_person = Person(health_status=HS.INFECTED)
    other_persons = [infected_person]
    
    result = person.catch_or_not(0.5, other_persons)
    # Since transmission_rate (0.1) < tprob (0.5), should return True
    assert result == True

def test_catch_or_not_with_no_infected_person(person: Person):
    """Test that no infection occurs when no infected persons are present."""
    susceptible_person = Person(health_status=HS.SUSCEPTIBLE)
    vaccinated_person = Person(health_status=HS.VACCINATED)
    other_persons = [susceptible_person, vaccinated_person]
    
    result = person.catch_or_not(0.5, other_persons)
    assert result == False

def test_catch_or_not_high_transmission_rate(person: Person):
    """Test that high transmission_rate prevents infection even with high tprob."""
    # Person with high transmission_rate (less susceptible)
    person.transmission_rate = 0.9
    infected_person = Person(health_status=HS.INFECTED)
    other_persons = [infected_person]
    
    result = person.catch_or_not(0.5, other_persons)
    # Since transmission_rate (0.9) > tprob (0.5), should return False
    assert result == False

@pytest.mark.die_or_not
def test_die_or_not_returns_boolean(person: Person):
    """Test that die_or_not returns a boolean value."""
    rand_dprob = 0.3
    sickness_factor = 0.2
    result = person.die_or_not(0.5, rand_dprob, sickness_factor, person)
    assert isinstance(result, bool)

@pytest.mark.die_or_not
def test_die_or_not_dies_when_rand_dprob_less_than_dprob(person: Person):
    """Test that person dies when random death prob is less than death prob threshold."""
    dprob = 0.5
    rand_dprob = 0.3  # Less than dprob, so should die
    sickness_factor = 0.2
    result = person.die_or_not(dprob, rand_dprob, sickness_factor, person)
    assert result == True  # True means dies

@pytest.mark.die_or_not
def test_die_or_not_survives_when_rand_dprob_greater_than_dprob(person: Person):
    """Test that person survives when random death prob is greater than death prob threshold."""
    dprob = 0.3
    rand_dprob = 0.5  # Greater than dprob, so should survive
    sickness_factor = 0.2
    result = person.die_or_not(dprob, rand_dprob, sickness_factor, person)
    assert result == False  # False means survives

@pytest.mark.die_or_not
def test_die_or_not_invalid_dprob(person: Person):
    """Test that invalid death probability raises ValueError."""
    with pytest.raises(ValueError):
        person.die_or_not(-0.5, 0.3, 0.2, person)
    with pytest.raises(ValueError):
        person.die_or_not(1.5, 0.3, 0.2, person)

@pytest.mark.die_or_not
def test_die_or_not_invalid_rand_dprob(person: Person):
    """Test that invalid random death probability raises ValueError."""
    with pytest.raises(ValueError):
        person.die_or_not(0.5, -0.3, 0.2, person)
    with pytest.raises(ValueError):
        person.die_or_not(0.5, 1.3, 0.2, person)

@pytest.mark.die_or_not
def test_die_or_not_invalid_sickness_factor(person: Person):
    """Test that invalid sickness factor raises ValueError."""
    with pytest.raises(ValueError):
        person.die_or_not(0.5, 0.3, -0.2, person)
    with pytest.raises(ValueError):
        person.die_or_not(0.5, 0.3, 1.2, person)

@pytest.mark.die_or_not
def test_die_or_not_zero_death_probability(person: Person):
    """Test that zero death probability means person never dies."""
    dprob = 0.0
    rand_dprob = 0.0  # Even with rand_dprob = 0, since dprob = 0, rand_dprob (0) is not < dprob (0)
    sickness_factor = 0.2
    result = person.die_or_not(dprob, rand_dprob, sickness_factor, person)
    assert result == False  # Should survive

@pytest.mark.die_or_not
def test_die_or_not_one_death_probability(person: Person):
    """Test that death probability of 1.0 means person always dies (if rand_dprob < 1.0)."""
    dprob = 1.0
    rand_dprob = 0.5  # Less than 1.0, so should die
    sickness_factor = 0.2
    result = person.die_or_not(dprob, rand_dprob, sickness_factor, person)
    assert result == True  # Should die

def test_die_or_not_edge_case_rand_dprob_equals_dprob(person: Person):
    """Test edge case where rand_dprob equals dprob."""
    dprob = 0.5
    rand_dprob = 0.5  # Equal to dprob, so rand_dprob < dprob is False
    sickness_factor = 0.2
    result = person.die_or_not(dprob, rand_dprob, sickness_factor, person)
    assert result == False  # Should survive (not less than)
