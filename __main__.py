#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import json
from sys import stderr
from collections import defaultdict
from matplotlib import pyplot as plt
from numpy import random

sid_mask = ["81", "01", "95", "000"]
datasheets_addr_prefix = "data/"
exports_addr_prefix = "export/"
levels = ["level2", "level1"]

def get_random_color():
    color_array = ["Maroon", "Olive", "Green", "Teal", "Navy", "Blue", "Purple", "Orange", "Purple", "DarkBlue", "Brown"]
    return color_array[int(random.randint(len(color_array)))]

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
    """ json format:
    [
        {
            "project_name": "",
            "file_name": "",
            "late_field": "",
            "sid_field": "",
            "original_score_field": "",
            "level1": 0,
            "level2": 0,
            "skip_rows": 0
        }
    ]
    """
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
    """json format:
    {
        "file_name": "",
        "name_field": "",
        "sid_field": ""
    }
    """
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

def visualize_scores_by_project(students_by_project, file_addr):
    avg_score_by_project = defaultdict(int)
    for project in students_by_project:
        score_sum = 0
        for level in levels:
            score_sum += sum(students_by_project[project][level].values())
        avg_score_by_project[project] = score_sum / sum([len(students_by_project[project][level]) for level in levels])

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.axis([-1, len(avg_score_by_project), 0, 110])
    ax.set_xticks(range(len(avg_score_by_project)))
    ax.set_xticklabels(list(avg_score_by_project.keys()))
    ax.set_ylabel("original score")
    ax.set_title("Scores by Project")
    ax.bar(range(len(avg_score_by_project)), avg_score_by_project.values(), color = get_random_color())
    for i in range(len(avg_score_by_project)):
        ax.text(i - 0.3, list(avg_score_by_project.values())[i] + 2, "%.3f" % list(avg_score_by_project.values())[i])

    fig.savefig(exports_addr_prefix + file_addr, bbox_inches='tight', dpi = 300)

def visualize_number_of_students_by_project(students_by_project, file_addr):
    number_of_students = dict((project, sum([len(students_by_project[project][level]) for level in levels])) for project in students_by_project)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.axis([-1, len(number_of_students), 0, max(list(number_of_students.values())) + 2])
    ax.set_xticks(range(len(number_of_students)))
    ax.set_xticklabels(list(number_of_students.keys()))
    ax.set_ylabel("students")
    ax.set_title("Number of Students by Project")
    ax.bar(range(len(number_of_students)), number_of_students.values(), color = get_random_color())
    for i in range(len(number_of_students)):
        ax.text(i - 0.1, list(number_of_students.values())[i] + 0.5, list(number_of_students.values())[i])

    fig.savefig(exports_addr_prefix + file_addr, bbox_inches='tight', dpi = 300)

def visualize_number_of_projects_by_student(students_by_sid, name_by_sid, file_addr, use_full_name = True):
    number_of_projects = dict((sid, sum([len(students_by_sid[sid][level]) for level in levels])) for sid in students_by_sid)
    number_of_projects = dict((sid, number_of_projects[sid]) for sid in [j for (i, j) in sorted([(value, key) for (key, value) in number_of_projects.items()], reverse = True)])

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.axis([0, max(list(number_of_projects.values())) + 0.5, -1, len(number_of_projects)])
    ax.set_yticks(range(len(number_of_projects)))
    ax.set_yticklabels([[sid, name_by_sid[sid]][use_full_name] for sid in number_of_projects], fontsize = 5)
    ax.set_title("Number of Projects by Student")
    ax.set_xlabel("projects")
    ax.barh(range(len(number_of_projects)), number_of_projects.values(), color = get_random_color())
    for i in range(len(number_of_projects)):
        ax.text(list(number_of_projects.values())[i] + 0.05, i, list(number_of_projects.values())[i], fontsize = 5)

    fig.savefig(exports_addr_prefix + file_addr, bbox_inches='tight', orientation='portrait', dpi=300)

def export_by_project(students_by_project, file_addr):
    with open(exports_addr_prefix + file_addr, 'w') as f:
        data_writer = csv.DictWriter(f, ["project_name"] + levels + ["sum"] , dialect = "excel")
        data_writer.writeheader()
        for project in students_by_project:
            row = {"project_name": project}
            for level in levels:
                row[level] = len(students_by_project[project][level])
            row["sum"] = sum(len(students_by_project[project][level]) for level in levels)
            data_writer.writerow(row)

def export_by_sid(students_by_sid, name_by_sid, file_addr):
    with open(exports_addr_prefix + file_addr, 'w') as f:
        data_writer = csv.DictWriter(f, ["sid", "name"] + levels + ["sum"] , dialect = "excel")
        data_writer.writeheader()
        for sid in students_by_sid:
            row = {"sid": sid, "name": name_by_sid[sid]}
            for level in levels:
                row[level] = len(students_by_sid[sid][level])
            row["sum"] = sum(len(students_by_sid[sid][level]) for level in levels)
            data_writer.writerow(row)

if __name__ == '__main__':
    students_by_project = extract_data("data_list.json")
    students_by_sid = students_by_project_to_students_by_sid(students_by_project)
    name_by_sid = extract_name_by_sid("list.json")

    visualize_scores_by_project(students_by_project, "scores_by_project.png")
    visualize_number_of_students_by_project(students_by_project, "number_of_students_by_project.png")
    visualize_number_of_projects_by_student(students_by_sid, name_by_sid, "number_of_projects_by_student.png", False)
    export_by_project(students_by_project, "by_project.csv")
    export_by_sid(students_by_sid, name_by_sid, "by_sid.csv")

    # plt.show()
