# De dónde sale cada número

Todo número de esta página sale de una corrida real. `corpus/frecuencias.json` tiene la
medición completa y `corpus/calibrar.py` la vuelve a hacer desde cero.

## Sobre qué se midió

| | |
|---|---|
| Corpus humano | 200 notas de la diaria, 72.615 palabras, todas publicadas antes de 2023 |
| Corpus de IA | 15 textos generados con el CLI `claude`, 10.471 palabras, tres géneros |
| Fecha de la corrida | 16 de setiembre de 2026 |

La fecha de corte de 2023 es el atajo que hace humano al corpus humano: lo publicado antes
de que ChatGPT existiera lo escribió una persona, sin que haya que confiar en nadie.

Los dos corpus se extraen igual: solo renglones de doce palabras o más. El de IA trae
títulos y botones y el humano viene de notas donde eso ya quedó afuera, así que sin
emparejarlo la medición compararía maquetación contra prosa. El costo es explícito: las
reglas que viven en el copy corto no se calibran, y se sostienen con los tests.

Al repo no sube texto ajeno. Sube `frecuencias.json`, que son conteos. La caché está en
`.gitignore` y `construir.py` la rehace desde `fuentes.json`.

## El criterio

Un patrón entra al scorer si cumple las tres:

| Umbral | Valor | Por qué |
|---|---|---|
| Ratio mínimo | 5x más frecuente por cada 10.000 palabras en el corpus de IA | abajo de eso, lo escriben también las personas |
| Techo de falsos positivos | 2% de los documentos humanos | una regla que marca uno de cada cincuenta textos honestos se apaga sola |
| Mínimo de apariciones | 10 en el corpus de IA | abajo de eso la muestra no dice nada, ni a favor ni en contra |

## El resultado honesto de esta corrida

**Ningún patrón quedó admitido.** No porque el catálogo esté mal, sino por algo que conviene
decir con todas las letras:

> El corpus de IA, generado con el CLI `claude` en 2026, casi no contiene los tells que el
> catálogo busca. En 10.471 palabras, `no solo X, sino Y` aparece una vez y `potenciar`,
> ninguna.

Un modelo de primera línea en 2026, con un prompt neutro y en español rioplatense, no
escribe el slop contra el que se construyó el catálogo inglés en 2024. El criterio de ratio
no se puede satisfacer contra este corpus, y forzarlo bajando el mínimo sería exactamente la
clase de número inventado que este proyecto dice no hacer.

Así que el catálogo queda **sin evidencia de ratio** y con el estado anotado en cada regla.
Sirve igual para texto salido de generadores más viejos, más baratos o peor prompteados,
que es de donde viene la mayoría del slop que uno se cruza. Pero eso es una afirmación sin
medir, y va dicha como tal.

## Lo que el corpus sí demostró

El otro criterio, el de no llorar lobo, hizo todo el trabajo y dejó recibos:

| Corrida | Textos humanos que puntúan 5/5 |
|---|---|
| Catálogo inicial | 83,1% |
| Después de lo que enseñó el corpus | **96,0%** |

Cinco reglas cambiaron por evidencia, y ninguna por conveniencia:

**`ritmo de tres` — marcaba el 7,8% de la prensa humana.** Disparaba con
~~políticos, empresarios y periodistas~~, ~~Francia, España e Italia~~ y
~~2010, 2011 y 2012~~. En español `X, Y y Z` es simplemente cómo se enumeran tres cosas. La
regla ahora exige que la enumeración abra la oración, que es donde vive el tricolon de copy,
y que los ítems arranquen con letra. Bajó a 0%.

**`prueba inventada` — marcaba el 3,5%.** Disparaba con ~~concurrían unos 250 estudiantes~~
y ~~trabajaban 104 personas~~: un diario cuenta gente todo el tiempo. Ahora el número tiene
que venir con marco de venta — un signo `+`, un adjetivo de campaña, un posesivo, o un verbo
que diga que esa gente ya eligió.

**`superlativo` — marcaba el 2,1%, y los tres aciertos eran `los más de`.** O sea
`los más de 5.000 socios`, que es una cantidad. El patrón `los más \w+` la leía como si
fuera un superlativo. Ahora es una lista cerrada de adjetivos de venta.

**`impulsar` — marcaba el 2,0%.** `impulso` e `impulsó` son palabras corrientes en prosa
política. Pasó a candidato.

**El sufijo `-ario` del stemmer.** Hacía que `revolucionar` cazara `revolucionarias`, que es
un adjetivo común. Salió.

## Rechazados, con su número al lado

Esta sección es la que hace defendible al catálogo. Son patrones que yo propuse y que la
medición volteó.

| Patrón | Medición | Veredicto |
|---|---|---|
| dos puntos por encima de un piso | toca el 49,5% de los textos humanos | rechazado, techo 2% |
| punto y coma | toca el 20,5% | rechazado, techo 2% |

El de los dos puntos **estaba en el scorer** cuando empecé. Lo había portado del umbral que
el linter inglés usa para el punto y coma, sin ningún número que lo respaldara, y disparó
sobre el primer documento de verdad que escribí. Volvió a la lista de candidatos.

Los 27 candidatos de `corpus/candidatos.py` que no aparecen acá quedaron sin evidencia: la
muestra de IA es demasiado chica para decir algo sobre ellos.

## Sobre qué se para esto

[SlopMonster](https://github.com/ItsssssJack/SlopMonster), MIT, de donde salen la estructura
del loop, la idea del puntaje que corta el build y la disciplina de no inventar prueba. Su
catálogo inglés fue el punto de partida de los candidatos, nunca del contenido: cada patrón
tuvo que ganarse el lugar contra el corpus en español.

El catálogo inglés que hay detrás de aquel es el de Wikipedia, *Signs of AI writing*, del
WikiProject AI Cleanup.

## Pendiente

**Falta una fuente argentina.** El corpus v1 es uruguayo. Página/12 no publica sitemap
general — 404 en `sitemap.xml` y en `sitemap-index.xml` al 16 de setiembre de 2026 — y no
quise adivinar URLs. El rioplatense del corpus es, por ahora, el de este lado del charco.

**Falta copy comercial humano.** El corpus humano es periodismo. Para los grupos de
marketing no hay género equivalente del otro lado, así que su evidencia se apoya solo en el
techo de falsos positivos. La salida sería sumar landings rioplatenses anteriores a 2023
desde Wayback.

**Falta un corpus de IA que tenga slop.** Es el hallazgo de arriba y es el trabajo más
importante que queda.
