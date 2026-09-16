#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Caza señales de IA y deslices de registro en textos en español rioplatense.

Dos ejes que puntúan por separado, porque fallan por razones distintas y se
arreglan con ediciones distintas: un texto puede ser humanísimo y estar escrito
en peninsular, o estar en voseo perfecto y ser slop puro.
"""
import sys
import html as _html      # con alias: `texto_visible` recibe un parámetro `html`
import re

# Etiquetas que cierran una pieza de copy. Un botón y el párrafo que le sigue son
# dos textos distintos, y la regla de CTA necesita ver dónde termina cada uno.
# `a`, `span`, `strong` y `em` quedan afuera a propósito: son de línea, y cortar
# ahí partiría oraciones al medio y dejaría ciegas a las reglas de construcción.
BLOQUE = re.compile(
    r'</?(?:p|div|section|article|h[1-6]|li|ul|ol|button|form|label'
    r'|td|th|tr|table|br|hr|blockquote|header|footer|nav|main)\b[^>]*>',
    re.I)


def normalizar(t):
    """Pliega las variantes tipográficas a las que los patrones sí matchean.

    Un guion de no separación no es `-`, un espacio duro no es un espacio y una
    comilla curva no es `'`. Si alguna se escapa, `de-vanguardia` y las formas
    con apóstrofo dejan de matchear justo sobre el texto real, que es de donde
    salen los caracteres lindos.

    Lo que NUNCA hace es sacar tildes. Es el reflejo normal al normalizar texto
    en español, y acá dejaría ciego al eje de registro entero: la tilde es lo
    único que separa `regístrate` (tuteo) de `registrate` (voseo).

    Los renglones se conservan. Marcan dónde termina una pieza de copy.
    """
    t = t.replace('‑', '-').replace(' ', ' ').replace('’', "'")
    t = re.sub(r'[^\S\n]+', ' ', t)
    renglones = [r.strip() for r in t.split('\n')]
    return '\n'.join(r for r in renglones if r)


def texto_visible(html):
    """Lo que un visitante lee de verdad. Sin script, sin style, sin etiquetas."""
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', html, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = BLOQUE.sub('\n', t)
    t = re.sub(r'<[^>]+>', ' ', t)
    # Todas las entidades, no seis escritas a mano: las numéricas se colaban como
    # texto literal y cada `&#xed;` rompía una palabra acentuada por la mitad.
    t = _html.unescape(t)
    return normalizar(t)


def prosa_markdown(md):
    """La prosa de un markdown, con los especímenes citados afuera.

    Un literal no es copy. Un catálogo que documenta `potenciar` no shipeó la
    palabra: la citó. Un linter que no distingue las dos cosas hace que todo
    catálogo puntúe cero, así que salen los bloques cercados, el código en
    línea, el texto tachado y el alt de las imágenes.

    El texto de los enlaces se queda, porque se lee como parte de la oración.
    """
    md = re.sub(r'```.*?```', '\n', md, flags=re.S)
    md = re.sub(r'!\[[^\]]*\]\([^)]*\)', '\n', md)
    md = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', md)
    # Suplentes, no borrados. Sacar `[falta dato]` del todo suelda la cláusula de
    # al lado y puede inventar un ritmo de tres que nadie escribió, y un linter
    # que inventa un acierto es peor que uno que se pierde uno.
    md = re.sub(r'`[^`]*`', ' eso ', md)
    md = re.sub(r'~~.*?~~', ' eso ', md, flags=re.S)
    md = re.sub(r'^\s{0,3}#{1,6}\s*(.*)$', r'\n\1\n', md, flags=re.M)
    md = re.sub(r'\|', '\n', md)
    md = re.sub(r'^\s*(?:[-*+]|\d+\.)\s+', '\n', md, flags=re.M)
    md = re.sub(r'^\s*>\s?', '\n', md, flags=re.M)
    md = re.sub(r'[*_>]', ' ', md)
    return normalizar(md)


GRUPOS_SLOP = ('lexico', 'construcciones', 'cadencia', 'ritmo', 'venta')
GRUPOS_REGISTRO = ('pronombres', 'imperativos', 'lexico_peninsular')

# ── eje 1: slop ──────────────────────────────────────────────────────────────

# Por raíz, para las palabras que en este registro no tienen uso honesto. El copy
# se escribe conjugado y con género, así que matchear la forma exacta se pierde
# la superficie más común de todas: `Acme potencia tu negocio`.
LEXICO_RAIZ = [
    'potenciar', 'optimizar', 'revolucionar', 'transformador', 'robusto',
    'holístico', 'sinergia', 'empoderar', 'desbloquear', 'inigualable',
    'vanguardia', 'meticuloso', 'maximizar', 'impulsar', 'innovador',
    'disruptivo', 'escalable', 'sofisticado', 'excepcional', 'inmersivo',
]

# Frases hechas y palabras que solo son tell en su forma exacta. Van enteras
# porque la raíz cazaría el uso corriente: `viaje` es una palabra común y
# marcarla sería llorar lobo, pero `un viaje de transformación` no lo es.
LEXICO_EXACTO = [
    'experiencia única', 'de última generación', 'en constante evolución',
    'en el mundo actual', 'en la era digital', 'sin precedentes',
    'de vanguardia', 'soluciones integrales', 'el poder de',
    'un viaje de', 'el mundo de hoy', 'a otro nivel', 'sin fisuras',
    'de primer nivel', 'de clase mundial', 'nuestra propuesta de valor',
]

SUFIJOS = (r'(?:a|as|o|os|e|es|an|en|ar|ado|ada|ados|adas|ando|amos|'
           r'ación|aciones|ador|adora|adores|adoras|able|ables|'
           r'ico|ica|icos|icas|ario|aria|arios|arias|mente|'
           r'ó|é|aron|aba|aban|ará|arán|aría|arían)?')


def _raiz(palabra):
    """La raíz de una palabra española, para que todas sus flexiones matcheen.

    Saca la terminación de infinitivo (`potenciar` → `potenci`) o la de género
    (`robusto` → `robust`), y después SUFIJOS deja volver a pegar cualquier
    flexión. Es deliberadamente tosco: no es un lematizador, es lo mínimo que
    hace falta para que una lista curada de veinte palabras no se pierda
    `potenciamos`, `potenciada` y `potenciando`.
    """
    if len(palabra) > 4 and palabra[-2:] in ('ar', 'er', 'ir'):
        return palabra[:-2]
    if len(palabra) > 4 and palabra[-1] in 'oae':
        return palabra[:-1]
    return palabra


def _patron_raiz(palabra):
    raiz = _raiz(palabra)
    if len(raiz) < 4:                      # muy corta para cortarla sin riesgo
        return r'(?<!\w)%s(?!\w)' % re.escape(palabra)
    return r'(?<!\w)%s%s(?!\w)' % (re.escape(raiz), SUFIJOS)


CONSTRUCCIONES = [
    (r'\bno\s+(?:solo|sólo|solamente|únicamente)\b[^.!?]{0,80}\bsino\b',
     'la forma «no solo X, sino Y»'),
    (r'\bno se trata (?:solo |sólo )?de\b[^.!?]{0,80}[,.]\s*(?:es|sino|se trata)',
     'la forma «no se trata de X, es Y»'),
    (r'\bah[íi] es donde entra\b', '«ahí es donde entra X»'),
    (r'\bya sea que\b', '«ya sea que X o Y»'),
    (r'\b(?:dec[íi]le|dec[íi]|dile|di) adi[óo]s a\b', '«decile adiós a»'),
    (r'\bimagin[áa] (?:un|una|el|la|por un momento)\b', 'el arranque «imaginá un…»'),
    (r'¿\s*(?:el|la|lo)\s+(?:resultado|respuesta|clave|consecuencia|mejor)\s*\?',
     'pregunta que el propio texto contesta'),
    (r'\ben (?:conclusión|resumen|definitiva)\b|\bpara resumir\b',
     'cierre de redacción escolar'),
    (r'\bcuando se trata de\b', 'relleno «cuando se trata de»'),
    (r'\bcabe (?:destacar|señalar|mencionar)\b|\bes importante (?:señalar|destacar|notar)\b'
     r'|\bvale la pena mencionar\b', 'carraspeo antes de la idea'),
    (r'\bla clave está en\b|\bla verdad es que\b', 'arranque de carraspeo'),
    (r'\bte ayuda a\b|\bpuede ayudar(?:te|lo|la) a\b', 'beneficio con pinzas'),
    (r'\bpodría potencialmente\b|\bquizás posiblemente\b|\bpuede llegar a poder\b',
     'dudas apiladas'),
    (r'\bal siguiente nivel\b', '«llevá tu X al siguiente nivel»'),
    (r'\btodo lo que necesit[áa]s saber\b', '«todo lo que necesitás saber sobre»'),
    (r'\ben un mundo cada vez más\b', 'arranque de posteo genérico'),
    (r'¿\s*list[oa]s?\s+para\s+(?:empezar|comenzar)\s*\?|\bempecemos\b',
     'llamada a la acción de plantilla'),
    (r'\bdescubr[íie] cómo\b', '«descubrí cómo»'),
    (r'\bmás que (?:un|una)\b[^.!?]{0,40}[,.]', 'la forma «más que un X»'),
]

# La raya al modo inglés: sin espacio de ninguno de los dos lados. En español el
# inciso abre con espacio afuera y cierra con espacio afuera, así que `\S—\S` es
# calco directo y no puede confundirse con un inciso bien escrito.
RAYA_INGLESA = re.compile(r'\S—\S')

# Dos rayas en una oración es lo NORMAL en español: una abre el inciso y la otra
# lo cierra. El umbral está en cuatro, que ya son dos incisos apilados.
RAYAS_POR_ORACION = 4

# Tres ítems seguidos donde el tercero cierra la cláusula. Si el tercero sigue de
# largo — «inspección, reparación y reemplazo para casas y comercios» — es una
# lista de servicios reales, no un ritmo, y marcarla es llorar lobo.
RITMO = re.compile(r'\b(\w{4,}),\s+(\w{4,})\s+[ye]\s+(\w{4,})\s*[.!?,;:\n]')

# Prueba inventada, con el número escrito como se escribe en español: el punto
# separa los miles y la coma es el decimal. El patrón en inglés lee `10,000` y
# acá no vería absolutamente nada.
PRUEBA = re.compile(
    r'(?:\+\s?)?(?:\d{1,3}(?:\.\d{3})+|\d+)(?:,\d+)?\s*\+?\s*'
    r'(?:(?:felices|satisfechos|satisfechas|activos|activas|verificados|contentos)\s+)?'
    r'(?:\w+\s+){0,1}'
    r'(?:usuarios?|clientes?|alumnos?|estudiantes?|equipos?|miembros?|empresas?'
    r'|negocios?|propietarios?|suscriptores?|pacientes?|lectores?|marcas?'
    r'|profesionales?|personas?|familias?|emprendedores?)'
    r'(?!\w)', re.I)

SUPERLATIVOS = [
    (r'\b(?:los|las) más \w+\b', 'superlativo que nadie puede chequear'),
    (r'\bl[íi]der(?:es)? (?:en|del|de la)\b', '«líderes en»'),
    (r'\bla mejor opción\b|\bel más completo\b|\bla más completa\b',
     'superlativo que nadie puede chequear'),
    (r'\bnúmero uno (?:en|del)\b', '«número uno en»'),
]


def _ventanas(texto, ancho=220):
    """Las oraciones del texto, cortadas en ventanas de ancho fijo.

    El límite hace trabajo real. El texto de interfaz no tiene puntos: los ítems
    de menú, los botones y las etiquetas corren todos juntos, así que un corte
    ingenuo de oraciones trata la página entera como una sola oración y las
    reglas de densidad disparan sobre todo. Un linter que llora lobo se apaga.
    """
    for oracion in re.split(r'(?<=[.!?])\s+|\n', texto):
        for i in range(0, max(1, len(oracion)), ancho):
            yield oracion[i:i + ancho]


def auditar(texto):
    hallazgos = {'slop': dict((g, []) for g in GRUPOS_SLOP),
                 'registro': dict((g, []) for g in GRUPOS_REGISTRO)}
    slop = hallazgos['slop']
    bajo = texto.lower()

    for palabra in LEXICO_RAIZ:
        n = len(re.findall(_patron_raiz(palabra), bajo))
        if n:
            slop['lexico'].append((palabra, n))
    for frase in LEXICO_EXACTO:
        n = len(re.findall(r'(?<!\w)%s(?!\w)' % re.escape(frase), bajo))
        if n:
            slop['lexico'].append((frase, n))

    for patron, etiqueta in CONSTRUCCIONES:
        n = len(re.findall(patron, bajo))
        if n:
            slop['construcciones'].append((etiqueta, n))

    for ventana in _ventanas(texto):
        if RAYA_INGLESA.search(ventana):
            slop['cadencia'].append(('raya al modo inglés, sin espacios',
                                     ventana[:70].strip()))
            break
    for ventana in _ventanas(texto):
        if ventana.count('—') >= RAYAS_POR_ORACION:
            slop['cadencia'].append(('%d rayas en una misma oración' % ventana.count('—'),
                                     ventana[:70].strip()))
            break
    for m in RITMO.finditer(texto):
        slop['ritmo'].append(('ritmo de tres', m.group(0)[:60].strip()))

    for m in PRUEBA.finditer(texto):
        slop['venta'].append(m.group(0).strip())
    for patron, etiqueta in SUPERLATIVOS:
        for m in re.finditer(patron, bajo):
            slop['venta'].append('%s: «%s»' % (etiqueta, m.group(0)))

    _auditar_registro(texto, hallazgos['registro'])
    return hallazgos


# ── eje 2: registro rioplatense ──────────────────────────────────────────────

# `te` NO está acá: es el pronombre del voseo. `vos te vas` es rioplatense
# perfecto, y meterlo en la lista dejaría marcado casi todo texto bien escrito.
# Las terminaciones son solo `-áis` y `-éis`. `-ís` tampoco entra, porque
# `vivís`, `salís` y `escribís` son voseo antes que vosotros.
PRONOMBRES = [
    (r'(?<!\w)tú(?!\w)', '«tú» en vez de «vos»'),
    (r'(?<!\w)ti(?!\w)', '«ti» en vez de «vos»'),
    (r'(?<!\w)contigo(?!\w)', '«contigo» en vez de «con vos»'),
    (r'(?<!\w)vosotr[oa]s(?!\w)', '«vosotros»'),
    (r'(?<!\w)os(?!\w)', '«os» como pronombre'),
    (r'(?<!\w)vuestr[oa]s?(?!\w)', '«vuestro»'),
    (r'\w+[áé]is(?!\w)', 'conjugación de vosotros'),
]

# Imperativos de tuteo con el pronombre pegado. El enclítico y la tilde en la
# raíz no dejan lugar a dudas: `regístrate` es tuteo, `registrate` es voseo, y
# la única diferencia entre los dos es el acento escrito.
ENCLITICOS_TUTEO = [
    'regístrate', 'suscríbete', 'únete', 'apúntate', 'inscríbete',
    'contáctanos', 'escríbenos', 'llámanos', 'síguenos', 'conócenos',
    'pruébalo', 'pruébala', 'descúbrelo', 'descúbrela', 'míralo', 'míranos',
    'compártelo', 'descárgalo', 'inténtalo', 'hazlo', 'elígelo', 'cuéntame',
    'cuéntanos', 'dime', 'dinos', 'úsalo', 'llévatelo', 'agéndalo',
]

# Verbos de copy en tuteo. Solo se marcan en posición de llamada a la acción,
# porque `prueba` y `conoce` son también tercera persona del indicativo y
# sustantivo: «el equipo conoce el rubro», «la prueba de carga».
VERBOS_CTA = [
    'descubre', 'prueba', 'conoce', 'elige', 'empieza', 'comienza', 'solicita',
    'agenda', 'reserva', 'descarga', 'contacta', 'aprende', 'consigue',
    'obtén', 'compra', 'explora', 'accede', 'ingresa', 'calcula', 'mira',
    'suscribe', 'registra', 'comparte', 'encuentra', 'suma',
]

# Lo que sigue al verbo cuando NO es una llamada a la acción: `prueba de carga`,
# `descarga del informe`. Un sustantivo arrastra su complemento; un botón no.
TRAS_SUSTANTIVO = ('de', 'del', 'que', 'para', 'en', 'con', 'por')

# Largo máximo de un renglón para considerarlo posición de botón o título. Una
# oración corrida que arranca con `Conoce` es tercera persona, no un botón.
LARGO_CTA = 60

PENINSULAR = [
    (r'(?<!\w)ordenador(?:es)?(?!\w)', '«ordenador» por «computadora»'),
    # Con determinante: `el móvil` es el teléfono, pero `app móvil` y `unidad
    # móvil` son de uso corriente acá y no son tell de nada.
    (r'(?<!\w)(?:el|un|los|unos|mi|tu|su) móvil(?:es)?(?!\w)', '«móvil» por «celular»'),
    (r'(?<!\w)coger(?!\w)', '«coger» por «agarrar» o «tomar»'),
    (r'(?<!\w)zumo(?!\w)', '«zumo» por «jugo»'),
    (r'(?<!\w)gafas(?!\w)', '«gafas» por «lentes» o «anteojos»'),
    (r'(?<!\w)aparcar(?!\w)', '«aparcar» por «estacionar»'),
    (r'(?<!\w)chaval(?:es)?(?!\w)', '«chaval»'),
    # `vale` solo como muletilla: arranca la oración y cierra con coma o punto.
    # `¿cuánto vale?` y `vale la pena` son español de acá y no se tocan.
    (r'(?:^|(?<=[.!?])\s+)vale\s*[,.]', '«vale» como muletilla'),
]


def _auditar_registro(texto, registro):
    bajo = texto.lower()

    for patron, etiqueta in PRONOMBRES:
        n = len(re.findall(patron, bajo))
        if n:
            registro['pronombres'].append((etiqueta, n))

    for forma in ENCLITICOS_TUTEO:
        n = len(re.findall(r'(?<!\w)%s(?!\w)' % re.escape(forma), bajo))
        if n:
            registro['imperativos'].append(('%s (enclítico de tuteo)' % forma, n))

    for renglon in bajo.split('\n'):
        renglon = renglon.strip()
        if not renglon or len(renglon) > LARGO_CTA:
            continue
        palabras = re.findall(r'[\wáéíóúñü]+', renglon)
        if not palabras or palabras[0] not in VERBOS_CTA:
            continue
        if len(palabras) > 1 and palabras[1] in TRAS_SUSTANTIVO:
            continue                      # `prueba de carga`: sustantivo, no botón
        registro['imperativos'].append(
            ('%s (imperativo de tuteo en posición de botón)' % palabras[0], 1))

    for patron, etiqueta in PENINSULAR:
        n = len(re.findall(patron, bajo, re.M))
        if n:
            registro['lexico_peninsular'].append((etiqueta, n))


# ── puntaje y reporte ────────────────────────────────────────────────────────

TITULOS = {
    'lexico': 'léxico de IA',
    'construcciones': 'construcciones de IA',
    'cadencia': 'cadencia de puntuación',
    'ritmo': 'ritmo de tres',
    'venta': 'venta y prueba inventada',
    'pronombres': 'pronombres de tuteo',
    'imperativos': 'imperativos que no son voseo',
    'lexico_peninsular': 'léxico peninsular',
}


def puntuar(hallazgos, permitir_prueba=False):
    """Los dos puntajes. Un grupo tocado descuenta un punto, tenga uno o veinte
    aciertos: el arreglo es el mismo trabajo."""
    pesos = dict((g, 1) for g in GRUPOS_SLOP)
    if permitir_prueba:
        # La única regla que un regex no puede juzgar: ve un número al lado de un
        # sustantivo, no si lo podés respaldar. Sigue imprimiendo los aciertos.
        pesos['venta'] = 0
    slop = max(0, 5 - sum(pesos[g] for g in GRUPOS_SLOP if hallazgos['slop'][g]))
    registro = max(0, 3 - sum(1 for g in GRUPOS_REGISTRO if hallazgos['registro'][g]))
    return slop, registro


def _imprimir_grupo(grupo, aciertos):
    print('  %s:' % TITULOS[grupo])
    for item in aciertos[:8]:
        if isinstance(item, tuple):
            print('    · %s%s' % (item[0], '  (%s)' % item[1] if len(item) > 1 else ''))
        else:
            print('    · %s' % item)
    if len(aciertos) > 8:
        print('    · …y %d más' % (len(aciertos) - 8))


def reportar(hallazgos, permitir_prueba=False, con_registro=True):
    slop, registro = puntuar(hallazgos, permitir_prueba)

    print('── slop')
    for grupo in GRUPOS_SLOP:
        if hallazgos['slop'][grupo]:
            _imprimir_grupo(grupo, hallazgos['slop'][grupo])
    print('\n  slop %d/5  %s' % (slop, 'limpio' if slop == 5 else 'necesita reescritura'))

    if not con_registro:
        return slop == 5

    print('\n── registro rioplatense')
    for grupo in GRUPOS_REGISTRO:
        if hallazgos['registro'][grupo]:
            _imprimir_grupo(grupo, hallazgos['registro'][grupo])
    print('\n  registro %d/3  %s' % (registro,
                                     'de acá' if registro == 3 else 'no suena de acá'))
    return slop == 5 and registro == 3


def leer_utf8(ruta):
    """Lee siempre como UTF-8, diga lo que diga el locale de la máquina.

    `open()` sin `encoding=` usa el del sistema. Un texto en UTF-8 leído como
    cp1252 convierte cada tilde en mojibake, y entonces `regístrate` deja de
    matchear y el eje de registro queda mudo. Un gate que aprueba porque no
    supo leer es peor que no tener gate.
    """
    return open(ruta, encoding='utf-8', errors='replace').read()


USO = """dino — caza señales de IA y deslices de registro en español rioplatense

  python3 dino.py ARCHIVO.md
  python3 dino.py pagina.html [--vista ID]
  python3 dino.py --texto "un borrador pegado acá"

  --sin-registro     apaga el eje de registro (público panhispánico)
  --permitir-prueba  la regla de venta pasa a aviso: imprime pero no descuenta
  --markdown         fuerza el modo markdown
"""


def main(argv):
    if not argv:
        sys.stderr.write(USO)
        return 2

    permitir_prueba = '--permitir-prueba' in argv
    con_registro = '--sin-registro' not in argv
    como_md = '--markdown' in argv
    vista = None
    if '--vista' in argv:
        vista = argv[argv.index('--vista') + 1]
        argv = [a for a in argv if a != vista]
    argv = [a for a in argv
            if a not in ('--permitir-prueba', '--sin-registro', '--markdown', '--vista')]

    if argv and argv[0] == '--texto':
        texto = ' '.join(argv[1:])
        if como_md:
            texto = prosa_markdown(texto)
        else:
            texto = normalizar(texto)
    elif argv:
        try:
            crudo = leer_utf8(argv[0])
        except (IOError, OSError) as e:
            sys.stderr.write('dino: no pude leer %s: %s\n' % (argv[0], e.strerror))
            return 2
        if argv[0].endswith('.md') or como_md:
            texto = prosa_markdown(crudo)
        else:
            if vista:
                inicio = crudo.find('id="%s"' % vista)
                if inicio < 0:
                    sys.stderr.write('dino: no hay ningún elemento con id "%s"\n' % vista)
                    return 2
                sigue = crudo.find('id="view-', inicio + 1)
                crudo = crudo[inicio:sigue if sigue > 0 else len(crudo)]
            texto = texto_visible(crudo)
    else:
        sys.stderr.write(USO)
        return 2

    # Nada que puntuar es una falla, nunca un aprobado.
    if not texto.split():
        sys.stderr.write('dino: no hay texto visible para puntuar — entrada vacía\n')
        return 2

    print('%d palabras de texto visible\n' % len(texto.split()))
    return 0 if reportar(auditar(texto), permitir_prueba, con_registro) else 1


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(errors='replace')
    except (AttributeError, ValueError):
        pass
    sys.exit(main(sys.argv[1:]))
