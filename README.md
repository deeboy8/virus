# Virus Simulation in Python

## Overview

This Python project simulates the spread of a virus on a variable population. It explores the effects of different factors, such as vaccination rates and transmission probability on the progression of a viral outbreak. This simulation provides insights into how preventive measures, such as masking and social distancing can mitigate the impact of the virus.

## Project Structure

The project consists of three parts with each acting as a commands to be passed in the Terminal to execute it's specific task:

1. **simulate**: Simulates the virus's progression over a variable day period. It tracks the health status of the population, categorizing individuals as susceptible, infected, recovered, vaccinated, or dead. Via command line options, you can explore the effects of different vaccination rates and transmission probabilities on the virus spread.

2. **analyze**: Runs multiple trials (e.g., 1,000) of a simulation to calculate the average number of deaths and the standard deviation. This functionality helps to analyze the impact of random variations and better understand overall trends.

3. **visualize**: Will generate a histogram to visualize the number of deaths after running the simulation multiple times (ie, running analyze command for nsimulations). This provides a graphical representation of how varying factors influence the outcome of the virus spread.

## Key Features

- **Random Interactions**: The program simulates random interactions between people. Susceptible individuals can contract the virus from infected individuals based on a specified transmission probability (`tprob`), while infected individuals either recover, die, or continue being sick.
  
- **Vaccination**: The program assumes that vaccinated people are fully protected from infection (a simplification for this simulation).

- **Transmission Probability**: The user can set the probability (`tprob`) of catching the virus from an infected individual to model different scenarios (e.g., lower probabilities due to social distancing or mask-wearing).

- **Multiple Trials**: The program can run the simulation multiple times under the same parameters to analyze the variance in results, providing average statistics and standard deviations for deeper insights.

## Running the Programs

The program uses the the Python library Typer which builds quick CLI applications based on type hinting. Most command options/arguments have defaults but can be overwritten.

### 1. Virus Spread Simulation (`simulate`)

To run a simulation, or one trial, for a variable amount of days with varying vaccination rates and transmission probabilities, use the following command:

```bash
python3 virus.py tprob dprob vprob infected days population_count output_file
```

Where:

- `tprob`: Transmission probability (e.g., `0.015` means 1.5% chance of transmission per encounter)
- `dprob`: Death probability (e.g., `0.35` means 35% chance of an infected persons dying)
- `vprob`: Fraction of the population vaccinated (e.g., `0.6` for 60% vaccinated)
- `infected`: Number of individuals who may be infected at start of simulation.
- `days`: Number of days to simulate a viral spread for.
- `population_count`: Number of individuals with population.
- `output_file`: Name of the file where the results will be saved.

Example:

```bash
python3 virus.py simulation 0.6 0.015 0.15 10 100 1000 simulate_output.csv
```

### 2. Analyze Multiple Trials (`analyze.py`)

Analyze multiple simulation runs and compute average deaths and standard deviations:

```bash
python3 virus.py analyze vprob tprob output_file
```

Where `n_trials` is the number of simulations to run. All other arguments are same as for simulate.

Example:

```bash
python virus.py analyze 1000 0.6 0.015 0.025 10  analyze_output.csv
```

### 3. Visualizing Results (`visualize.py`)

To visualize the results of multiple trials as a histogram, use the following command:

```bash
python visualize.py dmin dmax input_file output_file
```

Where:

- `dmin`: Minimum number of deaths to be included in the histogram,
- `dmax`: Maximum number of deaths to be included in the histogram,
- `input_file`: The output file from the analysis,
- `output_file`: The file where the histogram data will be saved.

Example:

```bash
python visualize.py 1000 1250 analyze_output.csv visualize_output.csv
```

## Example Workflow

1. Run the simulation for 100 days:

   ```bash
   python simulate.py 0.6 0.015 simulate_output.csv
   ```

2. Analyze multiple trials (e.g., 1,000 trials) to get average deaths:

   ```bash
   python analyze.py 0.6 0.015 analyze_output.csv
   ```

3. Visualize the results using a histogram:

   ```bash
   python visualize.py 1000 1250 analyze_output.csv visualize_output.csv
   ```

## Conclusion

This Python-based simulation provides insights into how factors like vaccination and transmission probability affect the spread of a virus. By adjusting the parameters, you can experiment with different scenarios and understand the critical impact of public health measures on virus outbreaks.
