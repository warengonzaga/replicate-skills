"""Load a script from a skill folder (the folder names have hyphens)."""

import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(folder, name):
    base = os.path.join(ROOT, "skills") if folder.startswith("replica-") else ROOT
    path = os.path.join(base, folder, name + ".py")
    spec = importlib.util.spec_from_file_location("replica_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
