class _Pf_input:
    
    def __init__(self):
        try:
            self.impl = _Pf_inputWindows()
        except ImportError:
            self.impl = _Pf_inputUnix()

    def __call__(self, prompt, prefill=''): return self.impl(prompt, prefill)


class _Pf_inputUnix:
    #def __init__(self):

    def __call__(self, prompt, prefill=''):
        readline.set_startup_hook(lambda: readline.insert_text(prefill))
        try:
            return raw_input(prompt)
        finally:
            readline.set_startup_hook()

class _Pf_inputWindows:
    def __init__(self):
        import win32console
    
    def __call__(self, prompt, prefill=''):
        import win32console
        
        _stdin = win32console.GetStdHandle(win32console.STD_INPUT_HANDLE)
        keys = []
        for c in str(prefill):
            evt = win32console.PyINPUT_RECORDType(win32console.KEY_EVENT)
            evt.Char = c
            evt.RepeatCount = 1
            evt.KeyDown = True
            keys.append(evt)
    
        _stdin.WriteConsoleInput(keys)
        return input(prompt)

prefilled_input = _Pf_input()
