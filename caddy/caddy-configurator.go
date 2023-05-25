package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"regexp"
	"strings"
	"text/template"
)

// Configurator is the struct for Caddy Configurator
type Configurator struct {
	DNSResolvers string
	DNSEmail     string
	DNSProvider  string
	DNSAPIKey    string
	Hosts        []Host
}

// Host represents a host configuration
type Host struct {
	Name     string
	Domain   string
	IP       string
	Port     string
	Wildcard bool
}

// createEnvList pulls all the HOSTs out of the environment variables and puts them in a list of Host structs.
func (c *Configurator) createEnvList() {
	for _, e := range os.Environ() {
		pair := strings.SplitN(e, "=", 2)
		key, value := pair[0], pair[1]
		match, _ := regexp.MatchString("HOST_[0-9]", key)
		if match {
			host := strings.Split(value, "|")
			if len(host) == 5 {
				c.Hosts = append(c.Hosts, Host{
					Name:     host[0],
					Domain:   host[1],
					IP:       host[2],
					Port:     host[3],
					Wildcard: host[4] == "true",
				})
			} else {
				fmt.Println(`
		FORMAT ERROR: Check HOST variable format.
		EXPECTING: <host>|<domain>|<ip>|<port>|<wildcard (true or false)>
				`)
			}
		}
	}
}

// generateSiteBlock creates the site block configuration based on the host list.
func (c *Configurator) generateSiteBlock() string {
	if len(c.Hosts) == 0 {
		return "!! No hosts found !!"
	}

	var tempStrings []string
	for _, host := range c.Hosts {
		if host.Wildcard {
			tempStrings = append(tempStrings, fmt.Sprintf("*.%s.%s ", host.Name, host.Domain))
		}
		tempStrings = append(tempStrings, fmt.Sprintf("%s.%s ", host.Name, host.Domain))
	}

	return strings.Join(tempStrings, "")
}

// generateTLSOptions creates the tls resource options based on DNS variables.
func (c *Configurator) generateTLSOptions() string {
	if c.DNSAPIKey == "XXX" || c.DNSProvider == "XXX" {
		return `
          Create DNS_PROVIDER and/or DNS_API_KEY device variables in balena.io console
		`
	}

	tlsTemplate := `
      tls %s {
        dns %s %s
        resolvers %s
      }
	`
	return fmt.Sprintf(tlsTemplate, c.DNSEmail, c.DNSProvider, c.DNSAPIKey, c.DNSResolvers)
}

// generateMatcherOptions creates the resource blocks for reverse proxy based on the host list.
func (c *Configurator) generateMatcherOptions() string {
	if len(c.Hosts) == 0 {
		return `
    !! Create HOST_<number> device variable in balena.io console       !!
    !! Format for device variable -                                    !!
    !!  Name: HOST_<number>                                            !!
    !!  Value: <host>|<domain>|<ip>|<port>|<wildcard (true or false)>  !!
    !! The name must start with 'HOST_' and have a number.             !!
    !! The value must separated with the pipe symbol '|'               !!
		`
	}

	var tempStrings []string
	for _, host := range c.Hosts {
		if host.Wildcard {
			tempStrings = append(tempStrings, fmt.Sprintf(`
        @%swild host *.%s.%s
          handle @%swild {
          reverse_proxy %s:%s
        }`, host.Name, host.Name, host.Domain, host.Name, host.IP, host.Port))
		}
		tempStrings = append(tempStrings, fmt.Sprintf(`
      @%s host %s.%s
        handle @%s {
        reverse_proxy %s:%s
      }`, host.Name, host.Name, host.Domain, host.Name, host.IP, host.Port))
	}

	return strings.Join(tempStrings, "")
}

// writeCaddyfile generates the Caddyfile based on the configuration and writes it to /etc/caddy/Caddyfile
func (c *Configurator) writeCaddyfile() {
	tmpl := `# Caddy configuration file
# This file is auto-generated on startup, changes to the file will not persist.
# See https://github.com/SamEureka/balenaCaddyReverser for configuration options.

{{ .SiteBlock }} {
{{ .TLSOptions }}
{{ .MatcherOptions }}
}
`
	data := struct {
		SiteBlock      string
		TLSOptions     string
		MatcherOptions string
	}{
		SiteBlock:      c.generateSiteBlock(),
		TLSOptions:     c.generateTLSOptions(),
		MatcherOptions: c.generateMatcherOptions(),
	}

	t := template.Must(template.New("caddyfile").Parse(tmpl))

	file, err := os.Create("/etc/caddy/Caddyfile")
	if err != nil {
		fmt.Println("Error creating Caddyfile:", err)
		return
	}
	defer file.Close()

	err = t.Execute(file, data)
	if err != nil {
		fmt.Println("Error writing Caddyfile:", err)
		return
	}
}

func main() {
	configurator := Configurator{
		DNSResolvers: os.Getenv("DNS_RESOLVERS"),
		DNSEmail:     os.Getenv("DNS_EMAIL"),
		DNSProvider:  os.Getenv("DNS_PROVIDER"),
		DNSAPIKey:    os.Getenv("DNS_API_KEY"),
	}

	configurator.createEnvList()

	configurator.writeCaddyfile()

	// Use caddy fmt to correct any problems with the formatting.
	cmd := exec.Command("caddy", "fmt", "--overwrite", "/etc/caddy/Caddyfile")
	err := cmd.Run()
	if err != nil {
		fmt.Println("Error running caddy fmt:", err)
		return
	}

	// Print the Caddyfile to console
	caddyfile, err := ioutil.ReadFile("/etc/caddy/Caddyfile")
	if err != nil {
		fmt.Println("Error reading Caddyfile:", err)
		return
	}
	fmt.Println(string(caddyfile))

	// Start the Caddy server if there are any hosts
	if len(configurator.Hosts) > 0 {
		cmd = exec.Command("caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile")
		err = cmd.Run()
		if err != nil {
			fmt.Println("Error running caddy:", err)
			return
		}
	}

	// Idle
	cmd = exec.Command("balena-idle")
	err = cmd.Run()
	if err != nil {
		fmt.Println("Error running balena-idle:", err)
		return
	}
}
