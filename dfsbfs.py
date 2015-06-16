def dfs(graph, start):
	visited, stack = set(), [start]
	while stack:
		vertex = stack.pop()
		if vertex not in visited:
			visited.add(vertex)
			stack.extend(graph[vertex] - visited)
	return visited

graph = {'1': set(['2', '3']),
				 '2': set(['1', '4', '5']),
				 '3': set(['1', '6']),
				 '4': set(['2']),
				 '5': set(['2', '6']),
				 '6': set(['3', '5'])}
dfs(graph, '1') 
# set(['1', '3', '2', '5', '4', '6']) 



