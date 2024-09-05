# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [v0.0.1](https://github.com/seandstewart/python-typelib/releases/tag/v0.0.1) - 2024-09-05

<small>[Compare with first commit](https://github.com/seandstewart/python-typelib/compare/ac01975a1a2d50a197716e9d5cfb03be13d26fa9...v0.0.1)</small>

### Features

- implement the top-level API ([611f590](https://github.com/seandstewart/python-typelib/commit/611f59049510fcea8d923683672be5e404cdb3c4) by Sean Stewart).
- rename some inspections and rework imports ([3a5946e](https://github.com/seandstewart/python-typelib/commit/3a5946e74463764d1b53332fe298f34caab56652) by Sean Stewart).
- re-organize utility modules ([5019468](https://github.com/seandstewart/python-typelib/commit/5019468518f27192d1bec4fe5a9835f13dd61048) by Sean Stewart).
- codec interface ([6996275](https://github.com/seandstewart/python-typelib/commit/69962756e54836735daf3a59da33b238e4ad3f34) by Sean Stewart).
- type-enforce signature binding ([a56418b](https://github.com/seandstewart/python-typelib/commit/a56418b0629706272c6f7599b7ad8e5f03bdbe8a) by Sean Stewart).
- add high-level API for creating marshal/unmarshal protocols ([2fa5345](https://github.com/seandstewart/python-typelib/commit/2fa53457423afc16004dbb5edba3c20b70f8a097) by Sean Stewart).
- Implement marshallers. ([ed159ef](https://github.com/seandstewart/python-typelib/commit/ed159ef10f90ea4e9a5ea89e3b2c62b03119a08c) by Sean Stewart).
- Support TypeAliasType ([e235f43](https://github.com/seandstewart/python-typelib/commit/e235f43f0e2322edc90526e6ba6c1af89abb3b7a) by Sean Stewart).
- Support for cyclic types. ([4422413](https://github.com/seandstewart/python-typelib/commit/44224130f5d129699652c59e6124e3164ffd4192) by Sean Stewart).
- Defining the unmarshal API. ([8117e0c](https://github.com/seandstewart/python-typelib/commit/8117e0c088c6de024f627e0a5aa17ccb731a68d9) by Sean Stewart).
- Better generics interface. ([0f96785](https://github.com/seandstewart/python-typelib/commit/0f9678560e7d3c5412704ac43763b94fee8d34ad) by Sean Stewart).
- Initial pass of complex types for unmarshalling. ([82b566c](https://github.com/seandstewart/python-typelib/commit/82b566c8715a346bde6ac59617b72f0313c0e994) by Sean Stewart).
- Unmarshallers for initial primitive types. ([1c6aa1c](https://github.com/seandstewart/python-typelib/commit/1c6aa1cead5b73a9da15dc26940e4909703ee4db) by Sean Stewart).
- Core utilities and graph resolver, with test coverage. ([108faa1](https://github.com/seandstewart/python-typelib/commit/108faa1a845775dbbc43bcf75289f8fc3a6921f1) by Sean Stewart).

### Bug Fixes

- treat sequences as unique from iterables in iteritems ([1f1b0fd](https://github.com/seandstewart/python-typelib/commit/1f1b0fdf85f2c13eec2682c35e1ea027c38f9f6c) by Sean Stewart).
- update param name for type input in dateparse ([1779b4e](https://github.com/seandstewart/python-typelib/commit/1779b4e52c0c51673160cc81d66e4daf980b9434) by Sean Stewart).
- weakref bug with slotted Codec ([0887083](https://github.com/seandstewart/python-typelib/commit/08870839b179ee0971810d3638e7b2c06b1f153d) by Sean Stewart).
- mypy type hinting for non py312 in compat.py ([b36c7d6](https://github.com/seandstewart/python-typelib/commit/b36c7d6d6c6c63496a0cbb041860a57d9f84d1fe) by Sean Stewart).
- use `datetime.timestamp` when converting date/time to numeric values ([ecdc908](https://github.com/seandstewart/python-typelib/commit/ecdc908c5d380291c25a0560c3b78f760d26d2ee) by Sean Stewart).
- reliable UTC timestamps for date objects. ([582686d](https://github.com/seandstewart/python-typelib/commit/582686d51970b948249f334404c5bcc8fb8eb321) by Sean Stewart).
- use compat for future types. ([2e8aa24](https://github.com/seandstewart/python-typelib/commit/2e8aa2442aa60b0ce60d8f72e747f590fcb2a14f) by Sean Stewart).
- Fix type-hints for lower versions of python ([7c08c8c](https://github.com/seandstewart/python-typelib/commit/7c08c8cc8aa7f144a14479660985b80d3b439c31) by Sean Stewart).
- Fix type hints for marshalled values ([f4742e0](https://github.com/seandstewart/python-typelib/commit/f4742e0161042304b980bb2c69c3b0de65705eab) by Sean Stewart).
- Enforce utc for tz-naive datetime.date during number conversion ([afe79fb](https://github.com/seandstewart/python-typelib/commit/afe79fbbafef93fbd9aac9c5eaf146cebb78cb22) by Sean Stewart).
- The factory function can handle strings/forwardrefs. ([34dd7dd](https://github.com/seandstewart/python-typelib/commit/34dd7dd807e72e5a48b2652898c95c85ccec7110) by Sean Stewart).
- Tweaking root node assignment. ([6b1f141](https://github.com/seandstewart/python-typelib/commit/6b1f14136e356179c63fb5bd4c38849de493f025) by Sean Stewart).
- Fix passing var names to unmarshaller ([38c2002](https://github.com/seandstewart/python-typelib/commit/38c2002c6bd0a509a24ca73250bad5403994c620) by Sean Stewart).