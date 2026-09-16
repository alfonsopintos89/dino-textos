#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mide las reglas de dino.py contra los dos corpus y dicta veredicto.

Importa el scorer en vez de copiar sus listas. Es a propósito: si la medición
tuviera su propia copia del catálogo, las dos se separarían con el tiempo y el
número publicado dejaría de describir la herramienta que corre de verdad.

    python3 corpus/calibrar.py            mide y escribe frecuencias.json
    python3 corpus/calibrar.py --breve    solo el resumen por estado
"""
import collections
import json
import os
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(AQUI), 'tools'))
sys.path.insert(0, AQUI)
import dino

# ── el criterio ──────────────────────────────────────────────────────────────
# Los tres números que deciden qué entra al scorer. Están acá, en una sola
# parte, y se publican junto con la medición que los justifica.

RATIO_MINIMO = 5.0             # veces más frecuente en texto de IA que en humano
TECHO_FALSOS_POSITIVOS = 0.005  # fracción de documentos humanos que puede tocar
MINIMO_APARICIONES = 10        # abajo de esto la muestra no dice nada

# Sobre el techo: la primera versión de este archivo decía 2%, y el corpus mostró
# que ese número era incompatible con el piso que pedía el verificador. Un scorer
# con veinticinco palabras de vocabulario, cada una tocando el 1% de los textos
# sobre documentos distintos, junta un 15% de union aunque ninguna regla pase el
# 2%. El techo por patrón y el piso por scorer no son dos criterios
# independientes: el primero tiene que salir del segundo, dividido por cuántos
# patrones tiene el catálogo. 0,5% sobre 592 documentos son tres textos, que es
# lo más chico que se puede medir sin que el número sea puro ruido.

Veredicto = collections.namedtuple('Veredicto', 'estado ratio motivo')


def veredicto(apariciones_ia, por_10k_ia, por_10k_humano, docs_humanos_tocados):
    """Admitido, rechazado o sin evidencia, siempre con el motivo al lado.

    El motivo no es decorativo: los rechazos se publican con su número, y esa
    lista es lo que hace defendible al catálogo.
    """
    if apariciones_ia < MINIMO_APARICIONES:
        return Veredicto('sin evidencia', 0.0,
                         'solo %d apariciones en el corpus de IA (mínimo %d)'
                         % (apariciones_ia, MINIMO_APARICIONES))

    ratio = float('inf') if por_10k_humano == 0 else por_10k_ia / por_10k_humano

    if docs_humanos_tocados > TECHO_FALSOS_POSITIVOS:
        return Veredicto('rechazado', ratio,
                         'toca el %.1f%% de los textos humanos (techo %.1f%%)'
                         % (docs_humanos_tocados * 100, TECHO_FALSOS_POSITIVOS * 100))

    if ratio < RATIO_MINIMO:
        return Veredicto('rechazado', ratio,
                         'ratio %.1fx, por debajo de %.1fx — %.2f contra %.2f cada 10k'
                         % (ratio, RATIO_MINIMO, por_10k_ia, por_10k_humano))

    return Veredicto('admitido', ratio,
                     'ratio %s, toca el %.1f%% de los textos humanos'
                     % ('∞' if ratio == float('inf') else '%.1fx' % ratio,
                        docs_humanos_tocados * 100))


# ── de dónde salen los patrones ──────────────────────────────────────────────

def patrones_del_scorer():
    """Cada regla que dino.py aplica hoy, como (grupo, etiqueta, regex compilado)."""
    for palabra in dino.LEXICO_RAIZ:
        yield ('lexico', palabra, re.compile(dino._patron_raiz(palabra)))
    for frase in dino.LEXICO_EXACTO:
        yield ('lexico', frase, re.compile(r'(?<!\w)%s(?!\w)' % re.escape(frase)))
    for patron, etiqueta in dino.CONSTRUCCIONES:
        yield ('construcciones', etiqueta, re.compile(patron))
    for patron, etiqueta in dino.SUPERLATIVOS:
        yield ('venta', etiqueta, re.compile(patron))
    yield ('venta', 'número pegado a un sustantivo de persona', dino.PRUEBA)
    yield ('ritmo', 'ritmo de tres', dino.RITMO)
    yield ('cadencia', 'raya al modo inglés', dino.RAYA_INGLESA)
    for patron, etiqueta in dino.PRONOMBRES:
        yield ('pronombres', etiqueta, re.compile(patron))
    for patron, etiqueta in dino.PENINSULAR:
        yield ('lexico_peninsular', etiqueta, re.compile(patron, re.M))


def patrones_candidatos():
    """Lo propuesto que todavía no entró. Se mide igual que lo que ya está."""
    try:
        import candidatos
    except ImportError:
        return
    for grupo, etiqueta, patron in candidatos.CANDIDATOS:
        yield (grupo, etiqueta, re.compile(patron))


# ── la medición ──────────────────────────────────────────────────────────────

PALABRAS_DE_PARRAFO = 12


def cargar(carpeta):
    """Los documentos de un corpus: solo párrafos, normalizados y en minúscula.

    Los dos corpus se extraen igual, y el filtro de párrafo es lo que los hace
    comparables. El de IA trae títulos y botones; el humano viene de notas de
    diario donde eso ya quedó afuera. Sin emparejarlo, la medición compararía
    maquetación contra prosa y cada número saldría torcido.

    El costo es explícito: las reglas que viven en el copy corto — botones,
    títulos — no se calibran acá. Se sostienen con los tests de falso positivo.
    """
    documentos = []
    if not os.path.isdir(carpeta):
        return documentos
    for nombre in sorted(os.listdir(carpeta)):
        if not nombre.endswith('.txt'):
            continue
        texto = dino.normalizar(dino.leer_utf8(os.path.join(carpeta, nombre)))
        parrafos = [r for r in texto.split('\n')
                    if len(r.split()) >= PALABRAS_DE_PARRAFO]
        if parrafos:
            documentos.append('\n'.join(parrafos).lower())
    return documentos


def medir(patron, documentos):
    """Apariciones totales, frecuencia cada 10.000 palabras y documentos tocados."""
    apariciones = 0
    tocados = 0
    palabras = 0
    for doc in documentos:
        palabras += len(doc.split())
        n = len(patron.findall(doc))
        apariciones += n
        if n:
            tocados += 1
    por_10k = (apariciones * 10000.0 / palabras) if palabras else 0.0
    fraccion = (float(tocados) / len(documentos)) if documentos else 0.0
    return apariciones, por_10k, fraccion


def main(argv):
    breve = '--breve' in argv
    ia = cargar(os.path.join(AQUI, 'ia'))
    humano = cargar(os.path.join(AQUI, 'humano', 'cache'))

    if not ia or not humano:
        sys.stderr.write(
            'calibrar: faltan corpus. Corré primero:\n'
            '  python3 corpus/construir.py --ia\n'
            '  python3 corpus/construir.py --humano\n'
            'Hay %d textos de IA y %d humanos.\n' % (len(ia), len(humano)))
        return 2

    print('corpus: %d textos de IA, %d humanos (%d y %d palabras)\n'
          % (len(ia), len(humano),
             sum(len(d.split()) for d in ia), sum(len(d.split()) for d in humano)))

    filas = []
    todos = list(patrones_del_scorer())
    en_el_scorer = set((g, e) for g, e, _ in todos)
    todos += [p for p in patrones_candidatos() if (p[0], p[1]) not in en_el_scorer]

    for grupo, etiqueta, patron in todos:
        ap_ia, p10k_ia, _ = medir(patron, ia)
        _, p10k_hum, frac_hum = medir(patron, humano)
        v = veredicto(ap_ia, p10k_ia, p10k_hum, frac_hum)
        filas.append({'grupo': grupo, 'etiqueta': etiqueta, 'estado': v.estado,
                      'ratio': None if v.ratio == float('inf') else round(v.ratio, 2),
                      'motivo': v.motivo, 'por_10k_ia': round(p10k_ia, 2),
                      'por_10k_humano': round(p10k_hum, 2),
                      'docs_humanos_tocados': round(frac_hum, 4),
                      'en_el_scorer': (grupo, etiqueta) in en_el_scorer})

    resumen = collections.Counter(f['estado'] for f in filas)
    if not breve:
        for estado in ('rechazado', 'sin evidencia', 'admitido'):
            elegidos = [f for f in filas if f['estado'] == estado]
            if not elegidos:
                continue
            print('── %s (%d)' % (estado, len(elegidos)))
            for f in sorted(elegidos, key=lambda f: -(f['ratio'] or 9999)):
                marca = '·' if f['en_el_scorer'] else '+'
                print('  %s %-46s %s' % (marca, f['etiqueta'][:46], f['motivo']))
            print('')

    print('total: ' + ', '.join('%d %s' % (n, e) for e, n in resumen.most_common()))
    print('\n· ya está en el scorer   + candidato todavía afuera')

    salida = os.path.join(AQUI, 'frecuencias.json')
    with open(salida, 'w') as f:
        json.dump({'criterio': {'ratio_minimo': RATIO_MINIMO,
                                'techo_falsos_positivos': TECHO_FALSOS_POSITIVOS,
                                'minimo_apariciones': MINIMO_APARICIONES},
                   'corpus': {'textos_ia': len(ia), 'textos_humanos': len(humano),
                              'palabras_ia': sum(len(d.split()) for d in ia),
                              'palabras_humanas': sum(len(d.split()) for d in humano)},
                   'patrones': filas}, f, ensure_ascii=False, indent=2)
    print('escrito %s' % salida)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
