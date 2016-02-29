MODE_SNAKE  = 1
MODE_UPPER  = 2
MODE_CAMEL  = 3
MODE_PAS    = 4

MODES_ALL = [MODE_SNAKE, MODE_CAMEL, MODE_PAS, MODE_UPPER]
MODES_STR = {
  MODE_SNAKE: 'snake_case',
  MODE_UPPER: 'UPPER_CASE',
  MODE_CAMEL: 'camelCase',
  MODE_PAS: 'PascalCase',
  }

STAT_BEGIN  = 0
STAT_CHANGE = 1
STAT_OTHER  = 2

def do_conv_char(ch, mode, state):
    if mode==MODE_SNAKE:
        return ch.lower()
    if mode==MODE_UPPER:
        return ch.upper()
    
    if state==STAT_BEGIN:
        if mode==MODE_PAS:
            return ch.upper()
        else:
            return ch.lower()
    elif state==STAT_CHANGE:
        if (mode==MODE_PAS) or (mode==MODE_CAMEL):
            return ch.upper()
        else:
            return ch.lower()
    elif state==STAT_OTHER:
        return ch.lower()
        

def do_conv_string(text, mode):
    result = ''
    res_pre = ''
    res_post = ''

    # preserve lead/trail underscores       
    while text.startswith('_'):
        res_pre += '_'
        text = text[1:]
    while text.endswith('_'):
        res_post += '_'
        text = text[:-1]
    
    for i in range(len(text)):
        if text[i]=='_':
            continue
            
        if i==0:
            stat=STAT_BEGIN
        elif (text[i-1]=='_') or (text[i].isupper() and text[i-1].islower()):
            stat=STAT_CHANGE
        else:
            stat=STAT_OTHER
        
        ch = do_conv_char(text[i], mode, stat)
        if (stat==STAT_CHANGE) and (mode==MODE_SNAKE or mode==MODE_UPPER):
            result += '_'
        result += ch
        
    return res_pre + result + res_post


if __name__=='__main__':
    s = 'AaaBbbb';
    print(s)
    for m in MODES_ALL:  
        print(MODES_STR[m], ':', do_conv_string(s, m))
    s = '__AaaBbbbCcccccccc____';
    print()
    print(s)
    for m in MODES_ALL:  
        print(MODES_STR[m], ':', do_conv_string(s, m))
