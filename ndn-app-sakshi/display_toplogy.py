import networkx as nx
import matplotlib.pyplot as plt
from topology import nodes, rpi1_nodes, rpi2_nodes

# Create a directed graph
G = nx.DiGraph()

network_data = nodes
# Add nodes and edges

for node, attributes in network_data.items():
    if node in rpi1_nodes:
        G.add_node(node, label=node, color="pink")
    elif node in rpi2_nodes:
        G.add_node(node, label=node, color="yellow")
    else:
        raise Exception("Invalid node id", node)
    # G.add_node(node, label=f"{node}\nIP: {attributes['server_IP']}\nPort: {attributes['server_port']}")
    for peer in attributes['peers']:
        G.add_edge(node, peer)

color_map = []
for node_index in G.nodes:
    color_map.append(G.nodes[node_index]["color"])

# Plot the graph
pos = nx.circular_layout(G)
nx.draw(G, pos, with_labels=True, font_weight='bold', node_size=800, node_color=color_map, font_size=8, edge_color="black", linewidths=1)
plt.title("Network Topology")
plt.show()
