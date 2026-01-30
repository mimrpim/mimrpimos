def shutdown():
    print("Shutting down the system...")
    subprocess.run(['sudo', 'shutdown', '-h', 'now'], check=True)

def reboot():
    print("Rebooting the system...")
    subprocess.run(['sudo', 'reboot'], check=True)

def clear():
    print("\033[H\033[J", end="")
cls = clear

def exit():
    print("Exiting into linux shell...")
    time.sleep(2)
    clear()
    sys.exit(0)
def cd(go_to: str="~"):
    global actual_directory
    try:  
        target = os.path.expanduser(go_to)
        os.chdir(target)
        actual_directory = os.getcwd()
    except Exception as e:
        print(f"Error: {e}")
