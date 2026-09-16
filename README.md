# dino

**Un linter que caza el acento de IA en textos en español rioplatense.**

La escritura de IA tiene olor. `potenciar`, `robusto`, `de vanguardia`,
`no solo es una herramienta, sino un aliado`. El lector ya lo detecta, y una página que
huele a eso es una página que deja de creerte.

En inglés esto está resuelto. [SlopMonster](https://github.com/ItsssssJack/SlopMonster) lo
hace bien, y su propio README dice dónde termina: *"The catalogue is English only. Copy in
another language scores 5/5 because the scorer cannot read it, not because it is clean."*
Este proyecto ocupa ese hueco.

Y le agrega un eje que en inglés no hace falta.

## Dos ejes, porque son dos fallas distintas

```
── slop
  construcciones de IA:
    · la forma «no solo X, sino Y»  (1)
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

El catálogo no se escribió de memoria. Se midió contra dos corpus: 200 notas de la diaria
anteriores a 2023 — humanas por construcción, porque ChatGPT todavía no existía — y 15
textos generados con el CLI `claude`.

Un patrón entra al scorer si aparece 5 veces más por cada 10.000 palabras en texto de IA que
en humano, si marca menos del 2% de los textos humanos, y si tiene al menos 10 apariciones
para que el número signifique algo.

**El corpus rechazó cinco reglas mías.**

| | textos humanos que puntúan 5/5 |
|---|---|
| Catálogo inicial | 83,1% |
| Después de lo que enseñó el corpus | **96,0%** |

`ritmo de tres` marcaba el 7,8% de la prensa humana, con cosas como
~~políticos, empresarios y periodistas~~ y ~~2010, 2011 y 2012~~: en español `X, Y y Z` es
simplemente cómo se enumeran tres cosas. `prueba inventada` marcaba el 3,5%, porque un
diario cuenta gente todo el tiempo. El umbral de dos puntos tocaba el 49,5% y lo había
portado de una regla pensada para el punto y coma en inglés, sin ningún número detrás.

Todos los rechazos están publicados con su medición en
[`referencias/fuentes.md`](referencias/fuentes.md), incluidos los que había escrito yo.

### Lo que esta corrida NO pudo demostrar

Conviene decirlo con todas las letras, porque es lo primero que cualquiera debería preguntar.

**Ningún patrón quedó admitido por ratio.** El corpus de IA, generado con un modelo de
primera línea en 2026, casi no contiene los tells que el catálogo busca: en 10.471 palabras,
`no solo X, sino Y` aparece una vez y `potenciar`, ninguna.

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

python3 tools/dino.py --texto "No solo es una web, sino una plataforma robusta."
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
tools/test_dino.py                    57 tests: aciertos y falsos positivos
corpus/construir.py                   arma los dos corpus
corpus/calibrar.py                    mide las reglas y dicta veredicto
corpus/candidatos.py                  lo propuesto que todavía no entró
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
