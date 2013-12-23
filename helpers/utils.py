def sort_on_list_len(first, second):
    first_len = len(first) if isinstance(first, list) else 0
    second_len = len(second) if isinstance(second, list) else 0
    if first_len < second_len:
        return -1
    elif first_len == second_len:
        return 0
    else:
        return 1
