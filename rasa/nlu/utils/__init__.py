import json
import os
import re
from typing import Any, Dict, List, Optional, Text
from pathlib import Path

import rasa.utils.io as io_utils

# backwards compatibility 1.0.x
# noinspection PyUnresolvedReferences
from rasa.utils.io import read_json_file
from rasa.nlu.constants import (
    ENTITY_ATTRIBUTE_GROUP,
    ENTITY_ATTRIBUTE_TYPE,
    ENTITY_ATTRIBUTE_ROLE,
)
from rasa.shared.nlu.constants import (
    ENTITY_ATTRIBUTE_VALUE,
    ENTITY_ATTRIBUTE_START,
    ENTITY_ATTRIBUTE_END,
)


def relative_normpath(f: Optional[Text], path: Text) -> Optional[Path]:
    """Return the path of file relative to `path`."""
    if f is not None:
        return Path(os.path.relpath(f, path))
    return None


def list_to_str(lst: List[Text], delim: Text = ", ", quote: Text = "'") -> Text:
    return delim.join([quote + e + quote for e in lst])


def module_path_from_object(o: Any) -> Text:
    """Returns the fully qualified class path of the instantiated object."""
    return o.__class__.__module__ + "." + o.__class__.__name__


def json_to_string(obj: Any, **kwargs: Any) -> Text:
    indent = kwargs.pop("indent", 2)
    ensure_ascii = kwargs.pop("ensure_ascii", False)
    return json.dumps(obj, indent=indent, ensure_ascii=ensure_ascii, **kwargs)


def write_json_to_file(filename: Text, obj: Any, **kwargs: Any) -> None:
    """Write an object as a json string to a file."""

    write_to_file(filename, json_to_string(obj, **kwargs))


def write_to_file(filename: Text, text: Any) -> None:
    """Write a text to a file."""

    io_utils.write_text_file(str(text), filename)


def build_entity(
    start: int,
    end: int,
    value: Text,
    entity_type: Text,
    role: Optional[Text] = None,
    group: Optional[Text] = None,
    **kwargs: Any,
) -> Dict[Text, Any]:
    """Builds a standard entity dictionary.

    Adds additional keyword parameters.

    Args:
        start: start position of entity
        end: end position of entity
        value: text value of the entity
        entity_type: name of the entity type
        role: role of the entity
        group: group of the entity
        **kwargs: additional parameters

    Returns:
        an entity dictionary
    """

    entity = {
        ENTITY_ATTRIBUTE_START: start,
        ENTITY_ATTRIBUTE_END: end,
        ENTITY_ATTRIBUTE_VALUE: value,
        ENTITY_ATTRIBUTE_TYPE: entity_type,
    }

    if role:
        entity[ENTITY_ATTRIBUTE_ROLE] = role
    if group:
        entity[ENTITY_ATTRIBUTE_GROUP] = group

    entity.update(kwargs)
    return entity


def is_model_dir(model_dir: Text) -> bool:
    """Checks if the given directory contains a model and can be safely removed.

    specifically checks if the directory has no subdirectories and
    if all files have an appropriate ending."""
    allowed_extensions = {".json", ".pkl", ".dat"}
    dir_tree = list(os.walk(model_dir))
    if len(dir_tree) != 1:
        return False
    model_dir, child_dirs, files = dir_tree[0]
    file_extenstions = [os.path.splitext(f)[1] for f in files]
    only_valid_files = all([ext in allowed_extensions for ext in file_extenstions])
    return only_valid_files


def is_url(resource_name: Text) -> bool:
    """Return True if string is an http, ftp, or file URL path.

    This implementation is the same as the one used by matplotlib"""

    URL_REGEX = re.compile(r"http://|https://|ftp://|file://|file:\\")
    return URL_REGEX.match(resource_name) is not None


def remove_model(model_dir: Text) -> bool:
    """Removes a model directory and all its content."""
    import shutil

    if is_model_dir(model_dir):
        shutil.rmtree(model_dir)
        return True
    else:
        raise ValueError(
            "Cannot remove {}, it seems it is not a model "
            "directory".format(model_dir)
        )
