from typing import Any
import time 

debug_char = "-"
debug_char_count = 2
err_msg_invalid_item = "Item {item} is not valid"
err_msg_created = "Item {item} is already created"
err_msg_invalid_type = "Item {item} has invalid type: {typeitem.__name__}, expected: {valid_item}"
msg_valid = "items are valid"

def dprint(*args, **kwargs):
    print(debug_char * debug_char_count, *args, **kwargs)
    
def ddprint(*args, **kwargs):
    print(debug_char * debug_char_count, *args, debug_char * debug_char_count, **kwargs)

def check(config: dict):
    struct = dict(config) if isinstance(config, dict) else config
    err_log = []
    old_time = time.time()
    ddprint("started validation")
    dprint(f"groups to valid: {", ".join(struct.keys())}")
    for num, key in enumerate(struct.keys()):
        if key in valid_dict:
            dprint(f"Process: {num + 1}/{len(struct.keys())}, group: {key}", end = "")
            try:
                is_valid, err_msg = valid_dict[key](struct[key])
            except Exception as e:
                is_valid, err_msg = valid_dict[key](struct[key]), "Unknown error"
            if is_valid:
                print(" - OK")
            else:
                print(" - ERROR")
                err_log.append(f"{key}: {err_msg}")
        else:
            dprint(f"Process: {num + 1}/{len(struct.keys())}, group: {key}", end = "")
            print(" - INVALID")
            
    ddprint("Finished validation")
    ddprint(f"Time: {(time.time() - old_time)*1000:.2f} ms")
    if err_log:
        ddprint("Errors have been occured during validation, raising exception...")
        raise ValueError(f"Validation errors:\n{"\n".join(err_log)}")
    
def _validate_items(items: dict, valid_items: dict):
    err_batch = []
    def _format_expected_types(expected):
        default_str = "expected "
        if isinstance(expected, (tuple, list)):
            return default_str + " or ".join(t.__name__ for t in expected)
        else:
            return default_str + expected.__name__

    _valid_keys = []
    _simple_mode = Any in valid_items and len(valid_items) == 1
    for item in items:
        if _simple_mode:
            if not isinstance(items[item], valid_items[Any]):
                err_batch.append(f"{item}: {expected_type_str} but get {actual_type_str} '{items[item]}'") # type: ignore
            _valid_keys.append(item)
            continue
        if item not in valid_items.keys():
            if Any in valid_items:
                if not isinstance(item, valid_items[Any]):
                    err_batch.append(f"{item}: {err_msg_invalid_type.format(item = item, valid_items = valid_items)}")
                continue
            err_batch.append(f"{item}: {err_msg_invalid_item.format(item = item)}")
        elif item in _valid_keys:
            err_batch.append(f"{item}: {err_msg_created.format(item = item)}")
        else:
            _valid_keys.append(item)

    if not _simple_mode:
        for item in _valid_keys:
            if valid_items[item] is Any: continue
            if not isinstance(items[item], valid_items[item]):
                err_batch.append(
                    f"{item}: {_format_expected_types(valid_items[item])} but get {type(items[item]).__name__} '{items[item]}'"
                )
    if err_batch:
        return None, "\n"+ "\n".join(err_batch)
    return _valid_keys, msg_valid
 
def _validate_group(valid_items: dict, substruct: Any):
    valid_items = valid_items
    items, msg = _validate_items(substruct, valid_items)
    return True if items else (False, msg)

def validate_window(window: Any):
    valid_items = {
        "title": str,
        "size": (list, tuple),
        "display": str,
        "utils": list,
        "fps": int,
        "resizable": bool,
        "ratio": (list, tuple)
    }
    return _validate_group(valid_items, window)
    
def validate_animations(substruct: Any):
    valid_items = {
        Any: dict,
    }
    return _validate_group(valid_items, substruct)

def validate_colors(substruct: Any):
    valid_items = {
        Any: (list, tuple, str),
    }
    return _validate_group(valid_items, substruct)

def validate_styles(substruct: Any):
    valid_items = {
        Any: (dict, str),
    }
    return _validate_group(valid_items, substruct)

def validate_generated(generated: Any):
    if isinstance(generated, bool):
        return True, msg_valid
    return False, err_msg_invalid_type.format(item = generated.name, typeitem = type(generated), valid_item = bool.__name__)

valid_dict = {
    "window": validate_window,
    "animations": validate_animations,
    "colors": validate_colors,
    "styles": validate_styles,
    "generated": validate_generated
}

def add_validator(key: str, func):
    valid_dict[key] = func

def remove_validator(key: str):
    valid_dict.pop(key)