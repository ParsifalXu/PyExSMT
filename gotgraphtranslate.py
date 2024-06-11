import pygraphviz as pgv

# Load the DOT file
dot_file_path = 'xxx.dot'
graph = pgv.AGraph(dot_file_path)

# Function to extract paths
def extract_paths(graph, node, path, paths):
    successors = graph.successors(node)
    if not successors:
        paths.append(path)
        return
    for successor in successors:
        edge = graph.get_edge(node, successor)
        if edge:
            condition = edge.attr['label'] == '1'
            new_path = path + [(successor, condition)]
            extract_paths(graph, successor, new_path, paths)

# Find the starting node (assuming the first node in the graph is the root)
start_node = list(graph.nodes())[0]

# Extract paths
paths = []
extract_paths(graph, start_node, [(start_node, None)], paths)

# Print the paths including the root node
for path in paths:
    print(" -> ".join(f"{node} ({'True' if condition else 'False'})" for node, condition in path))
