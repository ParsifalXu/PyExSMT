# Copyright: see copyright.txt

import logging

from symbolic.predicate import Predicate
from symbolic.constraint import Constraint

from symbolic import pred_to_SMT
from pysmt.shortcuts import *

class PathToConstraint:
    def __init__(self, add):
        self.constraints = {}
        self.add = add
        self.root_constraint = Constraint(None, None)
        self.current_constraint = self.root_constraint
        self.expected_path = None
        self.max_depth = 0
        self.mod = None

    def reset(self,expected):
        self.current_constraint = self.root_constraint
        if expected is None:
            self.expected_path = None
        else:
            self.expected_path = []
            tmp = expected
            while tmp.predicate is not None:
                self.expected_path.append(tmp.predicate)
                tmp = tmp.parent

    def whichBranch(self, branch, symbolic_type):
        """ This function acts as instrumentation.
        Branch can be either True or False."""

        if self.max_depth > 0 and self.current_constraint.getLength() >= self.max_depth:
            logging.debug("Max Depth (%d) Reached" % self.max_depth)
            return

        # add both possible predicate outcomes to constraint (tree)
        p = Predicate(symbolic_type, branch)
        p.negate()
        cneg = self.current_constraint.findChild(p)
        p.negate()
        c = self.current_constraint.findChild(p)

        if c is None:
            asserts = [pred_to_SMT(p) for p in self.current_constraint.get_asserts()]
            if self.mod is not None and not is_sat(And(self.mod, pred_to_SMT(p), *asserts)):
                logging.debug("Path pruned by mod (%s): %s %s" % (self.mod, c, p))
                return
            c = self.current_constraint.addChild(p)

            # we add the new constraint to the queue of the engine for later processing
            logging.debug("New constraint: %s" % c)
            self.add(c)
            
        # check for path mismatch
        # IMPORTANT: note that we don't actually check the predicate is the
        # same one, just that the direction taken is the same
        if self.expected_path != None and self.expected_path != []:
            expected = self.expected_path.pop()
            # while not at the end of the path, we expect the same predicate result.
            # At the end of the path, we expect a different predicate result
            done = self.expected_path == []
            logging.debug("DONE: %s; EXP: %s; C: %s" %(done, expected, c))
            if ( not done and expected.result != c.predicate.result or \
                done and expected.result == c.predicate.result ):
                print("Replay mismatch (done=",done,")")
                print(expected)
                print(c.predicate)

        if cneg is not None:
            # We've already processed both
            cneg.processed = True
            c.processed = True
            logging.debug("Processed constraint: %s" % c)

        self.current_constraint = c

    def toDot(self):
        # print the thing into DOT format
        header = "digraph {\n"
        footer = "\n}\n"
        return header + self._toDot(self.root_constraint) + footer

    def _toDot(self,c):
        if (c.parent == None):
            label = "root"
        else:
            label = c.predicate.symtype.__repr__()
            if not c.predicate.result:
                label = "Not("+label+")"
        node = "C" + c.id.__repr__() + " [ label=\"" + label + "\" ];\n"
        edges = [ "C" + c.id.__repr__() + " -> " + "C" + child.id.__repr__() + ";\n" for child in c.children ]
        return node + "".join(edges) + "".join([ self._toDot(child) for child in c.children ])
