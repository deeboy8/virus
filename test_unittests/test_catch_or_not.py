from simulate import Person, HealthStatus
import random
import pytest

@pytest.fixture
# returns a Person object
def person():
    return Person()

@pytest.fixture
def status_list():
    return [0, 1, 4, 0, -1, -2, -3] # mix of different HealthStatuses

def test_catch_or_not_returns_integer(person: Person, status_list: list):
    result = person.catch_or_not(0.5, status_list)
    print(result)
    assert isinstance(result, int) # compares types

def test_catch_or_not_zero_transmission(person: Person, status_list: list):
    result = person.catch_or_not(0.0, status_list)
    assert result == 0

def test_catch_or_not_full_transmission(person: Person, status_list: list):
    result = person.catch_or_not(1.0, status_list)
    assert result in [0, 1]

def test_catch_or_not_full_transmission_reproducible(person: Person, status_list: list):
    random.seed(42)
    result = person.catch_or_not(1.0, status_list)
    assert result in [0, 1]

def test_catch_or_not_invalid_tprob(person: Person, status_list: list):
    with pytest.raises(ValueError):
        person.catch_or_not(-0.5, status_list)
    with pytest.raises(ValueError):
        person.catch_or_not(1.5, status_list)

def test_catch_or_not_empty_status_list(person: Person):
    with pytest.raises(ValueError):
        result = person.catch_or_not(0.7, [])

def test_catch_or_not_two(person: Person, status_list: list):
    # arrange- person and status_list arranged/supplied by pytest fixture
    tprob: float = 0.1 
    nexposure: int = 10
    other_person: int = 1
    other_person_tprob: float = 0.2
    expected = 0
    #act
    actual = person.catch_or_not_two(tprob, status_list, nexposure, other_person, other_person_tprob)
    #assert-pseudo then correction
    #assert (actual, operator, expected)
    assert actual == expected
    
def test_catch_or_not_two_lower_other_person_tprob(person: Person):
    # arrange- person and status_list arranged/supplied by pytest fixture
    tprob: float = 0.2 
    status_list: list = [2, 2, 0, -2, 3]
    nexposure: int = 0
    other_person: int = 0
    other_person_tprob: float = 0.1
    expected = 1
    #act
    actual = person.catch_or_not_two(tprob, status_list, nexposure, other_person, other_person_tprob)
    #assert-pseudo then correction
    #assert (actual, operator, expected)
    assert actual != expected

def test_catch_or_not_two_other_person_tprob_higher(person: Person):
    # arrange- person and status_list arranged/supplied by pytest fixture
    tprob: float = 0.3 
    status_list: list = [0, -1, 0, -2, 3]
    nexposure: int = 2
    other_person: int = 2
    other_person_tprob: float = 0.4
    expected = 0
    #act
    actual = person.catch_or_not_two(tprob, status_list, nexposure, other_person, other_person_tprob)
    #assert-pseudo then correction
    #assert (actual, operator, expected)
    assert actual == expected

@pytest.mark.die_or_not
def test_die_or_not_returns_valid_status(person, status_list):
    result = person.die_or_not(0.5, 7, 1, status_list, 0.3, 1.2)
    assert isinstance(result, HealthStatus)
    assert result in [HealthStatus.DEAD, HealthStatus.RECOVERED, HealthStatus.INFECTED]

@pytest.mark.die_or_not
def test_die_or_not_zero_full_death_prob(person, status_list):
    result = person.die_or_not(1.0, 7, 1, status_list, 0.3, 1.2)
    expected = HealthStatus.DEAD
    assert result == expected  # Should never die with 0 probability

@pytest.mark.die_or_not
def test_die_or_not_invalid_dprob_probabilities(person, status_list):
    with pytest.raises(ValueError):
        person.die_or_not(-0.5, person.MAX_SICK_DAYS, 1, status_list, 0.3, 1.2)
    with pytest.raises(ValueError):
        person.die_or_not(1.5, person.MAX_SICK_DAYS, 1, status_list, 0.3, 1.2)
    with pytest.raises(ValueError):
        person.die_or_not(0.5, person.MAX_SICK_DAYS, 1, status_list, -0.3, 1.2)
    with pytest.raises(ValueError):
        person.die_or_not(0.5, person.MAX_SICK_DAYS, 1, status_list, 1.3, 1.2)

@pytest.mark.die_or_not
def test_die_or_not_max_sick_days_with_rand_dprob_greater_dprob(person, status_list): # [0, 1, 4, 0, -1, -2, -3]
    result = person.die_or_not(0.1, Person.MAX_SICK_DAYS, 1, status_list, 0.3, 0.02)
    assert result not in [HealthStatus.RECOVERED, HealthStatus.DEAD, HealthStatus.SUSCEPTIBLE, HealthStatus.VACCINATED] # Should either die or recover at max days

@pytest.mark.die_or_not
def test_die_or_not_max_sick_days_with_rand_dprob_below_dprob(person, status_list): # [0, 1, 4, 0, -1, -2, -3]
    result = person.die_or_not(0.3, Person.MAX_SICK_DAYS, 1, status_list, 0.1, 0.02)
    assert result == HealthStatus.DEAD

@pytest.mark.die_or_not
def test_die_or_not(person, status_list):
    result = person.die_or_not(0.1, 5, 4, [0, -1, 0, -2, 3], 0.2, 0.03)
    expected = HealthStatus.INFECTED
    assert result == 4

@pytest.mark.die_or_not
def test_die_or_not_empty_list(person, status_list):
    with pytest.raises(IndexError):
        result = person.die_or_not(0.1, 5, 4, [], 0.2, 0.03)
   
def test_die_or_not_random1(person: Person, status_list):  
    result = person.die_or_not(0.1, 14, 4, [0, -1, 0, -2, 3], 0.2, 0.03)
    assert result == 4

def test_die_or_not_random2(person, status_list):
    result = person.die_or_not(0.2, 14, 3, [2, 2, 0, -2, 3], 0.7, 0.01)
    assert result == -1

def test_die_or_not_random3(person, status_list):
    result = person.die_or_not(0.2, 14, 3, [2, 2, 0, -2, 3], 0.7, 0.01)
    assert result == -1 # negative 1 is the actual status value NOT healthstatus.recovered

def test_die_or_not_random4(person, status_list):
    result = person.die_or_not(0.3, 14, 2, [0, -1, 0, -2, 3], 0.22, 0.04)
    assert result == -3

def test_die_or_not_random5(person, status_list):
    result = person.die_or_not(0.4, 14, 1, [0, -1, 0, -2, 3], 0.43, 0.05)
    assert result == 0
