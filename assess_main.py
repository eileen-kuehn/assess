import argparse
import logging
import subprocess
import json
import datetime

from utility.report import update_parser, argparse_init, LVL
from utility.exceptions import mainExceptionFrame

from assess.algorithms.signatures.signatures import Signature
from assess.decorators.distancematrixdecorator import DistanceMatrixDecorator
from assess.decorators.compressionfactordecorator import CompressionFactorDecorator
from assess.generators.gnm_importer import GNMCSVEventStreamer, CSVTreeBuilder


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
    "--file",
    help="File to read input files where trees are read from",
    type=str
)
CLI.add_argument(
    "--maximum_number_of_files",
    help="Maximum number of files considered from given file",
    type=int
)
CLI.add_argument(
    "--configuration",
    help="Path to configuration used for algorithms",
    type=str
)
CLI.add_argument(
    "--no_diagonal",
    action="store_true",
    help="When given, the diagonal (regarding a distance matrix) is not calculated"
)
CLI.add_argument(
    "--no_upper",
    action="store_true",
    help="When given, the upper part (regarding a distance matrix) is not calculated"
)


def main():
    configdict = {}
    exec(open(options.configuration).read(), configdict)
    assert configdict["configurations"] is not None

    if options.file is not None:
        # load paths from file
        paths = []
        with open(options.file) as input_file:
            for index, line in enumerate(input_file):
                if options.maximum_number_of_files is not None \
                        and index >= options.maximum_number_of_files:
                    break
                paths.append(line.strip())
    else:
        paths = options.paths

    results = check_algorithms(
        paths=paths,
        configurations=configdict["configurations"]
    )
    if options.json:
        dump = {
            "meta": {
                "date": "%s" % datetime.datetime.now()
            },
            "data": results
        }
        print(json.dumps(dump, indent=2))
    else:
        print(results)


def check_algorithms(paths=None, configurations=None):
    if paths is None:
        paths = []
    if configurations is None:
        configurations = []
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
                # TODO: what if there is no decorator at all? Is it possible?
                decorator = configuration["decorator"]
                decorator.wrap_algorithm(alg)
                for index, path in enumerate(paths):
                    if options.no_upper:
                        # TODO: is it ok to ignore no_diagonal when no_upper
                        # is not given?
                        alg.start_tree(maxlen=index + (0 if options.no_diagonal else 1))
                    else:
                        alg.start_tree()
                    for event in GNMCSVEventStreamer(csv_path=path):
                        alg.add_event(event=event)
                    alg.finish_tree()
                results["results"].append({
                    "algorithm": "%s" % alg,
                    "signature": "%s" % signature_object,
                    "decorator": decorator.descriptive_data()
                })
    return results


def calculate_distance_matrix(paths=None, algorithm=None, signature=Signature):
    if paths is None:
        paths = []
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
        decorator.wrap_algorithm(alg)
        for event in GNMCSVEventStreamer(csv_path=path):
            alg.add_event(event=event)
    print("%s" % ", ".join("%.2f" % value for value
                           in compression.compression_factors()))
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
