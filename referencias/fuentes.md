# De dónde sale cada número

Todo número de esta página sale de una corrida real. `corpus/frecuencias.json` tiene la
medición completa y `corpus/calibrar.py` la vuelve a hacer desde cero.

## Sobre qué se midió

| | |
|---|---|
| Corpus humano | 592 notas, 355.386 palabras de prosa, todas publicadas antes de 2023 |
| | 294 de la diaria (Uruguay), 298 de eldiarioAR (Argentina) |
| Corpus de IA | 15 textos generados con el CLI `claude`, 10.471 palabras, tres géneros |
| Fecha de la corrida | 16 de setiembre de 2026 |

La fecha de corte de 2023 es lo que hace humano al corpus humano: lo publicado antes de que
ChatGPT existiera lo escribió una persona, y no hay que confiar en nadie para saberlo.

Los dos corpus se extraen igual: renglones de doce palabras o más, y después se les saca la
plantilla del sitio.

## Dos errores de método que hubo que corregir

Los dos aparecieron midiendo, y los dos invalidaron números que este archivo ya había
publicado. Van acá porque un catálogo que esconde sus vueltas atrás no se puede auditar.

### El corpus era mayormente términos y condiciones

La primera versión bajaba 200 notas de la diaria y contaba 72.615 palabras. Mirando un
artículo suelto apareció el problema: de sus 360 palabras, 215 eran el bloque legal, el
aviso de suscripción y la política de datos. La diaria tiene paywall, así que lo público de
cada nota es la bajada, y el resto de lo que se bajaba era plantilla repetida.

Las mediciones hechas sobre ese corpus no valían: medían el pie de página del diario.

La solución es general y no depende del sitio. `quitar_plantilla` saca los renglones que
aparecen en más del 20% de los documentos de una fuente. En la diaria eran 7 renglones y se
llevaron la mitad del texto; en eldiarioAR eran 31 y se llevaron el 43%. Ahí importaba el
doble, porque eldiarioAR comparte plantilla con elDiario.es y ese texto viene en peninsular:
habría ensuciado justo el eje que mide el registro.

### El techo por patrón y el piso por scorer eran incompatibles

Este archivo declaraba dos criterios: que ninguna regla marcara más del 2% de los textos
humanos, y que el scorer entero dejara limpio al 95%. Con el corpus corregido quedó claro
que no pueden valer los dos a la vez.

Un catálogo con veinticinco palabras de vocabulario, cada una marcando uno o dos documentos
de 592, junta un 4% de unión aunque ninguna regla pase el 2%. Los dos números no son
criterios independientes: **el techo por patrón tiene que salir del piso por scorer,
dividido por cuántos patrones tiene el catálogo.**

El techo quedó en **0,5%** — tres textos de 592, lo más chico que se puede medir sin que el
número sea ruido. El piso por scorer dejó de ser un objetivo y pasó a ser una guarda de
regresión al 90%, porque su valor sube o baja con el tamaño del catálogo aunque ninguna
regla haya cambiado.

## El criterio, como quedó

| Umbral | Valor | Por qué |
|---|---|---|
| Techo de falsos positivos | 0,5% de los documentos humanos | derivado del piso, dividido por el tamaño del catálogo |
| Ratio mínimo | 5x más frecuente por cada 10.000 palabras en el corpus de IA | abajo de eso, lo escriben también las personas |
| Mínimo de apariciones | 10 en el corpus de IA | abajo de eso la muestra no dice nada |

Hoy los 48 patrones de slop del scorer cumplen el techo. El peor marca el 0,34%.

## Lo que el corpus demostró

| Corrida | Textos humanos que el scorer deja limpios |
|---|---|
| Catálogo inicial, corpus corregido | 75,8% |
| Después de todo lo que sigue | **94,3%** |

### La forma insignia del catálogo inglés no transfiere

Es el hallazgo más fuerte del proyecto. `no solo X, sino Y` es la construcción más ruidosa
del inglés y la primera que cualquiera traduciría. En español marcaba el **8,6%** de la
prensa humana, con frases como estas, todas de notas anteriores a 2023:

> ~~advertido no solo por organizaciones ecologistas sino por organismos como el BCE~~
> ~~no solo se analizan casos de influenza, sino también otros virus respiratorios~~
> ~~ellas no solo rompían una imagen tradicional de la femineidad sino que se liberaban~~

En español es un correlativo gramatical corriente, no un tic de marketing. El inglés no
obliga a esa correlación y por eso ahí la forma llama la atención; el español sí, y por eso
acá no dice nada. **Rechazada.**

### Dos fallas de patrón que se veían como fallas de regla

**`potenciar` marcaba el 4,1%.** No era la palabra: era mi stemmer. La raíz `potenci`
cazaba también `potencia` y `potencias`, que en prosa política son
~~las grandes potencias occidentales~~ y no tienen nada que ver con el verbo. Ahora es un
patrón propio con las formas inequívocamente verbales, más la tercera persona cuando
arrastra objeto — `potencia tu marca` —, que es la superficie que el copy usa.

**`líderes en` marcaba el 4,9%.** Tampoco era la regla: el patrón aceptaba `del` y `de la`,
y cazaba ~~el líder de la asociación bancaria~~, que es una persona. Quedó solo `en`.

**La raya al modo inglés marcaba el 1,5%.** Era el mismo tipo de error. `\S—\S` leía
~~de gobierno corporativo—.~~ como raya sin espacios, cuando en realidad es un inciso que
cierra al final de la oración y lleva el punto pegado afuera, que es lo correcto en español.
Ahora la puntuación no cuenta como palabra pegada. Bajó a 0,34%.

### Once entradas que resultaron ser español corriente

Bajadas del scorer con su medición al lado. Están todas en `corpus/candidatos.py`, que las
sigue midiendo por si el corpus de IA cambia lo que se puede afirmar.

| Entrada | Marcaba | Ejemplo humano que la disparaba |
|---|---|---|
| `excepcional` | 1,86% | ~~estos episodios son excepcionales~~ |
| cierre de redacción escolar | 1,35% | ~~ese es, en definitiva, el gran tema~~ |
| `innovador` | 0,84% | ~~una política progresista, innovadora e integral~~ |
| `el poder de` | 0,84% | ~~el poder de compra de los salarios~~ |
| `cuando se trata de` | 0,84% | ~~incluso cuando se trata de propaganda~~ |
| `la clave está en` | 0,84% | ~~la clave está en la temperatura~~ |
| `sin precedentes` | 0,68% | uso corriente en prensa |
| `revolucionar` | 0,68% | ~~ideas revolucionarias~~ |
| `inmersivo` | 0,51% | uso corriente |
| llamada a la acción de plantilla | 0,51% | ~~empecemos~~ como conector |
| la forma `más que un X` | 0,51% | uso corriente |

### Rechazados de la lista de candidatos

| Patrón | Medición | Veredicto |
|---|---|---|
| dos puntos por encima de un piso | toca el 67,1% de los textos humanos | rechazado |
| punto y coma | toca el 27,5% | rechazado |
| `impulsar` | toca el 7,3% — ~~el impulso inicial~~, ~~impulsó la ley~~ | rechazado |

El de los dos puntos **estaba en el scorer** cuando empecé. Lo había portado del umbral que
el linter inglés usa para el punto y coma, sin ningún número que lo respaldara, y disparó
sobre el primer documento de verdad que escribí.

## Lo que esta corrida NO pudo demostrar

**Ningún patrón quedó admitido por ratio**, y conviene decirlo con todas las letras:

> El corpus de IA, generado con el CLI `claude` en 2026, casi no contiene los tells que el
> catálogo busca. En 10.471 palabras, `potenciar` no aparece ninguna vez.

Un modelo de primera línea en 2026, con un prompt neutro y en español, no escribe el slop
contra el que se construyó el catálogo inglés en 2024. El criterio de ratio no se puede
satisfacer contra este corpus, y bajar el mínimo para que diera sería exactamente el número
inventado que este proyecto dice no hacer.

El catálogo sigue sirviendo para texto de generadores más viejos, más baratos o peor
prompteados, que es de donde viene casi todo el slop que uno se cruza. Pero eso es una
afirmación sin medir y va dicha como tal.

Para cerrarla hay que generar el corpus con otros modelos:
`corpus/prompts-para-pegar.md` tiene los quince prompts y el procedimiento.

## Sobre qué se para esto

[SlopMonster](https://github.com/ItsssssJack/SlopMonster), MIT, de donde salen la estructura
del loop, la idea del puntaje que corta el build y la disciplina de no inventar prueba. Su
catálogo inglés fue el punto de partida de los candidatos, nunca del contenido: cada patrón
tuvo que ganarse el lugar contra el corpus en español, y varios no lo lograron.

El catálogo inglés que hay detrás de aquel es el de Wikipedia, *Signs of AI writing*, del
WikiProject AI Cleanup.

## Pendiente

**Falta copy comercial humano.** El corpus humano es todo periodismo. Para los grupos de
marketing no hay género equivalente del otro lado, así que su evidencia se apoya solo en el
techo de falsos positivos. La salida es sumar landings rioplatenses anteriores a 2023 desde
Wayback, que ya está probado que se puede consultar por fecha.

**Falta un corpus de IA que tenga slop.** Es el trabajo más importante que queda.
