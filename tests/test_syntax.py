import os
import py_compile
import pathlib


def test_sample_code_compiles():
    path = pathlib.Path(__file__).with_name('sample_code.py')
    py_compile.compile(os.fspath(path), doraise=True)
