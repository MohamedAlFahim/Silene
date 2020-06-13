from silene.analyzer import Analyzer

# The possible states are 0 and 1
lexer = Analyzer(num_of_states=2)

# if the from state is the same as the to state, it loops back

# if character is space or tab
lexer.add_transition(from_st=0, to_st=0, condition=[' ', '\t'])
# if character is +
# the action is begin token then append character then emit PLUS token
lexer.add_transition(from_st=0, to_st=0, condition='+',
                     actions=['B', 'A', 'E:PLUS'])
# if character is a digit inclusive between 0 and 9
# the action is begin token then append character
lexer.add_transition(from_st=0, to_st=1, condition='0-9', actions=['B', 'A'])

# if character is a digit inclusive between 0 and 9
# the action is append character
lexer.add_transition(from_st=1, to_st=1, condition='0-9', actions=['A'])
# if character is not a digit inclusive between 0 and 9
# the action is emit NUM token then feed the character to the next state (0)
lexer.add_transition(from_st=1, to_st=0, condition='else',
                     actions=['E:NUM', 'F'])

for i, each_transition_list in enumerate(lexer.transitions):
    print(f'From state {i}:')
    for each_transition in each_transition_list:
        print(each_transition)
