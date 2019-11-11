import os
import pandas as pd
import pyomo.environ as py

# ======================================================================================================================
# Linear optimization of district cooling system's load-curve CLASS
# ======================================================================================================================


class LinearOptimizer:
    """
    Constructs a linear optimization problem for operating the district cooling system at a minimal cost of electricity
    """

    # INITIALIZATION ===================================================================================================

    def __init__(
        self,
        parameters,
        coolinggrid,
        coolingplant,
        buildings_dict
    ):

        # Save parameter-object ----------------------------------------------------------------------------------------
        self.parameters = parameters

        # Save model-objects -------------------------------------------------------------------------------------------
        self.modelled_grid = coolinggrid
        self.modelled_plant = coolingplant
        self.modelled_buildings_dict = buildings_dict

        # Create Gurobi-Solver -----------------------------------------------------------------------------------------
        self.solver = py.SolverFactory('gurobi')

    # METHOD DEFINITIONS ===============================================================================================

    # Methods building the PYOMO problem -------------------------------------------------------------------------------

    def build_and_solve_problem(
        self,
        ets_head_difference_time_array,
        distributed_secondary_pumping=False
    ):
        # Create PYOMO-Problem -----------------------------------------------------------------------------------------
        problem = py.ConcreteModel(
            name="OptimalLoadCurve"
        )

        # Create PYOMO-Sets --------------------------------------------------------------------------------------------
        problem.time_set = py.Set(
            initialize=self.parameters.environment.index,
            ordered=True
        )
        problem.building_ids = py.Set(
            initialize=self.parameters.buildings.index,
            ordered=True
        )
        problem.line_ids = py.Set(
            initialize=self.parameters.lines.index,
            ordered=True
        )
        problem.node_ids = py.Set(
            initialize=self.parameters.nodes.index,
            ordered=True
        )

        # Create PYOMO-Variables ---------------------------------------------------------------------------------------
        problem.chillers_flow_var = py.Var(
            problem.time_set,
            domain=py.NonNegativeReals
        )
        problem.storage_flow_var = py.Var(
            problem.time_set,
            domain=py.Reals
        )
        problem.ets_flows_var = py.Var(
            problem.time_set,
            problem.building_ids,
            domain=py.NonNegativeReals
        )

        # Create Constraints and related pseudo PYOMO-Variables --------------------------------------------------------

        # CONSTRAINT 1: Heat flow taken in by chiller-set (=cooling power) can not overstep its cooling capacity
        """ 1. Chiller-set's cooling power is introduced as pseudo-variable, with the chiller-set's capacity  as upper 
        boundary. """
        problem.chillers_cooling_power = py.Var(
            problem.time_set,
            domain=py.NonNegativeReals,
            bounds=(
                0,
                self.parameters.cooling_plant["chiller-set cooling capacity [W]"]
            )
        )
        """ 2. Chiller-set's cooling power is linked with the variable of chiller-set's water flow."""
        def chillers_cool_flow_rule(
            problem,
            time_step
        ):
            rule = (
                    problem.chillers_cooling_power[time_step]
                    == self.modelled_plant.get_chillers_evaporator_heat_flow(
                        problem.chillers_flow_var[time_step]
                    )
            )
            return rule
        problem.chillers_cool_flow_rule_constraint = py.Constraint(
            problem.time_set,
            rule=chillers_cool_flow_rule
        )

        # CONSTRAINT 2: Energy Capacity of Thermal Energy Storage can not be overstepped
        """ 1. Storage energy content is introduced as pseudo-variable with its capacity as upper boundary """
        problem.storage_energy_content = py.Var(
            problem.time_set,
            domain=py.NonNegativeReals,
            bounds=(
                0,
                self.parameters.cooling_plant["TES energy capacity [J]"]
            )
        )
        """ 2. Storage's flows are linked with its energy content"""
        def storage_flow_and_energy_content_rule(
            problem,
            time_step
        ):
            if time_step == 1:
                rule = (
                    problem.storage_energy_content[time_step]
                    == (
                        self.parameters.cooling_plant["TES energy capacity [J]"]
                        * self.parameters.cooling_plant["TES initial charge ratio [-]"]
                        + self.modelled_plant.get_storage_energy_change_optimization_rule(
                            problem.storage_flow_var[time_step]
                        )
                    )
                )
            else:
                rule = (
                    problem.storage_energy_content[time_step]
                    == (
                        problem.storage_energy_content[(time_step-1)]
                        + self.modelled_plant.get_storage_energy_change_optimization_rule(
                            problem.storage_flow_var[time_step]
                        )
                    )
                )
            return rule
        problem.storage_flow_and_energy_content_constraint = py.Constraint(
            problem.time_set,
            rule=storage_flow_and_energy_content_rule
        )

        # CONSTRAINT 3: In the last time step TES energy content has to comply with predefined terminal charge ratio
        def storage_terminal_charge_rule(
            problem
        ):
            rule = (
                problem.storage_energy_content[problem.time_set[-1]]
                == (
                    self.parameters.cooling_plant["TES energy capacity [J]"]
                    * self.parameters.cooling_plant["TES terminal charge ratio [-]"]
                )
            )
            return rule
        problem.storage_terminal_charge_constraint = py.Constraint(
            rule=storage_terminal_charge_rule
        )

        # CONSTRAINT 4: Demand and supply of chilled water have to be equal in the system
        """ 1. Total flow demand of the distribution system, which occurs at the reference-node, is introduced as
        pseudo-variable """
        problem.total_flow_demand = py.Var(
            problem.time_set,
            domain=py.NonNegativeReals
        )
        """ 2. Total flow demand of the distribution system, which occurs at the reference-node, is set equal to the sum
         of chiller-set flow and Thermal Energy Storage flow"""
        def demand_and_supply_of_flow_rule(
            problem,
            time_step
        ):
            rule = (
                    problem.chillers_flow_var[time_step]
                    + problem.storage_flow_var[time_step]
                    == problem.total_flow_demand[time_step]
            )
            return rule
        problem.demand_and_supply_of_flow_constraint = py.Constraint(
            problem.time_set,
            rule=demand_and_supply_of_flow_rule
        )

        # CONSTRAINT 5: Flow balances are to be complied at every node of the Digraph
        """ 1. Line's water flows are introduced as pseudo-variable """
        problem.lines_flow = py.Var(
            problem.time_set,
            problem.line_ids,
            domain=py.NonNegativeReals,
        )
        """ 2. Total flow demand, the line's flows and building's water consumptions are all linked through the nodal 
        flow balances of the digraph"""
        def nodal_flow_balances_of_grid_rule(
            problem,
            time_step,
            node_id
        ):
            # Find IDs of all inflowing and outflowing lines of current node
            inflowing_lines = []
            outflowing_lines = []
            for line_id in self.parameters.lines.index:
                if self.modelled_grid.incidence_matrix_complete[node_id][line_id] == -1:
                    outflowing_lines.append(line_id)
                if self.modelled_grid.incidence_matrix_complete[node_id][line_id] == 1:
                    inflowing_lines.append(line_id)

            # Create nodal flow balance equations in dependence of node-type
            if self.parameters.nodes["Type"][node_id] == "building":
                rule = (
                    problem.ets_flows_var[time_step, node_id]
                    == (
                        py.quicksum(problem.lines_flow[time_step, line_id] for line_id in inflowing_lines)
                        - py.quicksum(problem.lines_flow[time_step, line_id] for line_id in outflowing_lines)
                    )
                )
            elif self.parameters.nodes["Type"][node_id] == "junction":
                rule = (
                    0
                    == (
                        py.quicksum(problem.lines_flow[time_step, line_id] for line_id in inflowing_lines)
                        - py.quicksum(problem.lines_flow[time_step, line_id] for line_id in outflowing_lines)
                    )
                )
            elif self.parameters.nodes["Type"][node_id] == "reference":
                rule = (
                    - problem.total_flow_demand[time_step]
                    == (
                        py.quicksum(problem.lines_flow[time_step, line_id] for line_id in inflowing_lines)
                        - py.quicksum(problem.lines_flow[time_step, line_id] for line_id in outflowing_lines)
                    )
                )
            else:
                rule = "Error: unknown node-type in parameters"
            return rule
        problem.nodal_flow_balances_grid_constraint = py.Constraint(
            problem.time_set,
            problem.node_ids,
            rule=nodal_flow_balances_of_grid_rule
        )

        # CONSTRAINT 6: Velocity boundaries for water flow in pipes
        """ 1. Line's velocities are introduced as pseudo-variable, with lower and upper boundaries """
        problem.lines_velocity = py.Var(
            problem.time_set,
            problem.line_ids,
            domain=py.NonNegativeReals,
            bounds=(
                self.parameters.distribution_system["minimum pipe velocity [m/s]"],
                self.parameters.distribution_system["maximum pipe velocity [m/s]"]
            )
        )
        """ 2. Line's velocities are linked with line's flows """
        def lines_flow_and_velocity_rule(
            problem,
            time_step,
            line_id
        ):
            rule = (
                    problem.lines_velocity[time_step, line_id]
                    == self.modelled_grid.get_pipe_velocity(
                        pipe_flow=problem.lines_flow[time_step, line_id],
                        pipe_diameter=self.parameters.lines["Diameter [m]"][line_id]
                    )
            )
            return rule
        problem.lines_flow_and_velocity_constraint = py.Constraint(
            problem.time_set,
            problem.line_ids,
            rule=lines_flow_and_velocity_rule
        )

        # CONSTRAINT 7: Flow in ETS results in heat-inflow coming from building (from the grid's perspective)
        """ 1. Heat flow leaving building is introduced as pseudo-variable"""
        problem.buildings_heat_inflow = py.Var(
            problem.time_set,
            problem.building_ids,
            domain=py.NonNegativeReals
        )
        """ 2. Heat flow from building is linked to water flow to building"""
        def buildings_flow_and_heat_rule(
            problem,
            time_step,
            building_id
        ):
            rule = (
                    problem.buildings_heat_inflow[time_step, building_id]
                    == self.modelled_grid.get_heat_intake_from_ets_flow(
                        problem.ets_flows_var[time_step, building_id]
                    )
            )
            return rule
        problem.buildings_flow_and_heat_constraint = py.Constraint(
            problem.time_set,
            problem.building_ids,
            rule=buildings_flow_and_heat_rule
        )

        # # CONSTRAINT 8: Temperature boundaries of buildings
        # """ 1. Building temperatures are introduced as pseudo-variables """
        # problem.buildings_temperature = py.Var(
        #     problem.time_set,
        #     problem.building_ids,
        #     domain=py.NonNegativeReals
        # )
        # """ 2. Building temperatures are limited by lower and upper boundaries, as defined in simple_buildings.csv """
        # def buildings_temperature_boundaries_rule(
        #         problem,
        #         time_step,
        #         building_id
        # ):
        #     rule = (
        #         self.parameters.buildings["Temperature MIN [Celsius]"][building_id],
        #         problem.buildings_temperature[time_step, building_id],
        #         self.parameters.buildings["Temperature MAX [Celsius]"][building_id]
        #     )
        #     return rule
        #
        # problem.buildings_temperature_boundaries_constraint = py.Constraint(
        #     problem.time_set,
        #     problem.building_ids,
        #     rule=buildings_temperature_boundaries_rule
        # )

        # # CONSTRAINT 9: Terminal temperatures in buildings have to equal initial temperatures
        # def buildings_temperature_terminal_rule(
        #         problem,
        #         building_id
        # ):
        #     rule = (
        #         problem.buildings_temperature[problem.time_set[-1], building_id]
        #         == self.parameters.buildings["Initial Temperature [Celsius]"][building_id]
        #     )
        #     return rule
        # problem.buildings_temperature_terminal_constraint = py.Constraint(
        #     problem.building_ids,
        #     rule=buildings_temperature_terminal_rule
        # )

        # # CONSTRAINT 10: Temperatures in buildings are linked with heat flows taken-in from buildings (=cooling)
        # def buildings_temperature_and_flow_rule(
        #         problem,
        #         time_step,
        #         building_id
        # ):
        #     rule = (
        #         problem.buildings_temperature[time_step, building_id]
        #         == self.modelled_buildings_dict[building_id].get_building_temperature(
        #             time_step,
        #             building_id,
        #             problem.buildings_heat_inflow  # 2-dimensional, time and building-number!
        #         )
        #     )
        #     return rule
        #
        # problem.buildings_temperature_and_flow_constraint = py.Constraint(
        #     problem.time_set,
        #     problem.building_ids,
        #     rule=buildings_temperature_and_flow_rule
        # )

        # CONSTRAINT 8.1: Buildings' initial state constraint
        """ 1. State vector timeseries is instantiated as variable"""
        problem.variable_state_timeseries = py.Var(
            problem.time_set,
            [
                (building_id, state)
                for building_id, building in self.modelled_buildings_dict.items()
                for state in building.set_states
            ],
            domain=py.Reals
        )

        """ 2. Initial state vector is defined"""
        problem.building_initial_state_constraints = py.ConstraintList()
        for building_id, building in self.modelled_buildings_dict.items():
            for state in building.set_states:
                problem.building_initial_state_constraints.add(
                    problem.variable_state_timeseries[problem.time_set[1], (building_id, state)]
                    ==
                    building.set_state_initial[state]
                )

        # CONSTRAINT 8.2: Buildings' state equation constraint
        """ 1. Control vector timeseries is instantiated as variable"""
        problem.variable_control_timeseries = py.Var(
            problem.time_set,
            [
                (building_id, control)
                for building_id, building in self.modelled_buildings_dict.items()
                for control in building.set_controls
            ],
            domain=py.NonNegativeReals
        )
        """ 2. State equation is defined"""
        problem.building_state_equation_constraints = py.ConstraintList()
        for building_id, building in self.modelled_buildings_dict.items():
            for state in building.set_states:
                for timestep in problem.time_set:
                    if timestep != problem.time_set[-1]:
                        problem.building_state_equation_constraints.add(
                            problem.variable_state_timeseries[timestep + 1, (building_id, state)]
                            ==
                            (
                                py.quicksum(
                                    building.state_matrix.loc[state, state_other]
                                    * problem.variable_state_timeseries[timestep, (building_id, state_other)]
                                    for state_other in building.set_states
                                )
                                + py.quicksum(
                                    building.control_matrix.loc[state, control]
                                    * problem.variable_control_timeseries[timestep, (building_id, control)]
                                    for control in building.set_controls
                                )
                                + py.quicksum(
                                    building.disturbance_matrix.loc[state, disturbance]
                                    * building.disturbance_timeseries.loc[building.set_timesteps[timestep - 1], disturbance]
                                    for disturbance in building.set_disturbances
                                )
                            )
                        )

        # CONSTRAINT 9.1: Buildings' output equation constraint
        """ 1. Output vector timeseries is instantiated as variable"""
        problem.variable_output_timeseries = py.Var(
            problem.time_set,
            [
                (building_id, output)
                for building_id, building in self.modelled_buildings_dict.items()
                for output in building.set_outputs
            ],
            domain=py.Reals
        )
        """ 2. Output equation is defined"""
        problem.building_output_equation_constraints = py.ConstraintList()
        for building_id, building in self.modelled_buildings_dict.items():
            for output in building.set_outputs:
                for timestep in problem.time_set:
                    problem.building_output_equation_constraints.add(
                        problem.variable_output_timeseries[timestep, (building_id, output)]
                        ==
                        (
                            py.quicksum(
                                building.state_output_matrix.loc[output, state]
                                * problem.variable_state_timeseries[timestep, (building_id, state)]
                                for state in building.set_states
                            )
                            + py.quicksum(
                                building.control_output_matrix.loc[output, control]
                                * problem.variable_control_timeseries[timestep, (building_id, control)]
                                for control in building.set_controls
                            )
                            + py.quicksum(
                                building.disturbance_output_matrix.loc[output, disturbance]
                                * building.disturbance_timeseries.loc[building.set_timesteps[timestep - 1], disturbance]
                                for disturbance in building.set_disturbances
                            )
                        )
                    )

        # CONSTRAINT 9.2: Output vector minimum / maximum constraint
        """ 1. Minimum / maximum constraints are defined"""
        problem.building_output_bounds_constraints = py.ConstraintList()
        for building_id, building in self.modelled_buildings_dict.items():
            for output in building.set_outputs:
                for timestep in problem.time_set:
                    # Minimum.
                    problem.building_output_bounds_constraints.add(
                        problem.variable_output_timeseries[timestep, (building_id, output)]
                        >=
                        building.output_constraint_timeseries_minimum.loc[building.set_timesteps[timestep - 1], output]
                    )
                    # Maximum.
                    problem.building_output_bounds_constraints.add(
                        problem.variable_output_timeseries[timestep, (building_id, output)]
                        <=
                        building.output_constraint_timeseries_maximum.loc[building.set_timesteps[timestep - 1], output]
                    )

        # CONSTRAINT 10: Connect building to grid
        """ 1. Building heat flow from grid constraint is defined"""
        problem.building_grid_constraints = py.ConstraintList()
        for building_id, building in self.modelled_buildings_dict.items():
            for timestep in problem.time_set:
                problem.building_grid_constraints.add(
                    problem.buildings_heat_inflow[timestep, building_id]
                    ==
                    py.quicksum(
                        (1.0 * problem.variable_output_timeseries[timestep, (building_id, output)])
                        if 'electric_power' in output else 0.0  # TODO: Define output for thermal power in CoBMo
                        for output in building.set_outputs
                    )
                )

        # CONSTRAINT 11: District cooling plant's total electric power consumption is related to chillers flow and
        # storage flow variables
        """ 1. District cooling plant's total electric power consumption is introduced as pseudo-variables """
        problem.district_cooling_plant_total_power = py.Var(
            problem.time_set,
            domain=py.NonNegativeReals
        )
        """ 2. District cooling plant's total electric power consumption is linked with the two variables of chiller-set
         flow and thermal energy storage flow """
        def district_cooling_plant_total_power_rule(
            problem,
            time_step
        ):
            rule = (
                    problem.district_cooling_plant_total_power[time_step]
                    == self.modelled_plant.get_plant_total_power(
                        problem.chillers_flow_var[time_step],
                        problem.storage_flow_var[time_step],
                        self.parameters.environment["Air wet-bulb temperature [°C]"][time_step]
                    )
            )
            return rule
        problem.district_cooling_plant_total_power_constraint = py.Constraint(
            problem.time_set,
            rule=district_cooling_plant_total_power_rule
        )

        # CONSTRAINT 12: Distribution system's total electric power consumption is related to building's flow variables
        """ 1. Distribution system's total electric power consumption is introduced as pseudo-variables """
        problem.distribution_system_total_power = py.Var(
            problem.time_set,
            domain=py.NonNegativeReals
        )
        """ 2. Distribution system's total electric power consumption is linked to building's flow variables, under 
        utilisation of the given hydraulic equilibrium (holding the estimated head losses) and the chosen pumping scheme
        for the distribution system:
            - central secondary pumping (False)
            - or distributed secondary pumping (True) """
        def distribution_system_pumping_power_rule(
            problem,
            time_step
        ):
            # Distributed Secondary Pumping
            if distributed_secondary_pumping:
                rule = (
                    problem.distribution_system_total_power[time_step]
                    == py.quicksum(
                        self.parameters.physics["water density [kg/m^3]"]
                        * self.parameters.physics["gravitational acceleration [m^2/s]"]
                        * self.parameters.distribution_system["pump efficiency secondary pump [-]"]
                        * ets_head_difference_time_array[time_step][building_id]
                        * problem.ets_flows_var[time_step, building_id]
                        for building_id in problem.building_ids
                    )
                )
                return rule
            # Central Secondary Pumping
            else:
                rule = (
                    problem.distribution_system_total_power[time_step]
                    == (
                        self.parameters.physics["water density [kg/m^3]"]
                        * self.parameters.physics["gravitational acceleration [m^2/s]"]
                        * self.parameters.distribution_system["pump efficiency secondary pump [-]"]
                        * ets_head_difference_time_array[time_step].max()
                        * problem.total_flow_demand[time_step]
                    )
                )
                return rule

        problem.distribution_system_pumping_power_constraint = py.Constraint(
            problem.time_set,
            rule=distribution_system_pumping_power_rule
        )

        # Create PYOMO-Objective ---------------------------------------------------------------------------------------
        def objective_cost_minimum(
            problem
        ):
            rule = (
                py.quicksum(
                    (
                        self.parameters.environment["Price [S$/MWh]"][time_step]
                        / (10 ** 6)
                        * (
                            problem.distribution_system_total_power[time_step]
                            + problem.district_cooling_plant_total_power[time_step]
                        )
                        * 0.5
                    ) for time_step in problem.time_set
                )
            )
            return rule

        problem.objective = py.Objective(
            rule=objective_cost_minimum,
            sense=1
        )

        # Give problem to solver and let it solve ----------------------------------------------------------------------
        self.solver.solve(problem, tee=False)

        # Return the solved problem ------------------------------------------------------------------------------------
        return problem

    def get_solution_as_dataframe(
        self,
        problem,
        save=False,
        index_for_saving=1,
    ):
        dcp_power_dict = {
            time_step: problem.district_cooling_plant_total_power[time_step]() for time_step in problem.time_set
        }
        dcp_power_frame = pd.DataFrame(
            data=dcp_power_dict,
            index=[None]
        )
        evaporator_heat_dict = {
            time_step: problem.chillers_cooling_power[time_step]() for time_step in problem.time_set
        }
        evaporator_heat_frame = pd.DataFrame(
            data=evaporator_heat_dict,
            index=[None]
        )
        chillers_flow_dict = {
            time_step: problem.chillers_flow_var[time_step]() for time_step in problem.time_set
        }
        chillers_flow_frame = pd.DataFrame(
            data=chillers_flow_dict,
            index=[None]
        )
        storage_flow_dict = {
            time_step: problem.storage_flow_var[time_step]() for time_step in problem.time_set
        }
        storage_flow_frame = pd.DataFrame(
            data=storage_flow_dict,
            index=[None]
        )
        storage_energy_dict = {
            time_step: problem.storage_energy_content[time_step]() for time_step in problem.time_set
        }
        storage_energy_frame = pd.DataFrame(
            data=storage_energy_dict,
            index=[None]
        )
        ds_power_dict = {
            time_step: problem.distribution_system_total_power[time_step]() for time_step in problem.time_set
        }
        ds_power_frame = pd.DataFrame(
            data=ds_power_dict,
            index=[None]
        )
        total_flow_dict = {
            time_step: problem.total_flow_demand[time_step]() for time_step in problem.time_set
        }
        total_flow_frame = pd.DataFrame(
            data=total_flow_dict,
            index=[0]
        )
        ets_flow_dict = {
            time_step: [
                problem.ets_flows_var[time_step, building_id]() for building_id in problem.building_ids
            ] for time_step in problem.time_set
        }
        ets_flow_frame = pd.DataFrame(
            data=ets_flow_dict,
            index=[building_id for building_id in problem.building_ids]
        )
        lines_flow_dict = {
            time_step: [
                problem.lines_flow[time_step, line_id]() for line_id in problem.line_ids
            ] for time_step in problem.time_set
        }
        lines_flow_frame = pd.DataFrame(
            data=lines_flow_dict,
            index=[line_id for line_id in problem.line_ids]
        )
        lines_velocity_dict = {
            time_step: [
                problem.lines_velocity[time_step, line_id]() for line_id in problem.line_ids
            ] for time_step in problem.time_set
        }
        lines_velocity_frame = pd.DataFrame(
            data=lines_velocity_dict,
            index=[line_id for line_id in problem.line_ids]
        )
        buildings_heat_inflow_dict = {
            time_step: [
                problem.buildings_heat_inflow[time_step, building_id]() for building_id in problem.building_ids
            ] for time_step in problem.time_set
        }
        buildings_heat_inflow_frame = pd.DataFrame(
            data=buildings_heat_inflow_dict,
            index=[building_id for building_id in problem.building_ids]
        )
        # buildings_temperature_dict = {
        #     time_step: [
        #         problem.buildings_temperature[time_step, building_id]() for building_id in problem.building_ids
        #     ] for time_step in problem.time_set
        # }
        # buildings_temperature_frame = pd.DataFrame(
        #     data=buildings_temperature_dict,
        #     index=[building_id for building_id in problem.building_ids]
        # )
        solution_frame = pd.concat(
            [
                dcp_power_frame,
                evaporator_heat_frame,
                chillers_flow_frame,
                storage_flow_frame,
                storage_energy_frame,
                ds_power_frame,
                total_flow_frame,
                ets_flow_frame,
                lines_flow_frame,
                lines_velocity_frame,
                buildings_heat_inflow_frame,
                # buildings_temperature_frame
             ],
            keys=[
                'DCP power [W]',
                'Heat-intake evaporator [W]',
                'Chiller-set flow [qbm/s]',
                'TES flow [qbm/s]',
                'TES energy [J]',
                'DS power [W]',
                'Total flow [qbm/s]',
                'ETS flow [qbm/s]',
                'Lines flow [qbm/s]',
                'Lines velocity [m/s]',
                'Heat-inflow buildings [W]',
                # 'Building temperature [C]'
            ]
        )
        solution_frame.index.names = ['VARIABLES', 'IDs']

        if save:
            solution_frame.to_csv(
                os.path.join(
                    os.path.dirname(os.path.normpath(__file__)),
                    '..', 'results', 'csv_files', str(index_for_saving) + '_solved_problem.csv'
                )
            )

        return solution_frame

    def iterative_solver(
        self,
        error_differential,
        distributed_secondary_pumping=False
    ):
        # Initializations for iteration --------------------------------------------------------------------------------

        iteration = 0
        iteration_condition = False
        ets_flow_time_array_previous_iteration = 0
        solution_linear_optimization_previous_iteration = 0

        # Iteration ----------------------------------------------------------------------------------------------------

        while not iteration_condition:

            # Iteration counter
            iteration += 1
            print("Iteration: "+str(iteration))

            # Setting ETS flows
            if iteration == 1:
                ets_flow_time_array = self.modelled_grid.build_ets_flow_time_array(
                    [0 for building_id in self.parameters.buildings.index]
                )
            else:
                ets_flow_time_dict = {
                    time_step: [
                        (
                            ets_flow_time_array_previous_iteration[time_step][building_id]
                            + solution_linear_optimization_previous_iteration.ets_flows_var[time_step, building_id]()
                        )
                        / 2
                        for building_id in self.parameters.buildings.index
                    ]
                    for time_step in self.parameters.environment.index
                }
                ets_flow_time_array = pd.DataFrame(
                    data=ets_flow_time_dict,
                    index=[building_id for building_id in self.parameters.buildings.index]
                )

            # Non-linear grid simulation
            grid_simulation = self.modelled_grid.get_grid_simulation(
                ets_flow_time_array
            )

            # Linear optimization with ETS head differences calculated by non-linear grid simulation
            solution_linear_optimization = self.build_and_solve_problem(
                ets_head_difference_time_array=grid_simulation.loc["Head difference over ETSs [m]"],
                distributed_secondary_pumping=distributed_secondary_pumping
            )

            # Check if iteration condition is complied
            boolean_expression_dict = {
                time_step: [
                    (
                        abs(
                            ets_flow_time_array[time_step][building_id]
                            - solution_linear_optimization.ets_flows_var[time_step, building_id]()
                        )
                        < error_differential
                    )
                    for building_id in self.parameters.buildings.index
                    ]
                for time_step in self.parameters.environment.index
            }
            boolean_expression_frame = pd.DataFrame(
                data=boolean_expression_dict,
                index=[building_id for building_id in self.parameters.buildings.index]
            )
            print(boolean_expression_frame)
            iteration_condition = boolean_expression_frame.all(axis=None)

            # Prepare next potential iteration
            ets_flow_time_array_previous_iteration = ets_flow_time_array
            solution_linear_optimization_previous_iteration = solution_linear_optimization

        # Return utilized ETS flow time array and Pyomo problem of last iteration, who have converged close enough -----

        return ets_flow_time_array, solution_linear_optimization