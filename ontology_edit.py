# -*- coding:utf-8 -*-
# ! usr/bin/env python3
"""
Created on 25/07/2020 下午4:15
@Author: xinzhi yao
"""



import os
import re
import string
import networkx as nx
from nltk.corpus import stopwords
from collections import defaultdict

class node():
    def __init__(self, _id: str, name=None, definition=None, syno_set=None, parents=None):
        self._id = _id
        self.name = name
        self.definition = definition
        self.synonym = syno_set
        self.parents = parents
        self.childs = set()

    def update_node(self, name: str, definition: str, syno_set: set, parents: set):
        self.name = name
        self.definition = definition
        self.synonym = syno_set
        self.parents = parents

    # todo: add warning of empty parents/childs.
    def add_parent(self, term):
        if term in self.parents:
            print('{0} is already in the parent node of {1}.'.format(term, self._id))
        else:
            self.parents.add(term)
            print('Successfully added {0} to the parent node of {1}.'.format(term, self._id))

    def del_parent(self, term):
        if term not in self.parents:
            print('{0} is not in the parent node of {1}.'.format(term, self._id))
        else:
            self.parents.remove(term)
            if not self.parents:
                print('Warning: Parent of {0} is empty.'.format(self._id))
            print('Successfully deleted {0} from the parent node of {1}.'.format(term, self._id))

    def add_child(self, term):
        if term in self.childs:
            print('{0} is already in the parent node of {1}.'.format(term, self._id))
        else:
            self.childs.add(term)
            # print('Successfully added {0} to the child node of {1}.'.format(term, self.id))

    def del_child(self, term):
        if term not in self.childs:
            print('{0} is not in the child node of {1}.'.format(term, self._id))
        else:
            self.childs.remove(term)
            print('Successfully deleted {0} from the child node of {1}.'.format(term, self._id))


class ontology_edit():
    def __init__(self, obo_file: str):
        self.obo_file = obo_file

        self.head_block = ''

        self.format_version = ''
        self.date = ''
        self.saved_by = ''
        self.default_namespace = ''

        self.nodes = {}
        self.node_set = set()
        self.term2id = {}
        self.isa_set = set()
        self.graph = nx.DiGraph()

        self.init_ontology()
        self.init_graph()

    def init_ontology(self):
        # print('init node.')
        _id = name = definition = ''
        syno_set = parent_set = set()

        with open(self.obo_file) as f:
            for line in f:

                l = line.strip()
                if l.startswith('format-version:'):
                    self.format_version = ' '.join(l.split()[1:])
                if l.startswith('date:'):
                    self.date = ' '.join(l.split()[1:])
                if l.startswith('saved-by:'):
                    self.saved_by = ' '.join(l.split()[1:])
                if l.startswith('default-namespace:'):
                    self.default_namespace = ' '.join(l.split()[1:])
                if l == '':
                    if _id:
                        self.term2id[name] = _id
                        # update node information.
                        if _id not in self.node_set:
                            self.nodes[_id] = node(_id, name, definition, syno_set, parent_set)
                            self.node_set.add(_id)
                        else:
                            self.nodes[_id].update_node(name, definition, syno_set, parent_set)
                        # update child nodes.
                        for p_id in parent_set:
                            self.isa_set.add((p_id, _id))
                            if p_id not in self.node_set:
                                self.nodes[p_id] = node(p_id)
                                self.node_set.add(p_id)
                            self.nodes[p_id].add_child(_id)

                        _id = name = definition = ''
                        syno_set = parent_set = set()
                if l.startswith('id:'):
                    _id = l.split()[1]
                if l.startswith('name:'):
                    name = ' '.join(l.split(' ')[1:])
                if l.startswith('def:'):
                    definition = ' '.join(l.split(' ')[1:])
                if l.startswith('synonym'):
                    syno = ' '.join(l.split(' ')[1:])
                    syno_set.add(syno)
                if l.startswith('is_a:'):
                    parent_term = l.split()[1]
                    parent_set.add(parent_term)

    def init_graph(self):

        for term, _id in self.term2id.items():
            self.graph.add_node(_id, name=term)
        self.graph.add_edges_from(self.isa_set)

    def change_head(self, format_version=None, date=None, saved_by=None, namespace=None):
        if format_version:
            self.format_version = format_version
        if date:
            self.date = date
        if saved_by:
            self.saved_by = saved_by
        if names:
            self.default_namespace = namespace

    @staticmethod
    def tsv_to_obo(tsv_file: str, obo_file: str, prefix: None):
        """

        :param tsv_file: tsv format file
        :param obo_file: obo format file
        :param prefix: ontology prefix
        :return:
        """
        ontology_name = os.path.basename(tsv_file).split('.')[ 0 ]
        wf = open(obo_file, 'w')
        # obo head
        wf.write('format-version: 1.0\n')
        wf.write('saved-by: xinzhi yao\n')
        wf.write('ontology: {0}\.'.format(ontology_name))
        wf.write('\n')
        wf.write('\n')

        syno_name = ''
        definition = ''
        with open(tsv_file) as f:
            f.readline()
            for line in f:
                l = line.strip().split('\t')
                if len(l) >= 2:
                    term_id = l[ 0 ].split('/')[ -1 ]
                    term_id = term_id.replace('_', ':')
                    prefix_id = term_id.split(':')[ 0 ]
                    if prefix:
                        if prefix_id != prefix:
                            continue
                    term_name = l[ 1 ]
                else:
                    term_id = ''
                    term_name = ''
                if len(l) > 4:
                    syno_name = l[ 4 ]
                if len(l) > 5:
                    definition = l[ 5 ]
                # save term
                if not term_id:
                    continue
                wf.write('[Term]\n')
                wf.write('id: {0}\n'.format(term_id))
                wf.write('name: {0}\n'.format(term_name))
                if definition:
                    wf.write('def: "{0}"\n'.format(definition))
                if syno_name:
                    wf.write('synonym: "{0}"\n'.format(syno_name))
                wf.write('\n')
        wf.close()
        print('save done: {0}'.format(obo_file))

    @staticmethod
    def obo_to_basic(obo_file: str, obo_basic_file: str, prefix: str):
        """
        :param obo_file: obo format file .
        :param obo_basic_file: obo-basic file.
        :param prefix: ontology prefix.
        :return:
        """
        count_total = 0
        count_basic = 0

        wf = open(obo_basic_file, 'w')
        flag = True
        with open(obo_file) as f:
            for line in f:
                l = line.strip()
                if l.startswith('id:'):
                    count_total += 1
                    id_prefix = l.split(' ')[ 1 ].split(':')[ 0 ]
                    if id_prefix == prefix:
                        flag = True
                        count_basic += 1
                        wf.write('{0}\n'.format(l))
                    else:
                        flag = False
                else:
                    if not flag:
                        continue
                    wf.write('{0}\n'.format(l))
        wf.close()
        print('total terms: {0}, basic terms: {1}'.format(count_total, count_basic))
        print('ontology basic obo: {0}'.format(obo_basic_file))

    def term_to_id(self, term):
        if not self.term2id.get(term):
            raise ValueError('The query node {0} does not exist.'.format(term))
        else:
            _id = self.term2id[term]
        return _id

    def add_relation(self, parent_node: str, child_node: str, use_id=True):
        if not use_id:
            parent_node = self.term_to_id(parent_node)
            child_node = self.term_to_id(child_node)

        if not self.nodes.get(parent_node) or not self.nodes.get(child_node):
            raise ValueError('The query node does not exist.')
        else:
            self.nodes[parent_node].add_child(child_node)
            self.nodes[child_node].add_parent(parent_node)

    def del_relation(self, parent_node: str, child_node: str, use_id=True):
        if not use_id:
            parent_node = self.term_to_id(parent_node)
            child_node = self.term_to_id(child_node)

        if not self.nodes.get(parent_node) or not self.nodes.get(child_node):
            raise ValueError('The query node does not exist.')
        else:
            self.nodes[parent_node].del_child(child_node)
            self.nodes[child_node].del_parent(parent_node)

    def del_node(self, node_id: str):
        for parent_node in self.nodes[node_id].parents:
            self.nodes[parent_node].del_child(node_id)
        for child_node in self.nodes[node_id].childs:
            self.nodes[child_node].del_parent(node_id)
        del self.nodes[node_id]


    def change_relation(self, old_parent_node: str, new_parent_node: str, child_node: str, use_id=False):
        self.del_relation(old_parent_node, child_node, use_id)
        self.add_relation(new_parent_node, child_node, use_id)

    def merge_node(self, old_node: str, new_node: str):
        for parent_node in self.nodes[old_node].parents:
            self.nodes[parent_node].del_child(old_node)
            self.nodes[parent_node].add_child(new_node)
        for child_node in self.nodes[old_node].childs:
            self.nodes[child_node].del_parent(child_node)
            self.nodes[child_node].add_child(child_node)
        del self.nodes[old_node]

    def get_child(self, root_node: str, use_id=True):

        child_set = set()
        traverse_nodes = set()

        if not use_id:
            root_node = self.term_to_id(root_node)

        for n_id in self.graph.adj[root_node]:
            traverse_nodes.add(n_id)
        child_set.add(root_node)
        child_set.update(traverse_nodes)
        while traverse_nodes:
            temp_set = traverse_nodes.copy()
            for n_id in traverse_nodes:
                child_set.add(n_id)
                temp_set.remove(node)
                for child in self.graph.adj(n_id):
                    temp_set.add(child_set)
            traverse_nodes = temp_set.copy()

        return child_set

    @staticmethod
    def save_nodes(node_set: set, ontology_file: str, out: str, write_head=True):
        wf = open(out, 'w')
        term_block = [ ]
        flag = False
        with open(ontology_file) as f:
            for line in f:
                l = line.strip()
                if l == '[Term]':
                    flag = True
                if not flag and write_head:
                    wf.write('{0}\n'.format(l))
                if flag:
                    if l != '':
                        if l.startswith('id:'):
                            term_id = l.split()[ 1 ]
                        term_block.append(l)
                    else:
                        # judgement and write file
                        if term_id in node_set:
                            for term_line in term_block:
                                wf.write('{0}\n'.format(term_line))
                            wf.write('\n')
                        term_block = [ ]
        wf.close()

    def export_obo(self, out: str):
        sorted_id = sorted(self.node_set)
        with open(out) as wf:
            wf.write('{0}\n'.format(self.format_version))
            wf.write('{0}\n'.format(self.date))
            wf.write('{0}\n'.format(self.saved_by))
            wf.write('{0}\n'.format(self.default_namespace))
            wf.write('\n')
            for _id in sorted_id:
                wf.write('[Term]\n')
                wf.write('id:\t{0}\n'.format(_id))
                wf.write('name:\t{0}\n'.format(self.nodes[_id].name))
                wf.write('def:\t{0}\n'.format(self.nodes[_id].definition))
                for syno in self.nodes[_id].synonym:
                    wf.write('synonym:\t{0}\n'.format(syno))
                for parent_node in self.nodes[_id].parents:
                    wf.write('is_a:{0} ! {1}\n'.format(parent_node, self.nodes[parent_node].name))
                wf.write('\n')

if __name__ == '__main__':
    obo_file = '../PTO/data/Ontology_db/wto-basic.obo'

    wto_edit = ontology_edit(obo_file)

    len(wto_edit.node_set)
    print(wto_edit.head_block)
    print(wto_edit.nodes['WTO:0000001']._id)
    print(wto_edit.nodes['WTO:0000001'].name)
    print(wto_edit.nodes['WTO:0000001'].definition)
    print(wto_edit.nodes['WTO:0000001'].parents)
    print(wto_edit.nodes['WTO:0000001'].childs)

