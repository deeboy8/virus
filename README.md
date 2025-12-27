# Virus Simulation in Python

## Overview

This Python project simulates the spread of a virus on a population. It explores the impact of different factors, such as vaccination rates and transmission probability on the progression of a viral outbreak. This simulation provides insights into how preventive measures, such as masking and social distancing can mitigate the impact of the virus.

## Project Structure

The project consists of three parts with each acting as a command to be passed in the Terminal to execute it's specific task:

1. **simulate**: Simulates the virus progression over a variable specified number of days. It tracks the health status of the population, categorizing individuals as either susceptible, infected, recovered, vaccinated, or dead. Via command line options, you can explore the effects of different vaccination rates and transmission probabilities on the virus spread.

2. **analyze**: Runs multiple simulations/trials (e.g., 1,000) to calculate the average number of deaths per simulation and the standard deviation. This functionality helps to analyze the impact of random variations and to better understand overall trends.

3. **visualize**: Will generate a histogram to visualize the results from running the analyze command for nsimulations. This provides a graphical representation of how varying factors influence the outcome of the virus spread.

## Key Features

- **Random Interactions**: The program simulates random interactions between people. Susceptible individuals can contract the virus from infected individuals based on a specified transmission probability (`tprob`), while infected individuals either recover, die, or continue being sick.
  
- **Vaccination**: The program assumes that vaccinated people are fully protected from infection (a simplification for this simulation).

- **Transmission Probability**: The user can set the probability (`tprob`) of catching the virus from an infected individual to model different scenarios (e.g., lower probabilities due to social distancing or mask-wearing).

- **Multiple Trials**: The program can run the simulation multiple times, using the analyze command, under the same parameters to analyze the variance in results, providing average statistics and standard deviations for deeper insights.

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd virus
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation by running tests:
```bash
pytest
```

Expected output: `54 passed, 10 skipped`

## Quick Start

Get up and running with a complete workflow:

```bash
# 1. Run a simple 30-day simulation
python3 virus.py simulate 0.02 0.1 0.3 5 30 500 my_simulation.csv

# 2. Run multiple trials for statistical analysis
python3 virus.py analyze 100 0.02 0.1 0.3 30 5 500 my_analysis.csv

# 3. Visualize the results
python3 virus.py visualize my_simulation.csv
```

This simulates a virus with:
- 2% transmission probability per encounter
- 10% death probability for infected individuals
- 30% of population vaccinated
- 5 initially infected people
- 500 total population
- 30 days of simulation

## Code Architecture

### Core Classes

**`HS` (Enum)** - Health Status Constants
- `SUSCEPTIBLE` (0): Not infected, can catch the virus
- `INFECTED` (1): Currently infected
- `RECOVERED` (2): Previously infected, now immune
- `DEAD` (3): Deceased from infection
- `VACCINATED` (4): Vaccinated, immune to infection

**`Person` (Dataclass)** - Individual in the Population
- Attributes: `health_status`, `sick_days`, `transmission_rate`, `MAX_SICK_DAYS`
- Key methods:
  - `catch_or_not()`: Determines if susceptible person gets infected based on exposure
  - `die_or_not()`: Determines if infected person dies or continues being sick
  - `validate_probability()`: Ensures probability values are between 0 and 1
  - `calculate_adjusted_sick_days()`: Calculates recovery likelihood

**`Simulation`** - Population Manager and Simulation Engine
- Manages a list of Person objects
- Tracks daily health status counts
- Key methods:
  - `run()`: Main simulation loop, returns DataFrame with daily statistics
  - `update_person_status()`: Updates each person's status daily
  - `health_status_dict()`: Returns current population status counts
  - `calculate_stats()`: Computes averages and standard deviations

**`Visualize`** - Results Visualization
- Generates histograms and time-series plots
- Reads CSV output from simulations
- Creates visual representations of virus spread

### How the Simulation Works

The simulation runs day-by-day, updating each person's status:

**Each day:**

1. **For SUSCEPTIBLE persons:**
   - Check if they encounter any infected persons in the population
   - Calculate infection probability: `transmission_rate < tprob`
   - If infected: change status to `INFECTED`, set `sick_days = 1`

2. **For INFECTED persons:**
   - Increment `sick_days` counter
   - **Death check**: If `random() < dprob`, person dies → status = `DEAD`
   - **Recovery check**: If `adjusted_sick_days > MAX_SICK_DAYS` (14 days), person recovers → status = `RECOVERED`
   - Otherwise: remain `INFECTED`

3. **VACCINATED, RECOVERED, and DEAD** persons don't change status

**Output:** DataFrame with daily counts of each health status

## Output Format

Simulation results are saved as CSV files with the following structure:

### Simulation Output (from `simulate` command)

| Day | SUSCEPTIBLE | INFECTED | RECOVERED | DEAD | VACCINATED |
|-----|-------------|----------|-----------|------|------------|
| 0   | 485         | 5        | 0         | 0    | 10         |
| 1   | 483         | 7        | 0         | 0    | 10         |
| 2   | 480         | 9        | 1         | 0    | 10         |
| ... | ...         | ...      | ...       | ...  | ...        |

### Analysis Output (from `analyze` command)

| AVG_INFECTED | AVG_DEATHS | AVG_DEATH_STDV |
|--------------|------------|----------------|
| 45.3         | 12.7       | 3.2            |

- **AVG_INFECTED**: Average number of infected individuals across all trials
- **AVG_DEATHS**: Average number of deaths across all trials
- **AVG_DEATH_STDV**: Standard deviation of death counts (measures variability)

## Running the Programs

The program uses the Python library Typer which builds CLI applications based on type hinting. All commands follow the pattern: `python3 virus.py <command> [arguments]`

### 1. Virus Spread Simulation (`simulate`)

Runs a single simulation trial for a specified number of days.

**Command syntax:**
```bash
python3 virus.py simulate <tprob> <dprob> <vprob> <infected> <days> <population_count> <output_file>
```

**Arguments:**
- `tprob`: Transmission probability (0.0-1.0). Example: `0.015` = 1.5% chance per encounter
- `dprob`: Death probability (0.0-1.0). Example: `0.35` = 35% chance of dying when infected
- `vprob`: Vaccination fraction (0.0-1.0). Example: `0.6` = 60% of population vaccinated
- `infected`: Number of initially infected individuals. Example: `10`
- `days`: Number of days to simulate. Example: `100`
- `population_count`: Total population size. Example: `1000`
- `output_file`: Name of CSV output file. Example: `simulate_output.csv`

**Example:**
```bash
python3 virus.py simulate 0.015 0.35 0.6 10 100 1000 simulate_output.csv
```

This simulates 100 days with 1,000 people, 10 initially infected, 60% vaccinated, 1.5% transmission rate, and 35% death rate.

### 2. Analyze Multiple Trials (`analyze`)

Runs multiple simulations to calculate average statistics and standard deviations.

**Command syntax:**
```bash
python3 virus.py analyze <nsimulations> <tprob> <dprob> <vprob> <infected> <days> <population_count> <output_file>
```

**Additional argument:**
- `nsimulations`: Number of simulation trials to run. Example: `1000`

**Note:** All other arguments are the same as `simulate`.

**Example:**
```bash
python3 virus.py analyze 1000 0.015 0.35 0.6 10 100 1000 analyze_output.csv
```

This runs 1,000 simulation trials with the same parameters and computes average deaths and standard deviation.

### 3. Visualizing Results (`visualize`)

Generates plots and histograms from simulation data.

**Command syntax:**
```bash
python3 virus.py visualize <input_file>
```

**Arguments:**
- `input_file`: Path to CSV file from `simulate` or `analyze` command

**Example:**
```bash
python3 virus.py visualize simulate_output.csv
```

This displays a time-series plot showing how each health status changes over time.

## Example Workflow

Here's a complete workflow demonstrating all three commands:

```bash
# Step 1: Run a simulation for 50 days
python3 virus.py simulate 0.02 0.15 0.4 10 50 800 day50_sim.csv

# Step 2: Run 500 trials to get statistical insights
python3 virus.py analyze 500 0.02 0.15 0.4 10 50 800 stats_500trials.csv

# Step 3: Visualize the single simulation results
python3 virus.py visualize day50_sim.csv
```

**Expected outcomes:**
- `day50_sim.csv`: Daily health status counts for 50 days
- `stats_500trials.csv`: Average infected count, average deaths, death standard deviation
- Visual plots showing infection curve over time

## Testing

This project includes comprehensive unit tests demonstrating software quality practices suitable for portfolio presentation.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=virus --cov-report=html

# Run specific test file
pytest test_unittests/test_simulation.py

# View detailed HTML coverage report
open htmlcov/index.html
```

### Test Structure

The test suite is organized into focused test files:

- **`test_person.py`** - Unit tests for Person class methods (16 tests)
  - Initialization and attribute validation
  - Probability validation
  - Sick days calculation
  - Survival/death logic

- **`test_simulation.py`** - Simulation logic and state management (20 tests)
  - Population initialization
  - Health status tracking
  - State transitions
  - Full simulation runs with edge cases

- **`test_catch_or_not.py`** - Infection transmission mechanics (18 tests)
  - Infection probability logic
  - Death probability logic
  - Edge cases and validation

- **`test_cli.py`** & **`test_visualization.py`** - Test stubs with documentation
  - Explains why CLI and visualization aren't unit tested
  - Documents future testing approach

- **`conftest.py`** - Shared test fixtures for code reuse

### Test Coverage

**Current coverage: 62%**

- ✅ **Core business logic: ~100% tested**
  - Person class methods fully tested
  - Simulation state management fully tested
  - All critical paths covered

- ❌ **Intentionally untested (with documentation):**
  - CLI commands (would require typer mocking)
  - Visualization methods (would require matplotlib mocking)
  - See `TESTING.md` for detailed rationale

The 62% coverage reflects strategic testing focused on high-value, testable business logic while documenting intentional exclusions.

### Running a Quick Test

```bash
# Verify all tests pass
pytest test_unittests/ -v

# Expected output: 54 passed, 10 skipped
```

## Known Limitations & Future Improvements

### Current Limitations

- **CLI Testing**: Command-line interface commands are not unit tested
  - Would require mocking `typer.CliRunner` and file I/O operations
  - Currently verified through manual testing (see Examples above)

- **Visualization Testing**: Plotting methods are manually verified
  - Would require mocking `matplotlib.pyplot` 
  - Future: Could use `pytest-mpl` for image comparison testing

- **Simplified Model Assumptions**:
  - Vaccination provides 100% immunity (real-world vaccines vary)
  - Uniform random exposure (no network/contact tracing model)
  - Fixed recovery period (14 days max)
  - Binary health states (no severity levels)

### Future Enhancements

- **Advanced Testing**: Add integration tests for CLI workflow
- **Network Model**: Implement contact-tracing with social networks
- **Variable Immunity**: Model partial vaccine effectiveness
- **Reinfection**: Allow recovered individuals to be reinfected
- **Age Demographics**: Different mortality rates by age group
- **Quarantine Modeling**: Simulate isolation policies

## Development

### Running Tests During Development

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest test_unittests/test_person.py -v

# Run specific test class
pytest test_unittests/test_person.py::TestPersonInitialization -v

# Run with coverage and watch for changes
pytest --cov=virus --cov-report=term-missing
```

### Project File Structure

```
virus/
├── virus.py                      # Main application (714 lines)
│   ├── HS (Enum)                 # Health status constants
│   ├── Person (Dataclass)        # Individual person logic
│   ├── Simulation (Class)        # Population manager
│   └── Visualize (Class)         # Plotting and visualization
│
├── test_unittests/               # Test suite
│   ├── conftest.py               # Shared test fixtures
│   ├── test_person.py            # Person class tests (16 tests)
│   ├── test_simulation.py        # Simulation tests (20 tests)
│   ├── test_catch_or_not.py      # Infection mechanics (18 tests)
│   ├── test_cli.py               # CLI test stubs
│   └── test_visualization.py     # Visualization test stubs
│
├── README.md                     # This file
├── TESTING.md                    # Comprehensive testing guide
├── COVERAGE_ANALYSIS.md          # Coverage report explanation
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Pytest configuration
└── .gitignore                    # Git ignore rules
```

### Code Style and Standards

This project follows:
- **PEP 8**: Python style guidelines
- **Type Hints**: All functions have type annotations
- **Docstrings**: Google-style docstrings for all classes and methods
- **Testing**: Comprehensive unit tests with >60% coverage
- **Documentation**: Clear README and technical documentation

### Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Write tests for new functionality
4. Ensure all tests pass: `pytest`
5. Ensure code coverage remains high: `pytest --cov=virus`
6. Update documentation as needed
7. Submit a pull request

### Key Implementation Details

**Random Transmission Logic:**
```python
# Person has unique transmission_rate (0-1)
# Infection occurs if: transmission_rate < tprob
if person.transmission_rate < tprob:
    person.health_status = HS.INFECTED
```

**Death vs. Recovery:**
```python
# Check death first
if random.random() < dprob:
    return HS.DEAD

# If survived, check recovery (14-day threshold with randomness)
if adjusted_sick_days > MAX_SICK_DAYS:
    return HS.RECOVERED
```

**Population Conservation:**
The simulation maintains a constant population count. The sum of all health statuses always equals the initial population (deaths are tracked, not removed).

## Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

Required libraries:
- `pandas` - Data manipulation and CSV handling
- `matplotlib` - Visualization and plotting
- `typer` - CLI application framework
- `pytest` - Testing framework
- `pytest-cov` - Test coverage reporting

## Conclusion

This Python-based simulation provides insights into how factors like vaccination and transmission probability affect the spread of a virus. By adjusting the parameters, the user can experiment with different scenarios and understand the critical impact of public health measures on virus outbreaks.

The project demonstrates professional software engineering practices including comprehensive testing, documentation, and modular design suitable for portfolio presentation.
