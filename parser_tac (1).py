#!/usr/bin/env python3
# parser_tac.py
# Parser + AST + Symbol table + TAC generator (recursion-only, no loops)
# Ejecutable: python3 parser_tac.py
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict, Any

@dataclass
class Node:
    pass

@dataclass
class Program(Node):
    decls: List['Decl']
    stmts: List['Assign']

@dataclass
class Decl(Node):
    type: str
    ids: List[str]

@dataclass
class Assign(Node):
    id: str
    expr: Node

@dataclass
class BinOp(Node):
    op: str
    left: Node
    right: Node
    type: Optional[str] = None
    constVal: Optional[Any] = None

@dataclass
class Const(Node):
    value: Any
    type: str

@dataclass
class Id(Node):
    name: str
    type: Optional[str] = None

class SymbolTable:
    def __init__(self):
        self.table: Dict[str, Dict[str, Any]] = {}
        self.next_offset = 0

    def insert(self, name: str, type_: str):
        if name in self.table:
            raise Exception(f"Declaración duplicada: {name}")
        self.table[name] = {"name": name, "type": type_, "scope": "global", "offset": self.next_offset}
        self.next_offset += 1

    def lookup(self, name: str):
        if name not in self.table:
            raise Exception(f"Identificador no declarado: {name}")
        return self.table[name]

    def entries(self):
        keys = list(self.table.keys())
        def rec(klist, acc):
            if not klist:
                return acc
            return rec(klist[1:], acc + [self.table[klist[0]]])
        return rec(keys, [])

def print_ast(node: Node, indent: int = 0) -> str:
    pad = "  " * indent
    if isinstance(node, Program):
        s = pad + "Program\n"
        s += pad + " Decls:\n"
        def rec_decls(dl, idx=0):
            if idx >= len(dl):
                return ""
            return print_ast(dl[idx], indent+2) + rec_decls(dl, idx+1)
        s += rec_decls(node.decls)
        s += pad + " Stmts:\n"
        def rec_stmts(sl, idx=0):
            if idx >= len(sl):
                return ""
            return print_ast(sl[idx], indent+2) + rec_stmts(sl, idx+1)
        s += rec_stmts(node.stmts)
        return s
    if isinstance(node, Decl):
        return pad + f"Decl(type={node.type}, ids={node.ids})\n"
    if isinstance(node, Assign):
        return pad + f"Assign(id={node.id})\n" + print_ast(node.expr, indent+1)
    if isinstance(node, BinOp):
        extra = f" [type={node.type} const={node.constVal}]" if node.type or node.constVal is not None else ""
        return pad + f"BinOp(op='{node.op}'){extra}\n" + print_ast(node.left, indent+1) + print_ast(node.right, indent+1)
    if isinstance(node, Const):
        return pad + f"Const({node.value}) [type={node.type}]\n"
    if isinstance(node, Id):
        return pad + f"Id({node.name}) [type={node.type}]\n"
    return pad + "Unknown\n"

class TACGenerator:
    def __init__(self):
        self.tmp_count = 0
        self.code: List[str] = []

    def new_temp(self):
        self.tmp_count += 1
        return f"t{self.tmp_count}"

    def emit(self, instr: str):
        self.code.append(instr)
        return instr

    def gen(self, node: Node) -> Tuple[str, List[str]]:
        if isinstance(node, Const):
            t = self.new_temp()
            self.emit(f"{t} = {node.value}")
            return t, [f"{t} = {node.value}"]
        if isinstance(node, Id):
            return node.name, []
        if isinstance(node, BinOp):
            left_place, _ = self.gen(node.left)
            right_place, _ = self.gen(node.right)
            if isinstance(node.left, Const) and isinstance(node.right, Const):
                if node.op == '+':
                    val = node.left.value + node.right.value
                elif node.op == '-':
                    val = node.left.value - node.right.value
                elif node.op == '*':
                    val = node.left.value * node.right.value
                elif node.op == '/':
                    val = node.left.value / node.right.value
                else:
                    raise Exception("Operador desconocido")
                t = self.new_temp()
                self.emit(f"{t} = {val}")
                return t, [f"{t} = {val}"]
            t = self.new_temp()
            self.emit(f"{t} = {left_place} {node.op} {right_place}")
            return t, [f"{t} = {left_place} {node.op} {right_place}"]
        raise Exception("Nodo no soportado en generación TAC")

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.symtab = SymbolTable()

    def peek(self, idx):
        if idx < len(self.tokens):
            return self.tokens[idx]
        return ('$', '$')

    def match(self, expected_kind, idx):
        tok = self.peek(idx)
        if tok[0] == expected_kind:
            return tok, idx+1
        raise Exception(f"Se esperaba {expected_kind} pero vino {tok} en posición {idx}")

    def parse_P(self, idx=0):
        decls, idx = self.parse_DList(idx)
        stmts, idx = self.parse_SList(idx)
        if self.peek(idx)[0] != '$':
            raise Exception(f"Se esperaba fin de entrada al final, vino {self.peek(idx)}")
        return Program(decls=decls, stmts=stmts), idx+1

    def parse_DList(self, idx):
        tok = self.peek(idx)
        if tok[0] in ('int','float'):
            d, idx = self.parse_D(idx)
            _, idx = self.match(';', idx)
            rest, idx = self.parse_DList(idx)
            return [d] + rest, idx
        else:
            return [], idx

    def parse_D(self, idx):
        tok = self.peek(idx)
        if tok[0] in ('int','float'):
            typ_tok, idx = self.match(tok[0], idx)
            typ = 'int' if typ_tok[0]=='int' else 'float'
            id_tok, idx = self.match('id', idx)
            ids_rest, idx = self.parse_L(idx, typ)
            ids = [id_tok[1]] + ids_rest
            def insert_list(lst):
                if not lst:
                    return None
                self.symtab.insert(lst[0], typ)
                return insert_list(lst[1:])
            insert_list(ids)
            return Decl(type=typ, ids=ids), idx
        raise Exception("Error en parse_D")

    def parse_L(self, idx, th):
        tok = self.peek(idx)
        if tok[0] == ',':
            _, idx = self.match(',', idx)
            id_tok, idx = self.match('id', idx)
            rest, idx = self.parse_L(idx, th)
            return [id_tok[1]] + rest, idx
        else:
            return [], idx

    def parse_SList(self, idx):
        tok = self.peek(idx)
        if tok[0] == 'id':
            s, idx = self.parse_S(idx)
            _, idx = self.match(';', idx)
            rest, idx = self.parse_SList(idx)
            return [s] + rest, idx
        else:
            return [], idx

    def parse_S(self, idx):
        id_tok, idx = self.match('id', idx)
        _, idx = self.match('=', idx)
        expr, idx = self.parse_E(idx)
        return Assign(id=id_tok[1], expr=expr), idx

    def parse_E(self, idx):
        tnode, idx = self.parse_T(idx)
        node, idx = self.parse_Ep(idx, tnode)
        return node, idx

    def parse_Ep(self, idx, inh):
        tok = self.peek(idx)
        if tok[0] in ('+','-'):
            op_tok, idx = self.match(tok[0], idx)
            tnode, idx = self.parse_T(idx)
            combined = BinOp(op=op_tok[0], left=inh, right=tnode)
            return self.parse_Ep(idx, combined)
        else:
            return inh, idx

    def parse_T(self, idx):
        fnode, idx = self.parse_F(idx)
        node, idx = self.parse_Tp(idx, fnode)
        return node, idx

    def parse_Tp(self, idx, inh):
        tok = self.peek(idx)
        if tok[0] in ('*','/'):
            op_tok, idx = self.match(tok[0], idx)
            fnode, idx = self.parse_F(idx)
            combined = BinOp(op=op_tok[0], left=inh, right=fnode)
            return self.parse_Tp(idx, combined)
        else:
            return inh, idx

    def parse_F(self, idx):
        tok = self.peek(idx)
        if tok[0] == '(':
            _, idx = self.match('(', idx)
            node, idx = self.parse_E(idx)
            _, idx = self.match(')', idx)
            return node, idx
        if tok[0] == 'id':
            id_tok, idx = self.match('id', idx)
            entry = None
            try:
                entry = self.symtab.lookup(id_tok[1])
                t = entry['type']
            except Exception as e:
                t = None
            return Id(name=id_tok[1], type=t), idx
        if tok[0] == 'num':
            num_tok, idx = self.match('num', idx)
            if '.' in num_tok[1]:
                t = 'float'
                val = float(num_tok[1])
            else:
                t = 'int'
                val = int(num_tok[1])
            return Const(value=val, type=t), idx
        raise Exception(f"Token inesperado en F: {tok}")

def decorate(node, parser_obj):
    if isinstance(node, Program):
        def rec_decls(dl, idx=0):
            if idx >= len(dl):
                return None
            decorate(dl[idx], parser_obj)
            return rec_decls(dl, idx+1)
        rec_decls(node.decls)
        def rec_stmts(sl, idx=0):
            if idx >= len(sl):
                return None
            decorate(sl[idx], parser_obj)
            return rec_stmts(sl, idx+1)
        rec_stmts(node.stmts)
    elif isinstance(node, Decl):
        return None
    elif isinstance(node, Assign):
        decorate(node.expr, parser_obj)
        try:
            info = parser_obj.symtab.lookup(node.id)
            return None
        except Exception as e:
            raise
    elif isinstance(node, BinOp):
        decorate(node.left, parser_obj)
        decorate(node.right, parser_obj)
        lt = getattr(node.left, 'type', None)
        rt = getattr(node.right, 'type', None)
        if lt == 'float' or rt == 'float':
            node.type = 'float'
        elif lt == 'int' or rt == 'int':
            node.type = 'int'
        if isinstance(node.left, Const) and isinstance(node.right, Const):
            if node.op == '+':
                val = node.left.value + node.right.value
            elif node.op == '-':
                val = node.left.value - node.right.value
            elif node.op == '*':
                val = node.left.value * node.right.value
            elif node.op == '/':
                val = node.left.value / node.right.value
            else:
                raise Exception("Operador desconocido")
            node.constVal = val
        return None
    elif isinstance(node, Const):
        return None
    elif isinstance(node, Id):
        try:
            info = parser_obj.symtab.lookup(node.name)
            node.type = info['type']
        except Exception:
            node.type = None
        return None

def run_example():
    # Sample program:
    # int a, b;
    # a = 3 + 4 * (2 - 1);
    tokens = [
        ('int','int'), ('id','a'), (',',','), ('id','b'), (';',';'),
        ('id','a'), ('=','='), ('num','3'), ('+','+'), ('num','4'), ('*','*'),
        ('(','('), ('num','2'), ('-','-'), ('num','1'), (')',')'), (';',';'),
        ('$', '$')
    ]

    parser = Parser(tokens)
    program_ast, _ = parser.parse_P(0)
    decorate(program_ast, parser)

    tacgen = TACGenerator()
    def gen_stmts_rec(stmts, idx=0):
        if idx >= len(stmts):
            return None
        s = stmts[idx]
        if isinstance(s, Assign):
            place, _ = tacgen.gen(s.expr)
            tacgen.emit(f"{s.id} = {place}")
        return gen_stmts_rec(stmts, idx+1)

    gen_stmts_rec(program_ast.stmts)

    print("=== AST Decorado (impreso) ===\n")
    print(print_ast(program_ast))

    print("=== Tabla de símbolos ===\n")
    for e in parser.symtab.entries():
        print(f"{e['name']} | type={e['type']} | scope={e['scope']} | offset={e['offset']}")

    print("\n=== Código TAC generado (ETDS) ===\n")
    for instr in tacgen.code:
        print(instr)

if __name__ == '__main__':
    run_example()
