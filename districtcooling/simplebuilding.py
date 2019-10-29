
# ======================================================================================================================
# Preliminary simple cubic building model CLASS
# ======================================================================================================================


class CubicBuilding:
    """
    INFO: Class representing a simple model of a cubic building.
    """

    # INITIALIZATION ===================================================================================================

    def __init__(
        self,
        building_id,
        parameters
    ):
        # Physical Values
        self.density_air = 1.19                         # [kg/m^3]
        self.specific_heat_capacity_air = 1005                   # [J/kg*K]
        self.density_concrete = 2100                    # [kg/m^3]
        self.specific_heat_capacity_concrete = 880               # [J/kg*K]

        # Volumetric shares of materials
        self.volumetric_share_air = 0.95
        self.volumetric_share_concrete = 0.05

        # Estimated overall heat transfer coefficient on outside surface
        self.overall_heat_transfer = 5                  # [W/m^2*K]

        # Values utilized from parameters-object
        self.parameters = parameters
        self.length_edge = parameters.buildings["Size [m]"][building_id]
        self.duration_of_one_time_step = parameters.physics["duration of one time step [s]"]
        self.initial_temperature = parameters.buildings["Initial Temperature [Celsius]"][building_id]

        # Calculating dimensions of the cube
        self.surface = (self.length_edge ** 2) * 6      # [m]
        self.volume = self.length_edge ** 3             # [m]

        # Calculating heat capacity of whole building
        self.heat_capacity_building = (
            self.specific_heat_capacity_air
            * self.volumetric_share_air
            * self.volume
            * self.density_air
            + self.specific_heat_capacity_concrete
            * self.volumetric_share_concrete
            * self.volume
            * self.density_concrete
        )

    # METHOD DEFINITIONS ===============================================================================================
    """ Methods to calculate a resulting temperature from a given cooling power and a given time step taking into
    account constant heat loss flow and heat capacity of building """

    def get_building_temperature_change(
        self,
        time_step,
        building_id,
        building_heat_flow_set
    ):
        buildings_temperature_change = 0
        for time in self.parameters.environment.index:
            buildings_temperature_change += (
                self.duration_of_one_time_step
                * (
                    (
                        self.overall_heat_transfer
                        * self.surface
                        * (28-21)
                    )
                    - building_heat_flow_set[time, building_id]
                )
                / self.heat_capacity_building
            )
            if time == time_step:
                break
        return buildings_temperature_change

    def get_building_temperature(
        self,
        time_step,
        building_id,
        building_heat_flow_set,
    ):
        building_temperature = (
            self.initial_temperature
            + self.get_building_temperature_change(
                time_step,
                building_id,
                building_heat_flow_set
            )
        )
        return building_temperature