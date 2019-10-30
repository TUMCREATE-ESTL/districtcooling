import matplotlib.pyplot as plt
import networkx as nx
import os

# ======================================================================================================================
# Tool-kit for visualization and plotting CLASS
# ======================================================================================================================

class Plotter:

    def __init__(self, parameters):
        self.parameters = parameters

    def plot_grid_simulation(
        self,
        grid_simulation,
        time_step,
        save=False,
        index_for_saving=0
    ):
        """
        Plots the digraph of the grid for a certain given state auf hydraulic equilibrium.
        """

        graph = nx.DiGraph()

        # -------------------- Nodes
        list_nodes = list(self.parameters.nodes.index)

        pos_nodes = {
            node: (
                self.parameters.nodes['position-X'][node],
                self.parameters.nodes['position-Y'][node]
            ) for node in list_nodes
        }

        nx.draw_networkx_nodes(
            graph,
            pos=pos_nodes,
            nodelist=list_nodes,
            node_color='c',
            edgecolors='k',
            node_size=400,
            alpha=1
        )
        # Add labels to nodes
        labels_for_nodes = {
            node_id: round(
                grid_simulation.loc["Total head at nodes [m]"][time_step][node_id], 1
            )
            for node_id in list_nodes}

        nx.draw_networkx_labels(
            graph,
            pos=pos_nodes,
            labels=labels_for_nodes,
            font_size=8)

        # -------------------- Lines (=edges)
        list_edges = [
            (
                self.parameters.lines.loc[index]['Start'],
                self.parameters.lines.loc[index]['End']
            )
            for index in self.parameters.lines.index
        ]

        weight_lines = [
            grid_simulation.loc["Flow in lines [qbm/s]"][time_step][index]
            * 8
            for index in self.parameters.lines.index
        ]

        nx.draw_networkx_edges(
            graph,
            pos_nodes,
            edgelist=list_edges,
            width=0.7,
            arrowstyle='->'
        )

        nx.draw_networkx_edges(
            graph,
            pos_nodes,
            edgelist=list_edges,
            width=weight_lines,
            edge_color='blue',
            alpha=0.4,
            arrowstyle='-'
        )
        # Add labels to lines
        labels_for_lines = {
            (self.parameters.lines.loc[index]['Start'], self.parameters.lines.loc[index]['End'])
            : (
                    "V="
                    + str(
                        round(
                            grid_simulation.loc["Flow in lines [qbm/s]"][time_step][index],
                            1
                        )
                    )
                    + ", h="
                    + str(
                        round(
                            grid_simulation.loc["Head loss over lines [m]"][time_step][index],
                            1
                        )
                    )
            )
            for index in self.parameters.lines.index
        }

        nx.draw_networkx_edge_labels(
            graph,
            pos=pos_nodes,
            edge_labels=labels_for_lines,
            font_size=8
        )
        # -------------------- Plot and save
        plt.axis("off")
        if save:
            plt.savefig(
                os.path.join(
                    os.path.dirname(os.path.normpath(__file__)),
                    '..', 'results', 'graph_plots', str(index_for_saving) + '_graph.png'
                )
            )

        plt.show()
