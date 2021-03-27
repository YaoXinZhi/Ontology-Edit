# -*- coding:utf-8 -*-
# ! usr/bin/env python3
"""
Created on 25/07/2020 下午4:15
@Author: xinzhi yao
"""

import re
import os
import datetime
import networkx as nx


class node:
    def __init__(self, _id: str, name=None, definition=None, syno_set=None,
                 parents=None, xref=None, comment=None, relationship=None,
                 is_obsolete=''):
        self._id = _id
        self.name = name
        self.definition = definition
        self.synonym = syno_set
        self.parents = parents
        self.xref = xref
        self.comment = comment
        self.relationship = relationship
        self.is_obsolete = is_obsolete
        self.childs = set()
        self.species = ''

    def update_node(self, name: str, definition: str, syno_set: set,
                    parents: set, xref: set, comment: set, relationship: set,
                    is_obsolete:str):
        self.name = name
        self.definition = definition
        self.synonym = syno_set
        self.parents = parents
        self.xref = xref
        self.comment = comment
        self.relationship = relationship
        self.is_obsolete = is_obsolete

    def add_parent(self, term):
        if term in self.parents:
            print('{0} is already in the parent node of {1}.'.format(term, self._id))
        else:
            self.parents.add(term)
            # print('Successfully added {0} to the parent node of {1}.'.format(term, self._id))

    def del_parent(self, term):
        if term not in self.parents:
            print('{0} is not in the parent node of {1}.'.format(term, self._id))
        else:
            self.parents.remove(term)
            if not self.parents:
                print('Warning: Parent of {0} is empty.'.format(self._id))
            # print('Successfully deleted {0} from the parent node of {1}.'.format(term, self._id))

    def add_child(self, term):
        if term in self.childs:
            print('{0} is already in the child node of {1}.'.format(term, self._id))
        else:
            self.childs.add(term)
            # print('Successfully added {0} to the child node of {1}.'.format(term, self.id))

    def del_child(self, term):
        if term not in self.childs:
            print('{0} is not in the child node of {1}.'.format(term, self._id))
        else:
            self.childs.remove(term)
            # print('Successfully deleted {0} from the child node of {1}.'.format(term, self._id))

    def add_xref(self, xref):
        if xref in self.xref:
            print('{0} is not in the child node of {1}.'.format(xref, self._id))
        else:
            self.xref.add(xref)

    def add_species(self, species):
        self.species = species

class ontology_edit:
    def __init__(self):

        self.head_block = ''

        self.format_version = '1.1'
        self.date = datetime.date.today().strftime('%y-%m-%d')
        self.saved_by = 'xzyao'
        self.default_namespace = 'rice_trait_ontology'

        self.nodes = {}
        self.node_set = set()
        self.term2id = {}
        self.isa_set = set()
        self.replaced_mapping = {}
        self.graph = nx.DiGraph()

        # self.add_ontology()
        self.init_graph()


    def add_ontology(self, obo_file: str):
        # print('init node.')
        _id = ''
        name = ''
        definition = ''
        syno_set = set()
        parent_set = set()
        xref_set = set()
        comment_set = set()
        relationship_set = set()
        is_obsolete = ''

        with open(obo_file, encoding='utf-8') as f:
            for line in f:

                l = line.strip()
                if l == '':
                    if _id:
                        self.term2id[name] = _id
                        # update node information.
                        if _id not in self.node_set:
                            self.nodes[_id] = node(_id, name, definition, syno_set, parent_set,
                                                   xref_set, comment_set, relationship_set, is_obsolete)
                            self.node_set.add(_id)
                        else:
                            self.nodes[_id].update_node(name, definition, syno_set, parent_set,
                                                        xref_set, comment_set, relationship_set, is_obsolete)
                        # update child nodes.
                        for p_id in parent_set:
                            self.isa_set.add((p_id, _id))
                            if p_id not in self.node_set:
                                self.nodes[p_id] = node(p_id)
                                self.node_set.add(p_id)
                            self.nodes[p_id].add_child(_id)

                        _id = ''
                        name = ''
                        definition = ''
                        is_obsolete = ''
                        syno_set = set()
                        parent_set = set()
                        xref_set = set()
                        comment_set = set()
                        relationship_set = set()

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
                if l.startswith('xref:'):
                    xref = ' '.join(l.split()[1:])
                    xref_set.add(xref)
                if l.startswith('comment:'):
                    comment = ' '.join(l.split()[1:])
                    comment_set.add(comment)
                if l.startswith('relationship'):
                    relationship = ' '.join(l.split()[1:])
                    relationship_set.add(relationship)
                if l.startswith('is_obsolete'):
                    is_obsolete = 'true'


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
        if namespace:
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
        with open(tsv_file, encoding='utf-8') as f:
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

    def add_relation(self, parent_node: str, child_node: str, input_id=True):
        if not input_id:
            parent_node = self.term_to_id(parent_node)
            child_node = self.term_to_id(child_node)

        if child_node in self.replaced_mapping.keys():
            child_node = self.replaced_mapping[child_node]

        if not self.nodes.get(parent_node) or not self.nodes.get(child_node):
            raise ValueError('The query node does not exist.')
        else:
            self.nodes[parent_node].add_child(child_node)
            self.nodes[child_node].add_parent(parent_node)
        print(f'Successfully add parent {parent_node} for {child_node}.')

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
        print('Warning: Deleting nodes may destroy the tree structure.')
        for parent_node in self.nodes[node_id].parents:
            self.nodes[parent_node].del_child(node_id)
        for child_node in self.nodes[node_id].childs:
            self.nodes[child_node].del_parent(node_id)
        del self.nodes[node_id]
        self.node_set.remove(node_id)
        print('Successfully deleted {0}.'.format(node_id))

    def del_unrooted_tree(self, root_node: str):
        nodes = self.node_set.copy()
        for node_id in self.node_set:
            if node_id not in nodes:
                continue
            if node_id != root_node and not self.nodes[node_id].parents:
                sub_tree_nodes = self.get_child(node_id)
                for sub_node in sub_tree_nodes:
                    self.del_node(sub_node)
                nodes -= sub_tree_nodes

    def change_relation(self, old_parent_node: str, new_parent_node: str, child_node: str, use_id=False):
        self.del_relation(old_parent_node, child_node, use_id)
        self.add_relation(new_parent_node, child_node, use_id)

    def merge_node(self, save_node: str, replace_node: str):

        self.nodes[save_node].add_xref(replace_node)
        for child_node in self.nodes[replace_node].childs:
            if child_node in self.replaced_mapping.keys():
                child_node = self.replaced_mapping[child_node]
            self.nodes[save_node].add_child(child_node)
            self.nodes[child_node].add_parent(save_node)

        for parent_node in self.nodes[replace_node].parents:
            if parent_node in self.replaced_mapping.keys():
                parent_node = self.replaced_mapping[parent_node]
            self.nodes[parent_node].add_child(save_node)
            self.nodes[save_node].add_parent(parent_node)

        self.node_set.remove(replace_node)
        del self.nodes[replace_node]
        self.replaced_mapping[replace_node] = save_node
        print(f'Successfully merged {replace_node} to {save_node}.')

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
                    temp_set.add(child)
            traverse_nodes = temp_set.copy()

        return child_set

    def del_subtree(self, root_node: str):
        child_node = self.get_child(root_node)
        for node_id in child_node:
            self.del_node(node_id)

    def add_species(self, _id: str, species: str):
        self.nodes[_id].add_species(species)

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

    def export_obo(self, export_file: str, split_by='\t'):

        save_count = 0
        sorted_id = sorted(self.nodes.keys())
        with open(export_file, 'w', encoding='utf-8') as wf:
            wf.write('format_version: {0}\n'.format(self.format_version))
            # wf.write('date: {0}\n'.format(self.date))
            wf.write('saved_by: {0}\n'.format(self.saved_by))
            wf.write('default_namespace: {0}\n'.format(self.default_namespace))
            wf.write('\n')
            for _id in sorted_id:
                saved_is_a = set()
                if not self.nodes[_id].name:
                    continue

                if not re.findall(r'.?O.*?:\d+', _id):
                    continue

                if self.nodes[_id].name == '<new term>':
                    continue

                save_count += 1
                wf.write('[Term]\n')
                wf.write(f'id:{split_by}{_id}\n')
                # wf.write('name: {0}\n'.format(self.nodes[_id].name))
                wf.write(f'name:{split_by}{self.nodes[_id].name}\n')
                if self.nodes[_id].definition:
                    wf.write(f'def:{split_by}{self.nodes[_id].definition}\n')
                if self.nodes[_id].comment:
                    for comment in self.nodes[_id].comment:
                        wf.write(f'comment:{split_by}{comment}\n')
                if self.nodes[_id].xref:
                    for xref in self.nodes[_id].xref:
                        wf.write(f'xref:{split_by}{xref}\n')
                # fixme: progete can not read this attributes
                # if self.nodes[_id].species:
                #     wf.write(f'species:{split_by}{self.nodes[_id].species}\n')
                for syno in self.nodes[_id].synonym:
                    wf.write(f'synonym:{split_by}{syno}\n')
                for parent_node in self.nodes[_id].parents:
                    if parent_node in self.replaced_mapping.keys():
                        parent_node = self.replaced_mapping[parent_node]
                    if self.nodes[parent_node].name not in saved_is_a:
                        wf.write(f'is_a:{split_by}{parent_node} ! {self.nodes[parent_node].name}\n')
                        saved_is_a.add(self.nodes[parent_node].name)
                if self.nodes[_id].is_obsolete:
                    wf.write(f'is_obsolete:{split_by}true\n')
                wf.write('\n')
            print(f"{export_file} save done, {save_count:,} terms saved.")

    def print_node(self, _id):
        print()
        print(f'id: {self.nodes[_id]._id}')
        print(f'name: {self.nodes[_id].name}')
        if self.nodes[_id].definition:
            print(f'definition: {self.nodes[_id].definition}')
        if self.nodes[_id].comment:
            for comment in self.nodes[_id].comment:
                print(f'comment: {comment}')
        if self.nodes[_id].xref:
            for xref in self.nodes[_id].xref:
                print(f'xref: {xref}')
        # print(self.nodes[_id].synonym)
        if self.nodes[_id].synonym:
            for synonym in self.nodes[_id].synonym:
                print(f'synonym: {synonym}')
        # if self.nodes[_id].species:
        #     print(f'species: {"".join(self.nodes[_id].species)}')
        if self.nodes[_id].parents:
            print(f'parent: {" ".join(self.nodes[_id].parents)}')
        if self.nodes[_id].childs:
            print(f'child: {" ".join(self.nodes[_id].childs)}')
        if self.nodes[_id].relationship:
            for relationship in self.nodes[_id].relationship:
                print(f'relationship: {relationship}')

    def batch_merge_node(self, merge_file: str):
        merge_count = 0
        with open(merge_file) as f:
            for line in f:
                replace_id, save_id = line.strip().split('\t')
                self.merge_node(save_id, replace_id)
                merge_count += 1
        print(f'Merge Count: {merge_count}.')

    def batch_add_parent(self, parent_file: str):
        add_parent_count = 0
        with open(parent_file) as f:
            for line in f:
                child_node, parent_node = line.strip().split('\t')
                self.add_relation(parent_node, child_node)
                add_parent_count += 1
        print(f'Add Parent Count: {add_parent_count}')

    def batch_add_species(self, species_file: str):
        add_species_count = 0
        with open(species_file) as f:
            for line in f:
                l = line.strip()
                if l.endswith('#'):
                    _id = l.replace('#', '')
                    species = 'wheat-barley'
                else:
                    _id = l
                    species = 'wheat'
                self.add_species(_id, species)
                add_species_count += 1
        print(f'Add Species Count: {add_species_count}.')


if __name__ == '__main__':

    # parser = argparse.ArgumentParser(description='Ontology Edit.')
    # parser.add_argument('-tf', dest='to_file', type=str,
    #                     default='../data/Ontology_db/to-basic.obo',
    #                     help='default: ../data/Ontology_db/to-basic.obo')
    # parser.add_argument('-wf', dest='wto_file', type=str,
    #                     default='../data/Ontology_db/wto-basic.obo',
    #                     help='default: ../data/Ontology_db/wto-basic.obo')
    #
    # parser.add_argument('-mf', dest='merge_file', type=str,
    #                     default='../data/Ontolgoy_db/ontology_edit.save.obo')

    to_file = '../data/Ontology_db/to-basic.obo'
    wto_file = '../data/Ontology_db/wto-basic.obo'
    # po_file = '../data/Ontology_db/po-basic.obo'
    # ppo_file = '../data/Ontology_db/ppo-basic.obo'
    # peco_file = '../data/Ontology_db/peco-basic.obo'
    # ro_file = '../data/Ontology_db/CO_320.obo'

    # save_file = '../data/Ontology_Merge/to.wto.po.ro.ppo.obo'
    save_file = '../data/Ontology_Merge/RTO-1.0.obo'

    merge_mapping_file = '../data/Ontology_Merge/yellowdot.txt'
    parent_mapping_file = '../data/Ontology_Merge/parent.mapping.txt'
    species_mapping_file = '../data/Ontology_Merge/exclusive.txt'

    wto_edit = ontology_edit()

    wto_edit.add_ontology(to_file)
    wto_edit.add_ontology(wto_file)
    # wto_edit.add_ontology(po_file)
    # wto_edit.add_ontology(ro_file)
    # wto_edit.add_ontology(peco_file)
    # wto_edit.add_ontology(ppo_file)


    # wto_edit.node_set
    # Merge test: done
    # wto_edit.print_node('TO:0000770')
    # wto_edit.print_node('WTO:0000298')
    # wto_edit.merge_node('TO:0000770', 'WTO:0000298')
    # wto_edit.print_node('TO:0000315')
    # wto_edit.print_node('WTO:0000158')
    # wto_edit.print_node('WTO:0000161')

    # wto_edit.nodes['WTO:0000077'].parents

    # Add parent node test:
    # wto_edit.print_node('WTO:0000065')
    # wto_edit.print_node('TO:1000022')
    # wto_edit.add_relation('TO:1000022', 'WTO:0000065')
    # wto_edit.print_node('WTO:0000065')
    # wto_edit.print_node('TO:1000022')
    # wto_edit.print_node('TO:1000026')

    # Add Species:
    # wto_edit.print_node('WTO:0000077')
    # wto_edit.add_species('WTO:0000077', 'wheat')
    # wto_edit.nodes['WTO:0000077'].add_species('wheat')
    # wto_edit.print_node('WTO:0000077')

    wto_edit.batch_merge_node(merge_mapping_file)
    wto_edit.batch_add_parent(parent_mapping_file)
    wto_edit.batch_add_species(species_mapping_file)

    wto_edit.export_obo(save_file, ' ')
    # wto_edit.export_obo(save_file, '\t')

    # PECO.tsv to PECO.basic.obo
    # peco_tsv_file = '../data/Ontology_db/PECO.tsv'
    # peco_obo_file = '../data/Ontology_db/peco-basic.obo'
    # wto_edit.tsv_to_obo(peco_tsv_file, peco_obo_file, 'PECO')

