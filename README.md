# dino

**Un linter que caza el acento de IA en textos en español rioplatense.**

La escritura de IA tiene olor. `potenciar`, `robusto`, `de vanguardia`,
`llevá tu negocio al siguiente nivel`. El lector ya lo detecta, y una página que huele a eso
es una página que deja de creerte.

En inglés esto está resuelto. [SlopMonster](https://github.com/ItsssssJack/SlopMonster) lo
hace bien, y su propio README dice dónde termina: *"The catalogue is English only. Copy in
another language scores 5/5 because the scorer cannot read it, not because it is clean."*
Este proyecto ocupa ese hueco.

Y le agrega un eje que en inglés no hace falta.

## Dos ejes, porque son dos fallas distintas

```
── slop
  construcciones de IA:
    · «llevá tu X al siguiente nivel»  (1)
  venta y prueba inventada:
    · 10.000 clientes felices

  slop 3/5  necesita reescritura

── registro rioplatense
  imperativos que no son voseo:
    · regístrate (enclítico de tuteo)  (1)

  registro 2/3  no suena de acá
```

Un texto puede ser humanísimo y estar escrito en peninsular. Otro puede estar en voseo
perfecto y ser slop puro. Se arreglan con ediciones distintas, así que puntúan aparte.
Abajo de 5/5 o de 3/3 el comando sale con código distinto de cero, y un build puede frenar
ahí.

## No es el catálogo inglés traducido

Cuatro cosas se rompen al portarlo, y cada una obligó a rediseñar la regla.

**El tell más ruidoso del copy en español no es una palabra, es un imperativo.** Todo lo que
genera un modelo dice `Descubre nuestra plataforma`, `Prueba gratis`, `Regístrate`. Pero
`descubre` y `prueba` son también tercera persona del indicativo y sustantivo:
*el equipo conoce el rubro*, *la prueba de carga*. Un patrón ingenuo marca prosa impecable,
así que este caza solo donde es inequívoco — el enclítico, la tilde que separa `regístrate`
de `registrate`, y el verbo encabezando un renglón corto.

**La raya es puntuación legítima en español, y el inciso lleva dos.** El linter inglés
cuenta guiones largos; acá eso marcaría todo texto bien puntuado. Lo que sí es calco es la
raya sin espacios de ningún lado.

**El español no usa coma de Oxford.** De las dos formas del ritmo de tres que busca el
linter inglés, la primera no dispararía nunca.

**Los números se escriben al revés.** El patrón inglés lee `10,000 users`. Acá el punto
separa los miles y la coma es el decimal, así que sobre `10.000 clientes` no ve nada.

## Recibos, no promesas

El catálogo no se escribió de memoria. Se midió contra dos corpus: 592 notas anteriores a
2023 — 294 de la diaria y 298 de eldiarioAR, humanas por construcción porque ChatGPT todavía
no existía — y 15 textos generados con el CLI `claude`. En total 355.386 palabras de prosa
rioplatense de las dos orillas.

Un patrón entra al scorer si aparece 5 veces más por cada 10.000 palabras en texto de IA que
en humano, y si marca menos del 0,5% de los textos humanos. Ese 0,5% no es un número
inventado: sale de dividir el piso que se le pide al scorer entero por el tamaño del
catálogo. Los 48 patrones que quedaron cumplen; el peor marca el 0,34%.

**El corpus volteó once entradas, arregló tres patrones rotos y corrigió dos errores de
método míos.**

| | textos humanos que el scorer deja limpios |
|---|---|
| Catálogo inicial | 75,8% |
| Después de lo que enseñó el corpus | **94,3%** |

Lo más fuerte que apareció: **la forma insignia del catálogo inglés no transfiere**.
`no solo X, sino Y` es la construcción más ruidosa del inglés y la primera que cualquiera
traduciría. En español marcaba el **8,6%** de la prensa humana, con frases como
~~advertido no solo por organizaciones ecologistas sino por organismos como el BCE~~. Es un
correlativo gramatical corriente, no un tic de marketing. El inglés no obliga a esa
correlación y por eso ahí llama la atención; el español sí, y por eso acá no dice nada.

Otras once entradas resultaron español corriente: ~~excepcional~~, ~~en definitiva~~,
~~cuando se trata de~~, ~~el poder de~~. Y el umbral de dos puntos, que yo había portado de
una regla pensada para el punto y coma en inglés sin ningún número detrás, tocaba el 67,1%
de los textos humanos.

Todos los rechazos están publicados con su medición en
[`referencias/fuentes.md`](referencias/fuentes.md), incluidos los dos errores de método que
invalidaron mediciones que este mismo README ya había publicado.

### Lo que esta corrida NO pudo demostrar

Conviene decirlo con todas las letras, porque es lo primero que cualquiera debería preguntar.

**Ningún patrón quedó admitido por ratio.** El corpus de IA, generado con un modelo de
primera línea en 2026, casi no contiene los tells que el catálogo busca: en 10.471 palabras,
`potenciar` no aparece ninguna vez.

El catálogo sigue sirviendo para texto salido de generadores más viejos, más baratos o peor
prompteados, que es de donde viene casi todo el slop que uno se cruza. Pero eso es una
afirmación sin medir, y va dicha como tal. Bajar el mínimo para que diera sería exactamente
el número inventado que este proyecto dice no hacer.

Lo que el corpus sí demostró es lo otro, y no es poco: que ninguna de estas reglas marca
prosa rioplatense escrita por personas. Un linter que llora lobo se apaga a la semana.

## Una corrida entera

Una landing de estudio contable, de 0/5 y 2/3 a 5/5 y 3/3, con el antes, el después y el
motivo de cada cambio: [`ejemplos/estudio-contable.md`](ejemplos/estudio-contable.md).

## Arrancar

```bash
git clone git@github.com:alfonsopintos89/dino-textos.git && cd dino-textos

python3 tools/dino.py --texto "Una plataforma robusta que potencia tu negocio."
python3 tools/dino.py borrador.md
python3 tools/dino.py index.html --vista hero
python3 tools/dino.py nota.md --sin-registro          # público de toda LatAm
python3 tools/dino.py index.html --permitir-prueba    # los números son reales

python3 tools/test_dino.py                            # tocaste un regex, corré esto
```

Sin dependencias. El scorer es biblioteca estándar y anda en el Python 3.9 que trae macOS de
fábrica. `.github/workflows/dino.yml` es el gate, listo para copiar.

### Como skill de un agente

**Claude Code:** copiá esta carpeta a `~/.claude/skills/dino/` y decí `/dino` o
"sacale la IA a esto". **Otros agentes:** apuntalos a `SKILL.md`, que es markdown y no tiene
nada específico de Claude.

## Rehacer la medición

```bash
python3 corpus/construir.py --humano 200    # baja prensa pre-2023 desde el sitemap
python3 corpus/construir.py --ia 15         # genera el corpus de IA
python3 corpus/calibrar.py                  # mide y dicta veredicto
python3 corpus/verificar_falsos_positivos.py
```

`calibrar.py` **importa** `dino.py` en vez de copiar sus listas. Si tuviera su propia copia
del catálogo, las dos se separarían con el tiempo y el número publicado dejaría de describir
la herramienta que corre de verdad.

Al repo no sube texto ajeno: la caché está en `.gitignore` y lo que se versiona son los
conteos. La descarga respeta `robots.txt` y va despacio.

## La regla dura

**Nunca inventar prueba.** Ni cantidades de clientes, ni testimonios, ni puntuaciones. Si
una afirmación necesita un número que no tenés, escribí `[falta dato]` y seguí. El lift de
un número inventado es más chico que el de la especificidad real, y es el único error sin
vuelta atrás.

Y esto nunca va a prometer pasar detectores de IA. Los detectores son ruido. El objetivo es
el estómago de un lector.

## El mapa

```
SKILL.md                              el loop entero, como instrucciones para el agente
tools/dino.py                         el scorer. stdlib, un archivo, sale rojo
tools/test_dino.py                    63 tests: aciertos y falsos positivos
corpus/construir.py                   arma los dos corpus
corpus/calibrar.py                    mide las reglas y dicta veredicto
corpus/candidatos.py                  lo propuesto y lo que el corpus volteó
corpus/prompts-para-pegar.md          para generar el corpus de IA con otros modelos
corpus/verificar_falsos_positivos.py  el scorer contra el corpus humano entero
referencias/senales-ia-espanol.md     el catálogo del eje slop
referencias/registro-rioplatense.md   el catálogo del eje registro
referencias/fuentes.md                de dónde sale cada número, rechazos incluidos
ejemplos/estudio-contable.md          una corrida entera, 0/5 → 5/5
.github/workflows/dino.yml            el gate
docs/superpowers/specs/               el diseño
```

Esta página pasa su propio scorer. `python3 tools/dino.py README.md` da 5/5 y 3/3, con el
mismo catálogo y los mismos regex que puntúan tu landing. No se ablandó nada para llegar:
los especímenes están marcados como literales, en `código` o ~~tachados~~, y la prosa de
alrededor se escribió limpia como cualquier otra.

MIT, igual que el proyecto del que deriva.
