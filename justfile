set shell := ["bash", "-c"]
set quiet

NAME := "weevely"
DATE := "2025-06-04"

# This thing
help:
	#!/bin/bash
	echo -e "{{YELLOW}}[+] {{MAGENTA}}{{NAME}} {{BLUE}}{{DATE}}{{NORMAL}}"
	echo -e "{{YELLOW}}[*] usage: {{GREEN}}just <target>{{NORMAL}}"
	just --list --list-heading "" --unsorted

# install in editable mode
dev:
	#!/bin/bash
	echo -e "{{YELLOW}}[+] {{MAGENTA}}{{NAME}} {{BLUE}}{{DATE}}{{NORMAL}}"
	uv tool install -e . --force

# uninstall package
uninstall:
	#!/bin/bash
	echo -e "{{YELLOW}}[+] {{MAGENTA}}{{NAME}} {{BLUE}}{{DATE}}{{NORMAL}}"
	uv tool uninstall weevely
