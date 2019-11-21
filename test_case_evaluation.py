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
    'results/csv_files/TESTCASE_BuildT=flex21-25_TES=0MWh_CSP__solved_problem.csv',
    index_col=[0]
)

TC_flex_625MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=flex21-25_TES=625MWh_CSP__solved_problem.csv',
    index_col=[0]
)
TC_flex_1250MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=flex21-25_TES=1250MWh_CSP__solved_problem.csv',
    index_col=[0]
)
TC_flex_1875MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=flex21-25_TES=1875MWh_CSP__solved_problem.csv',
    index_col=[0]
)

TC_flex_2500MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=flex21-25_TES=2500MWh_CSP__solved_problem.csv',
    index_col=[0]
)

# Inflexible Building Scenario -----------------------------------------------------------------------------------------

TC_fixed25_0MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=fixed25_TES=0MWh_CSP__solved_problem.csv',
    index_col=[0]
)
TC_fixed25_625MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=fixed25_TES=625MWh_CSP__solved_problem.csv',
    index_col=[0]
)
TC_fixed25_1250MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=fixed25_TES=1250MWh_CSP__solved_problem.csv',
    index_col=[0]
)
TC_fixed25_1875MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=fixed25_TES=1875MWh_CSP__solved_problem.csv',
    index_col=[0]
)
TC_fixed25_2500MWh = pd.read_csv(
    'results/csv_files/TESTCASE_BuildT=fixed25_TES=2500MWh_CSP__solved_problem.csv',
    index_col=[0]
)

# Full flexibility with constant price Scenario ------------------------------------------------------------------------

TC_flex_2500MWh_constant_price = pd.read_csv(
    'results/csv_files/TESTCASE_Price=const110.5_BuildT=flex21-25_TES=2500MWh_CSP__solved_problem.csv',
    index_col=[0]
)
TC_flex_10e6MWh_constant_price = pd.read_csv(
    'results/csv_files/TESTCASE_Price=const110.5_BuildT=flex21-25_TES=1000000MWh_CSP__solved_problem.csv',
    index_col=[0]
)

# Evaluation ===========================================================================================================

# Costs comparison -----------------------------------------------------------------------------------------------------

"""print(TC_flex_0MWh.loc['Costs in [S$]'].sum())
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
"""
# Costs per GFA comparison ---------------------------------------------------------------------------------------------

"""print(TC_flex_0MWh.loc['Costs in [S$]'].sum())
costs_perGFA_dict = {
    '0': [
        TC_fixed25_0MWh.loc['Costs in [S$]'].sum()/1106260.4,
        TC_flex_0MWh.loc['Costs in [S$]'].sum()/1106260.4
    ],
    '625': [
        TC_fixed25_625MWh.loc['Costs in [S$]'].sum()/1106260.4,
        TC_flex_625MWh.loc['Costs in [S$]'].sum()/1106260.4

    ],
    '1250': [
        TC_fixed25_1250MWh.loc['Costs in [S$]'].sum()/1106260.4,
        TC_flex_1250MWh.loc['Costs in [S$]'].sum()/1106260.4

    ],
    '1875': [
        TC_fixed25_1875MWh.loc['Costs in [S$]'].sum()/1106260.4,
        TC_flex_1875MWh.loc['Costs in [S$]'].sum()/1106260.4

    ],
    '2500': [
        TC_fixed25_2500MWh.loc['Costs in [S$]'].sum()/1106260.4,
        TC_flex_2500MWh.loc['Costs in [S$]'].sum()/1106260.4
    ]
}
costs_perGFA_dict_df = pd.DataFrame.from_dict(
    data=costs_perGFA_dict,
    orient='index',
    columns=['Inflexible Buildings', 'Flexible Buildings']
)
print(
    costs_perGFA_dict_df
)
plot_costs = costs_perGFA_dict_df.plot(
    kind='bar',
    use_index=True,
    y=['Inflexible Buildings', 'Flexible Buildings'],
    #fontsize=18,
    ylim=[20, 30],
    legend=True,
    rot=0
)
# label bars
for i in plot_costs.patches:
    plot_costs.text(i.get_x()+0.05, i.get_height()+.05,
        str(round(i.get_height(), 2)),
        #fontsize=18,
        #color='dimgrey'
    )
# label axis
plot_costs.set_xlabel(
    'TES capacities [MWh]',
    #fontsize=18
)
plot_costs.set_ylabel(
    'Yearly electricity costs per GFA [S\$/m$^2$ ]',
    #fontsize=18
)
plt.show()"""

# Price to Power -------------------------------------------------------------------------------------------------------

"""print(TC_flex_2500MWh.loc['DCS total Power in [MW]'])
print(TC_flex_2500MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values)
price_power_2500MWh = plt.scatter(
    x=parameters.environment['Price [S$/MWh]'].values,
    y=TC_flex_2500MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1,
    # c='darkgreen'
)
# label axis
plt.xlabel('Electricity price (S$ per MWh)')
plt.ylabel('DCS total power (MW)')
plt.title('TES = 2500 MWh, buildings=flex')
plt.show()

print(TC_fixed25_0MWh.loc['DCS total Power in [MW]'])
print(TC_fixed25_0MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values)
price_power_fixed_0MWh = plt.scatter(
    x=parameters.environment['Price [S$/MWh]'].values,
    y=TC_fixed25_0MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1
)
# label axis
plt.xlabel('Electricity price (S$ per MWh)')
plt.ylabel('DCS total power (MW)')
plt.title('TES = 0 MWh, buildings=inflex')
plt.show()"""

# Wet-bulb to Power ----------------------------------------------------------------------------------------------------
"""
wb_power_fixed_0MWh = plt.scatter(
    x=parameters.environment['Air wet-bulb temperature [°C]'].values,
    y=TC_fixed25_0MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1,
    # c='darkgreen'
)
# label axis
plt.xlabel('Air wet-bulb temperature (°C)')
plt.ylabel('DCS total power (MW)')
plt.title('TES = 0 MWh, buildings = inflex')
plt.show()

wb_power_2500MWh_flex_constant_price = plt.scatter(
    x=parameters.environment['Air wet-bulb temperature [°C]'].values,
    y=TC_flex_2500MWh_constant_price.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).values,
    marker='.',
    s=1
)
# label axis
plt.xlabel('Air wet-bulb temperature (°C)')
plt.ylabel('DCS total power (MW)')
plt.title('TES=2500 MWh, buildings=flex')
plt.show()
"""
# Histogram Power ------------------------------------------------------------------------------------------------------

"""histo_power_2500MWh = TC_flex_2500MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).plot.hist(
    bins=100,
    alpha=1,
    ylim=[0, 3000]
)
# label axis
plt.xlabel('DCS total power (MW)')
plt.ylabel('Frequency')
plt.title('TES = 2500 MWh, buildings = flex')
plt.show()

histo_power_0MWh = TC_fixed25_0MWh.loc['DCS total Power in [MW]'].drop(['IDs'], axis=0).plot.hist(
    bins=100,
    alpha=1,
    ylim=[0, 3000]
)
# label axis
plt.xlabel('DCS total power (MW)')
plt.ylabel('Frequency')
plt.title('TES = 0 MWh, buildings = inflex')
plt.show()"""

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
# Scatter ChS and TES flow vs price ------------------------------------------------------------------------------------

chs_2500MWh = plt.scatter(
    y=TC_flex_2500MWh.loc['Chiller-set flow [qbm/s]'].drop(['IDs'], axis=0).values,
    x=parameters.environment['Price [S$/MWh]'].values,
    marker='.',
    s=1,
    # c='r'
)
# label axis
plt.ylabel('Chiller set flow [m$^3$/s]')
plt.xlabel('Price [S$/MWh]')
plt.title('TES = 2500 MWh, buildings = flex')
plt.show()

tes_2500MWh = plt.scatter(
    y=TC_flex_2500MWh.loc['TES flow [qbm/s]'].drop(['IDs'], axis=0).values,
    x=parameters.environment['Price [S$/MWh]'].values,
    marker='.',
    s=1,
    # c='r'
)
# label axis
plt.ylabel('TES flow [m$^3$/s]')
plt.xlabel('Price [S$/MWh]')
plt.title('TES = 2500 MWh, buildings = flex')
plt.show()

chs_0MWh = plt.scatter(
    y=TC_fixed25_0MWh.loc['Chiller-set flow [qbm/s]'].drop(['IDs'], axis=0).values,
    x=parameters.environment['Price [S$/MWh]'].values,
    marker='.',
    s=1,
    # c='r'
)
# label axis
plt.ylabel('Chiller set flow [m$^3$/s]')
plt.xlabel('Price [S$/MWh]')
plt.title('TES = 0 MWh, buildings = inflex')
plt.show()

tes_0MWh = plt.scatter(
    y=TC_fixed25_0MWh.loc['TES flow [qbm/s]'].drop(['IDs'], axis=0).values,
    x=parameters.environment['Price [S$/MWh]'].values,
    marker='.',
    s=1,
    # c='r'
)
# label axis
plt.ylabel('TES flow [m$^3$/s]')
plt.xlabel('Price [S$/MWh]')
plt.title('TES = 0 MWh, buildings = inflex')
plt.show()