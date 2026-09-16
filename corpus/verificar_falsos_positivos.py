#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Corre el scorer entero sobre el corpus humano y exige que casi todo pase.

    python3 corpus/verificar_falsos_positivos.py

Es el test que decide si el linter sirve. Si marca texto rioplatense escrito
por personas, la regla está mal calibrada, no el corpus. Vive afuera de la
suite unitaria porque necesita la caché descargada, que no se versiona.
"""
import collections
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'tools'))
sys.path.insert(0, AQUI)
import calibrar
import dino

# Guarda de regresión, no objetivo de calidad. El número que de verdad se le
# exige a cada regla es el techo por patrón de calibrar.py; este de acá es la
# consecuencia agregada, y sube o baja con el tamaño del catálogo aunque ninguna
# regla haya cambiado. Sirve para avisar si algo se degrada de golpe.
PISO_LIMPIO = 0.90


def main():
    documentos = calibrar.cargar(os.path.join(AQUI, 'humano', 'cache'))
    if not documentos:
        sys.stderr.write('verificar: no hay corpus humano. '
                         'Corré python3 corpus/construir.py --humano\n')
        return 2

    limpios = 0
    culpables = collections.Counter()
    for texto in documentos:
        hallazgos = dino.auditar(texto)
        slop, _ = dino.puntuar(hallazgos)
        if slop == 5:
            limpios += 1
        for grupo in dino.GRUPOS_SLOP:
            if hallazgos['slop'][grupo]:
                culpables[grupo] += 1

    fraccion = float(limpios) / len(documentos)
    print('%d documentos humanos, %d limpios (%.1f%%)\n'
          % (len(documentos), limpios, fraccion * 100))

    if culpables:
        print('reglas que marcan texto humano:')
        for grupo, n in culpables.most_common():
            print('  %-16s %d documentos (%.1f%%)'
                  % (grupo, n, 100.0 * n / len(documentos)))
        print('')

    if fraccion >= PISO_LIMPIO:
        print('OK — la guarda de regresión está en %.0f%%' % (PISO_LIMPIO * 100))
        return 0
    print('FALLA — la guarda está en %.0f%% y estamos en %.1f%%.' % (PISO_LIMPIO * 100,
                                                                     fraccion * 100))
    print('Algo se degradó. Mirá qué patrón subió con corpus/calibrar.py.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
