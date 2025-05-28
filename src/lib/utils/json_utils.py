import json


def apply_patch(data: dict, patch: dict) -> dict:
    """
    Apply a patch to a SATB realization structure.

    Patch format:
    {
        "alto": {
            "2": ["C4", "D4", "E4"]
        },
        "tenor": {
            "3": ["A3", "G3"]
        }
    }

    This updates the specified measures (0-indexed) in each part.
    """
    for part, measures in patch.items():
        if part not in data:
            continue
        for measure_idx_str, updated_measure in measures.items():
            try:
                idx = int(measure_idx_str)
                data[part][idx] = updated_measure
            except (ValueError, IndexError):
                continue  # ignore invalid or out-of-bounds
    return data


def load_json(json_path: str, default: dict = None) -> dict:
    """
    Load a JSON file and return its content as a dictionary.
    If the file does not exist or is empty, return the default value.
    """
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                raise ValueError("JSON content is not a dictionary.")
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        return default if default is not None else {}
