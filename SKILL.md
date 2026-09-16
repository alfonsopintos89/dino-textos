---
name: dino
description: Saca el acento de IA de un texto en español rioplatense y lo deja sonando de acá. Puntúa, reescribe y vuelve a puntuar. Se dispara con /dino, "sacale la IA a esto", "esto suena a ChatGPT", "hacelo sonar rioplatense", "arreglá este copy".
---

# dino

Agarrá un borrador y dejalo como si lo hubiera escrito una persona de acá. Una landing,
un README, una newsletter, un mail.

El objetivo no es pasar un detector de IA. Los detectores son ruido y perseguirlos empeora
la prosa. El objetivo es el estómago de un lector que este mes leyó mil párrafos de IA.

Dos ejes que puntúan por separado, porque fallan por razones distintas y se arreglan con
ediciones distintas. Un texto puede ser humanísimo y estar escrito en peninsular, o estar
en voseo perfecto y ser slop puro.

```
1. PUNTUAR     python3 tools/dino.py texto.md      slop /5 y registro /3
2. REESCRIBIR  tres pases
3. REPUNTUAR   python3 tools/dino.py de nuevo      se shipea en 5/5 y 3/3
```

El linter tiene la primera y la última palabra, porque el linter es honesto y el modelo es
persuasivo. "Casi limpio" es como termina una página sonando igual que todas las demás.

## Paso 1 — puntuar

```bash
python3 tools/dino.py borrador.md
python3 tools/dino.py index.html
python3 tools/dino.py index.html --vista hero     # un solo elemento por id
python3 tools/dino.py --texto "pegá un borrador acá"
python3 tools/dino.py nota.md --sin-registro      # público de toda LatAm
python3 tools/dino.py index.html --permitir-prueba  # los números son reales y los podés mostrar
```

Regex, sin opiniones. Abajo de 5/5 o de 3/3 sale con código distinto de cero, así que sirve
de gate de build. Una entrada vacía falla, nunca aprueba: un gate que estampa limpio sobre
un archivo de cero bytes reporta slop como limpio justo cuando el pipeline se rompió.

Tocaste un regex, corré `python3 tools/test_dino.py`. Cada regla tiene un espécimen que la
dispara y un texto humano parecido que no. El segundo es el que importa.

## Paso 2 — reescribir, tres pases

El catálogo completo está en `referencias/senales-ia-espanol.md` y
`referencias/registro-rioplatense.md`. La versión corta:

1. **Léxico.** `potenciar`, `optimizar`, `robusto`, `holístico`, `de vanguardia`,
   `en el mundo actual`, `soluciones integrales`. Cambialo por una palabra más llana, no
   por un sinónimo más pomposo de la misma idea.
2. **Formas.** `no solo X, sino Y` es la más ruidosa del español ahora mismo. También el
   reflejo del ritmo de tres, la raya al modo inglés, las preguntas que el propio texto se
   contesta, el párrafo de cierre que nadie pidió y la negrita al principio de cada viñeta.
3. **Poné a alguien de acá adentro.** Sacar los tells deja texto limpio y muerto. Voseo, no
   tuteo. Una cifra concreta por afirmación, sacada del texto original y de ningún otro
   lado. Largos de oración que varíen fuerte. Una oración de tres palabras después de una
   larga. Una cosa que un escritor prolijo habría cortado.

Sobre el voseo: no alcanza con cambiar `tú` por `vos`. El imperativo es lo que delata todo
copy generado. `Descubre` → `Descubrí`. `Prueba gratis` → `Probá gratis`.
`Regístrate` → `Registrate`, sin tilde: la tilde es justamente lo que lo delata.

## Paso 3 — volver a puntuar

Siempre. Un modelo es muy bueno sacando tells y perfectamente capaz de meter otros nuevos
mientras lo hace. Una reescritura sin repuntuar es cara o cruz.

## La regla dura

**Nunca inventar prueba.** Ni cantidades de clientes, ni testimonios, ni puntuaciones, ni
un `+5.000 usuarios` que no puedas mostrar. Si una afirmación necesita un número que no
tenés, escribí `[falta dato]` y seguí. El linter marca cualquier número pegado a un
sustantivo de persona a propósito: un falso positivo cuesta diez segundos, un falso
negativo es una afirmación que no podés respaldar.

Lo específico y verificable rinde más que la credibilidad prestada. `Techos, y solo techos,
desde 2001` le gana a `los más confiables del rubro`, porque una fecha no se discute y un
superlativo el lector lo descuenta solo.

## Formato de salida

Primero el texto reescrito completo. Después `▎ qué cambié`, cinco líneas como máximo, cada
una nombrando el tell y el arreglo. Nunca devolver solo el análisis.

El significado del autor se mantiene exacto. Sacar el slop no es reescribir el argumento.
Y el registro que te dieron se respeta: si es técnico, sigue siendo técnico.
