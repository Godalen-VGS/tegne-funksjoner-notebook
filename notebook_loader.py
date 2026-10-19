"""Hjelpefil for automatisk retting. Ikke endre eller slett denne filen.

Laster funksjonene fra notebooken uten å kjøre resten av koden på toppnivå.
Slik ødelegger ikke input(), print-kall, selvtest-celler eller kode som
krasjer for testene av funksjonene.

Leser den konverterte .py-filen (fra `jupyter nbconvert --to python`) hvis
den finnes, ellers notebooken direkte.
"""
import ast
import json
import os
import re
import types

_MAPPE = os.path.dirname(os.path.abspath(__file__))

# Disse setningene på toppnivå beholdes. Alt annet (print, løkker, if,
# funksjonskall som test_xxx()) hoppes over.
_BEHOLD = (
    ast.Import, ast.ImportFrom,
    ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
    ast.Assign, ast.AnnAssign, ast.AugAssign,
)


def _bruker_input(node):
    return any(
        isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "input"
        for n in ast.walk(node)
    )


def _celler_fra_py(filsti):
    with open(filsti, encoding="utf-8") as f:
        kildekode = f.read()
    return re.split(r"^# In\[.*\]:[ \t]*$", kildekode, flags=re.M)


def _celler_fra_ipynb(filsti):
    with open(filsti, encoding="utf-8") as f:
        nb = json.load(f)
    celler = []
    for celle in nb["cells"]:
        if celle["cell_type"] != "code":
            continue
        kilde = "".join(celle["source"])
        # Fjern IPython-magi som %matplotlib inline og !pip install
        linjer = [l for l in kilde.splitlines() if not l.lstrip().startswith(("%", "!"))]
        celler.append("\n".join(linjer))
    return celler


def last_notebook(navn):
    """Laster `navn.py` (eller `navn.ipynb`) og returnerer en modul med funksjonene."""
    py = os.path.join(_MAPPE, navn + ".py")
    ipynb = os.path.join(_MAPPE, navn + ".ipynb")
    celler = _celler_fra_py(py) if os.path.exists(py) else _celler_fra_ipynb(ipynb)

    modul = types.ModuleType(navn)
    for celle in celler:
        # Hver celle tolkes for seg, så en syntaksfeil i én celle ikke tar med seg resten
        try:
            tre = ast.parse(celle)
        except SyntaxError:
            continue
        for node in tre.body:
            if not isinstance(node, _BEHOLD):
                continue
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and _bruker_input(node):
                continue
            kode = compile(ast.Module(body=[node], type_ignores=[]), navn, "exec")
            try:
                exec(kode, modul.__dict__)
            except Exception:
                pass
    return modul
