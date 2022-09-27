
import argparse
from pronto import Ontology

# this is a command line utility
if __name__ != "__main__":
  exit()

# utility takes two arguments - an input file and an output file
parser = argparse.ArgumentParser(description="owl2obo")
parser.add_argument("--owl", action="store",
                    help="path to owl file")
parser.add_argument("--obo", action="store",
                    help="path to obo file")
config = parser.parse_args()

# perform the conversion
ontology = Ontology(config.owl)
with open(config.obo, "wb") as f:
  ontology.dump(f, format="obo")
