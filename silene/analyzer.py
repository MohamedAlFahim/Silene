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


class ConditionRule:
    pass


class NotRule(ConditionRule, typing.NamedTuple):
    # i.e. '!A-Z'
    rule: ConditionRule


class OrRule(ConditionRule, typing.NamedTuple):
    # [a, b, c] translates to a or b or c
    values: typing.List[ConditionRule]


class CharacterRangeRule(ConditionRule, typing.NamedTuple):
    # i.e. 'A-Z' has start_char 'A' and end_char 'Z'
    start_char: str
    end_char: str


class SpecificCharacterRule(ConditionRule, typing.NamedTuple):
    char: str


class ElseRule(ConditionRule):
    def __init__(self):
        pass


# noinspection PyPep8Naming
def NeitherRule(values: typing.List[ConditionRule]):
    # (a, b, c) translates to not (a or b or c)
    return NotRule(rule=OrRule(values=values))


class Transition(typing.NamedTuple):
    if_char_logic: ConditionRule
    actions: typing.List[Action]
    to_st: int


# SYNTAX DETECTORS


def is_specific_character_syntax(syntax):
    # i.e. 'c'
    return isinstance(syntax, str) and (len(syntax) == 1)


def is_character_range_syntax(syntax):
    # i.e. 'a-z' and '0-9'
    return isinstance(syntax, str) and (len(syntax) == 3) and (syntax[1] == '-')


def is_exclamation_syntax(syntax):
    # i.e. '!c' and '!0-9'
    return isinstance(syntax, str) and (len(syntax) > 1) and syntax.startswith('!')


def is_or_syntax(syntax):
    return isinstance(syntax, list) and (len(syntax) > 1)


def is_neither_syntax(syntax):
    return isinstance(syntax, tuple) and (len(syntax) > 1)


# SYNTAX HANDLERS


def handle_specific_character_syntax(text: str):
    return SpecificCharacterRule(char=text)


def handle_character_range_syntax(text: str):
    return CharacterRangeRule(start_char=text[0], end_char=text[2])


def handle_exclamation_syntax(text: str):
    without_exclamation = text[1:]
    return NotRule(rule=(handle_specific_character_syntax(without_exclamation) if
                         is_specific_character_syntax(without_exclamation) else
                         handle_character_range_syntax(without_exclamation)))


def handle_or_syntax(values: typing.List[str]):
    or_values = []
    for each_value in values:
        if is_specific_character_syntax(each_value):
            or_values.append(handle_specific_character_syntax(each_value))
        elif is_character_range_syntax(each_value):
            or_values.append(handle_character_range_syntax(each_value))
        elif is_exclamation_syntax(each_value):
            or_values.append(handle_exclamation_syntax(each_value))
        else:
            raise ValueError(f'The condition {each_value} is invalid in the context of an OrRule')
    return OrRule(values=or_values)


def handle_neither_syntax(values: typing.List[str]):
    return NeitherRule(values=[(handle_specific_character_syntax(each_value) if
                                is_specific_character_syntax(each_value) else
                                handle_character_range_syntax(each_value)) for each_value in values])


class Analyzer:
    """
    Stores transition logic. Calling a code-generating function on it will generate the code necessary for a lexer.
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

    def add_transition(self, *, from_st: int, to_st: int,
                       condition: typing.Union[str, typing.Tuple[str], typing.List[str]],
                       actions: typing.Optional[typing.List[str]] = None) -> None:
        """
        Adds a transition from one state to either another state or the same state. The transition occurs if the
        specified condition is satisfied. In addition, a set of actions will be taken.

        :param from_st: The starting state of the transition.
        :param to_st: The ending state of the transition.
        :param condition: The condition that must be satisfied.
        :param actions: The set of actions to take.
        """
        actions: typing.List[str] = actions or []
        max_possible_state_num = self.num_of_states - 1
        action_list: typing.List[Action] = []

        # Range check from_st state number and to_st state number.
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
            elif each_action.startswith('E:'):
                action_list.append(Action(ActionType.EMIT, each_action[2:]))
            elif each_action.startswith('R:'):
                action_list.append(Action(ActionType.RAISE, each_action[2:]))
            else:
                raise ValueError(f'The action {each_action} is invalid')

        if_char_logic: ConditionRule
        if condition == 'else':
            if_char_logic = ElseRule()
        elif is_specific_character_syntax(condition):
            if_char_logic = handle_specific_character_syntax(condition)
        elif is_character_range_syntax(condition):
            if_char_logic = handle_character_range_syntax(condition)
        elif is_exclamation_syntax(condition):
            if_char_logic = handle_exclamation_syntax(condition)
        elif is_or_syntax(condition):
            if_char_logic = handle_or_syntax(condition)
        else:
            raise ValueError(f'The condition {condition} is invalid')

        self.transitions[from_st].append(Transition(if_char_logic=if_char_logic, actions=action_list, to_st=to_st))
