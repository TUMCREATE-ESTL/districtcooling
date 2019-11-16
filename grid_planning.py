import pandas as pd
import districtcooling as dc

# Finding full-load ETS flow ===========================================================================================
"""
solution_21 = pd.read_csv(
    'results/csv_files/fixed_temp_final_21_solved_problem.csv',
    index_col=[0]
)
print(solution_21)

heats = solution_21.loc['Heat-inflow buildings [W]']
print(heats)
heats.index = list(range(1, 23))
print(heats)
print(heats.loc[1])

ets_flows = solution_21.loc['ETS flow [qbm/s]']
print(ets_flows)
ets_flows = ets_flows.drop(['IDs'], axis=1)
ets_flows.index = list(range(1, 23))
print(ets_flows)

max_dict = {
    index: [
        round(heats.loc[index].max()/1000000, 6),
        heats.loc[index].idxmax(),
        round(ets_flows.loc[index].max(), 6),
        ets_flows.loc[index].idxmax()
    ]
    for index in heats.index
}
print(max_dict)
max_df = pd.DataFrame.from_dict(
    max_dict,
    orient='index',
    columns=['Maximal heat flow [MW]',
             'Index heat',
             'Maximal flow ets [qbm/s]',
             'Index flow'
             ]
)
print(max_df)

max_df.to_csv(
    'results/csv_files/max_buildings_from_optimization_rounded.csv'
)
"""
# With full-load ETS determine full-load line flows ====================================================================
max_rounded = pd.read_csv(
    'results/csv_files/max_buildings_from_optimization_rounded.csv',
    index_col=[0]
)
print(max_rounded)

ets_flows = max_rounded['Maximal flow ets [qbm/s]']
print(ets_flows)

parameters = dc.ParametersReader()
grid = dc.CoolingGrid(parameters=parameters)
plotter = dc.Plotter(parameters=parameters)

# print(grid.incidence_matrix_complete)
print(grid.incidence_matrix)
# print(grid.incidence_matrix_potential)
# print(grid.incidence_matrix_transposed)

plotter.plot_graph(
    save=False,
    index_for_saving=0
)

ets_flows_timearray = grid.build_ets_flow_time_array(ets_flow_vector=ets_flows.values)
print(ets_flows_timearray)

simulation_wrong_diameters = grid.get_grid_simulation(
    ets_flow_time_array=ets_flows_timearray
)

print(simulation_wrong_diameters)
print(simulation_wrong_diameters[1]['Flow in lines [qbm/s]'][1.0])

diameters_df = grid.get_diameters_from_flow(
        line_flows=simulation_wrong_diameters[1]['Flow in lines [qbm/s]'],
        u_max=2.0
    )

print(diameters_df)


