import districtcooling as dc
import pandas as pd
import matplotlib.pyplot as plt

# Generate objects =====================================================================================================

parameters = dc.ParametersReader()
grid = dc.CoolingGrid(parameters=parameters)
plant = dc.CoolingPlant(parameters=parameters)
plotter = dc.Plotter(parameters=parameters)

# Read data ============================================================================================================

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

# Evaluation ===========================================================================================================

costs_flex_dict = {
    '0MWh': TC_flex_0MWh.loc['Costs in [S$]'].sum(),
    '625MWh': TC_flex_625MWh.loc['Costs in [S$]'].sum(),
    '1250MWh': TC_flex_1250MWh.loc['Costs in [S$]'].sum(),
    '1875MWh': TC_flex_1875MWh.loc['Costs in [S$]'].sum(),
    '2500MWh': TC_flex_2500MWh.loc['Costs in [S$]'].sum()
}
costs_flex_df = pd.DataFrame.from_dict(
    data=costs_flex_dict,
    orient='index',
    columns=['Overall year costs in [S$]']
)
print(
    costs_flex_df
)
plot = costs_flex_df.plot(
    kind='bar',
    use_index=True,
    y='Overall year costs in [S$]'
)
plt.show()