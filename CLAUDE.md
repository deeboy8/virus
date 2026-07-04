# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
pytest

# Run a single test file
pytest test_unittests/test_simulation.py -v

# Run a single test class or method
pytest test_unittests/test_person.py::TestPersonInitialization -v

# Run with coverage
pytest --cov=virus --cov-report=term-missing

# Run a simulation (single trial)
python3 virus.py simulate <vprob> <tprob> <dprob> <infected> <days> <population_count> <output_file>

# Run multiple trials for statistical analysis
python3 virus.py analyze <nsimulations> <vprob> <tprob> <dprob> <days> <infected> <population_count> <output_file>

# Visualize results from a CSV
python3 virus.py visualize <input_file>
```

Expected test output: `54 passed, 10 skipped`

## Architecture

All code lives in a single file: `virus.py`. The CLI is built with Typer and exposes three commands (`simulate`, `analyze`, `visualize`) that wire together the three core classes.

### Class relationships

**`HS` (Enum)** — Health status constants used as dict keys throughout the simulation. Note the actual int values differ from the README: `SUSCEPTIBLE=0`, `INFECTED=1`, `RECOVERED=-1`, `VACCINATED=-2`, `DEAD=-3`.

**`Person` (dataclass)** — Represents one individual. Each person has a fixed `transmission_rate` (random float 0–1) that acts as their personal susceptibility threshold — infection occurs when `transmission_rate < tprob`. The two core probability methods are:
- `catch_or_not(tprob, other_persons)` — public entry point; validates then delegates to `_check_if_infected`
- `die_or_not(dprob, rand_dprob, sickness_factor, person)` — validates then delegates to `check_if_survive`
- Recovery uses `calculate_adjusted_sick_days` which adds `3.0 * sickness_factor` to `sick_days`; if this exceeds 14, person recovers

**`Simulation`** — Owns the `_population` list of `Person` objects. Population is shuffled on init. The `run()` loop mutates person objects in-place while tracking a `Counter` dict (`status_counts`) that maps `HS` enum values to current totals. `_handle_susceptible` and `_handle_infected` update both the person object and the counter atomically. Population total is conserved — dead persons remain in the list with `HS.DEAD`.

**`Visualize`** — Reads CSV output and generates plots. `plot()` produces a time-series line chart and saves `virus_simulation.png`. `generate_histogram()` is partially implemented (original histogram code is commented out; current code generates a grouped bar chart from `analyze` output).

### Data flow

`simulate`: `Simulation.run()` → `pd.DataFrame` (one row per day) → CSV

`analyze`: N × `Simulation.run()` → `calculate_stats()` per trial → aggregate `pd.DataFrame` (one row per trial, columns: `AVG_INFECTED`, `AVG_DEATHS`, `AVG_DEATH_STDV`) → CSV

`visualize`: CSV → `Visualize.read_file()` → `generate_histogram()` or `plot()`

### Testing approach

Tests live in `test_unittests/`. CLI (`test_cli.py`) and visualization (`test_visualization.py`) tests are intentionally stubbed/skipped — the rationale is documented in `TESTING.md`. All core business logic in `Person` and `Simulation` is fully tested. Shared fixtures are in `conftest.py`.

The `HS` enum values are used directly as DataFrame column names and Counter keys — tests that assert on DataFrames must use `HS.INFECTED` etc., not string column names.
