#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patrones propuestos que todavía NO están en el scorer.

Se miden igual que los que ya entraron. Si pasan el criterio, se mueven a mano a
`tools/dino.py` con su número anotado en `referencias/fuentes.md`. Si no pasan,
se publican rechazados, con el número que los rechazó.

Están acá porque sospecho de ellos, no porque tenga evidencia. Esa es
exactamente la diferencia que este archivo existe para marcar.
"""

CANDIDATOS = [
    # Léxico: palabras que suenan a modelo pero también son español corriente.
    # La sospecha es fuerte; la evidencia, ninguna todavía.
    # Salió del scorer: marcaba el 2,0% de la prensa humana, porque `impulso` y
    # `impulsó` son palabras corrientes en prosa política.
    ('lexico', 'impulsar', r'(?<!\w)impuls(?:a|o|ar|ando|amos|an|ado|ó|aron|ará)(?!\w)'),
    ('lexico', 'aprovechar', r'(?<!\w)aprovech(?:a|ar|ando|amos|an|ado)(?!\w)'),
    ('lexico', 'fomentar', r'(?<!\w)foment(?:a|ar|ando|amos|an|ado)(?!\w)'),
    ('lexico', 'ecosistema', r'(?<!\w)ecosistemas?(?!\w)'),
    ('lexico', 'panorama', r'(?<!\w)panoramas?(?!\w)'),
    ('lexico', 'ámbito', r'(?<!\w)ámbitos?(?!\w)'),
    ('lexico', 'integral', r'(?<!\w)integrales?(?!\w)'),
    ('lexico', 'crucial', r'(?<!\w)cruciales?(?!\w)'),
    ('lexico', 'clave (como adjetivo)', r'(?<!\w)clave(?!\w)'),
    ('lexico', 'viaje', r'(?<!\w)viajes?(?!\w)'),
    ('lexico', 'a medida', r'(?<!\w)a medida(?!\w)'),
    ('lexico', 'hoy en día', r'(?<!\w)hoy en día(?!\w)'),
    ('lexico', 'sin duda', r'(?<!\w)sin duda(?!\w)'),
    ('lexico', 'sumergirse en', r'(?<!\w)sumerg(?:irse|ite|ete) en(?!\w)'),

    # Construcciones: conectores de redacción formal. Un modelo los apila; una
    # persona escribiendo para la web casi no los usa. Eso dice la sospecha.
    ('construcciones', 'sin embargo', r'\bsin embargo\b'),
    ('construcciones', 'no obstante', r'\bno obstante\b'),
    ('construcciones', 'por otro lado', r'\bpor otro lado\b'),
    ('construcciones', 'asimismo', r'\basimismo\b'),
    ('construcciones', 'en este sentido', r'\ben este sentido\b'),
    ('construcciones', 'a su vez', r'\ba su vez\b'),

    # Cadencia: el punto y coma y los dos puntos como tic.
    ('cadencia', 'punto y coma', r';'),
    # Estaba en el scorer y salió: el umbral lo porté de una regla pensada para
    # el punto y coma en inglés, y disparó sobre el primer documento de verdad
    # que escribí. Vuelve cuando haya un número que lo sostenga.
    ('cadencia', 'dos puntos', r':'),

    # Registro: palabras que sospecho peninsulares pero que también se usan acá,
    # o que colisionan con otro sentido. `piso` es el caso de manual: vivienda en
    # España, suelo acá, y un regex no puede distinguirlos.
    ('lexico_peninsular', 'aquí', r'(?<!\w)aquí(?!\w)'),
    # Salió del scorer por la misma razón: se usa de este lado y no tengo con
    # qué defender que sea peninsular.
    ('lexico_peninsular', 'ahora mismo', r'(?<!\w)ahora mismo(?!\w)'),
    ('lexico_peninsular', 'actualmente', r'(?<!\w)actualmente(?!\w)'),
    ('lexico_peninsular', 'conducir', r'(?<!\w)conduc(?:ir|e|en|ía)(?!\w)'),
    ('lexico_peninsular', 'billete', r'(?<!\w)billetes?(?!\w)'),
    ('lexico_peninsular', 'piso (vivienda)', r'(?<!\w)pisos?(?!\w)'),
    ('lexico_peninsular', 'coche', r'(?<!\w)coches?(?!\w)'),
    ('lexico_peninsular', 'ordenador o portátil', r'(?<!\w)portátiles?(?!\w)'),
]
