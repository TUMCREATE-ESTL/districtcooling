import numpy as np

import cobmo.building
import cobmo.database_interface
import districtcooling as dc

# Generate objects =====================================================================================================

parameters = dc.ParametersReader()
grid = dc.CoolingGrid(parameters=parameters)
plant = dc.CoolingPlant(parameters=parameters)
plotter = dc.Plotter(parameters=parameters)
# buildings_dict = {
#     building_id: dc.CubicBuilding(
#         building_id=building_id,
#         parameters=parameters
#     )
#     for building_id in parameters.buildings.index
# }
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

# Test objects =========================================================================================================

# Non-linear simulation of the distribution system (DS) ----------------------------------------------------------------
plotter.plot_graph(
    save=False,
    index_for_saving=1
)

"""
ets_flow_time_array = grid.build_ets_flow_time_array(np.ones(parameters.buildings.shape[0]))
print(ets_flow_time_array)

grid_simulation = grid.get_grid_simulation(ets_flow_time_array)
print(grid_simulation)

plotter.plot_grid_simulation(
    grid_simulation=grid_simulation,
    time_step=1,
    save=True,
    index_for_saving=1
)
"""
# Linear simulation of the district cooling plant (DCP) ----------------------------------------------------------------
"""
plant_simulation = plant.get_plant_simulation(
    chiller_set_flow=0.2,
    tes_flow=0.1,
    air_wet_bulb=26
)
print(plant_simulation)

# Building and solving optimization problem for a given ets head difference array --------------------------------------
solved_optimization_problem = optimizer.build_and_solve_problem(
    ets_head_difference_time_array=grid_simulation.loc["Head difference over ETSs [m]"],
    distributed_secondary_pumping=True
)
solution = optimizer.get_solution_as_dataframe(
    solved_optimization_problem,
    save=True,
    index_for_saving=1
)
print(solution)
"""
"""
# Iterative solving algorithm of optimization problem ------------------------------------------------------------------
ets_head_difference_used, problem_result = optimizer.iterative_solver(
    error_differential=0.001,
    distributed_secondary_pumping=False
)
print(ets_head_difference_used)
print(optimizer.get_solution_as_dataframe(problem_result))
simulation = grid.get_grid_simulation(ets_head_difference_used)
print(simulation)
"""