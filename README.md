Weevely
=======

Weevely is a command line web shell dynamically extended over the network at runtime, designed for remote server administration and penetration testing.

Its terminal executes arbitrary remote code through the small footprint PHP agent that sits on the HTTP server. Over 30 modules shape an adaptable web administration and post-exploitation backdoor for access maintenance, privilege escalation and network lateral movement, even in restricted environment.

**Read the [Wiki](https://github.com/epinna/weevely3/wiki#getting-started) for tutorials and uses cases.**

The framework features:

* Ssh-like terminal
* SQL console pivoted on target
* HTTP proxy pivoted on target
* Host configuration security auditing
* Mount of the remote filesystem
* Network scan pivoted on target
* File upload and download
* Reverse and direct TCP shell
* Meterpreter support
* Service account bruteforce
* Compressed archive management

### The backdoor agent

The remote agent is a small PHP script which can extend its functionality over the network at run-time. The agent code is polymorphic and hardly detectable by AV and the traffic is obfuscated within the HTTP requests.

### Modules development

Weevely also provides python API to develop your own module to implement internal audit, account enumerator, sensitive data scraper, network scanner, make the modules work as a HTTP or SQL client and do a whole lot of other cool stuff.

> If you are a developer or a curious user and desire to contribute, you can to start reading the tutorial [Developing a new module ](https://github.com/epinna/weevely3/wiki/developing-a-new-module) and the [TODO list](https://github.com/epinna/weevely3/issues/1).
