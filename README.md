# Silene

![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)

---

**This project is incomplete. Do not use in production.**

---

A tool for creating programming language lexers based on the finite state
machine model, that follow character-by-character rules.

Each token object produced by the generated lexer contains:

- The token text (`token.token_text`)
- The token type (i.e. identifier, operator, etc.) (`token.token_type`)
- The column number, line number, and position at which the token started (`token.start_col_num`, `token.start_line_num`, and `token.start_pos`)
- The column number, line number, and position at which the token ended (`token.end_col_num`, `token.end_line_num`, and `token.end_pos`)

## Getting Started

```python
from silene.analyzer import Analyzer
from silene.codegenerators.python_generator import generate_python_code


# The possible states are 0 and 1
lexer = Analyzer(num_of_states=2)

# if the from state is the same as the to state, it loops back

# if character is space or tab
lexer.add_transition(from_st=0, to_st=0, condition=[' ', '\t'])
# if character is +
# the action is begin token then append character then emit PLUS token
lexer.add_transition(from_st=0, to_st=0, condition='+', actions=['B', 'A', 'E:PLUS'])
# if character is a digit inclusive between 0 and 9
# the action is begin token then append character
lexer.add_transition(from_st=0, to_st=1, condition='0-9', actions=['B', 'A'])
# if character is a digit inclusive between 0 and 9
# the action is append character
lexer.add_transition(from_st=1, to_st=1, condition='0-9', actions=['A'])
# if character is not a digit inclusive between 0 and 9
# the action is emit NUM token then feed the character to the next state (0)
lexer.add_transition(from_st=1, to_st=0, condition='else', actions=['E:NUM', 'F'])

print(generate_python_code(lexer))
```

## Condition Syntax

* `'!'` : if character is !
* `'!c'` : if character is not c
* `'!0-9'` : if character is not a digit inclusive between 0 and 9
* `'else'` : if none of the other conditions are true
* `['0-9', 'A-Z']` : if character is a digit inclusive between 0 and 9, or a capital letter inclusive between A and Z
* `('0-9', 'A-Z')` : if character is neither a digit inclusive between 0 and 9, nor a capital letter inclusive between A and Z
* `'else'` : if the conditions for all other transitions with the same `from_st` state are false

## Actions

- **Append (A):** Appends the character to the token text.
- **Begin (B):** Marks the beginning of a token in general to be the current column number, line number, and position.
- **Emit (E:TYPE):** Marks the end of a token in general to be the current column number, line number, and position. In addition, emits a token of the specified type.
- **Feed (F):** Feeds the character to the `to_st` state.
- **Raise error (R:MESSAGE):** Raise a lexer error with the message `MESSAGE`.
