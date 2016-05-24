import argparse
import logging
import subprocess
import json
import datetime
import multiprocessing
import time
import shlex
import os

from utility.report import update_parser, argparse_init, LVL
from utility.exceptions import mainExceptionFrame

from assess.generators.gnm_importer import CSVEventStreamer, CSVTreeBuilder


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
CLI.add_argument(
    "--output_path",
    help="Output path to store files",
    type=str
)

process_list = []
max_count = 0
current_count = 0


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

    if options.matrix:
        for tree_index, tree_path in enumerate(tree_paths):
            for prototype_index, prototype_path in enumerate(prototype_paths):
                if options.no_upper and tree_index < prototype_index:
                    break
                if options.no_diagonal and tree_index == prototype_index:
                    continue
                global max_count
                log_single_calculation(
                    tree=tree_path,
                    prototype=prototype_path,
                    name="%d_%d" % (tree_index, prototype_index)
                )
    else:
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


def check_single_algorithm(args):
    """
    This method expects several parameters to be passed:
    * signature - functor containing the signature to be created
    * algorithm - functor containing the algorithm to be created
    * decorator - functor containing the decorator to be created
    * tree - path to the tree to be processed
    * prototypes - List of prototypes

    :param args: Arguments to be passed to the method containing signature, algorithm, decorator,
                 tree, and prototypes
    :return: Decorator containing resulting data
    """
    signature = args.get("signature", None)()
    algorithm = args.get("algorithm", None)(signature=signature)
    algorithm.prototypes = args.get("prototypes", None)
    decorator = args.get("decorator", None)()
    decorator.wrap_algorithm(algorithm=algorithm)
    algorithm.start_tree()
    for event in CSVEventStreamer(args.get("tree", None)):
        algorithm.add_event(event=event)
    algorithm.finish_tree()
    return decorator


def log_single_calculation(tree=None, prototype=None, name=None):
    while len(process_list) >= options.pcount:
        for process in process_list[:]:
            if process.poll() is not None:
                process_list.remove(process)
                global current_count
                current_count += 1
                print("finished %d / %d processes" % (current_count, max_count))
        time.sleep(1)

    command = "pypy %s --trees %s --prototypes %s --configuration %s --pcount 1 --json" % (
        os.path.realpath(__file__), tree, prototype, options.configuration
    )
    filename = "%s/%s.json" % (options.output_path, name)
    process_list.append(subprocess.Popen(shlex.split(command), stdout=open(filename, "w")))


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

    if options.pcount > 1:
        for configuration in configurations:
            data = []
            for algorithm in configuration["algorithms"]:
                for signature in configuration["signatures"]:
                    for path in tree_paths:
                        data.append({
                            "algorithm": algorithm,
                            "signature": signature,
                            "decorator": configuration["decorator"],
                            "tree": path,
                            "prototypes": prototypes
                        })
            result_list = do_multicore(
                count=options.pcount,
                target=check_single_algorithm,
                data=data)
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
    else:
        for configuration in configurations:
            for algorithm in configuration["algorithms"]:
                for signature in configuration["signatures"]:
                    signature_object = signature()
                    alg = algorithm(signature=signature_object)
                    alg.prototypes = prototypes
                    decorator = configuration["decorator"]()
                    decorator.wrap_algorithm(alg)
                    for index, path in enumerate(tree_paths):
                        alg.start_tree()
                        for event in CSVEventStreamer(csv_path=path):
                            alg.add_event(event=event)
                        alg.finish_tree()
                    results["results"].append({
                        "algorithm": "%s" % alg,
                        "signature": "%s" % signature_object,
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
