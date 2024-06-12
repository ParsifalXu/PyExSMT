import pygraphviz as pgv

# Load the DOT file
dot_file_path = 'demo.py.dot'
test = """digraph {
"(in1 = 0)0" [ label="(in1 = 0)" ];
"(in1 = 0)0" -> "(in2 = 0)1" [ label="1" ];
"(in2 = 0)1" [ label="(in2 = 0)" ];
"(in2 = 0)1" -> "02" [ label="1" ];
"02" [ label="0" ];
"(in2 = 0)1" -> "(in2 + in3)3" [ label="0" ];
"(in2 + in3)3" [ label="(in2 + in3)" ];
"(in1 = 0)0" -> "(0 < (in1 + in2))4" [ label="0" ];
"(0 < (in1 + in2))4" [ label="(0 < (in1 + in2))" ];
"(0 < (in1 + in2))4" -> "05" [ label="1" ];
"05" [ label="0" ];
"(0 < (in1 + in2))4" -> "(in2 = 0)6" [ label="0" ];
"(in2 = 0)6" [ label="(in2 = 0)" ];
"(in2 = 0)6" -> "07" [ label="1" ];
"07" [ label="0" ];
"(in2 = 0)6" -> "(in2 + in3)8" [ label="0" ];
"(in2 + in3)8" [ label="(in2 + in3)" ];
}
"""
graph = pgv.AGraph(test)

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
