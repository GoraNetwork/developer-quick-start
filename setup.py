import os
import stat
import urllib.request
import http
import socket
import re
import json
import subprocess

"""
Check if Algod daemon is running on given localhost port.
"""
def check_algod_port(port):
    url = "http://localhost:" + port
    contents = ""
    print(f'Checking URL "{url}" for Algorand localnet node')
    try:
        contents = urllib.request.urlopen(url + "/versions", None, 2).read()
    except:
        print("Failed to connect")
        return False

    versions = json.loads(contents)
    if re.match(r"^(sand|docker)net-", versions["genesis_id"]):
        print("Algorand localnet node found")
        return True
    print("Algorand localnet node not detected")
    return False

"""
Return Algorand API server port.
"""
def get_algod_port():
    port = gora.algod_defl_port
    while True:
        if int(port) < 1024 or int(port) > 65535:
            print("Input not recognized as valid port number")
        elif check_algod_port(port):
            return port
        port = input("What is Algorand sandbox port number? ")

"""
Return boolean response to a Yes/No question.
"""
def ask_yes_no(question, defl_val = None):
    while True:
      if defl_val is None:
          postfix = "[y/n]"
      elif defl_val:
          postfix = "[Y/n]"
      else:
          postfix = "[y/N]"
      resp = input(f'{question}? {postfix} ')
      if resp == "":
          if defl_val is not None:
              return defl_val
      else:
        if resp.upper() in [ "Y", "YES" ]:
            return True;
        elif resp.upper() in [ "N", "NO" ]:
            return False;
      print("Please answer Y[es] or N[o]")

"""
Download CLI tool binary and make it executable.
"""
def init_cli_tool():
    if os.path.isfile(gora.cli_tool_path):
        if not ask_yes_no(f'CLI tool binary "{gora.cli_tool_path}" already exists, reuse', False):
            print(f'Reuse, rename or remove "{gora.cli_tool_path}" to complete setup')
            exit()
    else:
        print(f'Downloading Gora CLI tool from "{gora.cli_tool_url}"')
        urllib.request.urlretrieve(gora.cli_tool_url, gora.cli_tool_path)
    print(f'Making Gora CLI tool binary "{gora.cli_tool_path}" executable')
    os.chmod(gora.cli_tool_path, 0o744)

"""
Run dev environment initialization via CLI tool.
"""
def init_dev_env(algod_port):
    server = f'http://localhost:{algod_port}'
    gora.run_cli("dev-init", [ "--dest-server", server ],
                 { "GORA_CONFIG_FILE": "" }, True)

print("This will set up Gora development environment.")
print("Existing development environment settings may be overwritten.")
if not ask_yes_no("Continue", True):
    exit()

skip_module_install = False
try:
    import gora
except ImportError:
    if not ask_yes_no("Gora Python module is required to continue, install", True):
        skip_module_install = True

if not skip_module_install:
    cmd = [ "pip", "install", "-U", "gora" ]
    print(f'Running: "{" ".join(cmd)}"')
    subprocess.check_call(cmd, env=os.environ)

if not ask_yes_no("Do you have Algorand sandbox up and running now", True):
    print("You must set up and start Algorand Sandbox to proceed.")
    print("More info at: https://github.com/algorand/sandbox")
    exit()

algod_port = get_algod_port()
init_cli_tool()
init_dev_env(algod_port)
