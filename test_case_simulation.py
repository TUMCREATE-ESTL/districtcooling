import districtcooling as dc
import cobmo.building
import cobmo.database_interface
import pandas as pd

# Generate objects =====================================================================================================

parameters = dc.ParametersReader()
grid = dc.CoolingGrid(parameters=parameters)
plant = dc.CoolingPlant(parameters=parameters)
plotter = dc.Plotter(parameters=parameters)

buildings_dict = {
    building_id: cobmo.building.Building(
        conn=cobmo.database_interface.connect_database(),
        scenario_name=building['building_scenario_name']
    )
    for building_id, building in parameters.buildings.iterrows()
}

optimizer = dc.LinearOptimizer(
    parameters=parameters,
    coolinggrid=grid,
    coolingplant=plant,
    buildings_dict=buildings_dict
)

head_differences_ds = pd.read_csv(
    'data/headdifferencesETS_rounded.csv',
    index_col=[0]
)
print(head_differences_ds)
print(head_differences_ds[str(1)].max())

# Simulations ==========================================================================================================

# 1) TES = 0 Wh
solved_optimization_problem = optimizer.build_and_solve_problem(
    ds_head_differences_time_array=head_differences_ds,
    TES_capacity_Wh=-0.0001,
    distributed_secondary_pumping=False
)
solution = optimizer.get_solution_as_dataframe(
    solved_optimization_problem,
    save=True,
    index_for_saving='TESTCASE_BuildT=flex_TES=0MWh_'
)
print('TES = 0 Wh')
print(solution)

# 2) TES = -625 MWh
solved_optimization_problem = optimizer.build_and_solve_problem(
    ds_head_differences_time_array=head_differences_ds,
    TES_capacity_Wh=(-625*10**6),
    distributed_secondary_pumping=False
)
solution = optimizer.get_solution_as_dataframe(
    solved_optimization_problem,
    save=True,
    index_for_saving='TESTCASE_BuildT=flex_TES=625MWh_'
)
print('TES = 625 MWh')
print(solution)

# 3) TES = -1250 MWh
solved_optimization_problem = optimizer.build_and_solve_problem(
    ds_head_differences_time_array=head_differences_ds,
    TES_capacity_Wh=(-1250*10**6),
    distributed_secondary_pumping=False
)
solution = optimizer.get_solution_as_dataframe(
    solved_optimization_problem,
    save=True,
    index_for_saving='TESTCASE_BuildT=flex_TES=1250MWh_'
)
print('TES = 1250 MWh')
print(solution)

# 4) TES = -1875 MWh
solved_optimization_problem = optimizer.build_and_solve_problem(
    ds_head_differences_time_array=head_differences_ds,
    TES_capacity_Wh=(-1875*10**6),
    distributed_secondary_pumping=False
)
solution = optimizer.get_solution_as_dataframe(
    solved_optimization_problem,
    save=True,
    index_for_saving='TESTCASE_BuildT=flex_TES=1875MWh_'
)
print('TES = 1875 MWh')
print(solution)

# 5) TES = -2500 MWh
solved_optimization_problem = optimizer.build_and_solve_problem(
    ds_head_differences_time_array=head_differences_ds,
    TES_capacity_Wh=(-2500*10**6),
    distributed_secondary_pumping=False
)
solution = optimizer.get_solution_as_dataframe(
    solved_optimization_problem,
    save=True,
    index_for_saving='TESTCASE_BuildT=flex_TES=2500MWh_'
)
print('TES = 2500 MWh')
print(solution)