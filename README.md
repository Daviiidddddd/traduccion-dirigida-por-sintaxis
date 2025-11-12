# Proyecto: EDTS para una GIC que soporta + - * /

Este repositorio contiene mi entrega del trabajo: implementé un EDTS (Esquema de Traducción Sintáctica) para una Gramática Independiente del Contexto (GIC) que soporta suma, resta, multiplicación y división, además de declaraciones simples de variables. Aquí explico **en primera persona** cómo lo hice, cómo usar el código y qué produce.

---

## Contenido del repositorio

- `parser_tac.py`  
  Implementación recursiva en Python (sin bucles explícitos) que hace: análisis sintáctico recursivo (LL(1)), construcción del AST, decoración (propagación de tipos y folding parcial de constantes), tabla de símbolos y generación de código intermedio (TAC). Ejecutable con `python3 parser_tac.py`.

- `EDTS_GIC_entregable.md`  
  Documento con la gramática, definición de atributos, cálculo de FIRST/FOLLOW/PREDICT, reglas semánticas (SDD), ejemplos de AST y TAC, y la explicación del ETDS.

---

## Gramática que implementé

Terminales: `int`, `float`, `id`, `num`, `=`, `+`, `-`, `*`, `/`, `(`, `)`, `,`, `;`, `$`

No terminales: `P, DList, D, L, Type, SList, S, E, E', T, T', F`

Producciones (LL(1)):

```
P     -> DList SList

DList -> D ';' DList
       | ε

D     -> Type id L

L     -> ',' id L
       | ε

Type  -> 'int'
       | 'float'

SList -> S ';' SList
       | ε

S     -> id '=' E

E     -> T E'
E'    -> '+' T E'
       | '-' T E'
       | ε

T     -> F T'
T'    -> '*' F T'
       | '/' F T'
       | ε

F     -> '(' E ')'
       | id
       | num
```

---

## Atributos y SDD (resumen)

Trabajo principalmente con atributos sintetizados para expresiones y algunos heredados para listas de identificación (para propagar el tipo del `Type` a cada id). Las reglas semánticas implementadas realizan:

- Inserción en la tabla de símbolos durante la reducción de declaraciones.
- Construcción del AST durante el parseo.
- En la decoración: propagación de tipos (`int`/`float`) y *constant folding* parcial cuando ambos operandos son constantes.
- Generación de TAC con temporales (`t1`, `t2`, ...) y la emisión de instrucciones tipo `t = a + b`.

En el código, las funciones `new_temp()` y `emit(...)` implementan la generación TAC; las reglas SDD están documentadas en `EDTS_GIC_entregable.md`.

---

## Cálculo de FIRST / FOLLOW / PREDICT

En `EDTS_GIC_entregable.md` detallo los conjuntos FIRST y FOLLOW para cada no-terminal y los conjuntos PREDICT para cada producción — usé esos conjuntos para asegurar que la gramática es LL(1).

---

## ETDS / TAC

El esquema de traducción genera instrucciones de 3 direcciones. Por ejemplo, para el programa:

```
int a, b;
a = 3 + 4 * (2 - 1);
```

Generé (entre otras variantes) el siguiente TAC:

```
t1 = 2
t2 = 1
t3 = t1 - t2
t4 = 4
t5 = t4 * t3
t6 = 3
t7 = t6 + t5
a = t7
```

También implementé folding de constantes donde es posible (por ejemplo `2 - 1` es evaluable en compilación).

---

## Cómo ejecutar el ejemplo

1. Clona este repositorio en tu máquina o descarga el archivo `parser_tac.py`.
2. Asegúrate de tener Python 3 instalado.
3. Ejecuta:
```
python3 parser_tac.py
```

El script ejecuta un ejemplo embebido (el mostrado arriba), imprime el AST decorado, la tabla de símbolos y el TAC resultante.

---

## Comentarios finales (a modo personal)

Yo implementé la solución usando **recursión** para todas las partes del parseo y del tratamiento de listas, cumpliendo con la restricción de no usar bucles explícitos para travesar listas o árboles en las funciones principales. El objetivo fue producir un entregable completo: gramática, atributos (SDD), FIRST/FOLLOW/PREDICT, AST decorado, tabla de símbolos y el ETDS con generación de TAC y ejemplo reproducible.

Si quieres que suba este repositorio directamente a GitHub, puedo:
- Preparar un archivo ZIP listo para subir, o
- Crear un commit y un repo remoto si me proporcionas acceso (token/permiso), o
- Generar un `LICENSE` y `requirements.txt` si lo deseas.

Dime qué prefieres y lo preparo.
