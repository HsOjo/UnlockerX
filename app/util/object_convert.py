import json


def to_json(obj):
    return json.dumps(obj, indent=4, ensure_ascii=False)


def from_json(obj_str):
    try:
        return json.loads(obj_str)
    except:
        return None


def object_to_dict(obj):
    r = {}
    for k in dir(obj):
        if k[0] != '_':
            v = getattr(obj, k)
            if not callable(v):
                r[k] = v

    return r


def dict_to_object(d: dict, obj=object(), new_fields=True):
    for k, v in d.items():
        if new_fields or k in dir(obj):
            setattr(obj, k, v)
