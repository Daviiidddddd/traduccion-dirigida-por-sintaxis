
# Entregable: EDTS para GIC (suma, resta, multiplicación, división) David Andres Castellanos Angul

## 1) Gramática (GIC) - LL(1)
**Terminales:** `int`, `float`, `id`, `num`, `=`, `+`, `-`, `*`, `/`, `(`, `)`, `,`, `;`, `$`  
**No terminales:** `P, DList, D, L, Type, SList, S, E, E', T, T', F`

**Producciones:**
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

## 2) Atributos utilizados (basicamente en resumen serian estos)
- **Declaraciones:**
  - `Type.trad` : representación textual del tipo ("int"/"float")
  - `L.th` : atributo heredado que transporta el tipo para la lista de ids
  - `D.trad` : traducción textual (opcional)
- **Expresiones / AST:**
  - `node.type` : tipo de la subexpresión (`int`/`float`)
  - `node.constVal` : valor constante si es evaluable en tiempo de compilación
  - `E.code`, `E.place` : código TAC resultante y lugar (temporal/variable)
  - `newTemp()`, `emit(...)` : auxiliares para generar TAC
- **Tabla de símbolos (global):**
  - entradas con `name`, `type`, `scope`, `offset`

---

## 3) Cálculo de conjuntos: FIRST (F), FOLLOW (S), PREDICT (P) como lo pide

### FIRST (F)
- FIRST(F) = { `(`, `id`, `num` }  
- FIRST(T) = { `(`, `id`, `num` }  
- FIRST(T') = { `*`, `/`, ε }  
- FIRST(E') = { `+`, `-`, ε }  
- FIRST(E) = { `(`, `id`, `num` }  
- FIRST(S) = { `id` }  
- FIRST(SList) = { `id`, ε }  
- FIRST(Type) = { `int`, `float` }  
- FIRST(D) = { `int`, `float` }  
- FIRST(L) = { `,`, ε }  
- FIRST(DList) = { `int`, `float`, ε }  
- FIRST(P) = { `int`, `float`, `id` }  

### FOLLOW (S)
- FOLLOW(P) = { `$` }
- FOLLOW(DList) = { `id`, `$` }
- FOLLOW(D) = { `;` }
- FOLLOW(L) = { `;` }
- FOLLOW(Type) = { `id` }
- FOLLOW(SList) = { `$` }
- FOLLOW(S) = { `;`, `$` }
- FOLLOW(E) = { `;`, `$`, `)` }
- FOLLOW(E') = { `;`, `$`, `)` }
- FOLLOW(T) = { `+`, `-`, `;`, `$`, `)` }
- FOLLOW(T') = { `+`, `-`, `;`, `$`, `)` }
- FOLLOW(F) = { `*`, `/`, `+`, `-`, `;`, `$`, `)` }

### PREDICT (P) - ejemplos
- PREDICT(D -> Type id L) = { `int`, `float` }  
- PREDICT(L -> ',' id L) = { `,` }  
- PREDICT(L -> ε) = { `;` }  
- PREDICT(S -> id '=' E) = { `id` }  
- PREDICT(E -> T E') = { `(`, `id`, `num` }  
- PREDICT(E' -> '+' T E') = { `+` }  
- PREDICT(E' -> '-' T E') = { `-` }  
- PREDICT(E' -> ε) = { `;`, `$`, `)` }  
- PREDICT(T' -> '*' F T') = { `*` }  
- PREDICT(T' -> '/' F T') = { `/` }  
- PREDICT(T' -> ε) = { `+`, `-`, `;`, `$`, `)` }

---

## 4) Gramática de atributos (SDD) - reglas semánticas (

Se muestran acciones clave (estilo SDD):

```
D -> Type id L
  { L.th := Type.trad;
    insert_in_symtab(id.lexeme, Type.trad);
  }

L -> ',' id L1
  { insert_in_symtab(id.lexeme, L.th);
    L1.th := L.th;
  }

L -> ε { /* nada */ }

Type -> 'int'  { Type.trad := "int"; }
Type -> 'float'{ Type.trad := "float"; }

S -> id '=' E
  { if not lookup_symtab(id.lexeme) error "Undeclared id";
    S.code := E.code || emit(id.lexeme || " = " || E.place);
  }

E -> T E'
  { E'.inh := T.place; E.code := concat(T.code, E'.code); E.place := E'.place; }

E' -> '+' T E1
  { t := newTemp();
    E'.code := concat(E'.inh_code, T.code, emit(t || " = " || E'.inh || " + " || T.place));
    E1.inh := t;
  }

E' -> ε { E'.place := E'.inh; }

T -> F T'
  { T'.inh := F.place; T.code := concat(F.code, T'.code); T.place := T'.place; }

T' -> '*' F T1
  { t := newTemp();
    T'.code := concat(T'.inh_code, F.code, emit(t || " = " || T'.inh || " * " || F.place));
    T1.inh := t;
  }

T' -> ε { T'.place := T'.inh; }

F -> '(' E ')' { F.place := E.place; F.code := E.code; }
F -> id { F.place := id.lexeme; F.type := symtab[id.lexeme].type; }
F -> num { t := newTemp(); F.place := t; F.code := emit(t || " = " || num.lexeme); F.type := ... }
```

---

## 5) ETDS / Traducción a TAC (esquema y ejemplo) para complementar

**Estrategia:** generar instrucciones de 3 direcciones con `newTemp()` para temporales y `emit(instr)` para añadir instrucciones.

**Ejemplo (programa):**
```
int a, b;
a = 3 + 4 * (2 - 1);
```

**TAC (aplicando SDD/ETDS):**

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

(Opcional: constant-folding produciría `a = 7`.)

---

## 6) Tabla de símbolos (estructura y ejemplo)

**Estructura:**
```
SymbolEntry { name: string, type: string, scope: string, offset: int }
SymbolTable: map<string, SymbolEntry>, nextOffset counter
```

**Ejemplo tras `int a, b;`:**
```
a | type=int | scope=global | offset=0
b | type=int | scope=global | offset=1
```

---

## 7) AST  (o sea este es el impreso para el ejemplo)

```
Program
 Decls:
    Decl(type=int, ids=['a', 'b'])
 Stmts:
    Assign(id=a)
      BinOp(op='+') [type=int const=None]
        Const(3) [type=int]
        BinOp(op='*') [type=int const=None]
          Const(4) [type=int]
          BinOp(op='-') [type=int const=1]
            Const(2) [type=int]
            Const(1) [type=int]
```

---

## 8) (Entregable)

---

## Fin
