"""Verifica los asuntos de los commits incorporados entre dos revisiones de Git."""

import re
import subprocess
import sys


ASUNTO = re.compile(
    r"(?:feat|fix|docs|test|ci|build|chore|perf|refactor|revert|style)"
    r"(?:\([\w./-]+\))?!?: \S.*"
)


def verificar(base, revision):
    intervalo = revision if base == "0" * 40 else f"{base}..{revision}"
    historial = subprocess.check_output(
        ["git", "log", "--no-merges", "--format=%h%x09%s", intervalo],
        encoding="utf-8",
    )
    valido = True
    for linea in historial.splitlines():
        identificador, asunto = linea.split("\t", 1)
        if not ASUNTO.fullmatch(asunto):
            print(f"{identificador} — se esperaba 'tipo(ámbito): resumen'. Se recibió {asunto!r}")
            valido = False
    return valido


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Uso: python scripts/verificar_commits.py BASE REVISION")
    sys.exit(0 if verificar(*sys.argv[1:]) else 1)
