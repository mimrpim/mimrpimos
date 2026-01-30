import os
import sys
import subprocess
import platform
import time
import json
import urllib.request
import getpass
import signal
import termios
import readline
import readline
import glob
import libraries.commands as commands

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

def version_check():
    if not sys.platform == 'linux':
        print("This application only runs on Linux.")
        sys.exit(1)

def variables_init():
    global pc_name, username, command, commands_list, actual_directory
    pc_name = platform.node()
    username = getpass.getuser()
    command = ""
    actual_directory = os.getcwd()
    commands_list = [
        "help",
        "update",
        "shutdown",
        "reboot",
        "clear",
        "cls",
        "exit",
        "cd"
    ]

def setup_history():
    # Cesta, kam se historie uloží (ve tvé domovské složce)
    history_file = os.path.expanduser("~/.python_shell_history")
    
    # Pokud soubor s historií existuje, načti ho
    if os.path.exists(history_file):
        readline.read_history_file(history_file)
    
    # Nastavíme automatické ukládání při ukončení programu
    import atexit
    atexit.register(readline.write_history_file, history_file)

def check_internet():
    try:
        urllib.request.urlopen('https://www.google.com', timeout=3)
        return True
    except Exception as e:
        return False

def update(what: str):
    if input("Are you sure you want to update? (y/n): ").strip().lower() == 'y':
        if what == "linux":
            print("Starting update process for Linux...")
            try:
                subprocess.run(['sudo', 'apt', 'update'], check=True)
                subprocess.run(['sudo', 'apt', 'full-upgrade', '-y'], check=True)
                subprocess.run(['sudo', 'apt', 'autoremove', '-y'], check=True)
                print("Update completed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"An error occurred during the update: {e}")

def input_cmd():
    global command
    command = input(f"{username}@{pc_name}:{actual_directory}> ").strip()

def input_cmd_command():
    global command
    if not command: # Ošetření prázdného řádku
        return
        
    parts = command.split()
    cmd_name = parts[0].lower()
    args = parts[1:]

    if cmd_name not in commands_list:
        subprocess.run([command], shell=True)
    else:
        # SPECIÁLNÍ LOGIKA PRO CD
        if cmd_name == "cd":
            if args:
                # Vezmeme první argument jako string
                commands.cd(args[0])
            else:
                # Pokud napíšeš jen 'cd', jdi domů
                commands.cd(os.path.expanduser("~"))
        elif cmd_name == "update":
            update("linux")
        else:
            # Pro ostatní funkce bez argumentů
            try:
                # globals() najde funkci definovanou v commands() 
                # pokud jsi je vynesl ven pomocí 'global'
                globals()[cmd_name]()
            except KeyError:
                # Pokud je funkce vnořená, eval je nejrychlejší fix 
                # ale musíš volat bez argumentů, pokud je nemají
                eval("commands." + cmd_name + "()")


def disable_ctrl_c():
    # Získáme aktuální nastavení terminálu pro standardní vstup (stdin)
    fd = sys.stdin.fileno()
    attr = termios.tcgetattr(fd)
    
    # VINTR je index pro přerušovací znak (Ctrl+C)
    # Nastavením na 0 (nebo _POSIX_VDISABLE) ho úplně deaktivujeme
    attr[6][termios.VINTR] = 0 
    
    # Použijeme nové nastavení okamžitě
    termios.tcsetattr(fd, termios.TCSANOW, attr)

if __name__ == "__main__":
    variables_init()
    commands()
    #version_check()
    commands.clear()
    disable_ctrl_c()
    setup_history()
    if not check_internet():
        print("No internet connection detected. No automatical updates will be performed.")
    else:
        print("Internet connection detected. Checking for updates...")
        update("linux")
    time.sleep(2)
    commands.cd(os.path.expanduser("~"))
    setup_readline()
    while True:
        input_cmd()
        input_cmd_command()