SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:

MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

ifeq ($(VIRTUAL_ENV), )
	RUN_PREFIX := poetry run
else
	RUN_PREFIX :=
endif


# region: environment

bootstrap: setup-poetry update install .git/hooks/pre-commit  ## Bootstrap your local environment for development.
.PHONY: bootstrap

setup-poetry:  ## Set up your poetry installation and ensure it's up-to-date.
	@poetry self update -q
.PHONY: setup-poetry

install:  ## Install or re-install your app's dependencies.
	@poetry install
.PHONY: install

.git/hooks/pre-commit: .pre-commit  ## Install or re-install any commit hooks.
	@cp .pre-commit .git/hooks/pre-commit

update:  ## Update app dependencies
	@poetry update
.PHONY: update

# endregion
# region: dev

format:  ## Manually run code-formatters for the app.
	$(RUN_PREFIX) ruff format $(target) --config=pyproject.toml
	$(RUN_PREFIX) ruff check $(target) --fix --config=pyproject.toml
.PHONY: format

# endregion
# region: ci

lint:  ## Run this app's linters. Target a specific file or directory with `target=path/...`.
	$(RUN_PREFIX) ruff check $(target) --config=pyproject.toml
	$(RUN_PREFIX) mypy $(target) --config-file=pyproject.toml
.PHONY: lint

test: ## Run this app's tests with a test db. Target a specific path `target=path/...`.
	$(RUN_PREFIX) pytest $(target) $(TEST_ARGS)
.PHONY: test

TEST_ARGS ?= --cov --cov-config=.coveragerc --cov-report=xml --cov-report=term --junit-xml=junit.xml

bump-version:  ## Bump the version for this package.
	@poetry version $(rule)
.PHONY: bump-version

rule ?= patch

tag-version: bump-version  ## Bump and tag a new version for this package
	@$(eval version := $(shell poetry version -s))
	@$(eval message := [skip ci] Release $(version))
	@git add pyproject.toml && @git commit -m "$(message)"
	@git tag v$(version) -m "$(message)"
.PHONY: tag-version

report-version:  ## Show the current version of this application.
	@poetry version
.PHONY: report-version

target ?= .

# endregion

.PHONY: help
help: ## Display this help screen.
	@printf "$(BOLD)$(ITALIC)$(MAGENTA)✨  Make typelib with Make. ✨ $(RESET)\n"
	@printf "\n$(ITALIC)$(GREEN)Supported Commands: $(RESET)\n"
	@grep -E '^[a-zA-Z0-9._-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)$(MSGPREFIX) %-$(MAX_CHARS)s$(RESET) $(ITALIC)$(DIM)%s$(RESET)\n", $$1, $$2}'

.DEFAULT_GOAL := help

# Messaging
###
MAX_CHARS ?= 24
BOLD := \033[1m
RESET_BOLD := \033[21m
ITALIC := \033[3m
RESET_ITALIC := \033[23m
DIM := \033[2m
BLINK := \033[5m
RESET_BLINK := \033[25m
RED := \033[1;31m
GREEN := \033[32m
YELLOW := \033[1;33m
MAGENTA := \033[1;35m
CYAN := \033[36m
RESET := \033[0m
MSGPREFIX ?=   »
