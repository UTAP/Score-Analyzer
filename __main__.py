#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import csv
import json
from sys import stderr
from collections import defaultdict


sid_mask = ["81", "01", "95", "000"]
datasheets_addr_prefix = "data/"
levels = ["level2", "level1"]


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


def extract_data():
    with open("data_list.json") as f:
        data_list = json.loads(f.read().replace("    ", ""))

    data = {}

    for datasheet_attr in data_list:
        with open(datasheets_addr_prefix + datasheet_attr["file_name"]) as f:
            print("%s" % (datasheet_attr["file_name"]), file = stderr)
            # if "AP S96 Assign1 - mehdithreem.csv" != datasheet_attr["file_name"]:
                # continue
            students = {}
            for level in levels:
                students[level] = []
            data_reader = csv.DictReader(f, dialect = "excel")
            row_number = 0
            for row in data_reader:
                row_number += 1
                if row_number <= datasheet_attr["skip_rows"]:
                    continue
                sid = row[datasheet_attr["sid_name"]]
                try:
                    sid = normalize_sid(sid)
                except ValueError as ex:
                    print("\tERR @%d: \t%r" % (row_number + 1, ", ".join(row.values())), file = stderr)
                    continue
                late = row[datasheet_attr["late_name"]]
                if not late:
                    late = "0"
                try:
                    late = float(late.replace("%", ""))
                except ValueError as ex:
                    print("\tERR @%d: \t%r" % (row_number + 1, ", ".join(row.values())), file = stderr)
                    continue
                for level in levels:
                    if late > datasheet_attr[level]:
                        students[level].append(sid)
                        break
            data[datasheet_attr["file_name"]] = students

    return data


def students_by_project_to_students_by_sid(students_by_project):
    students_by_sid = defaultdict(dict)
    for project in students_by_project:
        for level in students_by_project[project]:
            for sid in students_by_project[project][level]:
                if not students_by_sid[sid]:
                    students_by_sid[sid] = dict((level, []) for level in levels)
                if not students_by_sid[sid][level]:
                    students_by_sid[sid][level] = []
                students_by_sid[sid][level].append(project)
    return students_by_sid


if __name__ == '__main__':
    # create_data_list()

    students_by_project = extract_data()
    students_by_sid = students_by_project_to_students_by_sid(students_by_project)

    print(json.dumps(students_by_project, indent = 4))
    print(json.dumps(students_by_sid, indent = 4))

