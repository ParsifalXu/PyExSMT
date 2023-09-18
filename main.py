#!/usr/bin/python3
# Copyright: see copyright.txt

import os
import re
import random
import sys
import logging
from argparse import ArgumentParser

from pyexsmt import uninterp_func_pair
from pyexsmt.loader import *
from pyexsmt.explore import ExplorationEngine

from pysmt.shortcuts import *

def main():
    print("PyExSMT (Python Exploration with SMT)")

    sys.path = [os.path.abspath(os.path.join(os.path.dirname(__file__)))] + sys.path

    parser = ArgumentParser()

    parser.add_argument("--log", dest="loglevel", action="store", \
                                    help="Set log level", default="")
    parser.add_argument('--uninterp', dest="uninterp", nargs=3, \
                                    metavar=('name', 'return_type', 'arg_types'), \
                                    help='<func_name> <return_type> <arg_types>')
    parser.add_argument("--entry", dest="entry", action="store", \
                                    help="Specify entry point", default="")
    parser.add_argument("--graph", dest="dot_graph", action="store_true", \
                                    help="Generate a DOT graph of execution tree")
    parser.add_argument("--summary", dest="summary", action="store_true", \
                                    help="Generate a functional summary")
    parser.add_argument("--max-iters", dest="max_iters", type=int, \
                                    help="Limit number of iterations", default=0)
    parser.add_argument("--max-depth", dest="max_depth", type=int, \
                                    help="Limit the depth of paths", default=0)
    parser.add_argument("--solver", dest="solver", action="store", \
                                    help="Choose SMT solver", default="z3")
    parser.add_argument(dest="file", action="store", help="Select Python file")

    options = parser.parse_args()


    if options.loglevel in ["info", "INFO", "i", "I"]:
        logging.basicConfig(level=logging.INFO, format='%(message)s')
    elif options.loglevel in ["debug", "DEBUG", "d", "D"]:
        logging.basicConfig(level=logging.DEBUG, format='DEBUG:\t%(message)s')
    elif options.loglevel == "":
        pass
    else:
        logging.error("Unrecognized Log Level")
        sys.exit(-1)

    logging.debug("Log Level Set to Debug")

    if options.file == "" or not os.path.exists(options.file):
        parser.error("Missing app to execute")
        sys.exit(1)

    mapping = replace_str2num(options.file)

    if not options.solver in get_env().factory.all_solvers():
        logging.error("Solver %s not available", options.solver)
        sys.exit(-1)
    else:
        solver = options.solver

    summary = options.summary

    filename = os.path.abspath(options.file)

    # Get the object describing the application
    app = loaderFactory(filename, options.entry)
    if app is None:
        sys.exit(1)

    print("Exploring " + app.get_file() + "." + app.get_entry())

    funcs = uninterp_func_pair(options.uninterp, app.get_file())

    result = None
    try:
        engine = ExplorationEngine(app.create_invocation(), solver=solver)
        result_struct = engine.explore(options.max_iters, options.max_depth, funcs)
        print(f"see res: {result_struct}")

        return_vals = result_struct.execution_return_values

        # check the result
        result = app.execution_complete(return_vals)

        # print summary
        if summary:
            summary = result_struct.to_summary()
            temp_summary = str(summary)
            for key, value in mapping.items():
                print(key, value)
                temp_summary = temp_summary.replace(str(value), f"'{key}'")
                
            print("\nSummary:\n%s\n" % temp_summary)

        # output DOT graph
        if options.dot_graph:
            result_struct.to_dot(filename, mapping)

        replace_num2str(options.file, mapping)


    except (ImportError, NotImplementedError, TypeError) as error:
        # create_invocation can raise ImportError
        # Some operators are not implemented.
        # Don't need a stack trace for this.
        logging.error(error)
        sys.exit(1)

    if result is None or result:
        sys.exit(0)
    else:
        sys.exit(1)


def replace_str2num(file):
    with open('demo.py', 'r') as file:
        content = file.read()

    # Find all the strings wrapped in single quotes
    strings = re.findall(r"'(.*?)'", content)
    strings = list(set(strings))
    print(strings)

    # Create a dictionary to store the mapping of strings to random numbers
    mapping = {}

    # Replace each string with a random number and store the mapping
    for string in strings:
        random_number = random.randint(10000, 99999)
        mapping[string] = random_number
        content = content.replace(f"'{string}'", str(random_number))

    print(mapping)
    # exit(0)

    # Write the modified content back to the file
    with open('demo.py', 'w') as file:
        file.write(content)

    return mapping

def replace_num2str(file, mapping):
    with open('demo.py', 'r') as file:
        content = file.read()
    
    for key, value in mapping.items():
        content = content.replace(str(value), f"'{key}'")
    
    with open('demo.py', 'w') as file:
        file.write(content)

if __name__ == "__main__":
    main()