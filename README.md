# Silene

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
from silene.lexer import Lexer


# The possible states are 0 and 1
lexer = Lexer('cool language', num_of_states=2)

# if the from state is the same as the to state, it loops back

# if character is space or tab
lexer.add_transition(from=0, to=0, if_char=[' ', '\t'])
# if character is +
# the action is begin token then append character then emit PLUS token
lexer.add_transition(from=0, to=0, if_char='+', action=['B', 'A', 'E:PLUS'])
# if character is a digit inclusive between 0 and 9
# the action is begin token then append character
lexer.add_transition(from=0, to=1, if_char='0-9', action=['B', 'A'])
# if character is a digit inclusive between 0 and 9
# the action is append character
lexer.add_transition(from=1, to=1, if_char='0-9', action='A')
# if character is not a digit inclusive between 0 and 9
# the action is emit NUM token then feed the character to the next state (0)
lexer.add_transition(from=1, to=0, if_char='else', action=['E:NUM', 'F'])

print(lexer.generate_code('python'))
```

## If Character Syntax

* `'!'` : if !
* `'!c'` : if not c
* `'!0-9'` : if not a digit inclusive between 0 and 9
* `'else'` : if none of the other conditions are true
* `['0-9', 'A-Z']` : if a digit inclusive between 0 and 9, or a capital letter inclusive between A and Z

## Actions

- **Append (A):** Appends the character to the token text.
- **Begin (B):** Marks the beginning of a token in general to be the current column number, line number, and position.
- **Emit (E:TYPE):** Marks the end of a token in general to be the current column number, line number, and position. In addition, emits a token of the specified type.
- **Feed (F):** Feeds the character to the `to` state.
