import districtcooling as dc
import cobmo.building
import cobmo.database_interface
import pandas as pd

# Generate objects =====================================================================================================

parameters = dc.ParametersReader()
grid = dc.CoolingGrid(parameters=parameters)
plant = dc.CoolingPlant(parameters=parameters)
plotter = dc.Plotter(parameters=parameters)
"""
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
"""
head_differences_ds = pd.read_csv(
    'data/headdifferencesETS_rounded.csv',
    index_col=[0]
)
print(head_differences_ds)

# Simulations ==========================================================================================================

plant_simulation = plant.get_plant_simulation(
    chiller_set_flow=0.2,
    tes_flow=0.1,
    air_wet_bulb=26
)
print(plant_simulation)

"""
solved_optimization_problem = optimizer.build_and_solve_problem(
    ets_head_difference_time_array=grid_simulation.loc["Head difference over ETSs [m]"],
    distributed_secondary_pumping=True
)
solution = optimizer.get_solution_as_dataframe(
    solved_optimization_problem,
    save=False,
    index_for_saving='fixed_temp_final_21'
)
print(solution)
"""