from screens.app import App
from utils.db import db

"""
Các thuật toán Collaborative Filtering
"""


def run_CF_cosine():
    from algorithm.collaborative_filtering.main import memory_based_run as run
    run(db, neighbourhood_size=5, similarity_func="cosine")
    # chỉnh lại theo cosine
    from utils.valuate import valuate
    valuate(db, "COLLABORATIVE_FILTERING",
            predicate="AND r.type_sim=\"cosine\"")
    # precision 0.057569296375266525 recall 0.033764068361817424 f_measure 0.042564372044140826


def run_CF_pearson():
    from algorithm.collaborative_filtering.main import memory_based_run as run
    run(db, neighbourhood_size=5, similarity_func="pearson")

    from utils.valuate import valuate
    valuate(db, "COLLABORATIVE_FILTERING",
            predicate="AND r.type_sim=\"pearson\"")
    # precision 0.04052098408104197 recall 0.02392140111063648 f_measure 0.030083266183185606


def run_CF_kmeans():
    from algorithm.collaborative_filtering.main import model_based_run as run
    run(db, neighbourhood_size=5, model="kmeans")

    from utils.valuate import valuate
    valuate(db, "COLLABORATIVE_FILTERING",
            predicate="AND r.model=\"kmeans\"")
    # precision 0.02643171806167401 recall 0.015741145605596852 f_measure 0.019731433269388875


"""
Các thuật toán Link Prediction
"""


def run_common_neighbor():
    from algorithm.link_prediction.common_neighbor import run
    run(db, neighbourhood_size=5,)

    from utils.valuate import valuate
    valuate(db, "COMMON_NEIGHBOR")
    # precision 0.08044382801664356 recall 0.05558217537134643 f_measure 0.06574100311703034


def run_adarmic_adar():
    from algorithm.link_prediction.adamic_adar import run
    run(db, neighbourhood_size=5,)

    from utils.valuate import valuate
    valuate(db, "ADAMIC_ADAR")
    # precision 0.08614748449345279 recall 0.05122950819672131 f_measure 0.06425083526085838


def run_jacard_coefficient():
    from algorithm.link_prediction.jaccard_coefficient import run
    run(db, neighbourhood_size=5,)

    from utils.valuate import valuate
    valuate(db, "JACCARD_COEFFICIENT")
    # precision 0.07788595271210014 recall 0.045845272206303724 f_measure 0.05771708322597269


def run_shortest_path():
    from algorithm.link_prediction.shortest_path import run
    run(db, neighbourhood_size=5,)

    from utils.valuate import valuate
    valuate(db, "SHORTEST_PATH")
    # precision 0.06882022471910113 recall 0.04021337710299549 f_measure 0.05076405076405076


def run_kazt():
    from algorithm.link_prediction.kazt import run
    run(db, neighbourhood_size=5,)

    from utils.valuate import valuate
    valuate(db, "KAZT")
    # precision 0.08991077556623199 recall 0.053909465020576135 f_measure 0.0674041677386159


"""
Các thuật toán Content based
"""


def run_content_based():
    from algorithm.content_based.main import run
    run(db, neighbourhood_size=5,)

    from utils.valuate import valuate
    valuate(db, "CONTENT_BASED")
    # precision 0.40135440180586907 recall 0.3284078315478389 f_measure 0.36123527021535967


# def run_svm_link_prediction():
#     from algorithm.svm import run_predict_link as run
#     run(graph)


"""
Các thuật toán Node2vec
"""


def run_node2vec():
    from algorithm.node2vec.learn import run, predicted_link_to_db
    run(db)
    predicted_link_to_db(db)


def valuate_node2vec():
    from algorithm.node2vec.learn import valuate as run
    run(db)
    # precision 0.3855421686746988 recall 0.3106796116504854 f_measure 0.3440860215053763


# def run_link_predict_node2vec():
#     from algorithm.node2vec.svm import prepare_training_pair_link_label
#     pairs = prepare_training_pair_link_label(graph)

#     from algorithm.svm import run
#     (w, b) = run(pairs)
#     print("w=", w, b)

"""
    Các thuật toán học máy
"""


def run_node2vec_logistic_regression():
    from algorithm.node2vec.logistic_regression import run, valuate

    run(db)
    valuate(db)
    # precision 0.7266009852216748 recall 0.4880066170388751 f_measure 0.5838693715982187


def run_link_prediction_logistic_regression():
    from algorithm.link_prediction.logistic_regression import run, valuate

    run(db)
    valuate(db)


def run_content_based_logistic_regression():
    from algorithm.content_based.logistic_regression import create_training_pair, run
    pairs = create_training_pair(db)

    run(pairs)


def create_inital_graph():
    from utils.time import watch
    from startup.database import init
    watch(init, db)


def create_machine_learning_database():
    from startup.machine_learning import create_machine_learning_database as run
    run(db)


def main():

    app = App()
    app.mainloop()

    """
    Khởi tạo mạng đồng tác giả
    """
    # create_inital_graph()
    """
    Khởi tạo mạng đồng tác giả dùng cho học máy
    """
    # create_machine_learning_database()
    """
    Các thuật toán Node2vec
    """
    # run_node2vec()
    # valuate_node2vec()
    """
    Các thuật toán học máy 
    """
    # run_node2vec_logistic_regression()
    # run_content_based_logistic_regression()
    # run_link_prediction_logistic_regression()
    """
    Các thuật toán Collaborative Filtering
    """
    # run_CF_cosine()
    # run_CF_pearson()
    # run_CF_kmeans()

    """
    Các thuật toán Content based
    """
    # run_content_based()
    """
    Các thuật toán Link Prediction
    """
    # run_kazt()
    # run_shortest_path()
    # run_jacard_coefficient()
    # run_adarmic_adar()
    # run_common_neighbor()


if __name__ == '__main__':
    main()
