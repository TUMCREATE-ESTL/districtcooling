import districtcooling as dc
import pandas as pd
import matplotlib.pyplot as plt

# Generate objects =====================================================================================================

parameters = dc.ParametersReader()
grid = dc.CoolingGrid(parameters=parameters)
plant = dc.CoolingPlant(parameters=parameters)
plotter = dc.Plotter(parameters=parameters)

# Read data ============================================================================================================

# Flexible Building Scenario -------------------------------------------------------------------------------------------

TC_flex_0MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=flex_TES=0MWh__solved_problem.csv',
    index_col=[0]
)

TC_flex_625MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=flex_TES=625MWh__solved_problem.csv',
    index_col=[0]
)
TC_flex_1250MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=flex_TES=1250MWh__solved_problem.csv',
    index_col=[0]
)
TC_flex_1875MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=flex_TES=1875MWh__solved_problem.csv',
    index_col=[0]
)

TC_flex_2500MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=flex_TES=2500MWh__solved_problem.csv',
    index_col=[0]
)
# Inflexible Building Scenario -----------------------------------------------------------------------------------------


# Evaluation ===========================================================================================================

# Costs comparison -----------------------------------------------------------------------------------------------------

print(TC_flex_0MWh.loc['Costs in [S$]'].sum())
costs_flex_dict = {
    '0': TC_flex_0MWh.loc['Costs in [S$]'].sum()*10**(-6),
    '625': TC_flex_625MWh.loc['Costs in [S$]'].sum()*10**(-6),
    '1250': TC_flex_1250MWh.loc['Costs in [S$]'].sum()*10**(-6),
    '1875': TC_flex_1875MWh.loc['Costs in [S$]'].sum()*10**(-6),
    '2500': TC_flex_2500MWh.loc['Costs in [S$]'].sum()*10**(-6)
}
costs_flex_df = pd.DataFrame.from_dict(
    data=costs_flex_dict,
    orient='index',
    columns=['Overall year costs in [*10**6 S$]']
)
print(
    costs_flex_df
)
plot_costs = costs_flex_df.plot(
    kind='bar',
    use_index=True,
    y='Overall year costs in [*10**6 S$]',
    ylim=[20, 30],
    legend=False,
    rot=0
)
# label bars
for i in plot_costs.patches:
    plot_costs.text(i.get_x()+0.05, i.get_height()+.05,
        str(round(i.get_height(), 2)),
        # fontsize=15,
        # color='dimgrey'
    )
# label axis
plot_costs.set_xlabel('TES capacities [MWh]')
plot_costs.set_ylabel('Electricity costs of entire year [million S$]')
plt.show()

# Costs per GFA comparison ---------------------------------------------------------------------------------------------

print(TC_flex_0MWh.loc['Costs in [S$]'].sum())
costs_flex_dict = {
    '0': TC_flex_0MWh.loc['Costs in [S$]'].sum()/1106260.4,
    '625': TC_flex_625MWh.loc['Costs in [S$]'].sum()/1106260.4,
    '1250': TC_flex_1250MWh.loc['Costs in [S$]'].sum()/1106260.4,
    '1875': TC_flex_1875MWh.loc['Costs in [S$]'].sum()/1106260.4,
    '2500': TC_flex_2500MWh.loc['Costs in [S$]'].sum()/1106260.4
}
costs_flex_df = pd.DataFrame.from_dict(
    data=costs_flex_dict,
    orient='index',
    columns=['Overall year costs per GFA [S$/m2]']
)
print(
    costs_flex_df
)
plot_costs = costs_flex_df.plot(
    kind='bar',
    use_index=True,
    y='Overall year costs per GFA [S$/m2]',
    ylim=[20, 27],
    legend=False,
    rot=0
)
# label bars
for i in plot_costs.patches:
    plot_costs.text(i.get_x()+0.05, i.get_height()+.05,
        str(round(i.get_height(), 2)),
        # fontsize=15,
        # color='dimgrey'
    )
# label axis
plot_costs.set_xlabel('TES capacities [MWh]')
plot_costs.set_ylabel('Electricity costs of entire year per GFA [S$/m2 ]')
plt.show()

# Price to Power -------------------------------------------------------------------------------------------------------
"""
print(TC_flex_2500MWh.loc['DCS total Power in [MW]'])
print(TC_flex_2500MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values)
price_power_2500MWh = plt.scatter(
    x=TC_flex_2500MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values,
    y=parameters.environment['Price [S$/MWh]'].values,
    marker='.',
    s=1,
    # c='darkgreen'
)
# label axis
plt.xlabel('DCS total power (MW)')
plt.ylabel('Electricity price (S$ per MWh)')
plt.show()

print(TC_flex_0MWh.loc['DCS total Power in [MW]'])
print(TC_flex_0MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values)
price_power_0MWh = plt.scatter(
    x=TC_flex_0MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values,
    y=parameters.environment['Price [S$/MWh]'].values,
    marker='.',
    s=1
)
# label axis
plt.xlabel('DCS total power (MW)')
plt.ylabel('Electricity price (S$ per MWh)')
plt.show()
"""
# Wet-bulb to Power -------------------------------------------------------------------------------------------------------
"""
print(TC_flex_2500MWh.loc['DCS total Power in [MW]'])
print(TC_flex_2500MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values)
wb_power_2500MWh = plt.scatter(
    x=TC_flex_2500MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values,
    y=parameters.environment['Air wet-bulb temperature [°C]'].values,
    marker='.',
    s=1,
    # c='darkgreen'
)
# label axis
plt.xlabel('DCS total power (MW)')
plt.ylabel('Air wet-bulb temperature (°C)')
plt.show()

print(TC_flex_0MWh.loc['DCS total Power in [MW]'])
print(TC_flex_0MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values)
wb_power_0MWh = plt.scatter(
    x=TC_flex_0MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values,
    y=parameters.environment['Air wet-bulb temperature [°C]'].values,
    marker='.',
    s=1
)
# label axis
plt.xlabel('DCS total power (MW)')
plt.ylabel('Air wet-bulb temperature (°C)')
plt.show()
"""
# Histogram Power ------------------------------------------------------------------------------------------------------
"""
histo_power_2500MWh = TC_flex_2500MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).plot.hist(
    bins=100,
    alpha=1
)
# label axis
plt.xlabel('DCS total power (MW)')
plt.ylabel('Frequency')
plt.show()

histo_power_0MWh = TC_flex_0MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).plot.hist(
    bins=100,
    alpha=1
)
# label axis
plt.xlabel('DCS total power (MW)')
plt.ylabel('Frequency')
plt.show()
"""
# Histogram Costs ------------------------------------------------------------------------------------------------------
"""
histo_costs_2500MWh = TC_flex_2500MWh.loc['Costs in [S$]'].drop(['IDs'], axis=0).plot.hist(
    bins=100,
    alpha=1
)
# label axis
plt.xlabel('Electricity costs of entire year [million S$]')
plt.ylabel('Frequency')
plt.show()

histo_costs_0MWh = TC_flex_0MWh.loc['Costs in [S$]'].drop(['IDs'], axis=0).plot.hist(
    bins=100,
    alpha=1
)
# label axis
plt.xlabel('Electricity costs of entire year [million S$]')
plt.ylabel('Frequency')
plt.show()
"""
# Scatter Power Time ---------------------------------------------------------------------------------------------------
"""
power_time_2500MWh = plt.scatter(
    x=parameters.environment.index.values,
    y=TC_flex_2500MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1,
    # c='darkgreen'
)
# label axis
plt.xlabel('Time step [0.5 h]')
plt.ylabel('DCS total Power (MW)')
plt.show()

power_time_0MWh = plt.scatter(
    x=parameters.environment.index.values,
    y=TC_flex_0MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1,
    # c='darkgreen'
)
# label axis
plt.xlabel('Time step [0.5 h]')
plt.ylabel('DCS total Power (MW)')
plt.show()
"""
# Scatter Cost Time ---------------------------------------------------------------------------------------------------
"""
cost_time_2500MWh = plt.scatter(
    x=parameters.environment.index.values,
    y=TC_flex_2500MWh.loc['Costs in [S$]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1,
    # c='darkgreen'
)
price_time = plt.scatter(
    x=parameters.environment.index.values,
    y=parameters.environment['Price [S$/MWh]'].values,
    marker='.',
    s=1,
    c='r',
    alpha=0.5
)
# label axis
plt.xlabel('Time step [0.5 h]')
plt.ylabel('Costs (S$)')
plt.show()

costs_time_0MWh = plt.scatter(
    x=parameters.environment.index.values,
    y=TC_flex_0MWh.loc['Costs in [S$]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1,
    # c='darkgreen'
)
# label axis
plt.xlabel('Time step [0.5 h]')
plt.ylabel('Costs (S$)')
plt.show()
"""
# Scatter ChS and TES Time ---------------------------------------------------------------------------------------------
"""
chsflow_time_2500MWh = plt.scatter(
    x=parameters.environment.index.values,
    y=TC_flex_2500MWh.loc['Chiller-set flow [qbm/s]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1,
    # c='darkgreen'
)

etsflow_time_2500MWh = plt.scatter(
    x=parameters.environment.index.values,
    y=TC_flex_2500MWh.loc['TES flow [qbm/s]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1,
    c='r'
)

# label axis
plt.xlabel('Time step [0.5 h]')
plt.ylabel('Volumetric flow (m3/s)')
plt.show()

chsflow_time_0MWh = plt.scatter(
    x=parameters.environment.index.values,
    y=TC_flex_0MWh.loc['Chiller-set flow [qbm/s]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1,
    # c='darkgreen'
)

etsflow_time_0MWh = plt.scatter(
    x=parameters.environment.index.values,
    y=TC_flex_0MWh.loc['TES flow [qbm/s]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1,
    c='r'
)

# label axis
plt.xlabel('Time step [0.5 h]')
plt.ylabel('Volumetric flow (m3/s)')
plt.show()
"""
# Scatter ChS and TES --------------------------------------------------------------------------------------------------
"""
ets_chs_2500MWh = plt.scatter(
    x=TC_flex_2500MWh.loc['Chiller-set flow [qbm/s]'].drop(['IDs'], axis=0).values,
    y=TC_flex_2500MWh.loc['TES flow [qbm/s]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1,
    # c='r'
)
# label axis
plt.xlabel('Chiller-set flow [qbm/s]')
plt.ylabel('TES flow [qbm/s]')
plt.show()

ets_chs_0MWh = plt.scatter(
    x=TC_flex_0MWh.loc['Chiller-set flow [qbm/s]'].drop(['IDs'], axis=0).values,
    y=TC_flex_0MWh.loc['TES flow [qbm/s]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1,
    # c='r'
)
# label axis
plt.xlabel('Time step [0.5 h]')
plt.ylabel('Volumetric flow (m3/s)')
plt.show()
"""