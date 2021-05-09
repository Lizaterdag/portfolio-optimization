from collections import defaultdict

from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
from dwave_networkx.algorithms.coloring import min_vertex_color_qubo
import networkx as nx

import matplotlib
matplotlib.use("agg")
from matplotlib import pyplot as plt

sampler = EmbeddingComposite(DWaveSampler())

G = nx.Graph()
G.add_edges_from([(1,2), (1,3), (2,3), (3,4), (3,5), (4,5), (4,6), (5,6), (6,7)])

Q = min_vertex_color_qubo(G)

sampleset = sampler.sample_qubo(Q, num_reads = 100)
for sample, energy, num_occ in sampleset.data(['sample', 'energy', 'num_occurrences']):
    colors_chosen = [i for i in sample if sample[i] == 1]
    print(colors_chosen, energy, num_occ)
