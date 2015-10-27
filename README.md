Weevely
=======

Weevely is a command line web shell dynamically extended over the network at runtime, designed for remote administration and penetration testing. It provides a ssh-like terminal just dropping a PHP script on the target server, even in restricted environments.

The low footprint agent and over 30 modules shape an extensible framework to administrate web accounts or post exploit a web access escalating privileges and moving laterally in the compromised networks.

**Read the [Wiki](https://github.com/epinna/weevely3/wiki#getting-started) for tutorials and uses cases.**

The modules feature:

* Ssh-like terminal
* Run a SQL console pivoting on target
* Proxy your HTTP traffic pivoting on target
* Host configurations security auditing
* Mount target file system locally
* Conduct network scans pivoting on target
* File upload and download
* Spawn reverse and direct TCP shells
* Bruteforce internal services
* Manage comprossed archives

### The backdoor agent

The remote agent is a small dynamically extended PHP script, extending the client functionalities over the network at run-time. The agent code is polymorphic and hardly detectable by AV and the traffic is obfuscated within the HTTP protocol using steganographic techniques.

### Modules development

Weevely also provides python API to develop your own module to implement internal audit, account enumerator, sensitive data scraper, network scanner, make the modules work as a HTTP or SQL client and do a whole lot of other cool stuff.

> If you are a developer or a curious user and desire to contribute, you can to start reading the tutorial [Developing a new module ](https://github.com/epinna/weevely3/wiki/developing-a-new-module) and the [TODO list](https://github.com/epinna/weevely3/issues/1).
