#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Registra en el manifiesto los textos de IA pegados a mano.

    python3 corpus/registrar.py --modelo "GPT-5.6 (web)"

Todo texto del corpus tiene que poder decir de dónde salió. Si no, la medición
deja de ser reproducible y el número publicado no vale nada.
"""
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
DESTINO = os.path.join(AQUI, 'ia')
MANIFIESTO = os.path.join(DESTINO, 'manifiesto.json')


def main(argv):
    if '--modelo' not in argv:
        sys.exit(__doc__)
    modelo = argv[argv.index('--modelo') + 1]

    previo = []
    if os.path.exists(MANIFIESTO):
        previo = json.load(open(MANIFIESTO, encoding='utf-8'))
    registrados = set(f['archivo'] for f in previo)

    nuevos = []
    for nombre in sorted(os.listdir(DESTINO)):
        if not nombre.endswith('.txt') or nombre in registrados:
            continue
        m = re.match(r'(?:([\w.-]+)-)?(landing|posteo|producto)-(\d+)\.txt$', nombre)
        if not m:
            sys.stderr.write('  nombre fuera de convención, salteado: %s\n' % nombre)
            continue
        palabras = len(open(os.path.join(DESTINO, nombre),
                            encoding='utf-8', errors='replace').read().split())
        nuevos.append({'archivo': nombre, 'genero': m.group(2),
                       'prompt': 'ver corpus/prompts-para-pegar.md, %s %s'
                                 % (m.group(2), m.group(3)),
                       'modelo': modelo, 'palabras': palabras, 'pegado_a_mano': True})

    if not nuevos:
        print('no hay textos nuevos para registrar')
        return 0
    with open(MANIFIESTO, 'w', encoding='utf-8') as f:
        json.dump(previo + nuevos, f, ensure_ascii=False, indent=2)
    print('%d textos registrados como %s (%d palabras)'
          % (len(nuevos), modelo, sum(n['palabras'] for n in nuevos)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
