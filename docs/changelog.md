# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.13][0.1.13] - 2025-09-17

### <!-- 7 -->⚙️ Miscellaneous Tasks
- Fix mypy analysis and lint tooling by @seandstewart


## [0.1.12][0.1.12] - 2025-02-09

### <!-- 10 -->💼 Other
- Fix signing and release creation by @seandstewart


## [0.1.11][0.1.11] - 2025-02-08

### <!-- 10 -->💼 Other
- Fix publication by @seandstewart


## [0.1.10][0.1.10] - 2025-02-08

### <!-- 10 -->💼 Other
- Turn on auto-tagging by @seandstewart
- Fix tag fetching by @seandstewart
- Cleanup bad tags by @seandstewart

### <!-- 7 -->⚙️ Miscellaneous Tasks
- Update CI/CD toolchain for uv and git-cliff by @seandstewart
- Re-work env checkout for uv in CI by @seandstewart
- Skip CI on changelog update by @seandstewart


## [0.1.9][0.1.9] - 2024-10-30

### <!-- 1 -->🐛 Bug Fixes
- Track "unwrapped" types during routine resolution by @seandstewart


## [0.1.8][0.1.8] - 2024-10-30

### <!-- 1 -->🐛 Bug Fixes
- Handle recursive and cyclic `TypeAliasType` by @seandstewart


## [0.1.7][0.1.7] - 2024-10-30

### <!-- 1 -->🐛 Bug Fixes
- Handle `TypeAliasType` within `TypeContext` lookups by @seandstewart


## [0.1.6][0.1.6] - 2024-10-30

### <!-- 1 -->🐛 Bug Fixes
- Unwrap `TypeAliasType` for all nested types in a type graph by @seandstewart

### <!-- 7 -->⚙️ Miscellaneous Tasks
- Tweaks to CI by @seandstewart


## [0.1.5][0.1.5] - 2024-10-30

### <!-- 1 -->🐛 Bug Fixes
- Extract the real `__value__` from a `TypeAliasType` when calling `origin(...)` by @seandstewart


## [0.1.4][0.1.4] - 2024-10-26

### <!-- 1 -->🐛 Bug Fixes
- Correct handling optional types by @seandstewart
- Remove use of `graphlib.TypeNode` in type context by @seandstewart


## [0.1.2][0.1.2] - 2024-10-16

### <!-- 1 -->🐛 Bug Fixes
- Inspect types when resolving field marshallers for structured types by @seandstewart
- Handle case where a resolved type reference can't match up to the original hint by @seandstewart

### <!-- 7 -->⚙️ Miscellaneous Tasks
- Reduce build matrix and fix GH release by @seandstewart
- Handle case where current commit is not the exact tag for a given release by @seandstewart
- Fix pipeline duplication by @seandstewart


## [0.1.1][0.1.1] - 2024-10-16

### <!-- 0 -->🚀 Features
- Support `enum.Enum` subtypes by @seandstewart

### <!-- 1 -->🐛 Bug Fixes
- Allow optional and union types to be marks as "stdlib" by @seandstewart

### <!-- 10 -->💼 Other
- Fix dist build and allow manual trigger for publishing the latest version by @seandstewart
- Fix wheel build by @seandstewart
- Fix wheel build - inputs, not matrix by @seandstewart
- Fix wheel build - inputs, not matrix by @seandstewart
- Update publish permissions and default to tag name if github.ref is missing by @seandstewart
- Fix artifact download for github release, allow failure for pypi publish by @seandstewart

### <!-- 3 -->📚 Documentation
- Fix license shield by @seandstewart
- Add site description by @seandstewart


## [0.1.0][0.1.0] - 2024-09-05

### <!-- 0 -->🚀 Features
- Core utilities and graph resolver, with test coverage. by @seandstewart
- Unmarshallers for initial primitive types. by @seandstewart
- Initial pass of complex types for unmarshalling. by @seandstewart
- Better generics interface. by @seandstewart
- Defining the unmarshal API. by @seandstewart
- Support for cyclic types. by @seandstewart
- Support TypeAliasType by @seandstewart
- Implement marshallers. by @seandstewart
- Add high-level API for creating marshal/unmarshal protocols by @seandstewart
- Type-enforce signature binding by @seandstewart
- Codec interface by @seandstewart
- Re-organize utility modules by @seandstewart
- Rename some inspections and rework imports by @seandstewart
- Implement the top-level API by @seandstewart

### <!-- 1 -->🐛 Bug Fixes
- Fix passing var names to unmarshaller by @seandstewart
- Tweaking root node assignment. by @seandstewart
- The factory function can handle strings/forwardrefs. by @seandstewart
- Enforce utc for tz-naive datetime.date during number conversion by @seandstewart
- Fix type hints for marshalled values by @seandstewart
- Fix type-hints for lower versions of python by @seandstewart
- Use compat for future types. by @seandstewart
- Reliable UTC timestamps for date objects. by @seandstewart
- Use `datetime.timestamp` when converting date/time to numeric values by @seandstewart
- Mypy type hinting for non py312 in compat.py by @seandstewart
- Mypy type hinting for non py312 in compat.py by @seandstewart
- Weakref bug with slotted Codec by @seandstewart
- Update param name for type input in dateparse by @seandstewart
- Treat sequences as unique from iterables in iteritems by @seandstewart

### <!-- 10 -->💼 Other
- Pycharm run configurations by @seandstewart
- Use run prefix when building docs and changelog by @seandstewart
- GIT_COMMITTER_* env vars are ignored by git by @seandstewart
- Fix git add when generating changelog by @seandstewart
- Use private app instead of public bot in CI by @seandstewart
- Fix env var reference by @seandstewart
- Pass release app variables as inputs by @seandstewart
- Only pass the secret for the release bot by @seandstewart
- Hard-code the app id by @seandstewart
- Extract token setup from bootstrap composite action by @seandstewart
- Set the git user info in bootstrap by @seandstewart
- Update dependencies by @seandstewart
- Pull latest from main and gh-pages before building docs by @seandstewart
- Enable fast-forward on pull by @seandstewart
- Toggle fetch depth on checkout to restore changelog by @seandstewart
- Don't refresh remotes by @seandstewart
- Update linters and fix commit command for changelog by @seandstewart
- Update linters and fix commit command for changelog by @seandstewart
- Drop unnecessary inputs by @seandstewart
- Fix version tagging by @seandstewart

### <!-- 3 -->📚 Documentation
- Docstrings for everything! by @seandstewart
- Extended docstrings for unmarshalling. by @seandstewart
- Extended docstrings for the marshal API. by @seandstewart
- Cleanup some bad refs by @seandstewart
- Docstring coverage for ABCs by @seandstewart
- Update README.md and docstrings by @seandstewart
- Fix a few refs in docstrings by @seandstewart
- Scaffold support for api docs. by @seandstewart
- Grammar by @seandstewart
- Add examples to serdes docstrings by @seandstewart
- Adjust file generation script by @seandstewart
- Fix some code refs by @seandstewart
- Drop nav generation from docs page gen by @seandstewart
- Complete first pass at documentation by @seandstewart
- Prepping docs and actions for initial release by @seandstewart
- Bug fixes for building docs by @seandstewart
- Allow empty changes when building changelog by @seandstewart
- Fix version provider configuration by @seandstewart
- Re-order tip and re-work some titles by @seandstewart
- Include nav footer by @seandstewart

### <!-- 6 -->🧪 Testing
- Test coverage for unmarshallers. by @seandstewart
- Tests for unmarshal API by @seandstewart
- Try xfail for 3.12-only test by @seandstewart
- Fix refs test helper by @seandstewart
- Introduce tox for local testing of all envs and shore up multi-version support by @seandstewart
- Shore up support for windows in tests by @seandstewart
- Shore up support for windows in tests by @seandstewart
- Add coverage for kwargs-only and args-only bindings by @seandstewart

### <!-- 7 -->⚙️ Miscellaneous Tasks
- Separate commands for lint. by @seandstewart
- Update development status by @seandstewart
- Switch to pre-commit for lint and format by @seandstewart
- Set up initial pass at CI/CD by @seandstewart
- Fix test matrix reference by @seandstewart
- Fix matrix os ref by @seandstewart
- Fix mypy args and CI job names. by @seandstewart
- Fix cache key by @seandstewart
- Update dependencies by @seandstewart
- Lint commit messages by @seandstewart
- Make lint runnable from tox by @seandstewart
- Troubleshoot codecov by @seandstewart
- Fix secrets inheritance by @seandstewart
- Type-checker support when used as a library by @seandstewart
- README.md and package name by @seandstewart
- Revert project name by @seandstewart
- Rename `format.py` to `interchange.py` by @seandstewart
- Drop displaying installed dependencies by @seandstewart
- Split tag creation and release publication workflows by @seandstewart
- Split changelog creation into separate workflow by @seandstewart
- Set default shell for all workflows by @seandstewart

## New Contributors
* @invalid-email-address made their first contribution
* @seandstewart made their first contribution

[0.1.13]: https://github.com/seandstewart/python-typelib/compare/v0.1.12..v0.1.13
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
