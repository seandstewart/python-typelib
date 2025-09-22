SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:

MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

RUN_PREFIX := uv run --

# region: environment

quickstart: setup-uv install  ## Bootstrap your local environment for development.
.PHONY: quickstart

setup-uv:  ## Set up your poetry installation and ensure it's up-to-date.
	@curl -LsSf https://astral.sh/uv/install.sh | sh
	@uv self update
.PHONY: setup-uv

install:  ## Install or re-install your app's dependencies.
	@uv sync --all-extras --dev --locked
	@$(RUN_PREFIX) pre-commit install && $(RUN_PREFIX) pre-commit install-hooks
.PHONY: install

update:  ## Update app dependencies
	@uv sync --all-extras --dev
	@$(RUN_PREFIX) pre-commit autoupdate
.PHONY: update

# endregion
# region: dev

target ?= .
files ?= --all-files
ifneq ($(target), .)
	files := --files=$(target)
endif

# endregion
# region: ci

lint:  ## Run this app's linters. Target a specific file or directory with `target=path/...`.
	@$(RUN_PREFIX) pre-commit run --hook-stage=manual $(files)
.PHONY: lint

test: ## Run this app's tests with a test db. Target a specific path `target=path/...`.
	$(RUN_PREFIX) pytest $(target) $(TEST_ARGS)
.PHONY: test

TEST_ARGS ?=

rule ?= patch
ref ?= main


release-version:  ## Bump the version for this package.
	$(eval message := "Release $(next_version)")
	@git tag -a $(next_version) -m $(message)
	@git push --follow-tags origin $(ref)
.PHONY: release-version


BUMP_CMD := git-cliff --bumped-version -o -

report-version:  ## Show the current version of this library.
	@echo $(version)
.PHONY: report-version

docs-version:  ## Show the current version of this library as applicable for documentation.
	@echo $(docs_version)
.PHONY: docs-version

docs: ## Build the versioned documentation
	@$(RUN_PREFIX) mike deploy -u --push $(version) $(alias)
.PHONY: docs

VERSION_CMD ?= hatchling version
SED_CMD ?= sed -En
CI_FILTER ?= 's/^([[:digit:]]+.[[:digit:]]+.[[:digit:]]+).*$$/v\1/p'
DOCS_FILTER ?= 's/^([[:digit:]]+.[[:digit:]]+).*$$/v\1/p'
version ?= $(shell $(RUN_PREFIX) $(VERSION_CMD) | $(SED_CMD) $(CI_FILTER))
docs_version ?= $(shell $(RUN_PREFIX) $(VERSION_CMD) | $(SED_CMD) $(DOCS_FILTER))
next_version ?= $(shell $(RUN_PREFIX) $(BUMP_CMD))
alias ?= latest

changelog:  ## Compile the latest changelog for the current branch.
	@$(RUN_PREFIX) git-cliff --bump
	@git add docs/changelog.md
	@git commit -m "[skip ci] Update changelog." --allow-empty
.PHONY: changelog

release-notes:  ## Compile release notes for VCS
	@$(RUN_PREFIX) git-cliff --bump --unreleased -o release-notes.md
.PHONY: release-notes

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
