# Virus Simulation in Python

## Overview

This Python project simulates the spread of a virus on the island of Nantucket, with a population of approximately 10,000 people. It explores the effects of different factors, such as vaccination rates and transmission probability, on the progression of a viral outbreak. This simulation provides insights into how preventive measures can mitigate the impact of the virus.

## Project Structure

The project consists of three main Python scripts:

1. **simulate.py**: Simulates the virus's progression over a 100-day period. It tracks the health status of the population, categorizing individuals as susceptible, infected, recovered, vaccinated, or dead. Via command line options, you can explore the effects of different vaccination rates and transmission probabilities on the virus spread.

2. **analyze.py**: Runs multiple trials (e.g., 1,000) of the simulation to calculate the average number of deaths and the standard deviation. This script helps to analyze the impact of random variations and better understand overall trends.

3. **visualize.py**: Will generate histograms to visualize the number of deaths after running the simulation multiple times. This provides a graphical representation of how varying factors influence the outcome of the virus spread.

## Key Features

- **Random Interactions**: The program simulates random interactions between people. Susceptible individuals can contract the virus from infected individuals based on a specified transmission probability (`tprob`), while infected individuals either recover, die, or continue being sick.
  
- **Vaccination**: The program assumes that vaccinated people are fully protected from infection (a simplification for this simulation).

- **Transmission Probability**: The user can set the probability (`tprob`) of catching the virus from an infected individual to model different scenarios (e.g., lower probabilities due to social distancing or mask-wearing).

- **Multiple Trials**: The program can run the simulation multiple times to analyze the variance in results, providing average statistics and standard deviations for deeper insights.

## Running the Programs

### 1. Virus Spread Simulation (`simulate.py`)

To run the simulation for 100 days with varying vaccination rates and transmission probabilities, use the following command:

```bash
python simulate.py vprob tprob output_file
```

Where:

- `vprob`: Fraction of the population vaccinated (e.g., `0.6` for 60% vaccinated),
- `tprob`: Transmission probability (e.g., `0.015` means 1.5% chance of transmission per encounter),
- `output_file`: Name of the file where the results will be saved.

Example:

```bash
python simulate.py 0.6 0.015 simulate_output.csv
```

### 2. Analyze Multiple Trials (`analyze.py`)

To analyze multiple simulation runs and compute average deaths and standard deviations, run:

```bash
python analyze.py vprob tprob output_file
```

Where `n_trials` is the number of simulations to run, typically set to 1,000.

Example:

```bash
python analyze.py 0.6 0.015 analyze_output.csv
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
