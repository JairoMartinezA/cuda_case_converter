import re
import string

import cudatext as app
import cudax_lib as ctx
import cuda_options_editor as op_ed

from enum import Enum
from cudatext import ed, msg_status, dlg_menu, dlg_custom

# Default chars to identify non-words in CudaText if the lexer has no defined it.
NONWORD_DEF = '''-+*=/\()[]{}<>"'.,:;~?!@#$%^&|`…'''

# Helper for previous variable
NONWORD = {}

# Config file name for this plugin
config_file = 'cuda_case_converter.json'

# Dictionary to save plugin configuration
config = {}

# Variables to keep word chars separator for this plugin
def_word_sep = []
def_word_sep_regex = ''

# Regex to divide by UpperLower chars. Consider do not touch this expression
def_case_pattern = r'[A-Z]{1}[a-z]+'

# Variable to indicate that selection is multi-line
# TODO: Validate this variable
multi_line = False

# Stores in a list all types of cases conversion to use in the Option Select Dialog.
cases_op_dialog = []

set_word_sep = []
set_word_sep_regex = ''
set_split_by_case = True
set_new_sep = ''


class Cases(Enum):
    CAMEL_CASE = 0
    DOT_CASE = 1
    KEBAB_CASE = 2
    PASCAL_CASE = 3
    SCREAMING_SNAKE_CASE = 4
    SNAKE_CASE = 5
    SLASH_CASE = 6
    BACK_SLASH_CASE = 7
    CUSTOM_CHAR = 8


class Opt(Enum):
    word_separator = 1
    max_chars_by_line = 2
    preserve_carets_after = 3
    select_word_on_caret = 4


OPTS_META = [
    {'opt': Opt.word_separator.name,
     'cmt': 'Chars used to separate words',
     'def': '._-\/ ',
     'frm': 'str',
     'chp': 'word',
     },
    {'opt': Opt.max_chars_by_line.name,
     'cmt': 'Set the max number of characters by line to proceed with conversion',
     'def': 500,
     'frm': 'int',
     'chp': 'line',
     },
    {'opt': Opt.preserve_carets_after.name,
     'cmt': 'Tell if carets remains in text after conversion',
     'def': True,
     'frm': 'bool',
     'chp': 'caret',
     },
    {'opt': Opt.select_word_on_caret.name,
     'cmt': 'Tell if the caret will be expanded to select whole word',
     'def': True,
     'frm': 'bool',
     'chp': 'caret',
     },
]

cases_str = {
    Cases.CAMEL_CASE.value          : 'camelCase',
    Cases.DOT_CASE.value            : 'dot.case',
    Cases.KEBAB_CASE.value          : 'kebab-case',
    Cases.PASCAL_CASE.value         : 'PascalCase',
    Cases.SCREAMING_SNAKE_CASE.value: 'SCREAMING_SNAKE_CASE',
    Cases.SNAKE_CASE.value          : 'snake_case',
    Cases.SLASH_CASE.value          : 'Separate by / slash',
    Cases.BACK_SLASH_CASE.value     : 'Separate by \ backslash',
    Cases.CUSTOM_CHAR.value         : 'Select separator...'
}


class Command:

    def __init__(self):
        load_config()

    def config_plugin(self):
        subset = ''  # Key for isolated storage on plugin settings
        title = 'Case Converter options'
        how = {'hide_lex_fil': True, 'stor_json': config_file}

        op_ed.OptEdD(
            path_keys_info=OPTS_META,
            subset=subset,
            how=how
        ).show(title)

        load_config()

    def cases_dialog(self):
        res = dlg_menu(app.MENU_LIST, cases_op_dialog,
                       caption='Select case conversion')
        if res is None: return
        case_convert(case_by_idx(res))

    def by_camel_case(self):
        case_convert(Cases.CAMEL_CASE)

    def by_dot_case(self):
        case_convert(Cases.DOT_CASE)

    def by_kebah_case(self):
        case_convert(Cases.KEBAB_CASE)

    def by_pascal_case(self):
        case_convert(Cases.PASCAL_CASE)

    def by_screaming_snake_case(self):
        case_convert(Cases.SCREAMING_SNAKE_CASE)

    def by_snake_case(self):
        case_convert(Cases.SNAKE_CASE)

    def by_slash_case(self):
        case_convert(Cases.SLASH_CASE)

    def by_backslash_case(self):
        case_convert(Cases.BACK_SLASH_CASE)

    def by_custom_chars(self):
        case_convert(Cases.CUSTOM_CHAR)


def get_opt(path, val):
    return ctx.get_opt(path, val, user_json=config_file)


def meta_default(key):
    return [it['def'] for it in OPTS_META if it['opt'] == key][0]


def case_by_idx(idx):
    return [i for i in Cases if i.value == idx][0]


def load_config():
    # Saving a dictionary with all plugin config
    for i in Opt:
        config[i.value] = get_opt(i.name, meta_default(i.name))

    for i in Cases:
        cases_op_dialog.append(str(int(i.value) + 1) + ' - ' +
                               cases_str[i.value])

    # Saving variables to get specific config about the words char separators
    def_word_sep.clear()
    for s in cfg(Opt.word_separator):
        def_word_sep.append(s)

    # Converting word char separator to regex expression
    global def_word_sep_regex
    def_word_sep_regex = '|'.join(get_escaped_chars(def_word_sep))


def get_escaped_chars(char_list):
    lst = []
    for i in char_list:
        if i in string.punctuation:
            lst.append('\\' + i)
        elif i == ' ':
            lst.append('\\s')
        else:
            lst.append(i)
    return lst


def cfg(key):
    return config[key.value]


def show_custom():
    c1 = chr(1)

    id_ori_char = 1
    id_new_char = 3
    id_case_split = 4
    id_btn_ok = 5

    res = dlg_custom('Custom case conversion...', 292, 130, '\n'.join([]
      +[c1.join(['type=label', 'cap=&Looking for:', 'pos=6,10,86,0'])]
      +[c1.join(['type=edit', 'val=', 'pos=96,6,126,0'])]
      +[c1.join(['type=label', 'cap=Replace &with:', 'pos=166,10,246,0'])]
      +[c1.join(['type=edit', 'val=', 'pos=256,6,286,0'])]
      +[c1.join(['type=check', 'cap=&Split by case change', 'pos=6,40,206,0', 'en=1'])]
      +[c1.join(['type=button', 'cap=&OK', 'props=1', 'pos=71,100,171,0'])]
      +[c1.join(['type=button', 'cap=&Cancel', 'pos=186,100,286,0'])]
      ))

    if res is None:
        msg_status("No options selected.")
        return

    (btn, text) = res

    if btn != id_btn_ok: return

    opts = text.splitlines()

    global set_word_sep
    global set_word_sep_regex
    global set_split_by_case
    global set_new_sep

    set_word_sep.clear()
    for s in list(opts[id_ori_char]):
        set_word_sep.append(s)

    set_word_sep_regex = '|'.join(get_escaped_chars(set_word_sep))
    set_split_by_case = bool(int(opts[id_case_split]))
    set_new_sep = opts[id_new_char]

    if set_word_sep_regex == '' and not set_split_by_case:
        msg_status("Cannot proceed with your sets.")
        return

    return True


def case_convert(mode):

    if mode == Cases.CUSTOM_CHAR:
        if not show_custom():
            return
    else:
        global set_word_sep
        global set_word_sep_regex
        global set_split_by_case
        global set_new_sep

        set_word_sep = def_word_sep
        set_word_sep_regex = def_word_sep_regex
        set_split_by_case = True
        set_new_sep = ''

    global multi_line
    multi_line = False

    carets = ed.get_carets()
    num_carets = len(carets)
    num_formats = 0
    new_carets = []

    # Variables to save the last caret
    x = y = None

    for caret in carets:
        text_info = get_current_text(caret)

        if not text_info:
            continue

        x, y, text = text_info

        if not text:
            continue

        word_list = get_whole_words(text)

        if mode in [Cases.CAMEL_CASE]:
            new_text = (word_list[0].lower() +
                        ''.join([s.title() for s in word_list[1:]]))
        elif mode in [Cases.DOT_CASE]:
            new_text = '.'.join([s.lower() for s in word_list])
        elif mode in [Cases.KEBAB_CASE]:
            new_text = '-'.join([s.lower() for s in word_list])
        elif mode in [Cases.PASCAL_CASE]:
            new_text = ''.join([s.title() for s in word_list])
        elif mode in [Cases.SCREAMING_SNAKE_CASE]:
            new_text = '_'.join([s.upper() for s in word_list])
        elif mode in [Cases.SNAKE_CASE]:
            new_text = '_'.join([s.lower() for s in word_list])
        elif mode in [Cases.SLASH_CASE]:
            new_text = '/'.join([s for s in word_list])
        elif mode in [Cases.BACK_SLASH_CASE]:
            new_text = '\\'.join([s for s in word_list])
        elif mode in [Cases.CUSTOM_CHAR]:
            new_text = set_new_sep.join([s for s in word_list])
        else:
            new_text = text

        if text == new_text and num_carets == 1:
            msg_status("The text is already formatted with case: " + cases_str[mode.value])
            return

        if text == new_text:
            continue

        tex_len = len(text)

        ed.replace(x, y, x + tex_len, y, new_text)

        if cfg(Opt.preserve_carets_after):
            new_carets.append([x, y, x + len(new_text)])

        num_formats += 1

    if num_formats == 0:
        if multi_line:
            msg_status("Multi-line selections not allowed")
    else:
        # Clean selections
        ed.set_caret(x, y, x, y)

        # Adding carets after conversion
        if cfg(Opt.preserve_carets_after):
            for caret in new_carets:
                ed.set_caret(caret[0], caret[1], caret[2],
                             caret[1], app.CARET_ADD)

        msg_status(str(num_formats) + " "
                   + ("word" if num_formats == 1 else "carets")
                   + " formatted with case: " + cases_str[mode.value])
    return


def get_current_text(caret):
    x1, y1, x2, y2 = caret

    if (y1, x1) > (y2, x2):
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    is_selection = y2 >= 0

    # TODO: Currently not prepared for multi-line uses.
    if y2 >= 0 and abs(y2 - y1) > 0:
        global multi_line
        multi_line = True
        return

    current_text = None
    x = x1

    # In this point there are just on valid value of y, no multi-line
    y = max(y1, y2)
    if not is_selection:
        if cfg(Opt.select_word_on_caret):
            word_info = get_word_under_caret(caret)
            if word_info:
                x, y, current_text = word_info
            else:
                return
        else:
            return
    else:
        current_line = get_line(y1)
        if current_line:
            current_text = current_line[x: x2]

    return x, y, current_text


def get_word_under_caret(caret):
    '''
    Gets tuple (min_x, max_y, word_under_caret)
    '''
    lex = ed.get_prop(app.PROP_LEXER_CARET)

    x1, y1, x2, y2 = caret

    # TODO: Currently not prepared for multi-line uses.
    if y2 >= 0 and abs(y2 - y1) > 0:
        global multi_line
        multi_line = True
        return

    l_char_is_word = r_char_is_word = ''
    current_line = get_line(y1)

    if current_line:
        new_x1 = new_x2 = x1
        if x1 > 0:
            l_char_is_word = is_word(current_line[x1 - 1], lex)
        if x1 < len(current_line):
            r_char_is_word = is_word(current_line[x1], lex)

        if not (l_char_is_word or r_char_is_word): return

        if l_char_is_word:
            new_x1 = next((i for i in range(x1 - 1, -1, -1)
                           if not is_word(current_line[i], lex)), -1) + 1

        if r_char_is_word:
            new_x2 = next((i for i in range(x1 + 1, len(current_line))
                           if not is_word(current_line[i], lex)),
                          len(current_line))

        if new_x1 == new_x2:
            return

        return new_x1, y1, current_line[new_x1: new_x2]
    else:
        return


def is_word(s, lexer):
    if not len(s):
        return False

    bads = NONWORD.get(lexer)
    if bads is None:
        bads = ctx.get_opt('nonword_chars', NONWORD_DEF, ctx.CONFIG_LEV_ALL,
                           lexer=lexer)
        NONWORD[lexer] = bads

    for ch in s:
        if ch in ' \t' + bads:
            return False
    return True


def get_line(n):
    # limit max length of line
    return ed.get_text_line(n, cfg(Opt.max_chars_by_line))


def get_whole_words(text):
    case_ix = []
    sep_ix = []

    if set_split_by_case:
        span_ix = [m.span() for m in re.finditer(def_case_pattern, text)]
        case_ix = [m[x] for m in span_ix for x in range(2)]

    if set_word_sep_regex != '':
        span_ix = [m.span() for m in re.finditer(set_word_sep_regex, text)]
        sep_ix = [m[x] for m in span_ix for x in range(2)]

    all_ix = sorted(set.union({0}, set(case_ix), set(sep_ix), {len(text)}))

    all_words = [text[m:n] for m, n in zip(all_ix, all_ix[1:])]

    words = [w for w in all_words if w not in set_word_sep]

    return words
