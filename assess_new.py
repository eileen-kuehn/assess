import argparse
import logging
import subprocess
import json
import datetime
import multiprocessing

from utility.report import update_parser, argparse_init, LVL
from utility.exceptions import mainExceptionFrame

from assess.generators.gnm_importer import CSVEventStreamer, CSVTreeBuilder
from assess.events.events import Event


CLI = argparse.ArgumentParser()
CLI.add_argument(
    "--json",
    action="store_true",
    help="Provide JSON output formatting"
)
CLI.add_argument(
    "--prototypes",
    nargs="+",
    help="Input paths where prototypes are read from",
    type=str
)
CLI.add_argument(
    "--prototype_file",
    help="File to read input paths where prototypes are read from",
    type=str
)
CLI.add_argument(
    "--trees",
    nargs="+",
    help="Input paths where trees are read from",
    type=str
)
CLI.add_argument(
    "--tree_file",
    help="File to read input paths where trees are read from",
    type=str
)
CLI.add_argument(
    "--maximum_number_of_trees",
    help="Maximum number of trees considered from given file",
    type=int
)
CLI.add_argument(
    "--configuration",
    help="Path to configuration used for algorithms",
    type=str,
    required=True
)
CLI.add_argument(
    "--pcount",
    help="Maximum amount of processes to start",
    type=int,
    default=4
)
# Enter matrix mode
# There are also some options you might consider like skipping diagonal or upper part
CLI.add_argument(
    "--matrix",
    action="store_true",
    help="When given, the prototypes/files are calculated to construct a distance matrix"
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


def read_paths(path, maximum=None):
    paths = []
    with open(path) as input_file:
        for index, line in enumerate(input_file):
            if maximum is not None and index >= maximum:
                break
            paths.append(line.strip())
    return paths


def main():
    configdict = {}
    execfile(options.configuration, configdict)
    assert configdict["configurations"] is not None

    if options.tree_file is not None:
        # read paths from input file
        tree_paths = read_paths(options.tree_file, options.maximum_number_of_trees)
    else:
        tree_paths = options.trees
    # if matrix option is set, trees are leading to generate lists
    if options.matrix:
        prototype_paths = tree_paths[:]
    else:
        # also read given prototypes
        if options.prototype_file is not None:
            # read paths from input file
            prototype_paths = read_paths(options.prototype_file)
        else:
            prototype_paths = options.prototypes
    assert len(tree_paths) > 0
    assert len(prototype_paths) > 0
    results = check_algorithms(
        tree_paths=tree_paths,
        prototype_paths=prototype_paths,
        configurations=configdict["configurations"]
    )

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


def do_multicore(count=1, target=None, data=None):
    pool = multiprocessing.Pool(processes=count)
    result_list = pool.map(target, data)
    pool.close()
    pool.join()
    return result_list


def check_algorithm(args):
    """
    :param prototypes:
    :param trees:
    :param algorithm:
    :param decorator:
    :return:
    """
    prototypes = args.get("prototypes", None)
    trees = args.get("trees", None)
    algorithm = args.get("algorithm", None)
    decorator = args.get("decorator", None)

    algorithm.prototypes = prototypes
    decorator.wrap_algorithm(algorithm=algorithm)
    for index, path in enumerate(trees):
        algorithm.start_tree()
        for event in CSVEventStreamer(path):
            algorithm.add_event(event=event)
        algorithm.finish_tree()
    return {
        "algorithm": "%s" % algorithm,
        "signature": "%s" % algorithm.signature,
        "decorator": decorator.descriptive_data()
    }


def check_single_algorithm(args):
    """
    :param prototypes:
    :param tree:
    :param algorithm:
    :param decorator:
    :return:
    """
    prototypes = args.get("prototypes", None)
    tree = args.get("tree", None)
    algorithm = args.get("algorithm", None)
    decorator = args.get("decorator", None)

    algorithm.prototypes = prototypes
    decorator.wrap_algorithm(algorithm=algorithm)
    algorithm.start_tree()
    for event in Event.from_tree(tree):
        algorithm.add_event(event=event)
    algorithm.finish_tree()
    return decorator


def check_algorithms(tree_paths=[], prototype_paths=[], configurations=[]):
    results = {
        "files": tree_paths[:],
        "prototypes": prototype_paths[:],
        "version": subprocess.check_output(["git", "describe"]).strip(),
        "results": []
    }
    tree_builder = CSVTreeBuilder()
    prototypes = []
    for path in prototype_paths:
        prototypes.append(tree_builder.build(path))
    for configuration in configurations:
        algorithms = []
        for algorithm in configuration["algorithms"]:
            for signature in configuration["signatures"]:
                alg = algorithm(signature=signature())
                alg.prototypes = prototypes
                algorithms.append(alg)
        result_list = do_multicore(
            count=options.pcount,
            target=check_single_algorithm,
            data=[{
                      "prototypes": prototypes,
                      "tree": tree_builder.build(path),
                      "algorithm": algorithm,
                      "decorator": configuration["decorator"]()
                  } for algorithm in algorithms for path in tree_paths]
        )
        decorator = None
        for result in result_list:
            if decorator is not None:
                if repr(decorator.algorithm) == repr(result.algorithm) and \
                        repr(decorator.algorithm.signature) == repr(result.algorithm.signature):
                    decorator.update(result)
                else:
                    # we identified a new decorator, so save the last one
                    results["results"].append({
                        "algorithm": "%s" % decorator.algorithm,
                        "signature": "%s" % decorator.algorithm.signature,
                        "decorator": decorator.descriptive_data()
                    })
                    decorator = result
            else:
                decorator = result
        if decorator is not None:
            results["results"].append({
                "algorithm": "%s" % decorator.algorithm,
                "signature": "%s" % decorator.algorithm.signature,
                "decorator": decorator.descriptive_data()
            })
    return results


if __name__ == '__main__':
    update_parser(CLI)
    argparse_init(CLI.parse_args())
    options = CLI.parse_args()

    logging.getLogger().setLevel(LVL.WARNING)
    logging.getLogger("EXCEPTION").setLevel(LVL.INFO)

    mainExceptionFrame(main)
