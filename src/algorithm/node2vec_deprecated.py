import itertools
from gensim import utils
from numpy import random
import networkx as nx

MAX_WORDS_IN_BATCH = 10000


# def test(source=""):
#     for line in itertools.islice(source, None):
#         line = utils.to_unicode(line).split()
#         i = 0
#         max_sentence_length = MAX_WORDS_IN_BATCH
#         lenght_line = len(line)
#         print("lenght_line:", lenght_line)
#         while i < lenght_line:
#             # list[startIndex:endIndex]
#             yield line[i: i + max_sentence_length]
#             i += max_sentence_length


def run():
    # result = test(
    #     "eqvgeuqg vukieq!#@123gkiuv. bqeuivu qegigivuqe. qeiugviuqegi")
    # for line in result:
    #     print("line: {0}".format(line))
    # once = random.RandomState(hash("sdasd") & 0xffffffff)
    # vector_size = 100
    # print("0x: {0}".format(int(0xffffffff)))
    # print("val: {0}".format(type(hash("sdasd") & 0xffffffff)))
    # print("once: {0}".format(once))
    # print("seeded_vector: {0}".format((once.rand(100) - 0.5)/vector_size))

    G = nx.read_edgelist("src/algorithm/graph",
                         nodetype=int, create_using=nx.DiGraph)

    for edge in G.edges():
        from_node = edge[0]
        to_node = edge[1]
        # return list<to_node:{properties}> from from_node
        # print("G[from_node]: {0}".format(G[from_node]))
        G[from_node][to_node]['weight'] = 1
    import random
    nodes = list(G.nodes())
    start_node = nodes[0]
    print("start_node: {0}".format(start_node))
    # random.shuffle(nodes)
    nbrs = G.neighbors(start_node)
    unnormalized_probs = [[G[start_node][nbr]['weight']]
                          for nbr in sorted(nbrs)]
    for unnormalized_prob in unnormalized_probs:
        print("unnormalized_prob: {0}".format(unnormalized_prob))
        alias
