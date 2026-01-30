import sys
import platform
import os
import termios
import readline

def os_check():
    if not sys.platform == 'linux':
        print("This application only runs on Linux.")
        sys.exit(1)

def disable_ctrl_c():
    # Získáme aktuální nastavení terminálu pro standardní vstup (stdin)
    fd = sys.stdin.fileno()
    attr = termios.tcgetattr(fd)
    
    # VINTR je index pro přerušovací znak (Ctrl+C)
    # Nastavením na 0 (nebo _POSIX_VDISABLE) ho úplně deaktivujeme
    attr[6][termios.VINTR] = 0 
    
    # Použijeme nové nastavení okamžitě
    termios.tcsetattr(fd, termios.TCSANOW, attr)

def setup_readline():
    # --- Historie ---
    history_file = os.path.expanduser("~/.python_shell_history")
    if os.path.exists(history_file):
        readline.read_history_file(history_file)
    import atexit
    atexit.register(readline.write_history_file, history_file)

    # --- Doplňování (Tab Completion) ---
    def completer(text, state):
        # Získáme celý řádek před kurzorem
        buffer = readline.get_line_buffer()
        
        # Pokud doplňujeme první slovo, doplňujeme příkazy z tvého seznamu
        if not buffer or ' ' not in buffer.strip():
            options = [c for c in commands_list if c.startswith(text)]
        else:
            # Pokud už je tam mezera, doplňujeme cesty k souborům/složkám
            # glob.glob najde odpovídající soubory
            options = [f for f in glob.glob(text + '*')]
        
        if state < len(options):
            return options[state]
        else:
            return None

    # Nastavení readline
    readline.set_completer(completer)
    # Na Linuxu (který cílíš) se Tab obvykle binduje takto:
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind("bind ^I rl_complete")
    else:
        readline.parse_and_bind("tab: complete")
        
    # Důležité: urči, které znaky neoddělují slova (aby doplňování cest fungovalo s lomítky)
    readline.set_completer_delims(' \t\n;')

def setup_history():
    # Cesta, kam se historie uloží (ve tvé domovské složce)
    history_file = os.path.expanduser("~/.python_shell_history")
    
    # Pokud soubor s historií existuje, načti ho
    if os.path.exists(history_file):
        readline.read_history_file(history_file)
    
    # Nastavíme automatické ukládání při ukončení programu
    import atexit
    atexit.register(readline.write_history_file, history_file)
