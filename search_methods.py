import numpy as np
import igraph as ig
import instance_generation as instances

'''
Now try to find k-colorings of each map, for both
k=3 and k =4, 
    backtracking, OK
    backtracking with forward checking OK
    backtracking with MAC OK
    using min-conflicts
    
Construct a table of average run times for each algorithm for values
of n up to the largest you can manage. Comment on your results.
'''
def valid_backtrack(g, k):
    c = set()
    for e in g.es:
        c1 = g.vs[e.source]['color']
        c2 = g.vs[e.target]['color']
        if c1 == c2:
            return False
        if c1 == -1 or c2 == -1:
            return False
        c.add(c1)
        c.add(c2)

    if len(c) > k:
        return False

    return True


def valid_backtrack_fc(g, k):
    return not -1 in g.vs['color']


def dead_end(steps, fail):
    return tuple(steps) in fail


def get_rules_backtrack(root, g, k):
    return np.arange(k)


# forward checking
def get_rules_backtrack_fc(root, g, k):
    invalid_colors = set()
    for v in g.neighbors(root):
        c = g.vs[v]['color']
        invalid_colors.add(c)

    rules = []
    for c in range(k):
        if c in invalid_colors:
            continue
        else:
            rules.append(c)
    return rules


def apply_rule(v, g, c):
    g_copy = g.copy()
    g_copy.vs[v]['color'] = c
    return g_copy


def get_next(g):
    degrees = [g.degree(i) if c == -1 else -1 for i, c in enumerate(g.vs['color'])]
    if set(degrees) == set({-1}):
        return -1
    return np.argmax(degrees)


def add_inference_backtrack(inferences, g, val):
    return True, inferences


def add_inference_backtrack_fc(inferences, g, x_i):
    neighbors = g.neighbors(x_i)
    c = g.vs[x_i]['color']
    inferences[x_i] = set({c})
    for n_index in neighbors:
        if c in inferences[n_index]:
            if g.vs[n_index]['color'] == -1:
                if len(inferences[n_index] - {c}) == 0:
                    return False, None
                inferences[n_index].remove(c)

    return True, inferences


def remove_inconsistent_values(inferences, x_i, x_j):
    removed = False
    for x in inferences[x_i].copy():
        if x in inferences[x_j]:
            if inferences[x_j] == set([x]):
                inferences[x_i].remove(x)
                removed = True
    return removed, inferences


# ac-3
def ac3(inferences, g, arcs):
    queue = arcs
    new_inferences = inferences.copy()
    while len(queue) > 0:
        x_i, x_j = queue[0]
        queue = queue[1:]
        removed, new_inferences = remove_inconsistent_values(new_inferences, x_i, x_j)
        if removed:
            if len(new_inferences[x_i]) == 0:
                return False, None
            inferences = new_inferences
            for x_k in g.neighbors(x_i):
                if x_k != x_j:
                    queue.append((x_k, x_i))

    return True, inferences


def add_inference_backtrack_mac(inferences, g, x_i):
    x_i_neighbors = g.neighbors(x_i)
    inferences[x_i] = {g.vs[x_i]['color']}
    arcs = []
    for x_j in x_i_neighbors:
        if g.vs[x_j]['color'] == -1:
            arcs.append((x_j, x_i))

    return ac3(inferences, g, arcs)


def _backtrack(g, k, inferences, add_inference, valid_colors):
    if valid_colors(g, k):
        return g

    val = get_next(g)

    if val == -1:
        return False
    rules = inferences[val]
    for rule in rules:
        g.vs[val]['color'] = rule
        inference_possible, new_inference = add_inference(inferences.copy(), g, val)
        if inference_possible:
            result = _backtrack(g, k, new_inference, add_inference, valid_colors)
            if result:
                return result
        g.vs[val]['color'] = -1

    return False


def backtrack(g, k, method=''):
    def get_name(pos):
        A = ['red', 'blue', 'green', 'orange', 'gray']
        return A[pos]

    g.vs['color'] = -1
    inferences = [set(np.arange(k)) for i in range(g.vcount())]
    if method == '':
        g_result = _backtrack(g.copy(), k, inferences, add_inference_backtrack, valid_backtrack)
    elif method == 'forward checking':
        g_result = _backtrack(g.copy(), k, inferences, add_inference_backtrack_fc, valid_backtrack_fc)
    elif method == 'MAC':
        arcs = [e.tuple for e in g.es]
        possible, inferences = ac3(inferences, g.copy(), arcs)
        if possible:
            g_result = _backtrack(g.copy(), k, inferences, add_inference_backtrack_mac, valid_backtrack_fc)
        else:
            g_result = False
    else:
        print('invalid method')
        return False

    if g_result:
        g_result.vs['color'] = [get_name(c) for c in g_result.vs['color']]
        return True, g_result
    else:
        g.vs['color'] = 'gray'
        return False, g


def init_colors(g, k):
    n = g.vcount()
    colors = np.random.randint(0, k, n, dtype='int')
    g.vs['color'] = colors
    return g


def conflict_var(g):
    count_conflicts = dict()
    for node1 in g.vs:
        count_conflicts[node1.index] = 0
        c1 = node1['color']
        for node2 in g.neighbors(node1):
            c2 = g.vs[node2]['color']
            if c1 == c2:
                count_conflicts[node1.index] += 1

    max_count = -1
    max_node = -1
    for node, count in count_conflicts.items():
        if count > max_count:
            max_node = node
            max_count = count

    return max_node


def get_value_min_conflict(g, k, x):

    colors = []
    for node in g.neighbors(x):
        c = g.vs[node]['color']
        colors.append(c)

    unique, count = np.unique(colors, return_counts=True)
    available_colors = set(np.arange(k)) - set(unique)

    if len(available_colors) > 0:
        return np.min(list(available_colors))
    else:
        arg = np.argmin(count)
        return unique[arg]


def min_conflicts(g, k, arg=None):
    names = ['red', 'blue', 'orange', 'green', 'gray']

    max_steps = g.vcount()*10
    current_state = init_colors(g.copy(), k)
    for _ in range(max_steps):
        if valid_backtrack(current_state, k):
            colors = [names[c] for c in current_state.vs['color']]
            current_state.vs['color'] = colors
            return True, current_state
        x = conflict_var(current_state)
        x_value = get_value_min_conflict(current_state, k, x)
        current_state.vs[x]['color'] = x_value

    g.vs['color'] = 'gray'
    return False, g


def get_toy():  # australia
    g = ig.Graph()
    g.add_vertices(7)
    g.vs['name'] = ['wa', 'nt', 'q', 'nsw', 'v', 'sa', 't']
    g.add_edges([('wa', 'nt'), ('wa', 'sa'), ('nt', 'sa'), ('nt', 'q'),
                 ('sa', 'q'), ('sa', 'nsw'), ('sa', 'v'),
                 ('q', 'nsw'), ('v', 'nsw')])
    return g


if __name__ == '__main__':
    for _ in range(5):
        g = instances.get_color_map_instance(5)
        print(g)

        # g = get_toy()
        k = 3
        solution, g1 = backtrack(g, k)
        print(solution)
        ig.plot(g1, vertex_size=10, layout=g.vs['coord'])

        solution, g2 = backtrack(g, k, 'forward checking')
        print(solution)
        ig.plot(g2, vertex_size=10, layout=g.vs['coord'])

        solution, g3 = backtrack(g, k, 'MAC')
        print(solution)
        ig.plot(g3, vertex_size=10, layout=g.vs['coord'])

        solution, g4 = min_conflicts(g, k)
        print(solution)
        ig.plot(g4, vertex_size=10, layout=g.vs['coord'])

        print('--------')
