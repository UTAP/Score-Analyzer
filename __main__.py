#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import csv
import json
from sys import stderr
from collections import defaultdict


sid_mask = ["8101", "95", "000"]
datasheets_addr_prefix = "data/"


def create_data_list():
    data_list = [
        {
            "file_name": "addr",
            "late_name": "فیلد",
            "level1": 1.0,
            "level2": 1.1,
            "sid_name": "ش.د",
            "skip_rows": 0
        }
    ]

    print(json.dumps(data_list, indent = 4))

    exit()


def normalize_sid(arg):
    sid_prefix_mask = "".join(sid_mask)
    sid_lens = [len(i) for i in reversed(sid_mask)]
    sid_lens = [sum(sid_lens[:i + 1]) for i in range(len(sid_lens))]

    arg = str(arg)
    for i in sid_lens:
        if len(arg) == i:
            return int(sid_prefix_mask[:-len(arg)] + arg)
    raise ValueError("invalid length SID")


if __name__ == '__main__':
    # create_data_list()

    with open("data_list.json") as f:
        data_list = json.loads(f.read().replace("    ", ""))
    # print(data_list, file = stderr)

    levels = ["level2", "level1"]

    data = []

    for datasheet_attr in data_list:
        with open(datasheets_addr_prefix + datasheet_attr["file_name"]) as f:
            students = {}
            for level in levels:
                students[level] = []
            data_reader = csv.DictReader(f, dialect = "excel")
            row_number = 0
            for row in data_reader:
                if row_number < datasheet_attr["skip_rows"]:
                    continue
                row_number += 1
                sid = row[datasheet_attr["sid_name"]]
                try:
                    sid = normalize_sid(sid)
                except ValueError as ex:
                    print("%s : %d\n>>>\t %r" % (datasheet_attr["file_name"], row_number + 1, ", ".join(row.values())), file = stderr)
                    continue
                late = row[datasheet_attr["late_name"]]
                if not late:
                    late = "0"
                late = float(late)
                for level in levels:
                    if late > datasheet_attr[level]:
                        students[level].append(sid)
                        break
            data.append(students)
    print(data)

