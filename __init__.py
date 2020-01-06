from cudatext import *
from .format_case import do_conv_string
from .format_case import MODE_SNAKE, MODE_UPPER, MODE_CAMEL, MODE_PAS, MODES_STR  
from .word_proc import *

class Command:
    def do_conv(self, mode):
        carets = ed.get_carets()
        num_carets = len(carets)
        num_formats = 0
        
        for caret in carets:
            x, y, nlen, text = get_word_info(caret)
            
            if text == '' and num_carets == 1:
                msg_status('Place caret under a word');
                return
            
            if text == '':
                continue
                
            text2 = do_conv_string(text, mode)
            
            if text == text2 and num_carets == 1:
                msg_status('Word is already formatted: '+MODES_STR[mode]);
                return
            
            if text == text2:
                continue
            
            ed.set_caret(x, y, -1, -1)
            ed.delete(x, y, x+nlen, y)
            ed.insert(x, y, text2)
            num_formats += 1
            
        msg_status(str(num_formats) + ' ' +
                   ('word' if num_formats <= 1 else 'carets') +
                   ' formatted: '+MODES_STR[mode])
        

    def conv_snake(self):
        self.do_conv(MODE_SNAKE)
        
    def conv_upper(self):
        self.do_conv(MODE_UPPER)
        
    def conv_camel(self):
        self.do_conv(MODE_CAMEL)
        
    def conv_pascal(self):
        self.do_conv(MODE_PAS)
