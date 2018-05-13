Weevely
=======

[![Build Status](https://travis-ci.org/epinna/weevely3.svg?branch=master)](https://travis-ci.org/epinna/weevely3)

Weevely is a web shell designed for remote server administration and penetration testing that can be extended over the network at runtime with more than 30 modules.

It executes remote code via an obfuscated PHP agent located on the compromised HTTP server. It fits both web administration and penetration testing post-exploitation scenarios to maintain access, provide situational awareness, escalate the privileges, and move laterally in the network.

**Read the [Wiki](https://github.com/epinna/weevely3/wiki#getting-started) for tutorials and uses cases.**

* Run operating system commands in a terminal
* Pivot SQL console on the target
* Proxy HTTP traffic on the target
* Audit remote target
* Mount the remote filesystem
* Pivot port scan on target
* Upload and download files
* Spawn reverse and direct TCP shells
* Upgrade to Meterpreter session
* Bruteforce SQL accounts
* Manage natively compressed archives

The agent is a small, polymorphic PHP script which is hardly detectable by AV software, and the communication between the client and the agent is obfuscated within HTTP requests.

### Modules development

Weevely is easily extendible to implement internal audit, account enumerator, sensitive data scraper, network scanner, make the modules work as a HTTP or SQL client and do a whole lot of other cool stuff.
