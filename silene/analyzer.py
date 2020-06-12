from enum import Enum, auto

import re
import string
import typing


class ActionType(Enum):
    APPEND = auto()  # A
    BEGIN = auto()  # B
    EMIT = auto()  # E:
    FEED = auto()  # F
    RAISE = auto()  # R:


class Action(typing.NamedTuple):
    action_type: ActionType
    argument: str = ''


class IfCharLogic:
    pass


class NotRule(IfCharLogic):
    # i.e. '!A-Z'
    def __init__(self, rule: IfCharLogic):
        pass


class NeitherRule(IfCharLogic):
    # (a, b, c) translates to not (a or b or c)
    def __init__(self, values: list):
        self.values = values


class OrRule(IfCharLogic):
    # [a, b, c] translates to a or b or c
    def __init__(self, values: list):
        self.values = values


class CharacterRangeRule(IfCharLogic):
    # i.e. A-Z has start_char A and end_char Z
    def __init__(self, start_char: str, end_char: str):
        self.start_char = start_char
        self.end_char = end_char


class SpecificCharacterRule(IfCharLogic):
    def __init__(self, char: str):
        self.char = char


class ElseRule(IfCharLogic):
    def __init__(self):
        pass


class Transition(typing.NamedTuple):
    if_char_logic: IfCharLogic
    actions: typing.List[Action]
    to_st: int


class Analyzer:
    """
    Stores transition logic. Calling a code generator function on it will generate the code necessary for a lexer.
    """

    def __init__(self, *, num_of_states: int):
        """
        Creates an Analyzer with the specified number of states.

        :param num_of_states: The number of states the lexer has.
        """
        self.num_of_states = num_of_states

        # An index represents a 'from_st' state, and the value at that index is a list of transitions that originate
        # from that 'from_st' state.
        self.transitions = [[] for _ in range(num_of_states)]

    def append_transition_from_state(self, *, if_char_logic: IfCharLogic,
                                     actions: typing.List[Action], to_st: int,
                                     from_st: int):
        self.transitions[from_st].append(Transition(
            if_char_logic=if_char_logic, actions=actions, to_st=to_st))

    def add_transition(self, *, from_st: int, to_st: int, if_char,
                       actions: typing.Optional[typing.List[str]] = None):
        """
        Adds a transition from one state to either another state or the same state. The transition occurs if the
        specified condition is satisfied. In addition, a set of actions will be taken.

        :param from_st: The starting state of the transition.
        :param to_st: The ending state of the transition.
        :param if_char: The condition that must be satisfied.
        :param actions: The set of actions to take.
        :return:
        """
        actions: typing.List[str] = actions or []
        max_possible_state_num = self.num_of_states - 1
        action_list: typing.List[Action] = []

        # Range check from_st state number and to_st state number
        if (from_st < 0) or (from_st > max_possible_state_num):
            raise IndexError(f'The "from" state {from_st} is not a possible state as it is either less than 0 or '
                             f'greater than {max_possible_state_num}')
        if (to_st < 0) or (to_st > max_possible_state_num):
            raise IndexError(f'The "to" state {to_st} is not a possible state as it is either less than 0 or greater '
                             f'than {max_possible_state_num}')

        for each_action in actions:
            if each_action == 'A':
                action_list.append(Action(ActionType.APPEND))
            elif each_action == 'B':
                action_list.append(Action(ActionType.BEGIN))
            elif each_action == 'F':
                action_list.append(Action(ActionType.FEED))
            else:
                pass
        if if_char == 'else':
            self.append_transition_from_state(
                if_char_logic=ElseRule(), actions=action_list, to_st=to_st,
                from_st=from_st)