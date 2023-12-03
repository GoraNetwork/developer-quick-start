import os
import stat
import urllib.request
import http
import re
import json
import gora

def get_algod_port():
    while True:
        prompt = f'What is Algorand sandbox port number [{gora.algod_defl_port}]? '
        port = input(prompt) or gora.algod_defl_port
        if port and int(port) > 1024 and int(port) < 65535:
            url = "http://localhost:" + port
            contents = ""
            try:
                contents = urllib.request.urlopen(url + "/versions").read()
            except:
                print(f'Unable to query "{url}"')
            versions = json.loads(contents)
            if re.match(r"^(sand|docker)net-", versions["genesis_id"]):
                print(f'Found an Algorand localnet node at "{url}"')
                return int(port)
            else:
                print(f'Could not find an Algorand localnet node at "{url}"')
        else:
            print("Input not recognized as valid port number")

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

def init_dev_env(algod_port):
    server = f'http://localhost:{algod_port}'
    gora.run_cli("dev-init", [ "--dest-server", server ],
                 { "GORACLE_CONFIG_FILE": "" }, True)

print("This will set up Gora development environment.")
print("Existing development environment settings may be overwritten.")
if not ask_yes_no("Continue", True):
    exit()

if not ask_yes_no("Do you have Algorand sandbox up and running now"):
    print("You must set up and start Algorand Sandbox to proceed.")
    print("More info at: https://github.com/algorand/sandbox")
    exit()

algod_port = get_algod_port()
init_cli_tool()
init_dev_env(algod_port)
