import numpy as np
import igraph as ig
import matplotlib.pyplot as plt
from collections import defaultdict

error = 0.0001 # constante utilizada como limite para considerar dois valores float como iguais

class Point:
    """
        Representação de um ponto com coordenadas x, y.
        Alguns métodos foram implementados para tratar, por exemplo,
        quando dois pontos são considerados iguais.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return np.abs(self.x - other.x) < error \
               and np.abs(self.y - other.y) < error

    def __hash__(self):
        return hash(str(self))

    def dist(self, other):
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2

    def val(self):
        return self.x, self.y

    def __iter__(self):
        return iter([self.x, self.y])


class Segment:
    """
        Representação de um segmento de reta, dados dois pontos P1 e P2 como entrada.
        Os coeficientes que descrevem a reta logo são calculados.
        b é o coeficiente angular
        Método para verificar quando há interseção entre dois segmentos foi implementado também.

    """
    def _b(self):
        if self.p1.x == self.p2.x:
            return 0
        return (self.p2.y - self.p1.y) / (self.p2.x - self.p1.x)

    def _a(self):
        return - self.b * self.p2.x + self.p2.y

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        # xb + a = y
        self.b = self._b()
        self.a = self._a()

    def get_intersection(self, other):
        x = (other.a - self.a) / (self.b - other.b)  # teste para evitar denominador 0 já foi feito antes
        return x

    '''
        Avalia se dois segmentos possuem interseção ou não.
        Para isso, são consideradas as retas onde os segmentos passam, é calculado o ponto
        da interseção (se houver) e por fim, se esse ponto pertence aos dois segmentos. 
    '''
    def intersects(self, other):
        # nesse caso, quando os pontos da extremidade são iguais não consideramos
        if self.p1 == other.p1 or self.p1 == other.p2:
            return False

        # nesse caso, quando os pontos da extremidade são iguais não consideramos
        if self.p2 == other.p1 or self.p2 == other.p2:
            return False

        # intervalos completamente diferentes
        if max(other.p1.x, other.p2.x) < min(self.p1.x, self.p2.x):
            return False

        if np.abs(self.b - other.b) < error:  # são paralelos e não coincidem
            return False

        x = self.get_intersection(other)

        return min(self.p1.x, self.p2.x) < x < max(self.p1.x, self.p2.x) \
               and min(other.p1.x, other.p2.x) < x < max(other.p1.x, other.p2.x)

    def plot(self):
        plt.plot([self.p1.x, self.p2.x], [self.p1.y, self.p2.y])


def is_possible(g, x, y):
    from shapely.geometry import LineString

    P1 = g.vs[x]['coord']
    P2 = g.vs[y]['coord']
    segm1 = Segment(P1, P2)
    line = LineString([P1.val(), P2.val()])

    for e in g.es:
        P3 = g.vs[e.source]['coord']
        P4 = g.vs[e.target]['coord']
        segm2 = Segment(P3, P4)

        my_test = segm1.intersects(segm2)

        other = LineString([P3.val(), P4.val()])
        shapely_test = line.intersects(other)

        if my_test != shapely_test:
            if x == e.source or x == e.target or y == e.source or y == e.target:
                pass
            else:
                plt.figure()
                segm1.plot()
                segm2.plot()
                plt.show()

        if my_test:
            return False

    return True


def get_nearest_point(points, x, invalid):
    arg_min = -1
    min_dist = 9999
    Px = points[x]
    for i, Pother in enumerate(points):
        if x == i or i in invalid:
            continue
        else:
            d = Px.dist(Pother)
            if d < min_dist:
                arg_min = i
                min_dist = d

    return arg_min


def get_points(n):
    points = set()
    while len(points) < n:
        x = np.random.uniform(0, 1)
        y = np.random.uniform(0, 1)
        points.add(Point(x, y))

    points = list(points)
    return points


'''
Método para a geração de instâncias de grafos planos. 
O argumento n é o tamanho do grafo dado como saída. 
O algoritmo segue a sugestão de implementação da questão 6.10 do livro do Russel.
'''
def get_color_map_instance(n):
    points = get_points(n)

    g = ig.Graph()
    g.add_vertices(n)
    g.vs['coord'] = points

    invalid_edges = defaultdict(lambda: set())
    valid_vertices = np.arange(0, n)
    while len(valid_vertices) > 0:
        np.random.shuffle(valid_vertices)
        x = valid_vertices[0]
        y = get_nearest_point(points, x, invalid_edges[x])

        if is_possible(g, x, y):
            g.add_edge(x, y)

        invalid_edges[x].add(y)
        invalid_edges[y].add(x)

        if len(invalid_edges[x]) >= n - 1:
            valid_vertices = valid_vertices[valid_vertices != x]
        if len(invalid_edges[y]) >= n - 1:
            valid_vertices = valid_vertices[valid_vertices != y]

    return g


if __name__ == '__main__':

    '''
    Se esse arquivo for executado sozinho, é possível rodar esse pequeno teste de geração de instâncias 
    com visualização.
    '''
    for n in range(100, 251, 50):
        print(n)
        for j in range(10):
            g = get_color_map_instance(n)
            ig.plot(g, vertex_size=5, layout=g.vs['coord'])
