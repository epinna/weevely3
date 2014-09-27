Weevely 
=======

> This is a complete rewrite of Weevely, and currently is a beta version. 
> Any module ported from the old version get close the first stable release. Any help is appreciated. Read below for further information.

Weevely is a PHP web shell that provides a weaponized telnet-like interface to administrate a remote web access.

Its modules extends the terminal providing a layer to interact to the target to administrate a web account, audit the target security, pivot deeper in the target network, and much more. It is an essential tool for web application post exploitation and access maintaining, even with heavily restricted remote environments. 

The modules feature:

* Weaponized Shell/PHP network console
* Common server misconfigurations auditing
* SQL console pivoting on target network 
* HTTP traffic proxy through target
* Mount target file system to local mount point
* Run scans or pivoted exploiting through target network
* File transfer from and to target
* Spawn reverse and direct TCP shells
* Bruteforce SQL accounts through target system users

The code is dynamically injected and so extended over the network at run-time. This keep a very small footprint backdoor, even providing an completely extensible environment. The backdoor agent code is polymorphic and hardly detectable from AV and HIDS, and the communication are covered and obfuscated within the HTTP protocol using steganographic techniques.

Weevely also provides python API which can be used to develop your own module to implement internal audit, account enumerator, sensitive data scraper, network scanner, make the modules work as a HTTP or SQL client and do a whole lot of other cool stuff.

#### This is still a version under heavy development and still some features are missing.

If you want to add a new module, or help us to port the old weevely modules, consult the [Wiki](https://github.com/epinna/weevely3/wikii) pages and the [Developing a new module](https://github.com/epinna/weevely3/wiki/developing-a-new-module) tutorial.
