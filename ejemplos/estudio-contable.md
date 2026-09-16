# Una corrida entera: landing de un estudio contable

Todo lo que sigue salió de una corrida real del 16 de setiembre de 2026. El borrador y la
reescritura van en bloques cercados, porque un espécimen no es copy y el scorer los saltea
al leer un `.md`. Así es como esta página pasa el linter que documenta.

## El borrador

```markdown
# Contadores Asociados

No solo somos un estudio contable, sino un aliado estratégico para tu empresa.

En el mundo actual, las empresas necesitan soluciones integrales que potencien su
crecimiento. Nuestro equipo de profesionales altamente capacitados ofrece un servicio
robusto, confiable y personalizado.

Descubre cómo más de 500 clientes felices ya transformaron su gestión financiera con
nosotros. Somos los más confiables del mercado—y podemos demostrarlo—con años de
experiencia de vanguardia.

¿El resultado? Tranquilidad para vos y tu negocio.

Regístrate hoy y lleva tu contabilidad al siguiente nivel.
```

## Lo que dijo el linter

```
$ python3 tools/dino.py borrador.md
85 palabras de texto visible

── slop
  léxico de IA:
    · potenciar  (1)
    · robusto  (1)
    · vanguardia  (1)
    · en el mundo actual  (1)
    · de vanguardia  (1)
    · soluciones integrales  (1)
  construcciones de IA:
    · la forma «no solo X, sino Y»  (1)
    · pregunta que el propio texto contesta  (1)
    · «llevá tu X al siguiente nivel»  (1)
    · «descubrí cómo»  (1)
  cadencia de puntuación:
    · raya al modo inglés, sin espacios
  ritmo de tres:
    · ritmo de tres  (robusto, confiable y personalizado.)
  venta y prueba inventada:
    · 500 clientes felices
    · superlativo que nadie puede chequear: «los más confiables»

  slop 0/5  necesita reescritura

── registro rioplatense
  imperativos que no son voseo:
    · regístrate (enclítico de tuteo)  (1)

  registro 2/3  no suena de acá
$ echo $?
1
```

Cero de cinco. Los cinco grupos tocados, y un solo acierto de registro que vale por todo el
resto: el borrador dice `Regístrate`, que es lo que delata a cualquier copy generado.

## La reescritura

```markdown
# Contadores Asociados

Somos cuatro contadores en una oficina de Pocitos. Llevamos la contabilidad de pymes
uruguayas desde 2011.

Hacemos balances, liquidación de sueldos y la declaración mensual de IVA. No asesoramos en
inversiones ni armamos estructuras en el exterior. Si necesitás eso, te pasamos el contacto
de alguien que lo hace bien.

Cuando llamás te atiende el contador que lleva tu empresa. No una mesa de entrada.

Hoy trabajamos con [falta dato] empresas. Ese número va acá antes de publicar la página, y
va el de verdad.

Escribinos y en una reunión te decimos si te podemos servir. Si no, también te lo decimos.
```

```
$ python3 tools/dino.py reescrito.md
104 palabras de texto visible

── slop

  slop 5/5  limpio

── registro rioplatense

  registro 3/3  de acá
$ echo $?
0
```

## Qué pasó, línea por línea

**`aliado estratégico` se fue y no vino nada en su lugar.** La forma
~~no solo X, sino Y~~ promete una revelación y entrega una abstracción. Sacarla no dejó un
hueco: dejó una oración menos.

**`500 clientes felices` se convirtió en `[falta dato]`.** Es la regla dura del proyecto.
Nadie sabía si eran quinientos, y decir que el casillero está vacío se lee como confianza.

**`los más confiables del mercado` se convirtió en una fecha.** Un superlativo el lector lo
descuenta solo porque no lo puede chequear. `desde 2011` no se discute.

**Apareció algo que el borrador no tenía: un límite.** `No asesoramos en inversiones ni
armamos estructuras en el exterior`. Una negativa viaja más lejos que una promesa, y
descalifica al cliente equivocado en un renglón.

**`Regístrate` se convirtió en `Escribinos`.** El voseo solo no alcanzaba: la línea también
tenía que pedir algo que una persona realmente hace.

El texto quedó 19 palabras más largo y dice bastante más. Eso no es casualidad: el borrador
tenía 85 palabras y casi ningún dato adentro.
