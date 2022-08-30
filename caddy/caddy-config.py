import os
import re
import time
import textwrap

defunk = textwrap.dedent

def create_env_list():
  output = []
  for key, val in os.environ.items():
    if re.match("HOST_[0-9]", key):
      host = val.split('|')      
      output.append({
        'host': host[0],
        'domain': host[1],
        'ip': host[2],
        'port': host[3],
        'wildcard': host[4]
      }) 
  return output

def generate_site_block():
  list = create_env_list()
  temp_list = []
  for e in list:
    if (e['wildcard'] == 'true'):
      temp_list.append(f"*.{e['host']}.{e['domain']} ")
    temp_list.append(f"{e['host']}.{e['domain']} ")
  return ''.join(temp_list)  

def generate_tls_options():
  tls_temp = f"""
    tls {{
      dns {os.environ['DNS_PROVIDER']} {os.environ['DNS_API_KEY']}
    }}
  """
  return tls_temp
  
def generate_matcher_options():
  list = create_env_list()
  temp_list = []
  for e in list:
    if (e['wildcard'] == 'true'):
      temp_list.append(f"""
        @{e['host']}wild host *.{e['host']}.{e['domain']}
          handle @{e['host']}wild {{
          reverse_proxy {e['ip']}:{e['port']}
        }}        
      """)
    temp_list.append(f"""
      @{e['host']} host {e['host']}.{e['domain']}
        handle @{e['host']} {{
        reverse_proxy {e['ip']}:{e['port']}  
      }}
    """)
  return ''.join(temp_list)

def write_caddyfile():
  if os.path.exists('/etc/caddy/Caddyfile'):
    os.remove("/etc/caddy/Caddyfile")
  with open('/etc/caddy/Caddyfile', 'a') as cf:
    temp_string = f"""
    # Caddy configuration file
    # This file is auto-generated on startup, changes to the file will not persist.
    # See https://github.com/SamEureka/balenaCaddy for configuration options.

    {generate_site_block()} {{
    {generate_tls_options()}
    {generate_matcher_options()}
    }}
    """
    defunked = defunk(temp_string)
    cf.write(defunked)

write_caddyfile()
os.system('caddy fmt --overwrite /etc/caddy/Caddyfile')
os.system('cat /etc/caddy/Caddyfile')
os.system('caddy stop')
os.system('caddy start --config /etc/caddy/Caddyfile')
while True:
    time.sleep(60000)