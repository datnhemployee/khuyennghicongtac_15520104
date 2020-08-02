from utils.db import db
from utils.file import PATH_GRAPH_NODE2VEC, PATH_GRAPH_NODE2VEC_NEO4J, FILE_GRAPH_NODE2VEC, PATH_PUBLIC_FOLDER, PATH_PUBLIC_FOLDER_NEO4J, connect_path_file
import networkx as nx
import numpy as np
import heapq


def alias_setup(normalized_probs):
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


def alias_draw(J, q):
    '''
    Draw sample from a non-uniform discrete distribution using alias sampling.
    '''
    K = len(J)

    kk = int(np.floor(np.random.rand()*K))
    if np.random.rand() < q[kk]:
        return kk
    else:
        return J[kk]


def get_num_author(uid: int, type_db: str) -> int:
    query = """
        MATCH (a:Author)
        WHERE a.{type_db}_{uid}=TRUE
        RETURN COUNT(DISTINCT a) AS num_au
    """.format(uid=uid, type_db=type_db)
    num_au = 0
    for row in db.run(query):
        num_au = int(row[0])
    return num_au


def get_all_author_id(uid: int, type_db: str) -> list:
    query = """
        MATCH (a:Author)
        WHERE a.{type_db}_{uid}=TRUE
        RETURN DISTINCT a.author_id
    """.format(uid=uid, type_db=type_db)
    num_au = get_num_author(uid, type_db=type_db)
    authors = [0 for idx in range(num_au)]

    for (idx, row)in enumerate(db.run(query)):
        authors[idx] = int(row[0])
    return authors


class NetWorkXGraph():
    def __init__(self, is_directed=False, p=1, q=1):
        self.G = None
        self.is_directed = is_directed
        self.p = p
        self.q = q
        self.weight = False
        self.alias_nodes = None
        self.alias_edges = None

    def _create_csv_file(self, project_uid: int, file_path=PATH_GRAPH_NODE2VEC_NEO4J, ):
        """
            Lấy file csv từ Neo4j
            Get CSV file from Neo4j
        """
        query = """
			WITH "MATCH (a:Author)-[r:COLLABORATE_PRIOR]->(b:Author)
				WHERE a.prior_{0}=TRUE AND b.prior_{0}=TRUE
				RETURN DISTINCT a.author_id AS au1, b.author_id AS au2" AS query
			CALL apoc.export.csv.query(query, $file_path, """.format(project_uid)
        query += """ { })
			YIELD file, rows
			RETURN file, rows
            """
        print("query", query)
        num_rows_effective = 0

        for row in db.run(query, parameters={"file_path": file_path}):
            file_name = row[0]
            num_rows_effective = row[1]

        return (file_name, num_rows_effective)

    def create(self, project_uid: int, file_name=FILE_GRAPH_NODE2VEC, weight=False):
        '''
            Khởi tạo mạng NetworkX
            Reads the input network in networkx.
        '''
        path = PATH_GRAPH_NODE2VEC
        neo4j_path = PATH_GRAPH_NODE2VEC_NEO4J
        if (file_name != FILE_GRAPH_NODE2VEC):
            path = connect_path_file(PATH_PUBLIC_FOLDER, file_name)
            neo4j_path = connect_path_file(PATH_PUBLIC_FOLDER_NEO4J, file_name)

        self._create_csv_file(file_path=neo4j_path, project_uid=project_uid)

        self.weight = weight
        if (self.weight):
            # no weights are add in graph init file
            self.G = nx.read_edgelist(path,
                                      nodetype=str,
                                      delimiter=",",
                                      data=(('weight', float),),
                                      create_using=nx.DiGraph(),)
        else:
            self.G = nx.read_edgelist(path,
                                      nodetype=str,
                                      delimiter=",",
                                      create_using=nx.DiGraph())
            for edge in self.G.edges():
                self.G[edge[0]][edge[1]]['weight'] = 1

        if not self.is_directed:
            self.G = self.G.to_undirected()

        self.G.remove_nodes_from(['"au1"', '"au2"'])
        self.G = nx.relabel_nodes(
            self.G, lambda name: name.replace("\"", ""))

    def _node2vec_walk(self, walk_length, start_node):
        '''
            Bước ngẫu nhiên với hệ số alpha
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
                        cur_nbrs[alias_draw(alias_nodes[cur][0], alias_nodes[cur][1])])
                else:
                    prev = walk[-2]
                    next = cur_nbrs[alias_draw(alias_edges[(prev, cur)][0],
                                               alias_edges[(prev, cur)][1])]
                    walk.append(next)
            else:
                break

        return walk

    def simulate_walks(self, num_walks, walk_length) -> list:
        import random
        '''
            Lặp lại bước ngẫu nhiên tại mỗi nút để lấy được tập bước
            Repeatedly simulate random walks from each node.
        '''
        if (self.G == None):
            raise "No graph has been create. The create function should be call first."
        self._preprocess_transition_probs()
        G = self.G

        nodes = list(G.nodes())
        num_nodes = len(nodes)
        print("num_node ", num_nodes)

        walks = [["" for l in range(walk_length)]
                 for idx_node in range(num_nodes * num_walks)]
        print('Walk iteration:')
        for walk_iter in range(num_walks):
            print(walk_iter+1, '/', num_walks, )
            random.shuffle(nodes)
            for node_idx, start_node in enumerate(nodes):
                step = self._node2vec_walk(
                    walk_length=walk_length, start_node=start_node)
                # print("walks[", walk_iter + node_idx *
                #       num_walks, ']')
                for (step_idx, node) in enumerate(step):
                    try:
                        # tempNode = node.replace("\"", "")
                        walks[walk_iter + node_idx *
                              num_walks][step_idx] = node
                    except:
                        print("Unable to walk from", start_node)

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

        return alias_setup(norm_probs)

    def _preprocess_transition_probs(self,):
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
            alias_nodes[node] = alias_setup(normalized_probs)

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

    def get_temp_graph(self):
        path = PATH_GRAPH_NODE2VEC
        G = nx.read_edgelist(path,
                             nodetype=str,
                             delimiter=",",
                             create_using=nx.DiGraph())
        G = G.to_undirected()
        G.remove_nodes_from(['"au1"', '"au2"'])
        G = nx.relabel_nodes(G, lambda name: int(name.replace("\"", "")))
        return G

    def get_2_hop_u(self, G, u,):
        result = []
        for v in nx.neighbors(G, u):
            for neighbor in nx.neighbors(G, v):
                if (u == neighbor):
                    continue
                result.append((u, neighbor))
        return result

    def export_jaccard_coefficient(self, G):

        print("train",)
        result = nx.jaccard_coefficient(G,)

        import csv
        with open("public/jaccard.csv", "w") as _file:
            wr = csv.writer(_file, dialect='excel')
            wr.writerows(result)

    def export_common_neighbor(self, G):

        print("train",)
        result = nx.common_neighbors(G,)

        import csv
        with open("public/commonNeigh.csv", "w") as _file:
            wr = csv.writer(_file, dialect='excel')
            wr.writerows(result)

    def export_adamic_adar(self, G, project_uid):

        import csv
        num_author = get_num_author(project_uid, "prior")
        predics = [(0, 0, 0.0) for author_idx in range(10 * num_author)]
        i = 0
        print("train", num_author)
        for u in G.nodes():
            # if (i >= 100000):
            #     break
            # if (i >= num_author):
            #     break
            _2hoplist = self.get_2_hop_u(G, u)
            preds = nx.adamic_adar_index(G, _2hoplist)
            preds = heapq.nlargest(10, preds, key=lambda x: x[2])
            for (idx, pred) in enumerate(preds):
                predics[i * 10 + idx] = pred
            # if (i < 4):
            #     print("result", predics[i])
            i += 1

        print(i)

        with open("public/jaccard.csv", "w") as _file:
            wr = csv.writer(_file, quoting=csv.QUOTE_NONE,
                            delimiter="|",)
            wr.writerows(predics)
        from datetime import datetime
        t2 = datetime.now()
        print("end:{0}".format(t2))
        print("done",)

        # from evalne.evaluation.evaluator import LPEvaluator
        # from evalne.evaluation.score import Scoresheet
        # from evalne.utils import preprocess as pp

        # print("train", num_author)
        # G = pp.load_graph(PATH_GRAPH_NODE2VEC)
        # G, _ = pp.prep_graph(G)

        # with open("public/jaccard.csv", "wb") as _file:
        #     wr = csv.writer(_file, dialect='excel')
        #     wr.writerows(predic)
        # print("done",)

    def export_katz(self, G):

        print("train",)
        result = nx.katz_centrality_numpy(G,)

        import csv
        with open("public/jaccard.csv", "w") as _file:
            wr = csv.writer(_file, dialect='excel')
            wr.writerows(result)
