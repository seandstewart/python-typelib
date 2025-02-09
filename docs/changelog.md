# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.12][0.1.12] - 2025-02-09

### <!-- 10 -->💼 Other
- Fix signing and release creation


## [0.1.11][0.1.11] - 2025-02-08

### <!-- 10 -->💼 Other
- Fix publication


## [0.1.10][0.1.10] - 2025-02-08

### <!-- 10 -->💼 Other
- Turn on auto-tagging
- Fix tag fetching
- Cleanup bad tags

### <!-- 7 -->⚙️ Miscellaneous Tasks
- Update CI/CD toolchain for uv and git-cliff
- Re-work env checkout for uv in CI
- Skip CI on changelog update


## [0.1.9][0.1.9] - 2024-10-30

### <!-- 1 -->🐛 Bug Fixes
- Track "unwrapped" types during routine resolution


## [0.1.8][0.1.8] - 2024-10-30

### <!-- 1 -->🐛 Bug Fixes
- Handle recursive and cyclic `TypeAliasType`


## [0.1.7][0.1.7] - 2024-10-30

### <!-- 1 -->🐛 Bug Fixes
- Handle `TypeAliasType` within `TypeContext` lookups


## [0.1.6][0.1.6] - 2024-10-30

### <!-- 1 -->🐛 Bug Fixes
- Unwrap `TypeAliasType` for all nested types in a type graph

### <!-- 7 -->⚙️ Miscellaneous Tasks
- Tweaks to CI


## [0.1.5][0.1.5] - 2024-10-30

### <!-- 1 -->🐛 Bug Fixes
- Extract the real `__value__` from a `TypeAliasType` when calling `origin(...)`


## [0.1.4][0.1.4] - 2024-10-26

### <!-- 1 -->🐛 Bug Fixes
- Correct handling optional types
- Remove use of `graphlib.TypeNode` in type context


## [0.1.2][0.1.2] - 2024-10-16

### <!-- 1 -->🐛 Bug Fixes
- Inspect types when resolving field marshallers for structured types
- Handle case where a resolved type reference can't match up to the original hint

### <!-- 7 -->⚙️ Miscellaneous Tasks
- Reduce build matrix and fix GH release
- Handle case where current commit is not the exact tag for a given release
- Fix pipeline duplication


## [0.1.1][0.1.1] - 2024-10-16

### <!-- 0 -->🚀 Features
- Support `enum.Enum` subtypes

### <!-- 1 -->🐛 Bug Fixes
- Allow optional and union types to be marks as "stdlib"

### <!-- 10 -->💼 Other
- Fix dist build and allow manual trigger for publishing the latest version
- Fix wheel build
- Fix wheel build - inputs, not matrix
- Fix wheel build - inputs, not matrix
- Update publish permissions and default to tag name if github.ref is missing
- Fix artifact download for github release, allow failure for pypi publish

### <!-- 3 -->📚 Documentation
- Fix license shield
- Add site description


## [0.1.0][0.1.0] - 2024-09-05

### <!-- 0 -->🚀 Features
- Core utilities and graph resolver, with test coverage.
- Unmarshallers for initial primitive types.
- Initial pass of complex types for unmarshalling.
- Better generics interface.
- Defining the unmarshal API.
- Support for cyclic types.
- Support TypeAliasType
- Implement marshallers.
- Add high-level API for creating marshal/unmarshal protocols
- Type-enforce signature binding
- Codec interface
- Re-organize utility modules
- Rename some inspections and rework imports
- Implement the top-level API

### <!-- 1 -->🐛 Bug Fixes
- Fix passing var names to unmarshaller
- Tweaking root node assignment.
- The factory function can handle strings/forwardrefs.
- Enforce utc for tz-naive datetime.date during number conversion
- Fix type hints for marshalled values
- Fix type-hints for lower versions of python
- Use compat for future types.
- Reliable UTC timestamps for date objects.
- Use `datetime.timestamp` when converting date/time to numeric values
- Mypy type hinting for non py312 in compat.py
- Mypy type hinting for non py312 in compat.py
- Weakref bug with slotted Codec
- Update param name for type input in dateparse
- Treat sequences as unique from iterables in iteritems

### <!-- 10 -->💼 Other
- Pycharm run configurations
- Use run prefix when building docs and changelog
- GIT_COMMITTER_* env vars are ignored by git
- Fix git add when generating changelog
- Use private app instead of public bot in CI
- Fix env var reference
- Pass release app variables as inputs
- Only pass the secret for the release bot
- Hard-code the app id
- Extract token setup from bootstrap composite action
- Set the git user info in bootstrap
- Update dependencies
- Pull latest from main and gh-pages before building docs
- Enable fast-forward on pull
- Toggle fetch depth on checkout to restore changelog
- Don't refresh remotes
- Update linters and fix commit command for changelog
- Update linters and fix commit command for changelog
- Drop unnecessary inputs
- Fix version tagging

### <!-- 3 -->📚 Documentation
- Docstrings for everything!
- Extended docstrings for unmarshalling.
- Extended docstrings for the marshal API.
- Cleanup some bad refs
- Docstring coverage for ABCs
- Update README.md and docstrings
- Fix a few refs in docstrings
- Scaffold support for api docs.
- Grammar
- Add examples to serdes docstrings
- Adjust file generation script
- Fix some code refs
- Drop nav generation from docs page gen
- Complete first pass at documentation
- Prepping docs and actions for initial release
- Bug fixes for building docs
- Allow empty changes when building changelog
- Fix version provider configuration
- Re-order tip and re-work some titles
- Include nav footer

### <!-- 6 -->🧪 Testing
- Test coverage for unmarshallers.
- Tests for unmarshal API
- Try xfail for 3.12-only test
- Fix refs test helper
- Introduce tox for local testing of all envs and shore up multi-version support
- Shore up support for windows in tests
- Shore up support for windows in tests
- Add coverage for kwargs-only and args-only bindings

### <!-- 7 -->⚙️ Miscellaneous Tasks
- Separate commands for lint.
- Update development status
- Switch to pre-commit for lint and format
- Set up initial pass at CI/CD
- Fix test matrix reference
- Fix matrix os ref
- Fix mypy args and CI job names.
- Fix cache key
- Update dependencies
- Lint commit messages
- Make lint runnable from tox
- Troubleshoot codecov
- Fix secrets inheritance
- Type-checker support when used as a library
- README.md and package name
- Revert project name
- Rename `format.py` to `interchange.py`
- Drop displaying installed dependencies
- Split tag creation and release publication workflows
- Split changelog creation into separate workflow
- Set default shell for all workflows


[0.1.12]: https://github.com/seandstewart/python-typelib/compare/v0.1.11..v0.1.12
[0.1.11]: https://github.com/seandstewart/python-typelib/compare/v0.1.10..v0.1.11
[0.1.10]: https://github.com/seandstewart/python-typelib/compare/v0.1.9..v0.1.10
[0.1.9]: https://github.com/seandstewart/python-typelib/compare/v0.1.8..v0.1.9
[0.1.8]: https://github.com/seandstewart/python-typelib/compare/v0.1.7..v0.1.8
[0.1.7]: https://github.com/seandstewart/python-typelib/compare/v0.1.6..v0.1.7
[0.1.6]: https://github.com/seandstewart/python-typelib/compare/v0.1.5..v0.1.6
[0.1.5]: https://github.com/seandstewart/python-typelib/compare/v0.1.4..v0.1.5
[0.1.4]: https://github.com/seandstewart/python-typelib/compare/v0.1.2..v0.1.4
[0.1.2]: https://github.com/seandstewart/python-typelib/compare/v0.1.1..v0.1.2
[0.1.1]: https://github.com/seandstewart/python-typelib/compare/v0.1.0..v0.1.1

<!-- generated by git-cliff -->
