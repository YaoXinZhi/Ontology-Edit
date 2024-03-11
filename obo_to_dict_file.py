# -*- coding:utf-8 -*-
# ! usr/bin/env python3
"""
Created on 15/07/2023 09:35
@Author: yao
"""
import re
import argparse
from collections import defaultdict


def obsolete_process(name: str):
    if 'obsolete' in name:
        name = name.replace('obsolete', '').strip()
    return name


def obo_to_dict(obo_file, save_file):
    """
    dict_file
    ID Name syno1|syno2|syno3
    """
    id_to_name = {}
    id_to_syno = defaultdict(set)
    with open(obo_file) as f:
        for line in f:
            if line.startswith('id:'):
                term_id = line.strip()[ 4: ]
            if line.startswith('name:'):
                term_name = line.strip()[ 6: ]

                term_name = obsolete_process(term_name)

                id_to_name[ term_id ] = term_name
                id_to_syno[ term_id ].add(term_name)

            if line.startswith('synonym:'):
                syno_name = re.findall(r'"(.*?)"', line)[ 0 ]

                syno_name = obsolete_process(syno_name)

                id_to_syno[ term_id ].add(syno_name)

    with open(save_file, 'w') as wf:
        for term_id, term_name in id_to_name.items():
            syno_set = id_to_syno[ term_id ]

            syno_wf = '|'.join(syno_set)

            wf.write(f'{term_id}\t{term_name}\t{syno_wf}\n')

    print(f'{len(id_to_name):,} terms saved in {save_file}.')


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('-of', dest='obo_file',
                      required=True)
    args.add_argument('-sf', dest='save_file',
                      required=True)
    args = args.parse_args()

    obo_to_dict(args.obo_file, args.save_file)
