#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Descubre el acento de un modelo: frases que usa mucho y la gente casi nunca.

    python3 corpus/descubrir.py claude

Calibrar valida patrones que alguien propuso. Esto hace lo otro: los propone a
partir de los datos. Hace falta porque el catálogo salió del slop inglés de
2024, y Claude en 2026 no escribe así.

Solo mira los textos de DESCUBRIMIENTO (números 00 a 09). Los del 10 al 14 no se
tocan acá: son los que después prueban si lo descubierto sirve. Un patrón que se
evalúa sobre el mismo texto del que salió da bien siempre, y no prueba nada.
"""
import collections
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'tools'))
sys.path.insert(0, AQUI)

TECHO_HUMANO = 0.005          # el mismo techo que calibrar.py
PALABRA = re.compile(r'[a-záéíóúñü0-9]+')


def ngramas(texto, n):
    """Los n-gramas de palabras del texto, en minúscula y sin puntuación."""
    palabras = PALABRA.findall(texto.lower())
    return set(' '.join(palabras[i:i + n]) for i in range(len(palabras) - n + 1))


def sobrerrepresentados(ia, humanos, n, minimo_docs_ia):
    """Frases de n palabras presentes en muchos textos de IA y casi ninguno humano.

    Se cuenta en cuántos DOCUMENTOS aparece cada frase, no cuántas veces. Un texto
    sobre café dice «café» veinte veces, y eso es tema, no acento.
    """
    docs_ia = collections.Counter()
    for doc in ia:
        docs_ia.update(ngramas(doc, n))
    candidatos = set(f for f, c in docs_ia.items() if c >= minimo_docs_ia)
    if not candidatos:
        return []

    docs_hum = collections.Counter()
    for doc in humanos:
        docs_hum.update(ngramas(doc, n) & candidatos)

    hallados = []
    for frase in candidatos:
        frac_ia = float(docs_ia[frase]) / len(ia)
        frac_hum = float(docs_hum[frase]) / len(humanos) if humanos else 0.0
        if frac_hum > TECHO_HUMANO:
            continue
        hallados.append({'frase': frase, 'docs_ia': docs_ia[frase], 'frac_ia': frac_ia,
                         'frac_humano': frac_hum,
                         'ratio': float('inf') if frac_hum == 0 else frac_ia / frac_hum})
    hallados.sort(key=lambda h: (-h['frac_ia'], h['frac_humano']))
    return hallados


def cargar_modelo(modelo, uso):
    """Los textos de un modelo, de descubrimiento (00-09) o de validación (10-14)."""
    import textosaurio as dino
    docs = []
    carpeta = os.path.join(AQUI, 'ia')
    for nombre in sorted(os.listdir(carpeta)):
        m = re.match(r'%s-\w+-(\d\d)\.txt$' % re.escape(modelo), nombre)
        if not m:
            continue
        es_validacion = int(m.group(1)) >= 10
        if (uso == 'validacion') != es_validacion:
            continue
        docs.append(dino.normalizar(dino.leer_utf8(os.path.join(carpeta, nombre))))
    return docs


def main(argv):
    import calibrar
    modelo = argv[0] if argv else 'claude'
    ia = cargar_modelo(modelo, 'descubrimiento')
    humanos = calibrar.cargar(os.path.join(AQUI, 'humano', 'cache'))
    if not ia or not humanos:
        sys.stderr.write('descubrir: faltan textos (%d de %s, %d humanos)\n'
                         % (len(ia), modelo, len(humanos)))
        return 2
    minimo = max(3, int(len(ia) * 0.2))
    print('%d textos de %s para descubrir, %d humanos. Una frase entra si está en al '
          'menos %d textos de %s y en menos del %.1f%% de los humanos.\n'
          % (len(ia), modelo, len(humanos), minimo, modelo, TECHO_HUMANO * 100))
    # Contraste: la misma frase en textos de los OTROS modelos. Una frase que
    # comparten todos es acento de IA en general; una que solo usa este modelo es
    # la que dice quién escribió.
    otros = []
    for nombre in os.listdir(os.path.join(AQUI, 'ia')):
        if nombre.endswith('.txt') and not nombre.startswith(modelo + '-'):
            import textosaurio as dino
            otros.append(dino.normalizar(dino.leer_utf8(os.path.join(AQUI, 'ia', nombre))))
    print('contraste: %d textos de otros modelos\n' % len(otros))
    for n in (1, 2, 3, 4):
        hallados = sobrerrepresentados(ia, humanos, n, minimo)
        print('── %d palabra%s (%d)' % (n, '' if n == 1 else 's', len(hallados)))
        for h in hallados[:30]:
            en_otros = sum(1 for d in otros if h['frase'] in ngramas(d, n))
            print('  %-36s %2d/%d %s   humanos %.2f%%   otros IA %3.0f%%'
                  % (h['frase'][:36], h['docs_ia'], len(ia), modelo, h['frac_humano'] * 100,
                     100.0 * en_otros / len(otros) if otros else 0))
        print('')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
