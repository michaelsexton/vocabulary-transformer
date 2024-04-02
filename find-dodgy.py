import os

from rdflib import Graph, SKOS

path = r"C:\W10DEV\workspace\cgi-vocabs\vocabularies\geosciml"

files = os.listdir(path)

for file in files:
    file_path = os.path.join(path, file)
    graph = Graph().parse(file_path)
    broader_triple = (None, SKOS.narrower, None)
    for s, p, o in graph.triples(broader_triple):
        if (o, SKOS.broader, s) not in graph:
            print(file)
            print(o, SKOS.broader , s)