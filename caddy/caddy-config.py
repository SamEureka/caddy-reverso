## Caddy Configurator
## Sam Dennon // 2022

import os
import subprocess
import re
import time
import textwrap

## Removes all the crazy indenting caused by the multi-line strings.
defunk = textwrap.dedent

## Grab some of the device variables
DNS_EMAIL = os.environ['DNS_EMAIL'] if 'DNS_EMAIL' in os.environ else ''
DNS_PROVIDER = os.environ[
    'DNS_PROVIDER'] if 'DNS_PROVIDER' in os.environ else 'XXX'
DNS_API_KEY = os.environ[
    'DNS_API_KEY'] if 'DNS_API_KEY' in os.environ else 'XXX'


## Pulls all the HOSTs out of the device variables and puts them in a list of dicts.
## Format for device variable - Name: HOST_<number>, Value: <host>|<domain>|<ip>|<port>|<wildcard (true or false)>
## The name must start with 'HOST_' and have a number. The value must separated with the pipe symbol '|'
def create_env_list():
    output = []
    for key, val in os.environ.items():
        if re.match("HOST_[0-9]", key):  ## Device variable name REGEX.
            host = val.split('|')  ## Splits the values on the pipe separator.
            try:
                output.append({
                    'host': host[0],
                    'domain': host[1],
                    'ip': host[2],
                    'port': host[3],
                    'wildcard': host[4]
                })
            except:
                print('''
        FORMAT ERROR: Check HOST variable format.
        EXPECTING: <host>|<domain>|<ip>|<port>|<wildcard (true or false)>
        ''')
    if (output != []):
        return output
    else:
        return []


## Creates the site block of the Caddyfile
def generate_site_block():
    list = create_env_list()
    if (list == []):
        return '!! No hosts found !! '
    temp_list = []
    for e in list:
        if (e['wildcard'] == 'true'):
            temp_list.append(f"*.{e['host']}.{e['domain']} ")
        temp_list.append(f"{e['host']}.{e['domain']} ")
    return ''.join(temp_list)


## Creates the tls resource options
## Required device variables - DNS_PROVIDER and DNS_API_KEY
## Optional device variable - DNS_EMAIL
def generate_tls_options():
    if (DNS_API_KEY == 'XXX' or DNS_PROVIDER == 'XXX'):
        return f"""
          Create DNS_PROVIDER and/or DNS_API_KEY device variables in balena.io console
    """
    else:
        tls_temp = f"""
      tls {DNS_EMAIL} {{
        dns {DNS_PROVIDER} {DNS_API_KEY}
      }}
    """
        return tls_temp


## Creates the resource blocks. Will let user know if there are not any hosts to proxy.
def generate_matcher_options():
    list = create_env_list()
    if (list == []):
        return """
    !! Create HOST_<number> device variable in balena.io console       !!
    !! Format for device variable -                                    !!
    !!  Name: HOST_<number>                                            !!
    !!  Value: <host>|<domain>|<ip>|<port>|<wildcard (true or false)>  !!
    !! The name must start with 'HOST_' and have a number.             !!
    !! The value must separated with the pipe symbol '|'               !!
    """
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
    # See https://github.com/SamEureka/balenaCaddyReverser for configuration options.

    {generate_site_block()} {{
    {generate_tls_options()}
    {generate_matcher_options()}
    }}
    """
        defunked = defunk(temp_string)
        cf.write(defunked)


## Write the Caddyfile to /etc/caddy/Caddyfile
write_caddyfile()

## Use caddy format to correct any problems with the formatting.
os.system('caddy fmt --overwrite /etc/caddy/Caddyfile')
## Print it to console so we can see what is being proxied.
os.system('cat /etc/caddy/Caddyfile')
## Start the caddy server passing in our new config file.
## If there aren't any HOSTs... don't start Caddy
if (create_env_list() != []):
    os.system('caddy run --config /etc/caddy/Caddyfile --adapter caddyfile')

## Idle... I like balena-idle as a fallback for troubleshooting. You can comment this out if you like.
os.system('balena-idle')