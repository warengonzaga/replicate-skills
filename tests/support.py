"""Load standalone tools without depending on a runtime's installation layout."""
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def module(skill, filename):
    name = 'replicate_test_' + filename
    spec = importlib.util.spec_from_file_location(name, ROOT / 'skills' / ('replica-' + skill) / (filename + '.py'))
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


def repository_module(filename):
    name = 'replicate_repo_' + filename
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (filename + '.py'))
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value
