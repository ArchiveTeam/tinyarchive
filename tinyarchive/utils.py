import itertools

def _code_order(char):
    if char >= '0' and char <= '9':
        return 0
    elif char >= 'a' and char <= 'z':
        return 1
    elif char >= 'A' and char <= 'Z':
        return 2
    return 3

def shortcode_compare(a, b):
    diff = len(a) - len(b)
    if diff:
        return diff
    for a, b in itertools.izip(a, b):
        if a != b:
            diff = _code_order(a) - _code_order(b)
            if diff:
                return diff
            else:
                return ord(a) - ord(b)
    return 0
