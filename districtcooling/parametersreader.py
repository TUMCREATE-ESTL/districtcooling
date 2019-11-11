import os
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
            os.path.join(os.path.dirname(os.path.normpath(__file__)), '..', 'data', 'lines.csv'),
            index_col=0
        )
        self.nodes = pd.read_csv(
            os.path.join(os.path.dirname(os.path.normpath(__file__)), '..', 'data', 'nodes.csv'),
            index_col=0
        )
        self.distribution_system = pd.read_csv(
            os.path.join(os.path.dirname(os.path.normpath(__file__)), '..', 'data', 'distribution_system.csv'),
            index_col=0,
            squeeze=True
        )
        # Parameters of buildings
        # self.buildings = pd.read_csv(
        #     os.path.join(os.path.dirname(os.path.normpath(__file__)), '..', 'data', 'simple_buildings.csv'),
        #     index_col=0
        # )
        self.buildings = pd.read_csv(
            os.path.join(os.path.dirname(os.path.normpath(__file__)), '..', 'data', 'buildings.csv'),
            index_col=0
        )
        # Parameters of district cooling plant
        self.cooling_plant = pd.read_csv(
            os.path.join(os.path.dirname(os.path.normpath(__file__)), '..', 'data', 'district_cooling_plant.csv'),
            index_col=0,
            squeeze=True
        )
        # Parameters of environment
        self.environment = pd.read_csv(
            os.path.join(os.path.dirname(os.path.normpath(__file__)), '..', 'data', 'environment.csv'),
            index_col=0
        )
        # Parameters of physical properties
        self.physics = pd.read_csv(
            os.path.join(os.path.dirname(os.path.normpath(__file__)), '..', 'data', 'physical_properties.csv'),
            index_col=0,
            squeeze=True
        )