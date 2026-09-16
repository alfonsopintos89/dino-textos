# dino-textos — diseño

Fecha: 2026-09-16

> **Reemplazado.** El proyecto pasó a llamarse Textosaurio y a dar cinco puntajes del
> 1 al 10 en vez de slop /5 y registro /3. Este diseño queda como registro de cómo se
> armó el corpus y la calibración, que siguen vigentes. Lo actual está en `README.md` y
> `SKILL.md`.
Estado: implementado. Este documento es el diseño tal como se aprobó; la
implementación lo corrigió en dos puntos, y las correcciones están medidas en
`referencias/fuentes.md`:

1. El techo de falsos positivos del 2% que se declara más abajo era incompatible
   con el piso del 95% del verificador. El techo pasó a derivarse del piso y
   quedó en 0,5%.
2. El catálogo daba por hecho que `no solo X, sino Y` era la forma más ruidosa.
   El corpus la rechazó: en español es un correlativo gramatical corriente y
   marcaba el 8,6% de la prensa humana.

## Qué es

Un linter de textos en español rioplatense que caza dos cosas distintas y las puntúa por
separado: señales de que el texto lo escribió un modelo, y señales de que no lo escribió
alguien de acá.

Es un equivalente de [SlopMonster](https://github.com/ItsssssJack/SlopMonster) para el
español del Río de la Plata. SlopMonster resuelve el problema en inglés y su propio README
dice dónde termina: *"The catalogue is English only. Copy in another language scores 5/5
because the scorer cannot read it, not because it is clean."* Este proyecto ocupa ese
hueco, y le agrega un eje que el original no tiene porque en inglés no hace falta.

El objetivo no es pasar detectores de IA. Los detectores son ruido y perseguirlos empeora
la prosa. El objetivo es el estómago de un lector que este mes leyó mil párrafos de IA.

## Por qué no es una traducción

Cuatro cosas rompen al portar el catálogo inglés, y cada una obliga a rediseñar la regla:

1. **El tell más ruidoso del copy en español no es una palabra, es un imperativo.** Todo lo
   que genera un modelo dice `Descubre nuestra plataforma`, `Prueba gratis`, `Regístrate`.
   Pero `descubre` y `prueba` también son tercera persona del indicativo y sustantivo:
   *el equipo conoce el rubro*, *la prueba de que funciona*. Un patrón ingenuo marca texto
   perfectamente escrito.
2. **La raya es legítima en español.** Marca incisos y diálogo. La regla de cadencia del
   original cuenta rayas; acá hay que mirar el uso anglosajón (raya pegada a la palabra,
   sin espacios) y la densidad, no la presencia.
3. **El español no usa coma de Oxford.** De las dos formas del ritmo de tres del original,
   la primera nunca dispararía.
4. **Los números se escriben distinto.** El regex de prueba inventada del original lee
   `10,000+ users`. En español eso es `10.000` o `+5.000 clientes`, y la coma es el
   separador decimal.

## Decisiones tomadas

| Decisión | Elección |
|---|---|
| Alcance de textos | Copy de marketing y landings, contenido largo (posts, artículos, newsletters), textos de producto y docs. Mensajes personales quedan afuera. |
| Rol del dialecto | Eje propio que puntúa aparte, con voseo obligatorio. No es solo un aviso. |
| Forma de entrega | Skill de Claude Code + CLI Python + GitHub Action, como el original. |
| Paso de limpieza con modelo rival | **Descartado.** El loop es lint → reescritura → re-lint. |
| Origen del catálogo | Validado contra corpus antes de entrar al scorer. |
| Corpus humano | Prensa y blogs rioplatenses publicados antes de 2023. |

## Restricciones del entorno

- Python 3.9.6 (el del sistema en macOS). Nada de sintaxis 3.10+: sin `match`, sin
  `X | Y` en anotaciones de tipo.
- `tools/dino.py` usa solo la biblioteca estándar y es un archivo único. Copiarlo a
  cualquier lado tiene que alcanzar para que corra.
- El único CLI de IA instalado es `claude`. Los scripts de corpus lo usan; el scorer no
  usa ninguno.

## Mapa del repo

```
SKILL.md                                el loop entero como instrucciones para el agente
README.md                               qué es, cómo se usa, la evidencia de cada regla
tools/dino.py                           el scorer. stdlib, archivo único, sale rojo
tools/test_dino.py                      suite de regresión: aciertos y falsos positivos
corpus/construir.py                     arma los dos corpus
corpus/calibrar.py                      mide las reglas contra los corpus, emite veredicto
corpus/candidatos.py                    patrones propuestos que todavía no entraron
corpus/frecuencias.json                 resultado derivado de la medición (versionado)
corpus/ia/                              textos generados + manifiesto.json (versionado)
corpus/humano/fuentes.json              URLs, fechas de publicación, notas de uso
corpus/humano/cache/                    texto bajado (en .gitignore, nunca se publica)
corpus/verificar_falsos_positivos.py    corre el scorer sobre todo el corpus humano
referencias/senales-ia-espanol.md       el catálogo del eje slop, con su evidencia
referencias/registro-rioplatense.md     el catálogo del eje registro
referencias/fuentes.md                  de dónde sale cada cosa, incluidos los rechazos
ejemplos/                               corridas reales, antes → después
.github/workflows/dino.yml              el gate
```

## Eje 1 — slop, 5 puntos

Un punto por grupo. Cada grupo que tenga al menos un acierto descuenta su punto.

### 1. Léxico de IA

Dos listas, como el original, por la misma razón.

**Por raíz**, para las palabras que no tienen uso honesto en este registro: `potenciar`,
`optimizar`, `revolucionar`, `transformador`, `robusto`, `holístico`, `sinergia`,
`empoderar`, `desbloquear`, `inigualable`, `vanguardia`, `sin precedentes`, `meticuloso`,
`impulsar`, `maximizar`.

**Exactas**, para las que sí tienen un uso literal cotidiano: `viaje`, `panorama`,
`ámbito`, `clave`, `integral`, `crucial`, `fundamental`, `experiencia única`,
`a medida`, `de última generación`, `en constante evolución`.

La lematización española es más dura que la inglesa: hay género, número y conjugación.
`potenciar` tiene que cazar `potencia`, `potencian`, `potenciado`, `potenciada`,
`potenciando`, `potenciamos`. El `(ed|ing|ly|e)$` del original no sirve. Hace falta un
stemmer chico y específico: cortar la terminación verbal o de género/número conocida y
permitir el conjunto de sufijos de vuelta, con el mismo cuidado que tiene el original con
la alternativa vacía.

### 2. Construcciones de IA

Formas, no palabras. Es el grupo que más pesa, porque un texto puede pasar el chequeo de
léxico y seguir leyéndose como escrito por una máquina.

Candidatos iniciales: `no solo X, sino (también) Y`, `no se trata de X, es Y`,
`más que un X`, `ahí es donde entra X`, `ya sea que X o Y`, `decile adiós a`,
`imaginá/imagina un`, `¿El resultado?` y demás preguntas que el propio texto contesta,
`en conclusión`, `en resumen`, `cuando se trata de`, `cabe destacar`,
`es importante señalar`, `vale la pena mencionar`, `la clave está en`, `la verdad es que`,
`te ayuda a`, `puede ayudarte a`, `podría potencialmente`, `llevá tu X al siguiente nivel`,
`todo lo que necesitás saber sobre`, `en el mundo actual`, `en la era digital`.

Se chequean las dos personas gramaticales de cada forma que las tenga. Escribir en tuteo
no es un disfraz: es lo que el modelo emite por defecto, y el eje 2 lo va a marcar aparte.

### 3. Cadencia de puntuación

- **Raya al modo inglés**: raya pegada a la palabra, sin espacios a los lados. En español
  el inciso lleva espacios afuera y no adentro; la forma sin espacios es un calco directo.
- **Densidad de rayas**: dos o más en una misma oración, con la misma ventana de 220
  caracteres que usa el original y por el mismo motivo — el texto de interfaz no tiene
  puntos, y un corte ingenuo de oraciones convierte una página entera en una sola oración
  y hace que la regla dispare sobre todo.
- **Dos puntos en exceso**, con piso escalado al largo del texto, como el original hace
  con los punto y coma.

### 4. Ritmo de tres

`rápido, simple y confiable`. Tres ítems seguidos son un ritmo, no un argumento.

El patrón se rediseña entero: sin coma de Oxford, la única forma posible es
`X, Y y Z`. Para no marcar listas de servicios reales — *"inspección, reparación y
reemplazo para casas y comercios"* es lo que hace un techista y tiene que puntuar limpio —
la regla exige que los tres ítems sean palabras sueltas o sintagmas cortos y que el
tercero cierre la cláusula.

### 5. Venta y prueba inventada

- **Prueba inventada**: número pegado a un sustantivo de persona, con el formato de número
  español (`10.000`, `+5.000`, `10.000+`), y la coma tratada como decimal, no como
  separador de miles. Deliberadamente amplio: un falso positivo cuesta diez segundos, un
  falso negativo es una afirmación que no podés respaldar.
- **Superlativos no verificables**: `los más confiables`, `líderes en`, `la mejor opción`,
  `el más completo`.

**La regla dura, que no es negociable:** nunca inventar prueba. Ni cantidades de clientes,
ni testimonios, ni puntuaciones. Si una afirmación necesita un número que no tenés, va
`[falta dato]` y se sigue.

## Eje 2 — registro rioplatense, 3 puntos

### 1. Pronombres y morfología de tuteo o voseo peninsular

`tú`, `te`, `ti`, `contigo`, `tuyo`, `vosotros`, `os`, `vuestro`, y las terminaciones
`-áis`, `-éis`, `-ís` de segunda persona del plural. Inequívoco, barato y sin falsos
positivos, salvo dentro de citas — que se resuelve excluyendo lo que esté entrecomillado.

### 2. Imperativos que no son voseo

El problema difícil. Se caza **solo donde es inequívoco**, por tres vías:

1. **Enclíticos de tuteo**: `regístrate`, `pruébalo`, `descúbrelo`, `contáctanos`,
   `suscríbete`, `únete`. El pronombre pegado no deja lugar a dudas.
2. **La tilde**: `regístrate` es tuteo, `registrate` es voseo. La forma acentuada en la
   antepenúltima sílaba no existe en el imperativo voseante.
3. **Posición de llamada a la acción**: un verbo de una lista cerrada de copy
   (`descubre`, `prueba`, `conoce`, `elige`, `empieza`, `comienza`, `solicita`,
   `agenda`, `reserva`, `descarga`) cuando aparece dentro de
   un `<button>`, un `<a>`, un encabezado, o una línea corta suelta.

Fuera de esos tres contextos no marca nada. Perder un acierto es barato; llorar lobo hace
que apagues el linter, y entonces no queda nada.

### 3. Léxico peninsular

`ordenador`, `móvil`, `vale`, `coger`, `zumo`, `gafas`, `conducir`, `aparcar`, `billete`,
`piso` (en el sentido de vivienda), `chaval`, `ahora mismo`.

`aquí` no entra como regla binaria: se usa en el Río de la Plata, aunque menos que `acá`.
Queda como candidato a medir por densidad, y entra solo si el corpus lo respalda.

## El CLI

```
python3 tools/dino.py ARCHIVO
python3 tools/dino.py --texto "un borrador pegado acá"
```

| Opción | Qué hace |
|---|---|
| `--texto TEXTO` | puntúa el texto que le pasás en vez de un archivo |
| `--markdown` | fuerza el modo markdown para entrada que no termina en `.md` |
| `--vista ID` | en un HTML, puntúa solo el elemento con ese `id` |
| `--sin-registro` | apaga el eje 2, para texto dirigido a público panhispánico |
| `--permitir-prueba` | la regla 5 pasa a aviso: imprime los aciertos pero no descuenta |

Entradas: HTML (se puntúa solo lo que un visitante ve, con `<script>` y `<style>` y las
etiquetas afuera), Markdown (fuera los bloques de código, el código en línea, el texto
tachado y el alt de las imágenes, porque un literal no es copy) y texto plano.

Salida, con los dos ejes separados:

```
842 palabras de texto visible

── slop
  construcciones de IA:
    · «no solo X, sino Y»  (2)
  ritmo de tres:
    · rápido, simple y confiable

  slop 3/5  necesita reescritura

── registro rioplatense
  imperativos que no son voseo:
    · regístrate  (enclítico)
  léxico peninsular:
    · ordenador  (1)

  registro 1/3  no suena de acá
```

Códigos de salida: `0` si los dos ejes están perfectos, `1` si hay hallazgos, `2` si no
pudo leer el archivo o la entrada quedó vacía. Entrada vacía es una falla, nunca un
aprobado: una entrada vacía que puntúa limpio reporta slop como limpio justo en el momento
en que el pipeline se rompió.

## El pipeline de corpus

### Corpus IA

60 textos generados con el CLI `claude`, 20 por género: landing, post largo, docs y UX.
Los prompts son neutros — *"escribí una landing para una inmobiliaria en Montevideo"* — y
**nunca** le piden evitar sonar a IA: el punto es medir el default. Se versiona en
`corpus/ia/`, con un `manifiesto.json` que guarda por texto el prompt, el género, el
modelo y la fecha. Es contenido generado, así que no hay derechos de terceros.

### Corpus humano

Prensa y blogs rioplatenses con fecha de publicación anterior al 2023-01-01. Esa fecha es
el atajo: lo publicado antes de que ChatGPT existiera es humano por construcción.

Meta: al menos 200 documentos y 200.000 palabras. `corpus/construir.py` baja las URLs de
`fuentes.json` con `urllib`, extrae el texto visible reutilizando la misma función que usa
el scorer, y lo guarda en `corpus/humano/cache/`, que está en `.gitignore`.

**Al repo no entra texto ajeno.** Se versiona `corpus/frecuencias.json`, que son conteos,
y un puñado de oraciones sueltas como especímenes de test, bajo cita y atribuidas. El
script es reproducible: cualquiera puede rehacer la medición desde `fuentes.json`.

La descarga respeta `robots.txt`, va a ritmo lento y toca solo páginas de acceso público.

### Criterio de admisión

`corpus/calibrar.py` **importa `tools/dino.py`** y mide sus reglas reales contra los dos
corpus, más los patrones propuestos en `corpus/candidatos.py`. Importar el scorer en vez
de copiar sus listas es lo que evita que la medición y la herramienta se separen con el
tiempo.

Cada patrón termina en uno de tres estados:

- **Admitido**: aparece al menos 5 veces más por cada 10.000 palabras en el corpus IA que
  en el humano, dispara en menos del 2% de los documentos humanos, y tiene al menos 10
  apariciones en el corpus IA.
- **Sin evidencia**: menos de 10 apariciones en el corpus IA. La muestra no alcanza para
  decir nada. Se queda en `candidatos.py`.
- **Rechazado**: no llega al 5× o dispara sobre más del 2% del texto humano.

Los dos umbrales quedan escritos en `referencias/fuentes.md` junto con la medición que los
justifica. **Lo rechazado no se borra**: va a una sección propia con su número al lado. Esa
sección es lo que hace defendible al catálogo, y es exactamente lo que ningún humanizador
existente puede mostrar.

Un patrón admitido pasa a `tools/dino.py` a mano, con su número anotado en las referencias.

## Tests

`tools/test_dino.py`, con `unittest` de la biblioteca estándar. **Ninguna regla entra sin
dos tests**: un espécimen que la dispara y un texto humano parecido que no la dispara. El
segundo es el que importa; es la diferencia entre un linter que usás y uno que apagás.

`corpus/verificar_falsos_positivos.py` corre el scorer sobre el corpus humano completo y
exige que al menos el 95% de los documentos den `slop 5/5`. Si no llega, la regla está mal
calibrada, no el corpus. Va aparte de la suite unitaria porque necesita la caché
descargada, que no está versionada.

Dos detalles de implementación que ya sabemos que muerden:

- **Lectura UTF-8 explícita.** `open()` sin `encoding=` usa el locale de la máquina. Un
  gate que aprueba porque no sabe leer es peor que no tener gate.
- **La normalización no puede quitar tildes.** Es contra el instinto: normalizar texto
  suele incluir plegar acentos, y acá la tilde es justo lo que separa `regístrate` de
  `registrate`. Se pliegan comillas tipográficas, espacios duros y guiones. Las tildes
  nunca.

El `README.md` y las referencias pasan su propio scorer, con la técnica del original: los
especímenes van en `código` o tachados, para que un literal citado no cuente como copy.

## El gate de CI

`.github/workflows/dino.yml` corre `tools/test_dino.py` y después el scorer sobre los
`.md` modificados en el push. Sin dependencias que instalar: solo Python.

## SKILL.md y el loop

```
1. LINT        python3 tools/dino.py texto.md      dos puntajes, sale rojo
2. REESCRIBIR  tres pases
3. RE-LINT     el linter tiene la primera y la última palabra
```

El linter cierra el loop porque el linter es honesto y el modelo es persuasivo.

Los tres pases de reescritura:

1. **Léxico.** Cada palabra marcada se cambia por una más llana, no por un sinónimo más
   pomposo de la misma idea.
2. **Formas.** `no solo X, sino Y` es la más ruidosa. También el reflejo del ritmo de tres,
   los amontonamientos de rayas, las preguntas que el texto se contesta solo, el párrafo
   de cierre que nadie pidió y la negrita al principio de cada viñeta.
3. **Poné a alguien de acá adentro.** Sacar los tells deja texto limpio y muerto. Voseo.
   Una cifra concreta por afirmación, sacada del texto original y de ningún otro lado.
   Largos de oración que varíen fuerte. Una cosa que un escritor prolijo habría cortado.

Salida del skill: el texto reescrito completo primero, después `▎ qué cambié` con cinco
líneas como máximo, cada una nombrando el tell y el arreglo. Nunca análisis solo. El
significado del autor se conserva exacto: sacar el slop no es reescribir el argumento.

## Fuera de alcance

- El paso de limpieza con un modelo de otra familia. Descartado por decisión explícita: el
  único CLI instalado es `claude` y el loop de tres pasos alcanza.
- Perfiles de registro configurables (neutro, peninsular). El usuario escribe rioplatense.
- Interfaz web. El núcleo es CLI y skill.
- Mensajes personales y chat como género de entrada.
- Cualquier promesa de pasar detectores de IA. No es el objetivo y perseguirlo empeora la
  prosa.

## Limitaciones conocidas

**Desajuste de género entre los corpus.** El corpus humano es periodismo y blogs; el de IA
incluye copy de landing. Para los grupos 1, 2 y 3 la comparación es limpia, porque hay
género equivalente de los dos lados (posts y artículos). Para los grupos 4 y 5, que son de
marketing, no hay copy comercial humano del otro lado: su evidencia es más floja y se
apoyan sobre todo en el segundo criterio, el de no disparar sobre texto humano. Si al
calibrar salen ruidosas, la solución es sumar landings rioplatenses anteriores a 2023
desde Wayback. Queda anotado; no se construye ahora.

**El eje de registro no se valida con corpus.** Sus reglas son de morfología, no de
frecuencia: `vosotros` es peninsular por gramática, no por estadística. Se validan con los
tests de falso positivo, no con el ratio de 5×.

## Fuentes

El proyecto se para sobre SlopMonster (MIT), del que toma la estructura del loop, la idea
del puntaje que corta el build y la disciplina de no inventar prueba. El catálogo inglés
sirve de punto de partida para los candidatos, no de contenido: cada patrón tiene que
ganarse el lugar contra el corpus en español.

Licencia: MIT, igual que el proyecto del que deriva.
