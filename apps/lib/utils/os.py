import subprocess
import os
def clear_console():
  subprocess.run('cls' if os.name == 'nt' else 'clear', shell=True)
  print(" --- CONSOLE CLEARED --- ")
