# Switch Statement in Python v3.10.0

![CI](https://github.com/UTK-CS594-Spring-2021/Team-Rabin/workflows/CI/badge.svg)

This is Team Rabin's implementation of a new switch statement in the [CPython](https://github.com/python/cpython) interpreter at Python version 3.10.0. Below is 
an example of the new syntax:

```py
switch val:
    case 0:
        print("it's zero")
    case 1:
        print("it's one")
    else:
        print("it's something")
```

### Team Members

- Isaac Sikkema ([@isikkema](https://github.com/isikkema))
- Joey Lemon ([@joeylemon](https://github.com/joeylemon))
- David Nguyen ([@dnguye201](https://github.com/dnguye201))

## Table of Contents

- [Project Description](blob/main/README.md#project-description)
- [Designing the Changes](blob/main/README.md#designing-the-changes)
- [Modifying the Grammar](blob/main/README.md#modifying-the-grammar)
- [Modifying the Tests](blob/main/README.md#modifying-the-tests)
- [Conclusion](blob/main/README.md#conclusion)

<a id="project-description"></a>
## Project Description

As students in COSC594: Software Development Tools at the [University of Tennessee](https://utk.edu), we were tasked with adding a new switch statement to the 
CPython interpreter, from the tokenizer all the way to the compiler. From the project assignment:

> The group project will entail students implementing a complex feature in a large, open source
development tool over the entire semester. Students will be given the freedom, and expectation, to
understand the feature request, convert the feature request into requirements and design
documents, and make the necessary code changes to implement the feature. Students must do
this without being given explicit instructions on how to do so.

> The feature request will be provided to students as if it were written by a customer/user of the
software project or a product manager, and may require students to elicit more details from
myself. Students have the freedom to design the feature as they see fit in an effort to try to satisfy
the feature request. There will be many open-ended design decisions that will need to be made.

<a id="designing-the-changes"></a>
## Designing the Changes

We initially went through preliminary design iterations to decide the easiest implementation of the feature request. We figured an easy implementation 
was one that resulted in the least collisions with existing syntax:
```py
sswitch 0:
    pass
scase 0:
    pass
sdefault:
    pass
```
Wanting to avoid the prepended 's' characters but also avoid colliding with many instances of `case` keywords throughout CPython, we considered the syntax:
```py
switch 0:
    circumstance 0:
        pass
    circumstance 0:
        pass
    circumstance 0:
        pass
    else:
        pass
```
Since `circumstance` was quite a large keyword to type out, the final syntax we decided upon before beginning changes to the grammar was:
```py
switch 0:
    kase 0:
        pass
    kase 0:
        pass
    kase 0:
        pass
    else:
        pass
```
Eventually, we would change to a more sane `case` keyword and rename all existing instances of the keyword in the repository.

<a id="modifying-the-grammar"></a>
## Modifying the Grammar

The first step to adding our new switch statement to CPython was creating definitions in the grammar to recognize our keywords `switch` and `kase`. 
Python provides an excellent developer guide, and we used the checklist from [24. Changing CPython’s Grammar](https://devguide.python.org/grammar/) to
complete this step. 

The main change at this stage was adding the definitions to `Grammar/python.gram`:
```
switch_stmt[stmt_ty]:
    | 'switch' a=named_expression &&':' NEWLINE INDENT b[asdl_kasehandler_seq*]=kase_block+ c=[else_block] DEDENT { _Py_Switch(a, b, c, EXTRA) }
kase_block[kasehandler_ty]:
    | 'kase' a=named_expression &&':' b=block { _Py_KaseHandler(a, b, EXTRA) }
```

as well as `Parser/Python.asdl`:
```
| Switch(expr value, kasehandler* handlers, stmt* orelse)

kasehandler = KaseHandler(expr value, stmt* body)
                attributes (int lineno, int col_offset, int? end_lineno, int? end_col_offset)
```

After running `make regen-all`, these changes would automatically be propagated throughout the interpreter in files such as 
`Parser/parser.c`, `Python/Python-ast.c`, and `Include/Python-ast.h`

## Modifying the Compiler

At this stage, Python would recognize our switch statement but not execute it. We still needed to generate and validate the appropriate AST nodes for the new 
grammar. To do so, we modified `Python/ast.c`:
```c
case Switch_kind:
    if (!validate_expr(stmt->v.Switch.value, Load))
        return 0;
    if (!asdl_seq_LEN(stmt->v.Switch.handlers)) {
        PyErr_SetString(PyExc_ValueError, "Switch has no kases");
        return 0;
    }
    for (i = 0; i < asdl_seq_LEN(stmt->v.Switch.handlers); i++) {
        kasehandler_ty handler = asdl_seq_GET(stmt->v.Switch.handlers, i);
        if ((handler->v.KaseHandler.value &&
             !validate_expr(handler->v.KaseHandler.value, Load)) ||
            !validate_body(handler->v.KaseHandler.body, "KaseHandler"))
            return 0;
    }
    return (!asdl_seq_LEN(stmt->v.Switch.orelse) ||
            validate_stmts(stmt->v.Switch.orelse));
```

Our AST nodes were now being validated properly. Next, we needed to modify `Python/compile.c` to generate new bytecode for our switch statement. This included 
adding a new function called [compile_switch()](https://github.com/UTK-CS594-Spring-2021/Team-Rabin/blob/main/Python/compile.c#L2797). It is a rather large function
that creates bytecode to follow the control flow:
```
BasicBlock Fall-Through Control Flow:

BEGIN -> kase_1_test -> kase_1_body -> kase_2_test -> kase_2_body -> ... -> kase_n_test -> kase_n_body -> orelse -> END

BasicBlock Jump Control Flow:
kase_1_test JUMP_IF_FALSE -> kase_2_test JUMP_IF_FALSE -> ...
kase_1_body JUMP_ALWAYS -> END
kase_2_body JUMP_ALWAYS -> END
...
orelse JUMP_ALWAYS -> END
```

After some miscellaneous changes, the new switch statement was finally being recognized and executed properly!

<a id="modifying-the-tests"></a>
## Modifying the Tests

At this point, we had failing tests. We needed to modify the `ast` module that helps Python applications to process trees of the Python abstract syntax grammar:
```py
def visit_Switch(self, node):
    self.fill("switch ")
    self.traverse(node.value)
    with self.block():
        for ex in node.handlers:
            self.traverse(ex)
        if node.orelse:
            self.fill("else")
            with self.block():
                self.traverse(node.orelse)

def visit_KaseHandler(self, node):
    self.fill("kase ")
    self.traverse(node.value)
    with self.block():
        self.traverse(node.body)
```

Tests were now passing and everything was working correctly. However, we wanted to change the `kase` keyword to `case`. Beyond modifying the grammar like we did
previously, it involved a multitude of changes to the tests to rename all instances of `case` to something else.

<a id="conclusion"></a>
## Conclusion

This project posed many challenges that required both critical thinking and intense knowledge of computer science principles. We gained deeper knowledge
into compilers and interpreters, and learned about abstract syntax trees and control flow graphs. Although the project seemed like a big undertaking, it turns
out there were only a handful of key places to modify the code. The [Python developer guide](https://devguide.python.org/) was extremely helpful and very well
documented. Our experience with Python as contributors to a massive open source project was very pleasant and serves as an example of the ideal open source
project.
