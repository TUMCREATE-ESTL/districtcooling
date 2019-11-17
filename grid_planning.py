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
print(max_df['Maximal heat flow [MW]'])
print(max_df['Maximal heat flow [MW]'].sum())

#max_df.to_csv(
 #   'results/csv_files/max_buildings_from_optimization_rounded.csv'
#)
"""
# With full-load ETS determine full-load line flows and diamaters ======================================================
"""
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

ets_flows_timearray = grid.build_ets_flow_time_array(ets_flow_vector=ets_flows.values)
print(ets_flows_timearray)

simulation_wrong_diameters = grid.get_grid_simulation(
    ets_flow_time_array=ets_flows_timearray
)
print(simulation_wrong_diameters)
plotter.plot_grid_simulation(
    grid_simulation=simulation_wrong_diameters,
    time_step=1
)

lines_df = simulation_wrong_diameters[1]['Flow in lines [qbm/s]']
print(lines_df)
lines_df_rounded = lines_df.round(decimals=6)
print(lines_df_rounded)
diameters_df = grid.get_diameters_from_flow(
        line_flows=lines_df,
        u_max=2.0
    )
diameters_df_rounded = diameters_df.round(decimals=2)
print(diameters_df)
print(diameters_df_rounded)

#lines_df.to_csv('results/csv_files/lineflow_21fixed.csv')
#lines_df_rounded.to_csv('results/csv_files/lineflow_21fixed_rounded6.csv')
#diameters_df.to_csv('results/csv_files/diameters_21fixed_u2.csv')
#diameters_df_rounded.to_csv('results/csv_files/diameters_21fixed_u2_rounded2.csv')

#grid.incidence_matrix_complete.to_csv('results/csv_files/I_complete')
#grid.incidence_matrix.to_csv('results/csv_files/I_reduced')
#grid.incidence_matrix_potential.to_csv('results/csv_files/I_pn')
#grid.incidence_matrix_transposed.to_csv('results/csv_files/I_T')
"""
# Hydraulic Equilibrium for full-load with determined diameters to calculate Heads =====================================
"""
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

ets_flows_timearray = grid.build_ets_flow_time_array(ets_flow_vector=ets_flows.values)
print(ets_flows_timearray)

simulation_right_diameters = grid.get_grid_simulation(
    ets_flow_time_array=ets_flows_timearray
)
print(simulation_right_diameters.loc['Flow in lines [qbm/s]'])
print(simulation_right_diameters.loc['Head difference over ETSs [m]'][1].max())
plotter.plot_grid_simulation(
    grid_simulation=simulation_right_diameters,
    time_step=1,
    save=True
)
#simulation_right_diameters.loc['Head difference over ETSs [m]'].to_csv(
    #"results/headdifferencesETS.csv"
#)
#simulation_right_diameters.loc['Head difference over ETSs [m]'].round(decimals=2).to_csv(
    #"results/headdifferencesETS_rounded.csv"
#)
"""