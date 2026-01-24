import os
import shutil

from ..utils.fs import get_ignore_patterns


def files_are_different(path_a, path_b):
    try:
        with open(path_a, "rb") as a, open(path_b, "rb") as b:
            return a.read() != b.read()
    except Exception:
        return True


def _walk_with_ignore(path, ignore_func):
    for root, dirs, files in os.walk(path):
        if ignore_func:
            ignored = ignore_func(root, dirs + files)
            dirs[:] = [d for d in dirs if d not in ignored]
            files[:] = [f for f in files if f not in ignored]
        yield root, dirs, files


def collect_diff_files(source_path, target_path, ignore_patterns=None):
    diff_files = []

    patterns = ignore_patterns
    if patterns is None:
        patterns = get_ignore_patterns(source_path)

    ignore_func = shutil.ignore_patterns(*patterns) if patterns else None

    for root, _, files in _walk_with_ignore(source_path, ignore_func):
        for filename in files:
            rel_path = os.path.relpath(os.path.join(root, filename), source_path)
            tgt_f = os.path.join(target_path, rel_path)
            src_f = os.path.join(source_path, rel_path)

            if not os.path.exists(tgt_f):
                diff_files.append((rel_path, "New"))
            elif files_are_different(src_f, tgt_f):
                diff_files.append((rel_path, "Modified"))

    for root, _, files in _walk_with_ignore(target_path, ignore_func):
        for filename in files:
            rel_path = os.path.relpath(os.path.join(root, filename), target_path)
            if not os.path.exists(os.path.join(source_path, rel_path)):
                diff_files.append((rel_path, "Deleted"))

    diff_files.sort(key=lambda x: x[0])
    return diff_files

