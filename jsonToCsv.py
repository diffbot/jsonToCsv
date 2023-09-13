import sys
import msgspec
import json
import csv
import traceback
import time

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

def generate_csv(ontology, data_list, start_time=time.time(), ont_delimiter=None):
    class Line(object):
        def __init__(self):
            self._line = None
        def write(self, line):
            self._line = line
        def read(self):
            return self._line

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

# Read & Convert the JSON data
def convert_json_to_csv(file, cli=False, json_paste=None, selected_ontology_string=None):
    start_time = time.time()
    if file:
        with open(file, 'rb') as f:
            content = f.read()
    else:
        content = json_paste

    data_list = None
    ont_delimiter = "/"
    try: 
        data_json = msgspec.json.decode(content)
    except:
        # Didn't parse, return invalid JSON
        raise

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

    # Filter Ontology by Selected Ontology
    if selected_ontology_string:
        selected_ontology = msgspec.json.decode(selected_ontology_string)
        if selected_ontology:
            ontology = [ont for ont in selected_ontology.keys() if selected_ontology.get(ont, False)]
        return generate_csv(ontology, data_list, start_time=start_time, ont_delimiter=ont_delimiter)

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
    example_record = {}
    for field in ontology:
        keys = field.split(ont_delimiter)
        value = get_nested_value(data_list[0], keys)
        example_record[field] = value
    return {
        "ontology": ontology,
        "example_record": example_record
    }
