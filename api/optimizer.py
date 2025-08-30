import heapq

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def shortest_path(graph, start, end):
    queue = [(0, start)]
    visited = set()
    came_from = {}

    while queue:
        cost, node = heapq.heappop(queue)

        if node in visited:
            continue
        visited.add(node)

        if node == end:
            path = []
            while node in came_from:
                path.append(node)
                node = came_from[node]
            path.append(start)
            return path[::-1]

        for neighbor, weight in graph.get(str(node), []):
            if neighbor not in visited:
                priority = cost + weight + heuristic(neighbor, end)
                heapq.heappush(queue, (priority, tuple(neighbor)))
                came_from[tuple(neighbor)] = node

    return []
