import logging
from graphviz import Source

from pyexsmt import pred_to_smt, get_concr_value, match_smt_type
from pyexsmt.symbolic_types import SymbolicObject
from pyexsmt.symbolic_types.symbolic_object import to_pysmt, is_instance_userdefined_and_newclass

from pysmt.shortcuts import *

class Result(object):
    def __init__(self, path):
        self.path = path
        self.generated_inputs = []
        self.execution_return_values = []
        self.list_rep = None
        self.curr_id = 0

    def record_inputs(self, inputs):
        inputs = [(k, get_concr_value(inputs[k])) for k in inputs]
        self.generated_inputs.append(inputs)
        logging.debug("RECORDING INPUTS: %s", inputs)

    def record_output(self, ret):
        logging.info("RECORDING EFFECT: %s -> %s", self.path.current_constraint, ret)
        self.path.current_constraint.effect = ret
        if isinstance(ret, SymbolicObject):
            ret = ret.get_concr_value()
        self.execution_return_values.append(ret)

    def to_dot(self, filename, mapping):
        header = "digraph {\n"
        footer = "}\n"
        if self.list_rep is None:
            self.list_rep = self._to_list_rep(self.path.root_constraint)
        print(f"see list rep: {self.list_rep}")
        # print(f"see list rep type: {type(self.list_rep[1])}")
        # print(f"check list rep type: {isinstance(self.list_rep[1], list)}")
        tree = rep2Tree(self.list_rep)
        print(tree)
        origin_paths = path_finder(tree)
        paths = []
        for path in origin_paths:
            for key, value in mapping.items():
                path = path.replace(str(value), f"'{key}'")
            paths.append(path)
        for path in paths:
            print(path)



        dot = self._to_dot(self.list_rep)
        dot = header + dot + footer
        for key, value in mapping.items():
            dot = dot.replace(str(value), f"'{key}'")
        
        s = Source(dot, filename=filename+".dot", format="png")
        s.view()

    def _to_dot(self, list_rep):
        curr = self.curr_id
        if isinstance(list_rep, list) and len(list_rep) == 3:
            rep = list_rep[0]
            dot = "\"%s%d\" [ label=\"%s\" ];\n" % (rep, curr, rep)
            self.curr_id += 1

            for slot in range(1, 3):
                child = list_rep[slot]
                if child is None:
                    continue
                crep = child[0] if isinstance(child, list) else to_pysmt(child)
                crep = str(crep).replace('"', '\\\"')
                dot += "\"%s%d\" -> \"%s%d\" [ label=\"%d\" ];\n" \
                        %(rep, curr, crep, self.curr_id, slot%2)
                dot += self._to_dot(child)
            return dot
        elif list_rep is not None:
            list_rep = to_pysmt(list_rep)
            list_rep = str(list_rep).replace('"', '\\\"')
            temp = "\"%s%d\" [ label=\"%s\" ];\n" % (list_rep, curr, list_rep)
            self.curr_id += 1
            return temp
        else:
            return ""

    def to_path(self, filename, mapping):
        header = "digraph {\n"
        footer = "}\n"
        if self.list_rep is None:
            self.list_rep = self._to_list_rep(self.path.root_constraint)
        # print(f"see list rep: {self.list_rep}")
        root = self.list_rep
        paths_list = []
        path = ""
        node_flag = 1
        pl = self.dfs(root, path, paths_list, node_flag)
        
        for i in range(len(pl)):
            for key, value in mapping.items():
                pl[i] = pl[i].replace(str(value), f"'{key}'")
                # print(path)
        print(f"see res: {pl}")

        dot = self._to_path(self.list_rep)
        dot = header + dot + footer
        for key, value in mapping.items():
            dot = dot.replace(str(value), f"'{key}'")
        s = Source(dot, filename=filename+".dot", format="png")
        s.view()

    def dfs(self, root, path, paths_list, node_flag):
        # 0->root / 1->left / 2->right
        if not isinstance(root, list):
            if root is not None:
                if node_flag:
                    path += str(root)
                else:
                    # l = path.split("->")
                    # l[-2] = '!' + l[-2]
                    # path = "->".join(l)
                    path += str(root)
                paths_list.append(path)
        else:
            # if node_flag:
            #     path += str(root[0])
            # else:
            #     path += '!' + str(root[0])
            path += str(root[0])
            path += "->"
            self.dfs(root[1], path, paths_list, 1)
            self.dfs(root[2], path, paths_list, 0)

        return paths_list

    def _to_path(self, list_rep):
        curr = self.curr_id
        if isinstance(list_rep, list) and len(list_rep) == 3:
            rep = list_rep[0]
            dot = "\"%s%d\" [ label=\"%s\" ];\n" % (rep, curr, rep)
            self.curr_id += 1

            for slot in range(1, 3):
                child = list_rep[slot]
                if child is None:
                    continue
                crep = child[0] if isinstance(child, list) else to_pysmt(child)
                crep = str(crep).replace('"', '\\\"')
                dot += "\"%s%d\" -> \"%s%d\" [ label=\"%d\" ];\n" \
                        %(rep, curr, crep, self.curr_id, slot%2)
                dot += self._to_path(child)
            return dot
        elif list_rep is not None:
            list_rep = to_pysmt(list_rep)
            list_rep = str(list_rep).replace('"', '\\\"')
            temp = "\"%s%d\" [ label=\"%s\" ];\n" % (list_rep, curr, list_rep)
            self.curr_id += 1
            return temp
        else:
            return ""

    
    
    
    def to_summary(self, unknown=Symbol('Unknown', INT)):
        if self.list_rep is None:
            self.list_rep = self._to_list_rep(self.path.root_constraint)
        summary = self._to_summary(self.list_rep, unknown)
        return summary

    def _to_summary(self, list_rep, unknown):
        if isinstance(list_rep, list) and len(list_rep) == 3:
            return Ite(list_rep[0], self._to_summary(list_rep[1], unknown),\
                        self._to_summary(list_rep[2], unknown))
        elif list_rep is not None:
            if isinstance(list_rep, SymbolicObject) or not is_instance_userdefined_and_newclass(list_rep):
                return match_smt_type(to_pysmt(list_rep), unknown.get_type())
            else:
                print(list_rep, type(list_rep))
                raise TypeError("Summaries don't support object returns")
        else:
            return unknown

    def _to_list_rep(self, node):
        if node is None:
            return None
        children = node.children
        if len(children) == 2:
            if node.children[0].predicate.symtype.symbolic_eq(node.children[1].predicate.symtype):
                left = node.children[0] if node.children[0].predicate.result else node.children[1]
                right = node.children[1] if not node.children[1].predicate.result else node.children[0]
                # print(f"see: {[pred_to_smt(left.predicate), self._to_list_rep(left), self._to_list_rep(right)]}")
                return [pred_to_smt(left.predicate), self._to_list_rep(left), self._to_list_rep(right)]
            else:
                raise ValueError("Two children of a constraint should have the same predicate!")
        elif len(node.children) == 1:
            return [pred_to_smt(node.children[0].predicate), self._to_list_rep(node.children[0]), None]
        elif len(children) == 0:
            return node.effect

        raise ValueError("Should not be possible! Can't have more than two children.")



class Node():
    def __init__(self, data):
        self.left = None
        self.data = data
        self.right = None

def path_finder_util(root, string, paths):
    if not root: return
    string += str(root.data)
    path_finder_util(root.left, string+'->', paths)
    path_finder_util(root.right, string+'->', paths)
    if not root.left and not root.right:
        paths.append(string)
 
def path_finder(root):
    if not root:
        print("")
        return
    paths = []
    path_finder_util(root, '', paths)
    depaths = list(set(paths))
    # for path in depaths:
    #     print(path)

    return depaths


def rep2Tree(rep):    
    if isinstance(rep, list):
        root = Node(rep[0])      
        if rep[1] is not None:
            if isinstance(rep[1], bool) or isinstance(rep[1], SymbolicObject):
                root.left = Node(rep[1])
            else:
                root.left = rep2Tree(rep[1])
        
        if rep[2] is not None:
            if isinstance(rep[2], bool) or isinstance(rep[2], SymbolicObject):
                root.right = Node(rep[2])
            else:
                root.right = rep2Tree(rep[2])
        return root
    else:
        return Node(rep)
