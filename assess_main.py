import argparse
import logging
import subprocess
import json
import datetime

from utility.report import update_parser, argparse_init, LVL
from utility.exceptions import mainExceptionFrame

from assess.decorators.distancematrixdecorator import DistanceMatrixDecorator
from assess.decorators.compressionfactordecorator import CompressionFactorDecorator
from assess.decorators.performancedecorator import PerformanceDecorator
from assess.generators.gnm_importer import CSVEventStreamer, CSVTreeBuilder
from assess.algorithms.signatures.signatures import *


CLI = argparse.ArgumentParser()
CLI.add_argument(
    "--json",
    action="store_true",
    help="Provide JSON output formatting"
)
CLI.add_argument(
    "--paths",
    nargs='+',
    help="Input files where trees are read from",
    type=str
)
CLI.add_argument(
    "--configuration",
    help="Path to configuration used for algorithms",
    type=str
)


def main():
    configdict = {}
    execfile(options.configuration, configdict)
    assert configdict["configurations"] is not None
    paths = options.paths

    results = check_algorithms(paths=paths, configurations=configdict["configurations"])
    if options.json:
        dump = {
            "meta": {
                "date": "%s" % datetime.datetime.now()
            },
            "data": results
        }
        print json.dumps(dump, indent=2)
    else:
        print(results)


def check_algorithms(paths=[], configurations=[]):
    results = {
        "files": paths,
        "version": subprocess.check_output(["git", "describe"]).strip(),
        "results": []
    }
    # fill general information
    tree_builder = CSVTreeBuilder()
    prototypes = []
    for path in paths:
        prototypes.append(tree_builder.build(path))
    for configuration in configurations:
        for algorithm in configuration["algorithms"]:
            for signature in configuration["signatures"]:
                # Most critical, so take as leading decorator
                performance = PerformanceDecorator()
                compression = CompressionFactorDecorator()
                distance = DistanceMatrixDecorator(normalized=False)
                # Build decorator chain with performance as last
                compression.decorator = performance
                distance.decorator = compression
                for path in paths:
                    signature_object = signature()
                    alg = algorithm(signature=signature_object)
                    alg.prototypes = prototypes
                    distance.algorithm = alg
                    for event in CSVEventStreamer(csv_path=path):
                        distance.add_event(event=event)
                results["results"].append({
                    "algorithm": "%s" % alg,
                    "signature": "%s" % signature_object,
                    "compression": compression.compression_factors(),
                    "accumulated_performance": performance.accumulated_performances(),
                    #"performance": performance.performances(),
                    "matrix": distance.distance_matrix
                })
    return results


def calculate_distance_matrix(paths=[], algorithm=None, signature=Signature):
    compression = CompressionFactorDecorator()
    decorator = DistanceMatrixDecorator(normalized=True)
    decorator.decorator = compression
    tree_builder = CSVTreeBuilder()
    prototypes = []
    for path in paths:
        prototypes.append(tree_builder.build(path))
    for path in paths:
        alg = algorithm(signature=signature())
        alg.prototypes = prototypes
        decorator.algorithm = alg
        for event in CSVEventStreamer(csv_path=path):
            decorator.add_event(event=event)
    print("%s" % ", ".join("%.2f" % value for value in compression.compression_factors()))
    print("----------------------")
    for values in decorator.distance_matrix:
        print(", ".join("%.2f" % value for value in values))
    return decorator.distance_matrix

if __name__ == '__main__':
    update_parser(CLI)
    argparse_init(CLI.parse_args())
    options = CLI.parse_args()

    logging.getLogger().setLevel(LVL.WARNING)
    logging.getLogger("EXCEPTION").setLevel(LVL.INFO)

    mainExceptionFrame(main)
