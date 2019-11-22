import geopandas
import matplotlib.pyplot as plt
import networkx as nx
import os
import pandas as pd
import shapely
import utm


# Settings.
scenario_name = 'WTP_MIX_medium_density'
input_path = os.path.join(os.path.dirname(os.path.normpath(__file__)), 'data', 'grid_input_data', scenario_name)
output_path = os.path.join(os.path.dirname(os.path.normpath(__file__)), 'data')

# Load data.
building_polygons = (
    geopandas.GeoDataFrame.from_file(os.path.join(input_path, 'inputs', 'building-geometry', 'zone.shp'))
)
street_linestrings = (
    geopandas.GeoDataFrame.from_file(os.path.join(input_path, 'inputs', 'networks', 'streets.shp'))
)

# Project coordinates to longlat.
building_polygons = building_polygons.to_crs('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
# Obtain UTM zone information based on first building centroid.
(
    easting,
    northing,
    zone_number,
    zone_letter
) = utm.from_latlon(
    building_polygons.geometry[0].centroid.coords.xy[1][0],  # Latitude.
    building_polygons.geometry[0].centroid.coords.xy[0][0]  # Longitude.
)
# Project coordinates to UTM.
building_polygons = (
    building_polygons.to_crs(
        '+proj=utm +zone=' + str(zone_number) + zone_letter + ' +ellps=WGS84 +datum=WGS84 +units=m +no_defs'
    )
)

# Find street connection point for each building.
building_connection_points = geopandas.GeoDataFrame(columns=['geometry', 'type'])
building_connection_point_index = 0
for building_polygon_index, building_polygon in building_polygons.iterrows():
    # Find nearest street linestring.
    street_linestring_nearest_index = street_linestrings.distance(building_polygon.geometry.centroid).idxmin()
    street_linestring_nearest_geometry = street_linestrings.at[street_linestring_nearest_index, 'geometry']

    # Find nearest connection point on nearest street linestring.
    # 1) Get shortest distance from building centroid point to nearest street linestring.
    # 2) Find connection point on nearest street linestring at shortest distance.
    building_connection_point = (
        street_linestring_nearest_geometry.interpolate(
            street_linestring_nearest_geometry.project(building_polygon.geometry.centroid)
        )
    )

    # Add to GeoDataFrame.
    building_connection_points.at[building_connection_point_index, 'type'] = 'building'
    building_connection_points.at[building_connection_point_index, 'geometry'] = building_connection_point
    building_connection_point_index += 1

# Find street intersection points.
intersection_points = geopandas.GeoDataFrame(columns=['geometry', 'type'])
intersection_point_index = 0
for street_linestring_index, street_linestring in street_linestrings.iterrows():
    # Find street linestrings intersecting with current street linestring.
    street_intersection_linestrings = street_linestrings.intersection(street_linestring.geometry.buffer(0.0001))
    street_intersection_linestrings = street_intersection_linestrings.drop(street_linestring_index)
    street_intersection_linestrings = street_intersection_linestrings.loc[street_intersection_linestrings.notnull()]

    for street_intersection_linestring_index, street_intersection_linestring in street_intersection_linestrings.iteritems():
        # Find intersection point.
        street_intersection_point = street_intersection_linestring.centroid

        # Add to GeoDataFrame.
        # - Only if intersection point does not coincide with a building connection point or another intersection point.
        if not (
            building_connection_points.intersects(street_intersection_point.buffer(0.1)).any()
            or intersection_points.intersects(street_intersection_point.buffer(0.1)).any()
        ):
            intersection_points.at[intersection_point_index, 'type'] = 'intersection'
            intersection_points.at[intersection_point_index, 'geometry'] = street_intersection_point
            intersection_point_index += 1

# Find substation point.
substation_points = geopandas.GeoDataFrame(intersection_points.iloc[-1, :]).T.reset_index(drop=True)
substation_points['type'] = 'substation'
intersection_points = intersection_points.iloc[:-1, :]  # Drop point from intersection_points.

# Get grid points GeoDataFrame by merging all points.
grid_points = pd.concat([substation_points, building_connection_points, intersection_points], ignore_index=True)

# Update indices on other dataframes for easier processing.
building_connection_points.index += substation_points.shape[0]
building_polygons.index += substation_points.shape[0]
intersection_points.index += substation_points.shape[0] + building_connection_points.shape[0]

# Derive possible grid linestrings.
grid_linestrings = geopandas.GeoDataFrame(columns=['geometry', 'node_1_index', 'node_2_index', 'length'])
grid_linestring_index = 0
for street_linestring_index, street_linestring in street_linestrings.iterrows():
    # Find building points intersecting with current street linestring.
    grid_intersection_points = grid_points.intersection(street_linestring.geometry.buffer(0.0001))
    grid_intersection_points = grid_intersection_points.loc[grid_intersection_points.notnull()]

    # Calculate distance from street linestring start point to building connection points and sort by distance.
    street_linestring_start_point = shapely.geometry.Point(street_linestring.geometry.coords[0])
    grid_intersection_points = geopandas.GeoDataFrame(grid_intersection_points, columns=['geometry'])
    grid_intersection_points['distance'] = grid_intersection_points.distance(street_linestring_start_point)
    grid_intersection_points = grid_intersection_points.sort_values(by='distance')

    # Create new grid lines.
    for point_1_index, point_2_index in (
        zip(grid_intersection_points.index[:-1], grid_intersection_points.index[1:])
    ):
        # Construct grid linestring.
        point_1 = grid_intersection_points.at[point_1_index, 'geometry']
        point_2 = grid_intersection_points.at[point_2_index, 'geometry']
        grid_linestring = shapely.geometry.LineString([point_1, point_2])

        # Add to GeoDataFrame.
        grid_linestrings.at[grid_linestring_index, 'node_1_index'] = point_1_index
        grid_linestrings.at[grid_linestring_index, 'node_2_index'] = point_2_index
        grid_linestrings.at[grid_linestring_index, 'geometry'] = grid_linestring
        grid_linestrings.at[grid_linestring_index, 'length'] = grid_linestring.length
        grid_linestring_index += 1

# Create network graph.
network_graph = nx.Graph()
for grid_point_index, grid_point in grid_points.iterrows():
    network_graph.add_node(
        grid_point_index,
        type=grid_point['type']
    )
for grid_linestring_index, grid_linestring in grid_linestrings.iterrows():
    network_graph.add_edge(
        grid_linestring['node_1_index'],
        grid_linestring['node_2_index'],
        weight=grid_linestring['length'],
        gene=grid_linestring_index,
        startnode=grid_linestring['node_1_index'],
        endnode=grid_linestring['node_2_index']
    )
positions = {point_index: (point.geometry.x, point.geometry.y) for point_index, point in grid_points.iterrows()}
building_polygons.plot(color='lightgrey')
nx.draw(network_graph, positions)
nx.draw_networkx_labels(network_graph, positions)
plt.show()

# Find grid lines for minimum spanning tree.
lines_minimum_spanning = nx.algorithms.tree.mst.minimum_spanning_edges(network_graph)
# Apply `bfs_tree` to get directed lines from the substaion towards the buildings.
network_graph_minimum_spanning = nx.algorithms.bfs_tree(nx.Graph(lines_minimum_spanning), 0)
lines_minimum_spanning = list(network_graph_minimum_spanning.edges)
# Remove intersection nodes which are at the ends of the tree without connecting to buildings.
nodes_to_keep = []
for building_connection_point_index, building_connection_point in building_connection_points.iterrows():
    nodes_to_keep.extend(nx.shortest_path(network_graph_minimum_spanning, 0, building_connection_point_index))
nodes_to_keep = list(set(nodes_to_keep))  # Keep distinct entries.
lines_to_keep = []
for line in lines_minimum_spanning:
    if (line[0] in nodes_to_keep) and (line[1] in nodes_to_keep):
        lines_to_keep.append(line)
# Apply `bfs_tree` to get directed lines from the substaion towards the buildings.
network_graph_minimum_spanning = nx.algorithms.bfs_tree(nx.Graph(lines_to_keep), 0)
lines_minimum_spanning = list(network_graph_minimum_spanning.edges)
positions = {point_index: (point.geometry.x, point.geometry.y) for point_index, point in grid_points.iterrows()}
building_polygons.plot(color='lightgrey')
nx.draw(network_graph_minimum_spanning, positions)
nx.draw_networkx_labels(network_graph_minimum_spanning, positions)
plt.show()

# Construct line data.
lines = pd.DataFrame(
    None,
    columns=pd.Index(['Start', 'End', 'Length [m]', 'Diameter [m]', 'Absolute Roughness [mm]']),
    index=pd.Index(range(len(lines_minimum_spanning)), name='ID')
)
for line_id, line in lines.iterrows():
    lines.at[line_id, 'Start'] = lines_minimum_spanning[line_id][0]
    lines.at[line_id, 'End'] = lines_minimum_spanning[line_id][1]
    lines.at[line_id, 'Length [m]'] = round(network_graph.edges[lines.at[line_id, 'Start'], lines.at[line_id, 'End']]['weight'], 8)
    lines.at[line_id, 'Diameter [m]'] = 10.0
    lines.at[line_id, 'Absolute Roughness [mm]'] = 4
print(lines)
lines.to_csv(os.path.join(output_path, 'lines.csv'))

# Construct node data.
nodes = pd.DataFrame(
    None,
    columns=pd.Index(['Type','position-X','position-Y']),
    index=pd.Index(nodes_to_keep, name='ID')
)
for node_id, node in nodes.iterrows():
    if grid_points.loc[node_id, 'type'] == 'substation':
        node_type = 'reference'
    elif grid_points.loc[node_id, 'type'] == 'building':
        node_type = 'building'
    else:
        node_type = 'junction'
    nodes.at[node_id, 'Type'] = node_type
    nodes.at[node_id, 'position-X'] = round(grid_points.loc[node_id, 'geometry'].coords[0][0], 4)
    nodes.at[node_id, 'position-Y'] = round(grid_points.loc[node_id, 'geometry'].coords[0][1], 4)
print(nodes)
nodes.to_csv(os.path.join(output_path, 'nodes.csv'))

# Construct building data.
buildings = pd.DataFrame(
    None,
    columns=['building_scenario_name'],
    index=building_connection_points.index.rename('ID')
)
for building_connection_point_index, building_connection_point in building_connection_points.iterrows():
    buildings.at[building_connection_point_index, 'building_scenario_name'] = (
        scenario_name.lower() + '_{}'.format(building_connection_point_index)
    )
print(buildings)
buildings.to_csv(os.path.join(output_path, 'buildings.csv'))

# Export building polygons for plotting.
building_polygons.to_file(os.path.join(output_path, 'building_polygons.shp'))
