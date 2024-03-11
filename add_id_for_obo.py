# -*- coding:utf-8 -*-
# ! usr/bin/env python3
"""
Created on 11/03/2024 18:19
@Author: yao
"""

"""
给诸如ADMO这样的本体添加ID
"""

import argparse

import re

def remove_punctuation(input_string):
    # 使用正则表达式替换所有标点符号为空字符串
    return re.sub(r'[^\w\s]', ' ', input_string)

def main(obo_file: str, save_file: str, id_prefix: str):

    term_to_id = {}
    id_to_ori_term = {}

    idx = 1
    fixed_id_len = 7
    # 先便利一遍把id安排了
    term_num = 0
    with open(obo_file) as f:
        for line in f:
            # print(line)
            if line.startswith('id:'):
                id_term = line.strip().split(' ')[ 1 ].replace('_', ' ')
                id_term = remove_punctuation(id_term).lower()

            if line.startswith('name:'):
                ori_term = ' '.join(line.strip().split()[1:]).strip()
                term = ' '.join(line.strip().split()[1:]).strip()
                term_num += 1
                # print(term)
                term = remove_punctuation(term).lower()
                if not term_to_id.get(term):
                    term_idx = '{:0>{width}}'.format(idx, width=fixed_id_len)
                    term_id = f'{id_prefix}:{term_idx}'
                    if id_term:
                        term_to_id[id_term] = term_id
                    # print(term)
                    # print(term_id)
                    term_to_id[term] = term_id
                    id_to_ori_term[term_id] = ori_term
                    idx += 1

    print(f'{len(term_to_id):,} terms.')

    idx = 1
    with open(obo_file) as f, open(save_file, 'w') as wf:
        for line in f:
            if line.startswith(f'id:'):
                continue
            elif line.startswith('name:'):
                term = ' '.join(line.strip().split()[ 1: ]).strip()

                # print(term)
                term = remove_punctuation(term).lower()

                term_id = term_to_id[term]

                wf.write(f'id: {term_id}\n')
                wf.write(line)

                if idx % 5 == 0:
                    print(f'{idx:,}/{term_num:,} terms processed.')
                idx += 1

            elif line.startswith('is_a:'):
                if len(line.strip().split(' ! ')) > 1:
                    # term = line.strip().split(' ! ')[1].strip().replace('_', ' ')
                    term = line.strip().split(' ')[1].strip().replace('_', ' ')
                else:
                    term = line.strip().split()[1].strip()

                term = remove_punctuation(term).lower()

                if not term_to_id.get(term):
                    term = line.strip().split(' ! ')[1].strip().replace('_', ' ')
                    term = remove_punctuation(term).lower()
                    term_id = term_to_id[term]
                else:
                    term_id = term_to_id[ term ]
                ori_term = id_to_ori_term[term_id]
                wf.write(f'is_a: {term_id} ! {ori_term}\n')
            else:
                wf.write(line)
    print(f'{save_file} saved.')





if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--obo_file', required=True)
    parser.add_argument('--save_file', required=True)
    parser.add_argument('--id_prefix',
                        default='ADMO')
    args = parser.parse_args()

    main(args.obo_file, args.save_file, args.id_prefix)

