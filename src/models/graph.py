import numpy as np
import random


class Graph():
    def __init__(self, nx_G, is_directed, p, q):
        self.G = nx_G
        self.is_directed = is_directed
        self.p = p
        self.q = q

    def _node2vec_walk(self, walk_length, start_node):
        '''
        Simulate a random walk starting from start node.
        '''
        G = self.G
        alias_nodes = self.alias_nodes
        alias_edges = self.alias_edges

        walk = [start_node]

        while len(walk) < walk_length:
            cur = walk[-1]
            cur_nbrs = sorted(G.neighbors(cur))
            if len(cur_nbrs) > 0:
                if len(walk) == 1:
                    walk.append(
                        cur_nbrs[_alias_draw(alias_nodes[cur][0], alias_nodes[cur][1])])
                else:
                    prev = walk[-2]
                    next = cur_nbrs[_alias_draw(alias_edges[(prev, cur)][0],
                                                alias_edges[(prev, cur)][1])]
                    walk.append(next)
            else:
                break

        return walk

    def simulate_walks(self, num_walks, walk_length):
        '''
        Repeatedly simulate random walks from each node.
        '''
        G = self.G
        walks = []
        nodes = list(G.nodes())
        print('Walk iteration:')
        for walk_iter in range(num_walks):
            print(str(walk_iter+1), '/', str(num_walks))
            random.shuffle(nodes)
            for node in nodes:
                walks.append(self._node2vec_walk(
                    walk_length=walk_length, start_node=node))

        return walks

    def _get_alias_edge(self, src, dst):
        '''
        Get the alias edge setup lists for a given edge.
        '''
        G = self.G
        p = self.p
        q = self.q

        unnormalized_probs = []
        for dst_nbr in sorted(G.neighbors(dst)):
            if dst_nbr == src:  # if d(u,x) = 0
                unnormalized_probs.append(G[dst][dst_nbr]['weight']/p)
            elif G.has_edge(dst_nbr, src):
                unnormalized_probs.append(G[dst][dst_nbr]['weight'])
            else:
                unnormalized_probs.append(G[dst][dst_nbr]['weight']/q)

        norm_const = sum(unnormalized_probs)
        norm_probs = [float(unnormalized_prob) /
                      norm_const for unnormalized_prob in unnormalized_probs]

        return _alias_setup(norm_probs)

    def preprocess_transition_probs(self,):
        '''
        Preprocessing of transition probabilities for guiding the random walks
        '''
        G = self.G
        is_directed = self.is_directed

        alias_nodes = {}
        for node in G.nodes():
            unnormalized_probs = [G[node][nbr]['weight']
                                  for nbr in sorted(G.neighbors(node))]

            norm_const = sum(unnormalized_probs)  # Z
            normalized_probs = [
                float(unnormalized_prob)/norm_const for unnormalized_prob in unnormalized_probs]
            alias_nodes[node] = _alias_setup(normalized_probs)

        alias_edges = {}

        if is_directed:
            for edge in G.edges():
                alias_edges[edge] = self._get_alias_edge(edge[0], edge[1])
        else:
            for edge in G.edges():
                alias_edges[edge] = self._get_alias_edge(edge[0], edge[1])
                alias_edges[(edge[1], edge[0])] = self._get_alias_edge(
                    edge[1], edge[0])

        self.alias_nodes = alias_nodes
        self.alias_edges = alias_edges


def _alias_setup(normalized_probs):
    '''
    Compute utility lists for non-uniform sampling from discrete distributions.
    see also: https://lips.cs.princeton.edu/the-alias-method-efficient-sampling-with-many-discrete-outcomes/
    '''

    # print("normalized_probs={0}".format(normalized_probs))
    K = len(normalized_probs)
    q = np.zeros(K)
    J = np.zeros(K, dtype=np.int)

    smaller = []
    larger = []
    for k, normalized_prob in enumerate(normalized_probs):
        # print("q[k={0}]={1}*{2}".format(
        #     k, K, normalized_prob))
        # thay vì chuyển về 1/K thì nhân ngược cho K để tính
        q[k] = K * normalized_prob
        if q[k] < 1.0:
            smaller.append(k)
        else:
            larger.append(k)

    # print("smaller={0}\n larger={1}\n\n".format(
    #     smaller, larger))

    while len(smaller) > 0 and len(larger) > 0:
        # print("pre:: smaller={0}\n larger={1}\n J={2}\n q={3} ".format(
        # smaller, larger, J, q))
        small = smaller.pop()  # get the lastest element
        large = larger.pop()  # get the lastest element

        J[small] = large  # Chính là phần lấp trống của 1/K, thêm phần lấp vào cột nhỏ
        # trừ đi 1 phần đã thêm vào cột nhỏ
        q[large] = q[large] - (1.0 - q[small])
        if q[large] < 1.0:
            smaller.append(large)  # cột lớn có nguy cơ thành cột nhỏ
        else:
            larger.append(large)  # cột lớn vẫn lớn thì giữ nguyên
        # print("post:: smaller={0}\n larger={1}\n J={2}\n q={3} ".format(
        #     smaller, larger, J, q))
    # print("J={0}\n q={1}\n\n".format(
    #     J, q))
    return J, q


def _alias_draw(J, q):
    '''
    Draw sample from a non-uniform discrete distribution using alias sampling.
    '''
    K = len(J)

    kk = int(np.floor(np.random.rand()*K))
    if np.random.rand() < q[kk]:
        return kk
    else:
        return J[kk]
