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
	uv tool install -e . --force

# uninstall package
uninstall:
	#!/bin/bash
	uv tool uninstall weevely

# format code
format:
	#!/bin/bash
	ruff format src

# clean build files
clean:
	#!/bin/bash
	rm -rf dist


# build packages
build:
	#!/bin/bash
	uv build --wheel

# install built whl packages
install-build: build
	#!/bin/bash
	uv tool install --force dist/*.whl
