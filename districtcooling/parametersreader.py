import pandas as pd

# ======================================================================================================================
# Parameter reading CLASS
# ======================================================================================================================


class ParametersReader:
    """
    Imports all parameters from file 'parameters' into a form the other classes understand
    """

    def __init__(self):

        # Parameters of distribution system
        self.lines = pd.read_csv(
            "data/lines.csv",
            index_col=0
        )
        self.nodes = pd.read_csv(
            "data/nodes.csv",
            index_col=0
        )
        self.distribution_system = pd.read_csv(
            "data/distribution_system.csv",
            index_col=0,
            squeeze=True
        )
        # Parameters of buildings
        self.buildings = pd.read_csv(
            "data/buildings.csv",
            index_col=0
        )
        # Parameters of district cooling plant
        self.cooling_plant = pd.read_csv(
            "data/district_cooling_plant.csv",
            index_col=0,
            squeeze=True
        )
        # Parameters of environment
        self.environment = pd.read_csv(
            "data/environment.csv",
            index_col=0
        )
        # Parameters of physical properties
        self.physics = pd.read_csv(
            "data/physical_properties.csv",
            index_col=0,
            squeeze=True
        )