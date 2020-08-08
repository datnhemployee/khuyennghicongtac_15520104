
import os
import argparse
import csv


def normalized(directory: str, neo4j=False) -> str:
    prefix = "file:\\\\\\"
    path = directory.replace(prefix, "")
    if (neo4j == True):
        path = prefix + directory
    return path


def get_current_directory(folder_path="", neo4j=False):
    cwd = os.getcwd()
    path = cwd + folder_path

    if (neo4j == True):
        path = "file:\\\\\\"+path
    return path


def deleteFileIfExisted(filename):
    import errno
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def write_csv(
    output_filename: str,
    content: list,
    header='',
    has_header=True,
    toStr=lambda row: ''
):
    try:
        deleteFileIfExisted(output_filename)
        with open(output_filename, mode='w', encoding='UTF-8') as writer:
            if (has_header):
                writer.write('{0}\n'.format(header))
            for row in content:
                # print("row", row)
                writer.write(toStr(row=row))
    except Exception as e:
        print("err:", e)


def load_model(file_name: str, toList: lambda csv_reader: []) -> list:
    import csv
    with open(file_name, mode='r', encoding='UTF-8') as reader:
        csv_reader = csv.reader(reader, delimiter='|')
        model = list(csv_reader)
        if (len(model) < 2):
            return []
        return toList(model)


def existing_file(filename: str) -> bool:
    if (os.path.isfile(filename) and
            os.access(filename, os.R_OK)):
        return True
    return False


def get_writter_outputfiles(
    elements: set,
    element_attributes: dict,
    output_filename: str,
    annotated: bool = False
) -> dict:
    (path, ext) = os.path.splitext(output_filename)
    output_files = dict()
    for element in elements:
        fieldnames = element_attributes.get(element, None)
        if fieldnames is not None and len(fieldnames) > 0:
            # insert field "id" to every element_attributes
            fieldnames = sorted(list(fieldnames))
            fieldnames.insert(0, 'id')
            # create one file per element
            output_path = '%s_%s%s' % (path, element, ext)
            output_file = open(output_path, mode='w', encoding='UTF-8')
            output_writer = csv.DictWriter(output_file, fieldnames=fieldnames, delimiter='|',
                                           quoting=csv.QUOTE_NONE, quotechar='"', doublequote=True,
                                           restval='', extrasaction='raise', )  # escapechar='\\'
            if not annotated:
                output_writer.writeheader()
            output_files[element] = output_writer
    return output_files


def connect_path_file(path: str, file_name: str) -> str:
    return (path +
            "/{0}".format(file_name)).replace('\\', '/')


"""
    Tệp
"""
FILE_GRAPH_NODE2VEC = "graph.csv"
"""
    Đường dẫn  
"""
PATH_PUBLIC_FOLDER = get_current_directory("\\public")
PATH_PUBLIC_FOLDER_NEO4J = get_current_directory("\\public", neo4j=True)
PATH_GRAPH_NODE2VEC_NEO4J = connect_path_file(
    PATH_PUBLIC_FOLDER_NEO4J, FILE_GRAPH_NODE2VEC)
PATH_GRAPH_NODE2VEC = connect_path_file(
    PATH_PUBLIC_FOLDER, FILE_GRAPH_NODE2VEC)

"""
    Demo database 
"""
FILE_AUTHORS_DB = "authors.csv"
FILE_PRIOR_GRAPH_DB = "prior_graph.csv"
FILE_TEST_GRAPH_DB = "test_graph.csv"


PATH_AUTHORS_DATABASE = connect_path_file(
    PATH_PUBLIC_FOLDER_NEO4J, FILE_AUTHORS_DB)
PATH_PRIOR_GRAPH_DATABASE = connect_path_file(
    PATH_PUBLIC_FOLDER_NEO4J, FILE_PRIOR_GRAPH_DB)
PATH_TEST_GRAPH_DATABASE = connect_path_file(
    PATH_PUBLIC_FOLDER_NEO4J, FILE_TEST_GRAPH_DB)


def get_path_node2vec_emb(_id): return "public/emb{0}".format(_id)


"""
    Hình  
"""
DEFAULT_IMAGE = connect_path_file(
    get_current_directory(), "img/default.png")
PRIOR_IMAGE = connect_path_file(
    get_current_directory(), "img/icon_prior_graph.png")
TEST_IMAGE = connect_path_file(
    get_current_directory(), "img/icon_test_graph.png")
PROBLEM_IMAGE = connect_path_file(
    get_current_directory(), "img/problem.png")
"""
    Icons
"""
ICON_WARNING = connect_path_file(
    get_current_directory(), "img/icon_warning.png")
ICON_BACK = connect_path_file(
    get_current_directory(), "img/icon_back.png")
ICON_ADD = connect_path_file(
    get_current_directory(), "img/icon_add.png")
ICON_NODE2VEC = connect_path_file(
    get_current_directory(), "img/icon_node2vec.png")
ICON_LINK_PREDICTION = connect_path_file(
    get_current_directory(), "img/icon_link_prediction.png")
ICON_CONTENT_BASED = connect_path_file(
    get_current_directory(), "img/icon_content_based.png")
ICON_APP = connect_path_file(
    get_current_directory(), "img/icon_app.png")
ICON_RESEARCHER = connect_path_file(
    get_current_directory(), "img/icon_researcher.png")
ICON_SWITCHER_OFF = connect_path_file(
    get_current_directory(), "img/icon_switch_off.png")
ICON_SWITCHER_ON = connect_path_file(
    get_current_directory(), "img/icon_switch_on.png")
"""
    Database
"""
FILE_DATABASE = "db.json"
PATH_DATABASE = connect_path_file(
    PATH_PUBLIC_FOLDER, FILE_DATABASE)
PAPER_DATABASE = connect_path_file(
    get_current_directory(neo4j=True), "public/paper.csv")
AUTHOR_PAPER_DATABASE = connect_path_file(
    get_current_directory(neo4j=True), "public/author_paper.csv")
AUTHOR_DATABASE = connect_path_file(
    get_current_directory(neo4j=True), "public/author.csv")

"""
    Bài giới thiệu chung
"""
FILE_REPORT = connect_path_file(
    PATH_PUBLIC_FOLDER, "15520104_ThuyetTrinh_KhuyenNghiCongTac.pdf")
FILE_INTRODUCTION = connect_path_file(
    PATH_PUBLIC_FOLDER, "15520104_HuongDanSuDung.pdf")
