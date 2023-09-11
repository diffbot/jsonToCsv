import sys
import msgspec
import json
import csv
import traceback
import time

"""
# --------------------------------------------------------------------
# A JSON to CSV Conversion Tool for Deeply Nested JSON
# author: @jeromechoo
# --------------------------------------------------------------------
# @usage:
# 1. Place this script (jsonToCsv.py) in a folder with the target json file
# 2. Run > python jsonToCsv.py <name_of_json_file_without_format_extension> e.g. (python jsonToCsv.py jsonFile)
#
"""

def get_nested_value(data_dict, keys_list, list_delimiter=";"):
    # Retrieve nested value from a dictionary based on a list of keys
    for key in keys_list:
        try: 
            if isinstance(data_dict, dict) and key in data_dict:
                data_dict = data_dict[key]
                # Join lists of primitives
                if isinstance(data_dict, list) and len(data_dict) > 0 and isinstance(data_dict[0], (int, float, str, bool)):
                    data_dict = f'{list_delimiter} '.join(data_dict)
            elif isinstance(data_dict, list) and len(data_dict) > 0:
                if key.isnumeric() and 0 <= int(key) < len(data_dict):
                    data_dict = data_dict[int(key)]
                else:
                    data_dict = ""
            else:
                return ""
        except Exception:
            print(traceback.format_exc())
            print(json.dumps(data_dict, indent=2))
            sys.exit()
    # Encode strings
    if isinstance(data_dict, str):
        data_dict = data_dict.encode("unicode_escape").decode("utf-8")
    return data_dict

def find_the_big_list(data_dict):
    largest_list_key = ""
    largest_list_len = 0
    big_list = None
    for key in data_dict.keys():
        if isinstance(data_dict[key], list) and len(data_dict[key]) > largest_list_len:
            largest_list_len = len(data_dict[key])
            largest_list_key = key
    if largest_list_key:
        big_list = data_dict[largest_list_key]
    return largest_list_key, big_list

def build_ontology(data, ontology, parent_field_name="", max_list_depth=3, delimiter="_"):
    if isinstance(data, dict):
        for key in data.keys():
            # Primitive Types
            if isinstance(data[key], (int, float, str, bool)):
                field_name = f"{parent_field_name}{delimiter}{key}" if parent_field_name else key
                if field_name not in ontology:
                    ontology.append(field_name)
            # Non-Primitive Types
            elif isinstance(data[key], (dict, list)):
                field_name = f"{parent_field_name}{delimiter}{key}" if parent_field_name else key
                ontology = build_ontology(data[key], ontology, parent_field_name=field_name, delimiter=delimiter)
            elif data[key] is None:
                continue
    elif isinstance(data, list) and parent_field_name:
        for (index, item) in zip(range(max_list_depth), data):
            # Primitive Types
            if isinstance(item, (int, float, str, bool)):
                if parent_field_name not in ontology:
                    ontology.append(parent_field_name)
            # Non-Primitive Types
            elif isinstance(item, (dict, list)):
                field_name = f"{parent_field_name}{delimiter}{index}"
                ontology = build_ontology(item, ontology, parent_field_name=field_name, delimiter=delimiter)
            elif item is None:
                continue
    else:
        raise AttributeError
    return ontology


# Read & Convert the JSON data
def convert_json_to_csv(file, cli=False, json_paste=None):
    start_time = time.time()
    if file:
        with open(file, 'rb') as f:
            content = f.read()
    else:
        content = json_paste

    data_json = msgspec.json.decode(content)
    data_list = None
    ont_delimiter = "/"

    # Navigate through the top level keys for the primary list
    try:
        largest_list_key, data_list = find_the_big_list(data_json)
        if not largest_list_key:
            raise AttributeError
        print(f"[{largest_list_key}] is the key with the biggest list at {len(data_list)} items")
    except AttributeError:
        # No large list found, top level is either just a single json object or the json array itself
        if isinstance(data_json, dict): # Single json object
            data_list = [data_json]
        else:
            data_list = data_json

    # Build an ontology of fields
    ontology = []
    for item in data_list:
        try:
            ontology = build_ontology(item, ontology, delimiter=ont_delimiter)
        except AttributeError:
            # No keys, either a list or primitive, skip
            continue
    ontology_time_elapsed = time.time() - start_time
    print(f"Ontology generated in {ontology_time_elapsed} seconds")

    class Line(object):
        def __init__(self):
            self._line = None
        def write(self, line):
            self._line = line
        def read(self):
            return self._line

    # Create CSV
    if cli:
        filename = f"{input_filename}.csv"
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(ontology)
            for item in data_list:
                row = []
                for field in ontology:
                    keys = field.split(ont_delimiter)
                    value = get_nested_value(item, keys)
                    row.append(value)
                writer.writerow(row)
        time_complete = time.time() - start_time
        print(f"CSV conversion completed in {time_complete} seconds")
        return

    # Create CSV
    line = Line()
    writer = csv.writer(line)

    # Write header
    writer.writerow(ontology)
    yield line.read()

    for item in data_list:
        row = []
        for field in ontology:
            keys = field.split(ont_delimiter)
            value = get_nested_value(item, keys)
            row.append(value)
        writer.writerow(row)
        yield line.read()

    time_complete = time.time() - start_time
    print(f"CSV conversion completed in {time_complete} seconds")

# Not working. Fix this later.
if input_filename := sys.argv[1]:
    convert_json_to_csv(input_filename, cli=True)