# Testing Documentation

## Test Philosophy

This project demonstrates professional testing practices focused on:

1. **Strategic Coverage** - Test high-value business logic comprehensively
2. **Pragmatic Exclusions** - Document what's intentionally not tested and why
3. **Clear Communication** - Make testing decisions transparent
4. **Maintainability** - Write tests that are easy to understand and extend

## What We Test

### Core Business Logic (100% Coverage Goal)

We comprehensively test the **Person** and **Simulation** classes because they contain:
- Critical state transitions (susceptible → infected → recovered/dead)
- Complex probability calculations
- Population health tracking logic
- The "rules" of the virus simulation

**Why:** These are the core algorithms that determine simulation accuracy. Bugs here would invalidate all results.

### Specific Test Coverage

#### Person Class (`test_person.py`)

**Initialization Tests**
- Default values are correct
- Different health statuses initialize properly
- Transmission rates stay within valid bounds [0, 1]

**Validation Tests**
- `validate_probability()` catches invalid inputs (< 0 or > 1)
- Edge cases (exactly 0, exactly 1) are accepted

**Calculation Tests**
- `calculate_adjusted_sick_days()` math is correct
- Recovery threshold calculations work properly
- Boundary conditions handled correctly

**Survival Logic Tests**
- `check_if_survive()` / `die_or_not()` implement correct probability logic
- Random number comparisons work as expected
- Edge case: equal probabilities handled correctly

#### Simulation Class (`test_simulation.py`)

**Initialization Tests**
- Population distribution matches parameters
- Status counts are accurate (verifies bug fix)
- Edge cases: all vaccinated, all infected, single person

**State Management Tests**
- `health_status_dict()` tracks counts correctly
- Initial values set properly
- Status updates persist correctly

**Integration Tests**
- `run()` method executes full simulation
- DataFrame structure is correct
- Conservation law: population stays constant
- Zero transmission prevents spread (validation test)
- All vaccinated population has no infections

**Private Method Testing**
- `_handle_susceptible()` tested indirectly through `run()`
- `_handle_infected()` tested indirectly through `run()`
- We test behavior, not implementation details

#### Infection Mechanics (`test_catch_or_not.py`)

**Transmission Tests**
- `catch_or_not()` respects transmission probability
- Works correctly with infected/non-infected populations
- Edge cases: zero transmission, full transmission

**Death Tests**
- `die_or_not()` implements correct survival logic
- Probability validation works
- Edge cases handled properly

## What We Don't Test (And Why)

### CLI Commands (`test_cli.py` - Stubs Only)

**Not Tested:**
- `simulate` command
- `analyze` command
- `visualize` command

**Reasoning:**
- Requires mocking `typer.CliRunner`
- Requires temporary file system fixtures
- Time investment high, value moderate for portfolio
- Commands are thin wrappers around tested logic

**Alternative Verification:**
- Manual testing (see README examples)
- Integration testing would be next step in production

**Future Implementation:**
```python
from typer.testing import CliRunner
runner = CliRunner()
result = runner.invoke(app, ["simulate", ...])
assert result.exit_code == 0
```

### Visualization Methods (`test_visualization.py` - Stubs Only)

**Not Tested:**
- `generate_histogram()`
- `plot()`

**Reasoning:**
- Requires mocking `matplotlib.pyplot`
- Visual output difficult to assert programmatically
- Would need image comparison testing (`pytest-mpl`)
- Time investment very high for portfolio

**Alternative Verification:**
- Manual visual inspection with sample data
- Screenshots in documentation

**Future Implementation:**
```python
from unittest.mock import patch
with patch('matplotlib.pyplot.subplots') as mock_plot:
    viz.generate_histogram(df)
    mock_plot.assert_called_once()
```

### Property Setters and Edge Cases

Some property setters and edge case branches aren't fully covered because:
- They're defensive programming (prevent future bugs)
- Hard to trigger in normal usage
- Would require contrived test scenarios

## Test Organization

### Fixtures (`conftest.py`)

We use pytest fixtures to avoid code duplication:

```python
@pytest.fixture
def infected_person():
    """Reusable infected person for multiple tests."""
    return Person(health_status=HS.INFECTED, sick_days=5)
```

**Benefits:**
- DRY (Don't Repeat Yourself)
- Consistent test data
- Easy to modify for all tests at once

### Test Class Organization

Tests are grouped into classes by functionality:

```python
class TestPersonInitialization:
    """All tests related to Person creation."""
    
class TestValidateProbability:
    """All tests for probability validation."""
```

**Benefits:**
- Clear organization
- Easy to find related tests
- Can use class-level fixtures if needed

## How to Add New Tests

### Adding a Test for Existing Functionality

1. **Identify the test file** - Find the appropriate test file (`test_person.py`, etc.)
2. **Find the test class** - Locate the relevant test class
3. **Write the test** - Follow the Arrange-Act-Assert pattern:

```python
def test_new_feature(self):
    """Test description: what does this verify?"""
    # Arrange - Set up test data
    person = Person(health_status=HS.INFECTED)
    
    # Act - Execute the code being tested
    result = person.some_method()
    
    # Assert - Verify the result
    assert result == expected_value
```

### Adding Tests for New Features

1. **Create new test file** if needed: `test_newfeature.py`
2. **Add fixtures** to `conftest.py` if they'll be reused
3. **Write test classes** grouping related tests
4. **Run tests**: `pytest test_unittests/test_newfeature.py -v`

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test<FeatureName>`
- Test methods: `test_<what_it_tests>`

**Good names:**
- `test_validate_probability_rejects_negative_values`
- `test_simulation_conserves_population_count`
- `test_infected_person_can_die_or_recover`

**Bad names:**
- `test_1`
- `test_function`
- `test_stuff`

## Running Tests Effectively

### Quick Feedback Loop

```bash
# Run just one test
pytest test_unittests/test_person.py::TestPersonInitialization::test_default_initialization -v

# Run one test class
pytest test_unittests/test_person.py::TestPersonInitialization -v

# Run one file
pytest test_unittests/test_person.py -v
```

### Coverage Analysis

```bash
# Generate coverage report
pytest --cov=virus --cov-report=html

# View in browser
open htmlcov/index.html

# See missing lines in terminal
pytest --cov=virus --cov-report=term-missing
```

### Debugging Failed Tests

```bash
# Show full output (disable capture)
pytest -s

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb
```

## Test Design Principles

### 1. Tests Should Be Independent

❌ **Bad:**
```python
def test_first():
    global counter
    counter = 1

def test_second():
    assert counter == 1  # Depends on test_first
```

✅ **Good:**
```python
def test_first():
    counter = 1
    assert counter == 1

def test_second(counter_fixture):
    assert counter_fixture == 1
```

### 2. Tests Should Be Readable

❌ **Bad:**
```python
def test_x():
    assert Person(HS.INFECTED, 5).die_or_not(0.5, 0.3, 0.2, Person()) == True
```

✅ **Good:**
```python
def test_infected_person_dies_when_random_below_threshold():
    """Test that person dies when rand_dprob < dprob."""
    infected_person = Person(health_status=HS.INFECTED, sick_days=5)
    dprob = 0.5
    rand_dprob = 0.3  # Below threshold
    
    dies = infected_person.die_or_not(dprob, rand_dprob, 0.2, infected_person)
    
    assert dies is True
```

### 3. Test One Thing at a Time

❌ **Bad:**
```python
def test_everything():
    # Tests initialization AND calculation AND validation
    person = Person()
    assert person.health_status == HS.SUSCEPTIBLE
    assert person.calculate_adjusted_sick_days(person, 0.5) > 0
    person.validate_probability(0.5, "test")
```

✅ **Good:**
```python
def test_default_initialization():
    person = Person()
    assert person.health_status == HS.SUSCEPTIBLE

def test_calculate_adjusted_sick_days_with_factor():
    person = Person(sick_days=10)
    adjusted = person.calculate_adjusted_sick_days(person, 0.5)
    assert adjusted == 11.5

def test_validate_probability_accepts_valid_input():
    person = Person()
    person.validate_probability(0.5, "test")  # Should not raise
```

## Edge Cases to Consider

When writing tests, always consider:

1. **Boundary values**: 0, 1, max values
2. **Empty inputs**: Empty lists, None values
3. **Invalid inputs**: Negative numbers, out-of-range values
4. **Extreme cases**: Very large/small populations, single person
5. **State transitions**: How do objects move between states?

## Coverage Goals

- **Core business logic**: Aim for 90-100%
- **Overall project**: 60-80% is realistic with CLI/visualization
- **New features**: Aim for 80%+ coverage before merging

Remember: **Coverage is a tool, not a goal**. 100% coverage doesn't guarantee bug-free code, but thoughtful testing does.

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## Questions?

For questions about testing approach or to suggest improvements, refer to:
- This document
- Test stubs in `test_cli.py` and `test_visualization.py`
- `COVERAGE_ANALYSIS.md` for coverage details

