from rdflib import Graph, SKOS

file_path = r"..\cgi-vocabs\vocabularies\earthresourceml\EnvironmentalImpact.ttl"
graph = Graph().parse(file_path)
broader_triple = (None, SKOS.narrower, None)
for s, p, o in graph.triples(broader_triple):
    graph.add((o, SKOS.broader, s))

graph.serialize(file_path)
