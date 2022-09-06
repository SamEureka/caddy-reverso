# <img src="caddy-dumb.png" alt="crappy caddy logo" width="60" /> caddy-reverso

__caddy-reverso__ is a Caddy based reverse-proxy server running on your Raspberry Pi! It implements ACME DNS Challenge to obtain tls certificates from Let's Encrypt and is configured via balena device variables in the cloud dashboard. Tested on all Raspberry Pi from v1 to Pi-4-64!

## Status
* ~~Works!!!~~ I broke some stuff... working on it.
* Needs to be documented properly
* Uses device variables to config the Caddyfile
* Wildcard certificates are working!!
* ACME provisioning works (digital ocean tested sat)
* The python is pretty janky...

## TODO
1. Document
2. Figure out how to publish as an app on [Balena Hub](https://hub.balena.io)
3. Test other DNS providers for the ACME provisioning
4. OAUTH authentication integration
5. Basic authentication integration (should be easy :laughing:)

## Device Variables
|Name|Value|Notes|
|---|---|---|
|HOST_\<number>| \<host>\|\<domain>\|\<ip>\|\<port>\|\<wildcard (true or false)>|The name must start with `HOST_` and have a number. Example name: `HOST_13` The values must separated with the pipe symbol `\|`. Example value: `nodered\|awesomedomain.com\|192.168.0.13\|4200\|true` If you aren't sure why/if you need a wildcard... set it to `false`|
|DNS_PROVIDER|digitalocean, cloudflare, googleclouddns... etc|This is the value provided to the ACME DNS Challenge and is also used to build the DNS Provider module. It needs to be set in the [docker-compose.yml](./docker-compose.yml) and set as a device variable. Check the [DNS Provider module WIKI](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148) for general information about how this works and to find out if your DNS provider is supported. [Quick Link: List of all Providers](https://github.com/orgs/caddy-dns/repositories?type=all)|
|DNS_API_KEY|\<string of randomness>|See your DNS provider's doccumentation on how to create an API Key.|
|DNS_EMAIL|sam@awesomedomain.com|This is OPTIONAL. This is the email address provided to the ACME DNS Challenge process. If you don't set an email variable you'll get a WARN in the logs but it will all still work.|
