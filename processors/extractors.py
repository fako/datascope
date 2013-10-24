import json

def extractor(target, objective):
    # Result list to return
    results = []

    def extract(target):
        # Recursively use this function when confronted with list
        if isinstance(target,list):
            for i in target:
                extract(i)
        # Extract data when confronted with dict
        elif isinstance(target, dict):
            result = {}
            for k in target.iterkeys():
                # When a key in target is an objective and there is no result yet, create default result from objective and override found key
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
    target_dict = json.loads(json_string)
    return extractor(target_dict, objective)