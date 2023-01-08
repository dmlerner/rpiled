def close(a, b):
    obob = abs(a - b) < 1
    if obob:
        if a != b:
            print("wtf", a, b)
    return obob


def close_rel(a, b):
    avg = (a + b) / 2
    if avg == 0:
        return True
    rel_max = max(a, b) / avg
    return abs(rel_max - 1) < 0.005


def myround(x):
    if x < 0.1:
        return round(x, 2)
    if x < 1:
        return round(x, 1)
    return round(x)

