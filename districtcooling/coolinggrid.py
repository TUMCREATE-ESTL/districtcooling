import pandas as pd
import numpy as np

# ======================================================================================================================
# Model of distribution system (=cooling grid) CLASS
# ======================================================================================================================


class CoolingGrid:
    """
    Defines the model of the distribution system, including distribution piping system (DPS) and energy transfer
    stations (ETS)
    """

    # INITIALIZATION ===================================================================================================

    def __init__(
        self,
        parameters
    ):
        # Saving parameters --------------------------------------------------------------------------------------------

        self.parameters = parameters

        # Forming incidence matrices of the Digraph --------------------------------------------------------------------

        # Incidence matrix of full grid
        dict_temp = {}
        for n_id in self.parameters.nodes.index:
            list_temp = []
            for l_id in self.parameters.lines.index:
                if n_id == self.parameters.lines["Start"][l_id]:
                    list_temp.append(-1)
                elif n_id == self.parameters.lines["End"][l_id]:
                    list_temp.append(+1)
                else:
                    list_temp.append(0)
                dict_temp[n_id] = list_temp
        self.incidence_matrix_complete = pd.DataFrame(dict_temp, columns=dict_temp.keys())
        self.incidence_matrix_complete.index = list(self.parameters.lines.index)

        # Excluding reference node (root) - having a predefined head of 0 - from matrix, resulting in square incidence
        # matrix, suitable for direct calculation
        for n_id in self.parameters.nodes.index:
            if self.parameters.nodes["Type"][n_id] == "reference":
                self.incidence_matrix_potential = self.incidence_matrix_complete[[n_id]]
                self.incidence_matrix = self.incidence_matrix_complete.drop(columns=n_id)

        # Transposing square incidence matrix
        self.incidence_matrix_transposed = self.incidence_matrix.transpose()

    # METHOD DEFINITIONS ===============================================================================================

    # Methods to calculate the steady-state, non-linear hydraulic-equilibrium of a tree-like grid ----------------------

    def build_ets_flow_time_array(
            self,
            ets_flow_vector
    ):
        ets_flow_dict = {
            time_step: ets_flow_vector
            for time_step in self.parameters.environment.index
        }
        ets_flows_frame = pd.DataFrame(
            data=ets_flow_dict,
            index=list(self.parameters.buildings.index)
        )
        return ets_flows_frame

    def get_nodal_consumptions_time_array(
        self,
        ets_flows_time_array
    ):
        # Creating junction-DataFrame relating 0 water consumption with all junction-nodes over time
        junction_nodes_ids = []
        for nodes_id in self.parameters.nodes.index:
            if self.parameters.nodes["Type"][nodes_id] == "junction":
                junction_nodes_ids.append(nodes_id)
        junction_consumptions_dict = {
            time_step: [0*id for id in junction_nodes_ids]
            for time_step in self.parameters.environment.index
        }
        junction_consumptions_frame = pd.DataFrame(
            data=junction_consumptions_dict, index=[id for id in junction_nodes_ids])

        # Merging junction-DataFrame with ets-flow-DataFrame
        nodal_consumptions_over_time = pd.concat([ets_flows_time_array, junction_consumptions_frame])

        # Sort according to index
        nodal_consumptions_over_time.sort_index(inplace=True)

        return nodal_consumptions_over_time

    @staticmethod
    def get_reference_node_consumption_time_row(
            nodal_consumptions_time_array
    ):
        reference_node_consumption_dict = {
            time_step: -nodal_consumptions_time_array[time_step].sum()
            for time_step in nodal_consumptions_time_array.columns
        }
        reference_node_consumption_time_row = pd.DataFrame(
            data=reference_node_consumption_dict,
            index=[0]
        )
        return reference_node_consumption_time_row

    def get_line_flows_time_array(
        self,
        nodal_consumptions_time_array
    ):
        """
        :var nodal_consumption: volumetric flows entering or leaving the grid at its nodes, in [cbm/s].
        :param self.incidence_matrix_transposed: grid-layout expressed as transposed incidence matrix.
        :return: All volumetric flows of the grid's lines listed inside a panda, in [cbm/s].
        """
        line_flows_temp = {
            time_step: np.linalg.solve(
                self.incidence_matrix_transposed.values,
                nodal_consumptions_time_array[time_step].values
            )
            for time_step in nodal_consumptions_time_array.columns
        }
        line_flows = pd.DataFrame(
            data=line_flows_temp,
            index=list(self.incidence_matrix.index))
        return line_flows

    @staticmethod
    def get_pipe_velocity(
        pipe_flow,
        pipe_diameter
    ):
        """
        :var pipe_flow: volumetric flow through the pipe in cubic metres per second [cbm/s].
        :param pipe_diameter: in metres [m].
        :return: pipe's velocity in m per second [m/s].
        """
        pipe_velocity = 4 * pipe_flow / (np.pi * pipe_diameter ** 2)
        return pipe_velocity

    def get_reynold(
        self,
        pipe_flow,
        pipe_diameter
    ):
        """
        :var pipe_flow: volumetric flow through the pipe in cubic metres per second [cbm/s].
        :param pipe_diameter: in metres [m].
        :return: Reynolds number, dimensionless in terms of unit.
        """
        pipe_velocity = self.get_pipe_velocity(pipe_flow, pipe_diameter)

        reynold = np.fabs(pipe_velocity) * pipe_diameter / self.parameters.physics["water kinematic viscosity [m^2/s]"]
        return reynold

    def get_pipe_friction_factor(
        self,
        pipe_flow,
        pipe_diameter,
        pipe_roughness
    ):
        """
        :var pipe_flow: volumetric flow through the pipe in cubic metres per second [cbm/s].
        :param pipe_diameter: in metres [m].
        :param pipe_roughness: absolute roughness (epsilon) in millimeters [mm].
        :return: Darcy-Weisbach friction factor f, dimensionless in terms of unit.
        """
        pipe_velocity = self.get_pipe_velocity(pipe_flow, pipe_diameter)
        reynold = self.get_reynold(pipe_velocity, pipe_diameter)

        # No flow at all
        if reynold == 0:
            pipe_friction_factor = 0
            return pipe_friction_factor

        # Laminar Flow, based on Hagen-Poiseuille velocity profile, analytical correlation
        elif 0 < reynold < 4000:
            pipe_friction_factor = 64 / reynold
            return pipe_friction_factor

        # Turbulent flow, Swamee-Jain formula, approximating correlation of Colebrook-White equation
        elif 4000 <= reynold <= 100000000 and 0.000001 <= ((pipe_roughness/1000) / pipe_diameter) <= 0.01:
            pipe_friction_factor = 1.325 / (
                np.log(
                    (pipe_roughness / 1000) / (3.7 * pipe_diameter) + 5.74 / (reynold ** 0.9)
                )
            ) ** 2
            return pipe_friction_factor

        # Outside of scope:
        else:
            return "Error"

    def get_pipe_head_loss(
        self,
        pipe_flow,
        pipe_diameter,
        pipe_roughness,
        pipe_length
    ):
        """
        :var pipe_flow: volumetric flow through the pipe in cubic metres per second [cbm/s].
        :param pipe_diameter: in metres [m].
        :param pipe_roughness: absolute roughness (epsilon) in millimeters [mm].
        :param pipe_length: in meters [m].
        :return: pipe head in meters of water [m].
        """
        pipe_friction_factor = self.get_pipe_friction_factor(pipe_flow, pipe_diameter, pipe_roughness)

        # Darcy-Weisbach Equation
        pipe_head_loss = pipe_friction_factor * 8 * pipe_length * pipe_flow * np.fabs(pipe_flow) / (
                self.parameters.physics["gravitational acceleration [m^2/s]"] * (np.pi ** 2) * pipe_diameter ** 5
        )
        return pipe_head_loss

    def get_line_head_loss_time_array(
        self,
        line_flow_time_array
    ):
        """
        :var line_flows: all volumetric flows through the lines (pipes) listed inside a panda,
         in cubic metres per second [cbm/s].
        :param self.lines_parameters: all parameters related to the grid's lines.
        :return: All head losses occurring over the grid's lines due to friction listed inside a panda, in meters of
        water [m].
        """
        line_head_loss_dict = {
            time_step: [
                self.get_pipe_head_loss(
                    line_flow_time_array[time_step][line_id],
                    self.parameters.lines["Diameter [m]"][line_id],
                    self.parameters.lines["Absolute Roughness [mm]"][line_id],
                    self.parameters.lines["Length [m]"][line_id]
                )
                for line_id in line_flow_time_array.index
            ]
            for time_step in line_flow_time_array.columns
        }
        line_head_loss_frame = pd.DataFrame(
            data=line_head_loss_dict,
            index=list(line_flow_time_array.index)
        )
        return line_head_loss_frame

    def get_nodal_head_time_array(
        self,
        line_head_loss_time_array
    ):
        """
        :var line_heads: all head losses occurring over the grid's lines due to friction listed inside a panda, in
        meters of water [m].
        :param self.incidence_matrix: grid-layout expressed as incidence matrix.
        :return: nodal_heads: Total heads occurring at all nodes of the grid, listed inside a panda, in meters of
        water [m].
        """
        nodal_head_calculation_dict = {
            time_step: np.linalg.solve(
                self.incidence_matrix.values,
                -line_head_loss_time_array[time_step].values
                )
            for time_step in line_head_loss_time_array.columns
        }
        nodal_head_calculation_frame = pd.DataFrame(
            data=nodal_head_calculation_dict,
            index=list(self.incidence_matrix_transposed.index)
        )
        reference_node_head_dict = {
            time_step: 0
            for time_step in line_head_loss_time_array.columns
        }
        reference_node_head_frame = pd.DataFrame(
            data=reference_node_head_dict,
            index=[0]
        )
        all_nodal_heads_frame = pd.concat(
            [
                reference_node_head_frame,
                nodal_head_calculation_frame
             ]
        )
        return all_nodal_heads_frame

    def get_tree_equilibrium_time_array(
        self,
        ets_flow_time_array
    ):
        nodal_consumptions_time_array = self.get_nodal_consumptions_time_array(
            ets_flows_time_array=ets_flow_time_array
        )
        reference_node_consumption_time_row = self.get_reference_node_consumption_time_row(
            nodal_consumptions_time_array=nodal_consumptions_time_array
        )
        line_flow_time_array = self.get_line_flows_time_array(
            nodal_consumptions_time_array=nodal_consumptions_time_array
        )
        line_head_loss_time_array = self.get_line_head_loss_time_array(
            line_flow_time_array=line_flow_time_array
        )
        nodal_head_time_array = self.get_nodal_head_time_array(
            line_head_loss_time_array=line_head_loss_time_array
        )
        tree_equilibrium_time_array = pd.concat(
            [
                nodal_consumptions_time_array,
                reference_node_consumption_time_row,
                line_flow_time_array,
                line_head_loss_time_array,
                nodal_head_time_array
            ],
            keys=[
                'Nodal consumptions [qbm/s]',
                'Ref. node consumption [qbm/s]',
                'Flow in lines [qbm/s]',
                'Head loss over lines [m]',
                'Total head at nodes [m]'
            ]
        )
        tree_equilibrium_time_array.index.names = ['VARIABLES', 'IDs']
        return tree_equilibrium_time_array

    # Methods for calculating electrical power demand of pumps in distribution system ----------------------------------

    def get_ets_head_difference_time_array(
        self,
        nodal_head_time_array
    ):
        ets_head_difference_time_array_dict = {
            time_step: [
                2
                * np.fabs(nodal_head_time_array[time_step][building_id])
                + self.parameters.distribution_system["head loss in heat exchanger ETS [m]"]
                for building_id in self.parameters.buildings.index
            ] for time_step in nodal_head_time_array.columns
        }
        ets_head_difference_time_array_frame = pd.DataFrame(
            data=ets_head_difference_time_array_dict,
            index=list(self.parameters.buildings.index)
        )
        return ets_head_difference_time_array_frame

    def get_central_pumping_power_time_row(
        self,
        ets_head_difference_time_array,
        central_flow_time_row
    ):
        central_pumping_power_time_dict = {
            time_step: (
                    self.parameters.physics["water density [kg/m^3]"]
                    * self.parameters.physics["gravitational acceleration [m^2/s]"]
                    * self.parameters.distribution_system["pump efficiency secondary pump [-]"]
                    * ets_head_difference_time_array[time_step].max()
                    * np.fabs(central_flow_time_row[time_step][0])
            )
            for time_step in ets_head_difference_time_array.columns
        }
        central_pumping_power_time_row = pd.DataFrame(
            data=central_pumping_power_time_dict,
            index=[0]
        )
        return central_pumping_power_time_row

    def get_distributed_pumping_power_time_array(
        self,
        ets_head_difference_time_array,
        nodal_consumptions_time_array
    ):
        distributed_pumping_power_time_dict = {
            time_step: [
                self.parameters.physics["water density [kg/m^3]"]
                * self.parameters.physics["gravitational acceleration [m^2/s]"]
                * self.parameters.distribution_system["pump efficiency secondary pump [-]"]
                * ets_head_difference_time_array[time_step][ets_id]
                * np.fabs(nodal_consumptions_time_array[time_step][ets_id])
                for ets_id in ets_head_difference_time_array.index
            ]
            for time_step in ets_head_difference_time_array.columns
        }
        distributed_pumping_power_time_array = pd.DataFrame(
            data=distributed_pumping_power_time_dict,
            index=list(ets_head_difference_time_array.index)
        )
        return distributed_pumping_power_time_array

    def get_grid_pumping(
        self,
        tree_equilibrium_time_array
    ):
        ets_head_difference_time_array = self.get_ets_head_difference_time_array(
            nodal_head_time_array=tree_equilibrium_time_array.loc["Total head at nodes [m]"]
        )
        central_pumping_power_time_row = self.get_central_pumping_power_time_row(
            ets_head_difference_time_array=ets_head_difference_time_array,
            central_flow_time_row=tree_equilibrium_time_array.loc["Ref. node consumption [qbm/s]"]
        )
        distributed_pumping_power_time_array = self.get_distributed_pumping_power_time_array(
            ets_head_difference_time_array=ets_head_difference_time_array,
            nodal_consumptions_time_array=tree_equilibrium_time_array.loc["Nodal consumptions [qbm/s]"]
        )
        overall_distributed_pumping_power_time_dict = {
            time_step: distributed_pumping_power_time_array[time_step].sum()
            for time_step in tree_equilibrium_time_array.columns
        }
        overall_distributed_pumping_power_time_row = pd.DataFrame(
            data=overall_distributed_pumping_power_time_dict,
            index=[None]
        )
        grid_pumping = pd.concat(
            [
                ets_head_difference_time_array,
                central_pumping_power_time_row,
                overall_distributed_pumping_power_time_row,
                distributed_pumping_power_time_array
            ],
            keys=[
                'Head difference over ETSs [m]',
                'CSP power [W]',
                'Overall DSP power [W]',
                'DSP power at ETSs [W]'
            ]
        )
        grid_pumping.index.names = ['VARIABLES', 'IDs']
        return grid_pumping

    # Method triggering a complete non-linear simulation of the distribution system ------------------------------------

    def get_grid_simulation(
        self,
        ets_flow_time_array
    ):
        # Calculating hydraulic equilibrium of return-side grid
        tree_equilibrium_time_array = self.get_tree_equilibrium_time_array(
            ets_flow_time_array=ets_flow_time_array
        )
        # Based on hydraulic equilibrium of return-side grid, calculating pumping powers of Distribution System
        distribution_system_pumping = self.get_grid_pumping(
            tree_equilibrium_time_array=tree_equilibrium_time_array
        )
        # All calculated results are packed into one DataFrame
        distribution_system_simulation = pd.concat(
            [
             tree_equilibrium_time_array,
             distribution_system_pumping
            ]
        )
        return distribution_system_simulation

    # Methods used by optimizer  ---------------------------------------------------------------------------------------

    def get_heat_intake_from_ets_flow(
        self,
        ets_flow
    ):
        heat_flow_from_building = (
            self.parameters.physics["water density [kg/m^3]"]
            * self.parameters.physics["specific enthalpy difference DW [J/kg]"]
            * ets_flow
        )
        return heat_flow_from_building

    # Methods for planning ---------------------------------------------------------------------------------------------

    def get_diameters_from_flow(
        self,
        line_flows,
        u_max
    ):
        diameters_dict = {
            'Diameters': [
                (
                    (4 / np.pi)
                    * (line_flows[line] / u_max)
                ) ^ 0.5
            ] for line in line_flows.index
        }
        diameters_df = pd.DataFrame(
            data=diameters_dict,
            index=[line for line in line_flows.index]
        )
        return diameters_df