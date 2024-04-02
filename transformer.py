import os
import re

from rdflib.namespace import SKOS
from rdflib import Graph, URIRef

import pandas as pd
import functools


LocalHierarchyKey = URIRef('http://resource.geosciml.org/datatype/LocalHierarchyKey')
AbbreviatedLabel = URIRef('http://resource.geosciml.org/datatype/AbbreviatedLabel')

path = r"C:\W10DEV\workspace\cgi-vocabs\vocabularies\earthresourceml"

files = os.listdir(path)

for file in files:
    file_path = os.path.join(path, file)
    graph = Graph()
    graph = graph.parse(file_path, format="ttl")

    broader_triple = (None, SKOS.broader, None)
    broader_frame = pd.DataFrame(((s, p, o) for s, p, o in graph.triples(broader_triple)),
                                 columns=["URL", "Predicate", "Broader"])
    broader_frame.drop("Predicate", axis=1, inplace=True)

    definition_triple = (None, SKOS.definition, None)
    definition_frame = pd.DataFrame(((s, p, o) for s, p, o in graph.triples(definition_triple) if o.language == 'en'),
                                    columns=["URL", "Predicate", "Definition"])
    definition_frame.drop("Predicate", axis=1, inplace=True)

    preflabel_triple = (None, SKOS.prefLabel, None)
    preflabel_frame = pd.DataFrame(((s, p, o) for s, p, o in graph.triples(preflabel_triple) if o.language == 'en'),
                                   columns=["URL", "Predicate", "prefLabel"])
    preflabel_frame.drop("Predicate", axis=1, inplace=True)

    altlabel_triple = (None, SKOS.altLabel, None)
    altlabel_frame = pd.DataFrame(((s, p, o) for s, p, o in graph.triples(altlabel_triple) if o.language == 'en'),
                                  columns=["URL", "Predicate", "altLabel"])
    altlabel_frame.drop("Predicate", axis=1, inplace=True)
    altlabel_frame = altlabel_frame.groupby("URL").altLabel.agg([("altLabel", ', '.join)]).reset_index()

    abbreviated_triple = (None, SKOS.notation, None)
    abbreviated_frame = pd.DataFrame(
        ((s, p, o) for s, p, o in graph.triples(abbreviated_triple) if o.datatype == AbbreviatedLabel),
        columns=["URL", "Predicate", "Abbreviation"])
    abbreviated_frame.drop("Predicate", axis=1, inplace=True)

    hierarchy_key_triple = (None, SKOS.notation, None)
    hierarchy_key_frame = pd.DataFrame(
        ((s, p, o) for s, p, o in graph.triples(hierarchy_key_triple) if o.datatype == LocalHierarchyKey),
        columns=["URL", "Predicate", "Hierarchy Key"])
    hierarchy_key_frame.drop("Predicate", axis=1, inplace=True)

    frames = [abbreviated_frame, preflabel_frame, hierarchy_key_frame, definition_frame, altlabel_frame, broader_frame]

    frames = [frame for frame in frames if not frame.empty]

    output: pd.DataFrame = functools.reduce(lambda left, right: pd.merge(left, right, on='URL', how="outer"), frames)
    output.sort_values("Hierarchy Key", inplace=True)
    output.dropna(subset=["Hierarchy Key"], inplace=True)

    output_file = re.sub("ttl$", 'xlsx', file)
    output.to_excel(os.path.join("vocabs", output_file), index=False)
