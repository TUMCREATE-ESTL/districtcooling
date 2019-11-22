# District Cooling System Model and Optimal Scheduling

- Author: Mischa Grussmann
- Contributor: Sebastian Troitzsch

## Installation

1. Check requirements:
    - [Anaconda](https://www.anaconda.com/distribution) Python 3.6 environment
    - [Gurobi Optimizer](http://www.gurobi.com/) (tested with version 8.0.1)
2. Clone or download repository.
3. In your Python environment, run:
    1. `conda install geopandas`
    2. `pip install -e path_to_repository`
    3. `pip install -e path_to_repository/cobmo`

## Getting started

The repository includes the following modules and data directories:

- `districtcooling`: District cooling system model and optimal scheduling module.
- `cobmo`: Control-oriented building model module.
- `data`: Test case input data specification.
- `results`: All generated results will be stored here.

The following run scripts are included in the root directory:

- `test_case_simulation.py`: Initiate the optimization of different test case scenarios and save the results.
- `test_case_evaluation.py`: Generate plots from the obtained optimization results.
- `main.py`: Example script, demonstrating various functionality of the repository.
- `preprocess_grid_data.py`: Generate the district cooling system data (`nodes.csv`, `lines.csv` `buildings.csv`) from a [CEA test case](https://github.com/architecture-building-systems/CityEnergyAnalyst/tree/v2.25/cea/examples).
