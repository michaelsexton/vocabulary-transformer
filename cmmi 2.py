from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import OWL, RDF, RDFS, SDO, SKOS, XSD
import csv
CMMI = Namespace("http://resource.geosciml.org/classifier/cgi/cmmi/")
CS = URIRef("http://resource.geosciml.org/classifier/cgi/cmmi")


def id_to_iri(id: str):
    replacements = {
        ' ': '-',
        '(': '',
        ')': '',
        '/': '',
        '±': '',
        ',': '',
    }
    replaced_chars = [replacements.get(char, char) for char in id.lower()]
    return ''.join(replaced_chars).replace("--", "-")


IRI_LOOKUP = {}

# make a number-based lookup for all label-based IRIs
with open("deposit-model-terms.csv") as f:
    for lines in csv.reader(f):
        if "DEPOSIT_MODEL_NO" in lines[0]:
            continue
        concept_iri = CMMI[id_to_iri(lines[1])]
        IRI_LOOKUP[lines[0]] = concept_iri


g = Graph()
with open("deposit-model-terms.csv") as f:
    for lines in csv.reader(f):
        if "DEPOSIT_MODEL_NO" in lines[0]:
            continue

        label = lines[1]
        concept_iri = CMMI[id_to_iri(label)]

        g.add((concept_iri, RDF.type, SKOS.Concept))
        g.add((concept_iri, SKOS.prefLabel, Literal(label, lang="en")))
        g.add((concept_iri, SKOS.definition, Literal(label, lang="en")))
        g.add((concept_iri, RDFS.isDefinedBy, CS))
        g.add((concept_iri, SKOS.inScheme, CS))

        g.add((concept_iri, SDO.additionalType, CMMI[lines[2].title()]))
        if lines[2] == "environment":
            g.add((concept_iri, SKOS.topConceptOf, CS))
            g.add((CS, SKOS.hasTopConcept, concept_iri))
        else:  # group or type
            g.add((concept_iri, SKOS.broader, IRI_LOOKUP[lines[3]]))


CS_TEXT = f"""
PREFIX cmmi: <{CMMI}>
PREFIX owl: <{OWL}>
PREFIX sdo: <{SDO}>
PREFIX skos: <{SKOS}>
PREFIX xsd: <{XSD}>

cmmi:Type
    a owl:Class ;
    sdo:name "Mineral Type" ;
.

cmmi:Group
    a owl:Class ;
    sdo:name "Mineral Group" ;
.

cmmi:Environment
    a owl:Class ;
    sdo:name "Mineral Environment" ;
.

<https://linked.dat.gov.au/org/ga>
    a sdo:Organization ;
    sdo:name "Geoscience Australia" ;
    sdo:url "https://www.ga.gov.au"^^xsd:anyURI ;
.

<https://linked.dat.gov.au/org/cgi>
    a sdo:Organization ;
    sdo:name "Commission for Geoscience Information" ;
    sdo:url "https://cgi-iugs.org"^^xsd:anyURI ;
.

<{CS}> a skos:ConceptScheme ;
    skos:prefLabel "Deposit Model Minerals"@en ;
    skos:definition "Minerals and groups of them from the Critical Mineral Mapping Initiative project"@en ;
    sdo:creator <https://linked.dat.gov.au/org/ga> ;
    sdo:publisher <https://linked.dat.gov.au/org/cgi> ;
    sdo:dateCreated "2022-06-30"^^xsd:date ;
    sdo:dateModified "2023-11-11"^^xsd:date ;
    skos:historyNote "Taken from Geoscience Australia's internal database, November 2023" ;
    sdo:copyrightNotice "(c) Commission for Geoscience Information, 2023" ;
    sdo:license <https://purl.org/NET/rdflicense/cc-by4.0> ;
.
"""

g.parse(data=CS_TEXT, format="turtle")

g.bind("cs", CS)
g.bind("", CMMI)
g.serialize(destination="cmmi.ttl", format="longturtle")

