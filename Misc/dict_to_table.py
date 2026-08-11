# dict_to_table.py
# converts a list of python dictionaries into a HTML table, with headers based off of dictionary keys

test = [
    {'name': 'steph',
        'dob': '1/5/2003'},
    {'name': 'not steph',
        'dob': 'not 1/5/2003'}
]

def dict_to_table(list_of_dict):
    dict_keys = list_of_dict[0].keys()
    for dictionary in list_of_dict:
        if dictionary.keys() != dict_keys:
            raise Exception("List of dicts is not uniform.")

    output = "<table>"

    # add table headers
    output += f"""
    <thead>
        <th>{"</th><th>".join([key for key in dict_keys])}</th>
    </thead>
    <tbody>
    """

    for dictionary in list_of_dict:
        dict_data = list(dictionary.values())
        output += "<tr><td>"
        output += "</td><td>".join([key for key in dict_data])
        output += "</td></tr>\n"

    output += "</tbody>\n</table>"
    return output

if __name__ == "__main__":
    print(dict_to_table(test))
