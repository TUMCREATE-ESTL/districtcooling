import pandas as pd

# ======================================================================================================================
# Model of district cooling plant CLASS
# ======================================================================================================================


class CoolingPlant:
    """
    Defines the model of the District Cooling Plant
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

    def get_chillers_condensation_temperature(
        self,
        air_wet_bulb
    ):
        condensation_temperature = 12.47 + 0.727 * air_wet_bulb
        return condensation_temperature

    def get_chillers_cop(
        self,
        air_wet_bulb
    ):
        cop = (
            self.parameters.cooling_plant["COP efficiency [-]"]
            * (
                self.parameters.cooling_plant["evaporation temperature [Celsius]"] + 273.15
            )
            / (
                self.get_chillers_condensation_temperature(air_wet_bulb)
                - self.parameters.cooling_plant["evaporation temperature [Celsius]"]
            )
        )
        return cop

    def get_chillers_power(
        self,
        chillers_water_flow,
        air_wet_bulb
    ):
        power_chillers = (
            self.get_chillers_evaporator_heat_flow(chillers_water_flow)
            / self.get_chillers_cop(air_wet_bulb)
        )
        return power_chillers

    def get_chillers_condenser_heat_flow(
        self,
        chillers_water_flow,
        air_wet_bulb
    ):
        condenser_heat_flow = (
            self.get_chillers_evaporator_heat_flow(chillers_water_flow)
            + self.get_chillers_power(chillers_water_flow, air_wet_bulb)
        )
        return condenser_heat_flow

    def get_chillers_pumping_power(
        self,
        chillers_water_flow
    ):
       chillers_pumping_power = (
            self.parameters.physics["gravitational acceleration [m^2/s]"]
            * self.parameters.physics["water density [kg/m^3]"]
            * self.parameters.cooling_plant["pump efficiency chillers pump [-]"]
            * self.parameters.cooling_plant["head chillers pump [m]"]
            * chillers_water_flow
       )
       return chillers_pumping_power

    # Methods for condenser water-circuit calculations -----------------------------------------------------------------

    def get_condenser_circuit_water_flow(
        self,
        chillers_water_flow,
        air_wet_bulb
    ):
        condenser_circuit_water_flow = (
            self.get_chillers_condenser_heat_flow(chillers_water_flow, air_wet_bulb)
            / (
                self.parameters.physics["water density [kg/m^3]"]
                * (
                    self.parameters.physics["specific enthalpy condenser warm [J/kg]"]
                    - self.parameters.physics["specific enthalpy condenser cold [J/kg]"]
                )
            )
        )
        return condenser_circuit_water_flow

    def get_condenser_circuit_pumping_power(
        self,
        chillers_water_flow,
        air_wet_bulb
    ):
        condenser_circuit_pumping_power = (
                self.parameters.physics["gravitational acceleration [m^2/s]"]
                * self.parameters.physics["water density [kg/m^3]"]
                * self.parameters.cooling_plant["pump efficiency condenser pump [-]"]
                * self.parameters.cooling_plant["head condenser pump [m]"]
                * self.get_condenser_circuit_water_flow(chillers_water_flow, air_wet_bulb)
        )
        return condenser_circuit_pumping_power

    # Methods for Cooling Towers calculations --------------------------------------------------------------------------

    def get_cooling_towers_power(
        self,
        chillers_water_flow,
        air_wet_bulb
    ):
        cooling_towers_power = (
            self.get_chillers_condenser_heat_flow(chillers_water_flow, air_wet_bulb)
            * self.parameters.cooling_plant["ventilation factor cooling towers [J/J]"]
        )
        return cooling_towers_power

    # Methods for thermal energy storage calculations ------------------------------------------------------------------

    def get_storage_pumping_power(
        self,
        storage_water_flow
    ):
        storage_pumping_power = (
                self.parameters.physics["gravitational acceleration [m^2/s]"]
                * self.parameters.physics["water density [kg/m^3]"]
                * self.parameters.cooling_plant["pump efficiency TES pump [-]"]
                * self.parameters.cooling_plant["head TES pump [m]"]
                * storage_water_flow
        )
        return storage_pumping_power

    def get_storage_total_flow_until_time_step(
        self,
        time_step,
        storage_water_flow_set
    ):
        storage_total_flow_until_time_step = 0
        for time in self.parameters.environment.index:
            storage_total_flow_until_time_step += (
                (-1) # positive flow of variable means supplying the grid, resulting in storage-discharge
                *storage_water_flow_set[time]
                * self.parameters.physics["duration of one time step [s]"]
            )
            if time == time_step:
                break
        return storage_total_flow_until_time_step

    def get_storage_energy_content(
        self,
        time_step,
        storage_water_flow_set,
    ):
        # Calculate the energetic content of the storage
        storage_energy_content = (
            self.parameters.cooling_plant["TES energy capacity [J]"]
            * self.parameters.cooling_plant["TES initial charge ratio [-]"]
            + (
                self.parameters.physics["water density [kg/m^3]"]
                * self.parameters.physics["specific enthalpy difference DW [J/kg]"]
            )
            * self.get_storage_total_flow_until_time_step(time_step, storage_water_flow_set)
        )
        return storage_energy_content

    def get_storage_energy_change_optimization_rule(
        self,
        storage_flow
    ):
        # Calculate the energetic content of the storage
        storage_energy_change = (
            self.parameters.physics["water density [kg/m^3]"]
            * self.parameters.physics["specific enthalpy difference DW [J/kg]"]
            * (-1) * storage_flow
            * self.parameters.physics["duration of one time step [s]"]
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
            + self.get_chillers_pumping_power(chillers_water_flow)
            + self.get_condenser_circuit_pumping_power(chillers_water_flow, air_wet_bulb)
            + self.get_cooling_towers_power(chillers_water_flow, air_wet_bulb)
            + self.get_storage_pumping_power(storage_water_flow)
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
        storage_pumping_power = self.get_storage_pumping_power(
            storage_water_flow=tes_flow
        )
        cooling_towers_power = self.get_cooling_towers_power(
            chillers_water_flow=chiller_set_flow,
            air_wet_bulb=air_wet_bulb
        )
        condenser_circuit_water_flow = self.get_condenser_circuit_water_flow(
            chillers_water_flow=chiller_set_flow,
            air_wet_bulb=air_wet_bulb
        )
        condenser_circuit_pumping_power = self.get_condenser_circuit_pumping_power(
            chillers_water_flow=chiller_set_flow,
            air_wet_bulb=air_wet_bulb
        )
        chillers_pumping_power = self.get_chillers_pumping_power(
            chillers_water_flow = chiller_set_flow
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
        chiller_set_cop = self.get_chillers_cop(
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
                chiller_set_cop,
                chiller_set_power,
                chillers_condenser_heat_flow,
                condenser_circuit_water_flow,
                condenser_circuit_pumping_power,
                cooling_towers_power,
                plant_total_power
            ],
            index=[
                'Chiller-set flow in [qbm/s]',
                'TES flow in [qbm/s]',
                'Air wet-bulb [C]',
                'TES pumping power [W]',
                'Evaporators pumping power [W]',
                'Evaporator heat flow [W]',
                'Chiller-Set COP [-]',
                'Chiller-Set Power [W]',
                'Condenser heat flow [W]',
                'Condenser water flow [qbm/s]',
                'Condenser pumping [W]',
                'Cooling towers power [W]',
                'DCP total power demand [W]'
            ]
        )
        return simulation