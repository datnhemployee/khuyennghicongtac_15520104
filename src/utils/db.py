from py2neo import Graph as Connector
username = "neo4j"
password = "a"
uri = "http://localhost:7474/db/data/"
# Connect to authenticated graph database
db = Connector(uri, auth=(username, password), )
