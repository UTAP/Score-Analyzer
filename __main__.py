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
            "project_name": "sth",
            "file_name": "addr",
            "late_field": "فیلد",
            "sid_field": "ش.د",
            "original_score_field": "sth",
            "level1": 1.0,
            "level2": 1.1,
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

def extract_data(file_addr):
    with open(file_addr) as f:
        data_list = json.loads(f.read().replace("    ", ""))

    data = {}

    for datasheet_attr in data_list:
        with open(datasheets_addr_prefix + datasheet_attr["file_name"]) as f:
            print("%s" % (datasheet_attr["file_name"]), file = stderr)

            students = {}
            for level in levels:
                students[level] = {}
            data_reader = csv.DictReader(f, dialect = "excel")
            row_number = 0
            for row in data_reader:
                row_number += 1
                if row_number <= datasheet_attr["skip_rows"]:
                    continue
                sid = row[datasheet_attr["sid_field"]]
                try:
                    sid = normalize_sid(sid)
                except ValueError as ex:
                    print("\tERR @%d: \t%r" % (row_number + 1, ", ".join(row.values())), file = stderr)
                    continue
                late = row[datasheet_attr["late_field"]]
                if not late:
                    late = "0"
                try:
                    late = float(late.replace("%", ""))
                except ValueError as ex:
                    print("\tERR @%d: \t%r" % (row_number + 1, ", ".join(row.values())), file = stderr)
                    continue
                score = row[datasheet_attr["original_score_field"]]
                try:
                    score = float(score.replace("%", ""))
                except ValueError as ex:
                    print("\tERR @%d: \t%r" % (row_number + 1, ", ".join(row.values())), file = stderr)
                    continue
                for level in levels:
                    if late > datasheet_attr[level]:
                        students[level][sid] = score
                        break
            data[datasheet_attr["project_name"]] = students

    return data

def students_by_project_to_students_by_sid(students_by_project):
    students_by_sid = defaultdict(dict)
    for project in students_by_project:
        for level in students_by_project[project]:
            for sid in students_by_project[project][level]:
                if not students_by_sid[sid]:
                    students_by_sid[sid] = dict((level, {}) for level in levels)
                # if not students_by_sid[sid][level]:
                    # students_by_sid[sid][level] = []
                students_by_sid[sid][level][project] = students_by_project[project][level][sid]
    return students_by_sid

def extract_name_by_sid(file_addr):
    with open(file_addr) as f:
        datasheet_attr = json.loads(f.read().replace("    ", ""))

    name_by_sid = {}
    with open(datasheets_addr_prefix + datasheet_attr["file_name"]) as f:
        data_reader = csv.DictReader(f, dialect = "excel")
        for row in data_reader:
            sid = row[datasheet_attr["sid_field"]]
            try:
                sid = normalize_sid(sid)
            except ValueError as ex:
                print("\tERR @%d: \t%r" % (row_number + 1, ", ".join(row.values())), file = stderr)
                continue
            name_by_sid[sid] = row[datasheet_attr["name_field"]]

    return name_by_sid

if __name__ == '__main__':
    # create_data_list()

    students_by_project = extract_data("data_list.json")
    students_by_sid = students_by_project_to_students_by_sid(students_by_project)
    name_by_sid = extract_name_by_sid("list.json")

    # print(json.dumps(students_by_project, indent = 4))
    # print(json.dumps(students_by_sid, indent = 4))
    # print(name_by_sid)
