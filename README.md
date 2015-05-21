Weevely
=======

Weevely is a command line web shell dynamically extended over the network at runtime used for remote administration and pen testing. It provides a weaponized telnet-like console through a PHP script running on the target, even in restricted environments.

The low footprint agent and over 30 modules shape an extensible framework to administrate, conduct a pen-test, post-exploit, and audit remote web accesses in order to escalate privileges and pivot deeper in the internal networks.

**Try the [Wiki](https://github.com/epinna/weevely3/wiki#getting-started) for tutorial and uses cases.**

The modules feature:

* Shell/PHP telnet-like network terminal
* Common server misconfigurations auditing
* SQL console pivoting on target
* HTTP traffic proxying through target
* Mount target file system to local mount point
* Run scans pivoting on target
* File upload and download
* Spawn reverse and direct TCP shells
* Zip, gz, bz2 and tar handling

### The backdoor agent

The remote agent is a very low footprint php script that receives dynamically injected code from the client, extending the client functionalities over the network at run-time. The agent code is polymorphic and hardly detectable by AV and HIDS. The communication is covered and obfuscated within the HTTP protocol using steganographic techniques.

### Modules development

Weevely also provides python API which can be used to develop your own module to implement internal audit, account enumerator, sensitive data scraper, network scanner, make the modules work as a HTTP or SQL client and do a whole lot of other cool stuff.

> If you are a developer or a curious user and desire to contribute, you can to start reading the tutorial [Developing a new module ](https://github.com/epinna/weevely3/wiki/developing-a-new-module) and the [TODO list](https://github.com/epinna/weevely3/issues/1).
