import pandas as pd

# ======================================================================================================================
# Model of district cooling plant CLASS
# ======================================================================================================================


class CoolingPlant:
    """
    Defines the model of the District Cooling Plant. All linear correlations.
    """
    # INITIALIZATION ===================================================================================================

    def __init__(
        self,
        parameters
    ):
        self.parameters = parameters

    # METHOD DEFINITIONS ===============================================================================================

    # Methods for chiller-set calculations -----------------------------------------------------------------------------

    def get_chillers_evaporator_heat_flow(
        self,
        chillers_water_flow
    ):
        evaporator_heat_flow = (
            self.parameters.physics["water density [kg/m^3]"]
            * self.parameters.physics["specific enthalpy difference DW [J/kg]"]
            * chillers_water_flow
        )
        return evaporator_heat_flow

    def get_cw_supply_temperature(
        self,
        air_wet_bulb
    ):
        cw_supply_temperature = (
            self.parameters.cooling_plant["CTS reference T CW supply [C]"]
            + (
                self.parameters.cooling_plant["CTS reference T slope [-]"]
                * (
                    air_wet_bulb
                    - self.parameters.cooling_plant["CTS reference T wet-bulb [C]"]
                )
            )
        )
        return cw_supply_temperature


    def get_chillers_condensation_temperature(
        self,
        air_wet_bulb
    ):
        cw_supply_temperature = self.get_cw_supply_temperature(
            air_wet_bulb
        )
        condensation_temperature = (
            cw_supply_temperature
            + 273.15
            + self.parameters.cooling_plant["CW delta T [K]"]
            + self.parameters.cooling_plant["chiller-set delta T cnd min [K]"]
        )
        return condensation_temperature

    def get_chillers_inverse_cop(
        self,
        air_wet_bulb
    ):
        condensation_temperature = self.get_chillers_condensation_temperature(
            air_wet_bulb
        )
        inverse_cop = (
            (
                (
                    condensation_temperature
                    / self.parameters.cooling_plant["chiller-set evaporation T [K]"]
                )
                - 1
            )
            * (
                self.parameters.cooling_plant["chiller-set beta [-]"]
                + 1
            )
        )
        return inverse_cop

    def get_chillers_power(
        self,
        chillers_water_flow,
        air_wet_bulb
    ):
        inverse_cop = self.get_chillers_inverse_cop(
            air_wet_bulb
        )
        power_chillers = (
            inverse_cop
            * self.get_chillers_evaporator_heat_flow(chillers_water_flow)
        )
        return power_chillers

    def get_chillers_condenser_heat_flow(
        self,
        chillers_water_flow,
        air_wet_bulb
    ):
        condenser_heat_flow = (
            self.get_chillers_evaporator_heat_flow(
                chillers_water_flow
            )
            + self.get_chillers_power(
                chillers_water_flow,
                air_wet_bulb
            )
        )
        return condenser_heat_flow

    def get_evaporator_pumping_power(
        self,
        chillers_water_flow
    ):
       evaporator_pumping_power = (
           (1 / self.parameters.cooling_plant["pumping total efficiency [-]"])
            * self.parameters.physics["gravitational acceleration [m^2/s]"]
            * self.parameters.physics["water density [kg/m^3]"]
            * self.parameters.cooling_plant["pump head evaporators [m]"]
            * chillers_water_flow
       )
       return evaporator_pumping_power

    # Methods for condenser water-circuit calculations -----------------------------------------------------------------

    def get_CW_water_flow(
        self,
        chillers_water_flow,
        air_wet_bulb
    ):
        condenser_heat_flow = self.get_chillers_condenser_heat_flow(
            chillers_water_flow,
            air_wet_bulb
        )
        CW_water_flow = (
            condenser_heat_flow
            / (
                self.parameters.physics["water density [kg/m^3]"]
                * self.parameters.physics["specific enthalpy difference CW [J/kg]"]
            )
        )
        return CW_water_flow

    def get_CW_pumping_power(
        self,
        chillers_water_flow,
        air_wet_bulb
    ):
        CW_water_flow = self.get_CW_water_flow(
            chillers_water_flow,
            air_wet_bulb
        )
        CW_pumping_power = (
                (1 / self.parameters.cooling_plant["pumping total efficiency [-]"])
                * self.parameters.physics["gravitational acceleration [m^2/s]"]
                * self.parameters.physics["water density [kg/m^3]"]
                * self.parameters.cooling_plant["pump head CW [m]"]
                * CW_water_flow
        )
        return CW_pumping_power

    # Methods for Cooling Towers calculations --------------------------------------------------------------------------

    def get_CTS_ventilation_power(
        self,
        chillers_water_flow,
        air_wet_bulb
    ):
        condenser_heat_flow = self.get_chillers_condenser_heat_flow(
            chillers_water_flow,
            air_wet_bulb
        )
        ventilation_power = (
            self.parameters.cooling_plant["CTS ventilation factor [-]"]
            * condenser_heat_flow
        )
        return ventilation_power

    # Methods for thermal energy storage calculations ------------------------------------------------------------------

    def get_TES_pumping_power(
        self,
        TES_water_flow
    ):
        TES_pumping_power = (
                (1 / self.parameters.cooling_plant["pumping total efficiency [-]"])
                * self.parameters.physics["gravitational acceleration [m^2/s]"]
                * self.parameters.physics["water density [kg/m^3]"]
                * self.parameters.cooling_plant["pump head TES [m]"]
                * TES_water_flow
        )
        return TES_pumping_power

    def get_TES_flow_sum_until_time_step(
        self,
        time_step,
        TES_water_flow_set
    ):
        TES_flow_sum_until_time_step = 0
        for time in self.parameters.environment.index:
            TES_flow_sum_until_time_step += (
                TES_water_flow_set[time]
            )
            if time == time_step:
                break
        return TES_flow_sum_until_time_step

    def get_TES_energy_content(
        self,
        time_step,
        TES_water_flow_set,
        TES_capacity_Wh
    ):
        TES_flow_sum_until_time_step = self.get_TES_flow_sum_until_time_step(
            time_step,
            TES_water_flow_set
        )
        # Calculate the energetic content of the storage
        TES_energy_content = (
            TES_capacity_Wh
            * self.parameters.cooling_plant["TES initial charge ratio [-]"]
            + (
                self.parameters.physics["water density [kg/m^3]"]
                * self.parameters.physics["specific enthalpy difference DW [J/kg]"]
                * self.parameters.physics["duration of one time step [h]"]
                * TES_flow_sum_until_time_step
            )
        )
        return TES_energy_content

    def get_storage_energy_change_optimization_rule(
        self,
        storage_flow
    ):
        # Calculate the energetic content of the storage
        storage_energy_change = (
            self.parameters.physics["water density [kg/m^3]"]
            * self.parameters.physics["specific enthalpy difference DW [J/kg]"]
            * storage_flow
            * self.parameters.physics["duration of one time step [h]"]
        )
        return storage_energy_change

    # Method for calculating total power demand of district cooling plant ----------------------------------------------

    def get_plant_total_power(
        self,
        chillers_water_flow,
        storage_water_flow,
        air_wet_bulb
    ):
        plant_total_power = (
            self.get_chillers_power(chillers_water_flow, air_wet_bulb)
            + self.get_evaporator_pumping_power(chillers_water_flow)
            + self.get_CW_pumping_power(chillers_water_flow, air_wet_bulb)
            + self.get_CTS_ventilation_power(chillers_water_flow, air_wet_bulb)
            + self.get_TES_pumping_power(storage_water_flow)
        )
        return plant_total_power

    # Method triggering a complete simulation of the district cooling plant --------------------------------------------

    def get_plant_simulation(
        self,
        chiller_set_flow,
        tes_flow,
        air_wet_bulb
    ):
        plant_total_power = self.get_plant_total_power(
            chillers_water_flow=chiller_set_flow,
            storage_water_flow=tes_flow,
            air_wet_bulb=air_wet_bulb
        )
        storage_pumping_power = self.get_TES_pumping_power(
            TES_water_flow=tes_flow
        )
        cooling_towers_power = self.get_CTS_ventilation_power(
            chillers_water_flow=chiller_set_flow,
            air_wet_bulb=air_wet_bulb
        )
        condenser_circuit_water_flow = self.get_CW_water_flow(
            chillers_water_flow=chiller_set_flow,
            air_wet_bulb=air_wet_bulb
        )
        condenser_circuit_pumping_power = self.get_CW_pumping_power(
            chillers_water_flow=chiller_set_flow,
            air_wet_bulb=air_wet_bulb
        )
        chillers_pumping_power = self.get_evaporator_pumping_power(
            chillers_water_flow=chiller_set_flow
        )
        chillers_evaporator_heat_flow = self.get_chillers_evaporator_heat_flow(
            chillers_water_flow=chiller_set_flow
        )
        chillers_condenser_heat_flow = self.get_chillers_condenser_heat_flow(
            chillers_water_flow=chiller_set_flow,
            air_wet_bulb=air_wet_bulb
        )
        chiller_set_power = self.get_chillers_power(
            chillers_water_flow=chiller_set_flow,
            air_wet_bulb=air_wet_bulb
        )
        chiller_set_inverse_cop = self.get_chillers_inverse_cop(
            air_wet_bulb=air_wet_bulb
        )
        simulation = pd.Series(
            [
                chiller_set_flow,
                tes_flow,
                air_wet_bulb,
                storage_pumping_power,
                chillers_pumping_power,
                chillers_evaporator_heat_flow,
                chiller_set_inverse_cop,
                chiller_set_power,
                chillers_condenser_heat_flow,
                condenser_circuit_water_flow,
                condenser_circuit_pumping_power,
                cooling_towers_power,
                plant_total_power
            ],
            index=[
                'Chiller-set flow in [m3/s]',
                'TES flow in [m3/s]',
                'Air wet-bulb [C]',
                'TES pumping power [W]',
                'Evaporators pumping power [W]',
                'Evaporator heat flow [W]',
                'Chiller-Set COP^(-1) [-]',
                'Chiller-Set Power [W]',
                'Condenser heat flow [W]',
                'Condenser water flow [m3/s]',
                'Condenser pumping [W]',
                'CTS ventilation power [W]',
                'DCP total power demand [W]'
            ]
        )
        return simulation