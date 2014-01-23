import json

def reach(key, data):
    try:
        for part in key.split('.'):
            if part.isdigit():
                data = data[int(part)]
            else:
                data = data[part]
        else:
            return data
    except (IndexError, KeyError):
        return data[key] if key in data else None


def extractor(target, objective):
    """
    This function takes a data construct and a dictionary
    From the data it tries to create instances like dictionary
    Whenever it encounters a key from the dict in the data it will initiate a new copy of dict
    And fill the rest of the keys with values coming from the same keys present in data construct.
    """

    # Result list to return
    results = []

    def extract(target):
        # Recursively use this function when confronted with list
        if isinstance(target, list):
            for i in target:
                extract(i)
        # Extract data when confronted with dict
        elif isinstance(target, dict):
            result = {}
            for k in target.iterkeys():
                # When a key in target is an objective and there is no result yet, create default result from objective
                # and override found key
                if k in objective and not result:
                    result = dict(objective)
                    result[k] = target[k]
                # When a key in target is an objective and there already is result, just override default result values.
                elif k in objective:
                    result[k] = target[k]
                # Recursively use self when confronted with something else then an objective
                else:
                    extract(target[k])
            # Append extracted result to the results
            if result:
                results.append(result)
        # Only return the value when not dealing with lists or dicts.
        else:
            return target

    extract(target)
    return results


def json_extractor(json_string, objective):
    """
    This function turns a JSON string into python data and passes it to extractor()
    """
    target_dict = json.loads(json_string)
    return extractor(target_dict, objective)




# EVERYTHING IN THIS COMMENT IS CURRENTLY UNUSED
# def flattener(target, sort_comparison=None):
#     """
#
#     """
#
#     def flatten(target):
#         if isinstance(target, list):
#             result = []
#             for i in target:
#                 result.append(flatten(i))
#             if sort_comparison:
#                 result.sort(sort_comparison)
#             return result if not len(result) == 1 else result[0]
#
#         elif isinstance(target, dict):
#             result = []
#             for k, v in target.iteritems():
#                 result.append(flatten(v))
#             if sort_comparison:
#                 result.sort(sort_comparison)
#             return result if not len(result) == 1 else result[0]
#
#         else:
#             return target
#
#     return flatten(target)
#
# def json_flattener(json_string):
#     target = json.loads(json_string)
#     return flattener(target)
#
# def sort_on_list_len(first, second):
#     first_len = len(first) if isinstance(first, list) else 0
#     second_len = len(second) if isinstance(second, list) else 0
#     if first_len < second_len:
#         return -1
#     elif first_len == second_len:
#         return 0
#     else:
#         return 1