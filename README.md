# Proyecto: EDTS para una GIC que soporta + - * / David Andres Castellanos Angulo

Esté repositorio conteine la entrega del trabajo: hay un EDTS (Esquema de Traducción Sintáctica) para una Gramática Independientee del Contexto (GIC) que soporta suma, resta, multiplicación y división, además de declaraciones simples de variables. 
---

## Contenido del repositorio

- `parser_tac.py`  
  Implementación recursiva en Python (sin bucles ademas) que hace: análisis sintáctico recursivo (LL(1)), construcción del AST, decoración (propagación de tipos y folding parcial de connstantes), tabla de símbolos y generación de código intermedio (TAC). Ejecutable con `python3 parser_tac.py`.

- `EDTS_GIC_entregable.md`  
  Documento con la gramática, definición de atributos, cálculo de FIRST/FOLLOW/PREDICT, reglas semánticas (SDD), ejemplos de AST y TAC, y la explicación del ETDS.

---

## Gramática que se implement´o

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

En `EDTS_GIC_entregable.md` se detalla los conjuntos FIRST y FOLLOW para cada no-terminal y los conjuntos PREDICT para cada producción — tambien s eusaron esos conjuntos para asegurar que la gramática es LL(1).

---

## ETDS / TAC

El esquema de traducción genera instrucciones de 3 direcciones. Por ejemplo, para el programa:

```
int a, b;
a = 3 + 4 * (2 - 1);
```

se genero tamnbien (entre otras variantes) el siguiente TAC:

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

También se implementó folding de constantes donde es posible (por ejemplo `2 - 1` es evaluable en compilación).

---

## Cómo ejecutar el ejemplo

1. se pone este repositorio en la máquina o se descarga ya directamente is se quiere el archivo `parser_tac.py`.
2. se intala el Python 3 
3. se ejecuta:
```
python3 parser_tac.py
```

El script ejecuta un ejemplo embebido (el mostrado arriba), imprime el AST decorado, la tabla de símbolos y el TAC resultante.

---

## Fin Tarea 12 de noviembre de 2025..
