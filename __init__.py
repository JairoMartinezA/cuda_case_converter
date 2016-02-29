from cudatext import *
from .format_case import do_conv_string
from .format_case import MODE_SNAKE, MODE_UPPER, MODE_CAMEL, MODE_PAS, MODES_STR  
from .word_proc import *

class Command:
    def do_conv(self, mode):
        x, y, nlen, text = get_word_info()
        if text=='':
            msg_status('Place caret under a word');
            return
        text2 = do_conv_string(text, mode)
        if text==text2:
            msg_status('Word is already formatted: '+MODES_STR[mode]);
            return
           
        ed.set_caret(x, y, -1, -1)
        ed.delete(x, y, x+nlen, y)
        ed.insert(x, y, text2)   
        msg_status('Word formatted: '+MODES_STR[mode])
        

    def conv_snake(self):
        self.do_conv(MODE_SNAKE)
        
    def conv_upper(self):
        self.do_conv(MODE_UPPER)
        
    def conv_camel(self):
        self.do_conv(MODE_CAMEL)
        
    def conv_pascal(self):
        self.do_conv(MODE_PAS)
