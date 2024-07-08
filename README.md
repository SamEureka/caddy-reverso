# <img src="caddy-dumb.png" alt="crappy caddy logo" width="60" /> caddy-reverso

__caddy-reverso__ is a Caddy based reverse-proxy server running on your Raspberry Pi! It implements ACME DNS Challenge to obtain tls certificates from Let's Encrypt & basic authentication. Everything is configured via balena device variables in the balena.io cloud dashboard. Tested on all Raspberry Pi from v1 to Pi-4-64!

## Status
* Works!!! ~~I broke some stuff... working on it.~~
* Needs to be documented properly
* Uses device variables to config the Caddyfile
* Wildcard certificates are working!!
* ACME provisioning works (digital ocean tested sat)
* The python is pretty janky...
* Basic authentication (user/pass) works. 

## TODO
1. Document properly
~~2. Figure out how to publish as an app on [Balena Hub](https://hub.balena.io)~~
3. Test other DNS providers for the ACME provisioning
~~4. OAUTH authentication integration ([module](https://github.com/greenpau/caddy-security))~~

## Bare Bones Instructions

### Balena-CLI method 
> [!CAUTION]
> assumes you have some balena-cli chops and a decent understanding of what you are trying to do here. Reverse-proxy isn't beginner shit.

1. In the [docker-compose.yml](./docker-compose.yml) file set your DNS provider. [Quick Link: List of all supported Providers](https://github.com/orgs/caddy-dns/repositories?type=all)
2. Deploy to your Fleet using [`balena push`](https://docs.balena.io/learn/deploy/deployment/#balena-push) <-- click for balena-cli docs 
3. Start the application you want to proxy. You'll need the IP and Port at a minimum.
4. Create a `HOST_<number>` (see the table below) device variable for your to-be-proxied application. This will be parsed by the caddy-config.py script so follow the format exactly.
5. See the Device Variables table below. You'll need `DNS_API_KEY`, `DNS_PROVIDER`, & at least one `HOST_<number>`
6. These instructions are terrible... if you need help, create an issue. I'll try to help but I'm not going to teach you networking or help you set up your DNS. I will try to help you configure caddy-reverso only.  

> [!TIP]
> Example name: `HOST_1` value: `nodered|awesomedomain.com|192.168.0. 13|4200|true|true` 
> ***This will proxy*** `https://nodered.awesomedomain.com` ***to*** `192.168.0.13:4200`    

## Device Variables
|Name|Value|Notes|
|---|---|---|
|HOST_\<number>| \<host>\|\<domain>\|\<ip>\|\<port>\|\<wildcard (true or false)>\|\<auth_req (true or false)>|The name must start with `HOST_` and have a number. Example name: `HOST_13` The values must separated with the pipe symbol `\|`. Example value: `nodered\|awesomedomain.com\|192.168.0.13\|4200\|true\|true` If you aren't sure why/if you need a wildcard... set it to `false`|
|BASIC_AUTH_USER|`your-username`|This is only required if 'auth_req' is set to true in any of your HOST_X variables. |
|BASIC_AUTH_PASSWORD|`your-password`|This is only required if 'auth_req' is set to true in any of your HOST_X variables. |
|DNS_PROVIDER|digitalocean, cloudflare, googleclouddns... etc|This is the value provided to the ACME DNS Challenge and is also used to build the DNS Provider module. It needs to be set in the [docker-compose.yml](./docker-compose.yml) and set as a device variable. Check the [DNS Provider module WIKI](https://caddy.community/t/how-to-use-dns-provider-modules-in-caddy-2/8148) for general information about how this works and to find out if your DNS provider is supported. [Quick Link: List of all Providers](https://github.com/orgs/caddy-dns/repositories?type=all)|
|DNS_API_KEY|\<string of randomness>|See your DNS provider's doccumentation on how to create an API Key.|
|DNS_EMAIL|sam@awesomedomain.com|This is OPTIONAL. This is the email address provided to the ACME DNS Challenge process. If you don't set an email variable you'll get a WARN in the logs but it will all still work.|


### _Enjoy!_

<img src="pixel-sam.png" alt="sam image" width="40" />
// Sam
