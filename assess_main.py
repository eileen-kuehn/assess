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
from assess.decorators.datadecorator import DataDecorator
from assess.generators.gnm_importer import CSVEventStreamer, CSVTreeBuilder
from assess.algorithms.signatures.signatures import *


CLI = argparse.ArgumentParser()
CLI.add_argument(
    "--json",
    action="store_true",
    help="Provide JSON output formatting"
)
CLI.add_argument(
    "--skip",
    action="store_true",
    help="When given two input trees, just a 1x1 matrix is calculated"
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
        "files": paths[:],
        "version": subprocess.check_output(["git", "describe"]).strip(),
        "results": []
    }
    # fill general information
    tree_builder = CSVTreeBuilder()
    prototypes = []
    if options.skip and len(paths) == 2:
        prototypes.append(tree_builder.build(paths.pop(0)))
    else:
        for path in paths:
            prototypes.append(tree_builder.build(path))
    for configuration in configurations:
        for algorithm in configuration["algorithms"]:
            for signature in configuration["signatures"]:
                signature_object = signature()
                alg = algorithm(signature=signature_object)
                alg.prototypes = prototypes

                # Most critical, so take as leading decorator
                performance = PerformanceDecorator()
                compression = CompressionFactorDecorator()
                data = DataDecorator()
                distance = DistanceMatrixDecorator(normalized=False)
                distance2 = DistanceMatrixDecorator(normalized=True)
                # Build decorator chain with performance as last
                compression.decorator = performance
                data.decorator = compression
                distance2.decorator = data
                distance.decorator = distance2
                distance.algorithm = alg
                for path in paths:
                    distance.start_tree()
                    for event in CSVEventStreamer(csv_path=path):
                        distance.add_event(event=event)
                    distance.finish_tree()
                results["results"].append({
                    "algorithm": "%s" % alg,
                    "signature": "%s" % signature_object,
                    "data": data.data(),
                    "compression": compression.data(),
                    "accumulated_performance": performance.accumulated_data(),
                    #"performance": performance.performances(),
                    "matrix": distance.data(),
                    "normalized_matrix": distance2.data()
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
