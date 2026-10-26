# [2.4.0](https://github.com/IBM/data-intelligence-sdk/compare/v2.3.0...v2.4.0) (2026-10-26)


### Features

* **examples:** add extract_custom_properties, extract_target_info, is_valid_draft_id, get_draft_contract_info to contract_utils.py ([778a37a](https://github.com/IBM/data-intelligence-sdk/commit/778a37a71c8f3f4e80792d8d165a621d13df5d51))
* **examples:** handle catalog: prefixed contract pairs in save_test_results.py ([67ceed0](https://github.com/IBM/data-intelligence-sdk/commit/67ceed0fa9681295c47d90b06a051a826c85d129))
* **examples:** route DPH contracts to catalog and link to draft in create_contract.py ([ae20731](https://github.com/IBM/data-intelligence-sdk/commit/ae2073153c9084b03b7883f427f1f0581227e087))
* **examples:** validate DPH draftId format and draft existence in validate_contract.py ([50ca7ee](https://github.com/IBM/data-intelligence-sdk/commit/50ca7eef1c3e7856ace6e2ac66d0d022d5de0e70))

# [2.3.0](https://github.com/IBM/data-intelligence-sdk/compare/v2.2.1...v2.3.0) (2026-10-15)


### Features

* update contract defintions (already merged, missed important change) ([f51abed](https://github.com/IBM/data-intelligence-sdk/commit/f51abed82d925a29e866a637f54d7edff15b9e82))

## [2.2.1](https://github.com/IBM/data-intelligence-sdk/compare/v2.2.0...v2.2.1) (2026-09-03)


### Bug Fixes

* Patch CVEs for idna and pyjwt ([a973d2e](https://github.com/IBM/data-intelligence-sdk/commit/a973d2e139c93e2d774d076a3cd24ee4e747cb03))

# [2.2.0](https://github.com/IBM/data-intelligence-sdk/compare/v2.1.0...v2.2.0) (2026-08-27)


### Features

* Merge pull request [#26](https://github.com/IBM/data-intelligence-sdk/issues/26) from IBM/data-contract-sdk ([c49a1a3](https://github.com/IBM/data-intelligence-sdk/commit/c49a1a35ed7e045c40b794af01a2e79df4eefb9e))

# [2.1.0](https://github.com/IBM/data-intelligence-sdk/compare/v2.0.0...v2.1.0) (2026-05-29)


### Features

* **dq:** Sync from enterprise cf57469 on 2026-05-20 ([8f0474a](https://github.com/IBM/data-intelligence-sdk/commit/8f0474ac4c8890bc1171367f616a32f7c900fdbb))

# [2.1.0-rc.1](https://github.com/IBM/data-intelligence-sdk/compare/v2.0.0...v2.1.0-rc.1) (2026-05-20)


### Features

* **dq:** Sync from enterprise cf57469 on 2026-05-20 ([8f0474a](https://github.com/IBM/data-intelligence-sdk/commit/8f0474ac4c8890bc1171367f616a32f7c900fdbb))

# [2.0.0](https://github.com/IBM/data-intelligence-sdk/compare/v1.0.0...v2.0.0) (2026-04-23)


* Upgrade to version 2.0.0 ([#13](https://github.com/IBM/data-intelligence-sdk/issues/13)) ([41f25ce](https://github.com/IBM/data-intelligence-sdk/commit/41f25cefc349a9d2add7d99bc94945d123104ca1)), closes [#7](https://github.com/IBM/data-intelligence-sdk/issues/7)


### BREAKING CHANGES

* Bug fixes for Data Quality and addition of Data Product Hub modules

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* fix relative path of Actions scripts

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* fix script condition

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* fix script condition again

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* add missing Makefile and fix documentation

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* add dq tests and upgrade python

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* try to extend build timeout

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* upgrade to python 3.10 as 3.9 is EOL

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* modify constraint_model to use custom StrEnum in python 3.10

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* add pylint

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* skip linting until ready

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* make sure to build before checking

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

# [2.0.0-rc.1](https://github.com/IBM/data-intelligence-sdk/compare/v1.0.0...v2.0.0-rc.1) (2026-04-22)


### Perf

* Sync from enterprise 4e91aee (via .ignore) on 2026-04-17 ([#7](https://github.com/IBM/data-intelligence-sdk/issues/7)) ([eeeffba](https://github.com/IBM/data-intelligence-sdk/commit/eeeffba17ce0e399446099d47352f7738259feae))


### BREAKING CHANGES

* Bug fixes for Data Quality and addition of Data Product Hub modules

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* fix relative path of Actions scripts

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* fix script condition

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* fix script condition again

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* add missing Makefile and fix documentation

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* add dq tests and upgrade python

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* try to extend build timeout

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* upgrade to python 3.10 as 3.9 is EOL

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* modify constraint_model to use custom StrEnum in python 3.10

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* add pylint

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* skip linting until ready

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

* make sure to build before checking

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>

# [1.0.0](https://github.com/IBM/data-intelligence-sdk/compare/v0.5.3...v1.0.0) (2026-03-17)


### Performance Improvements

* Empty commit ([5741e42](https://github.com/IBM/data-intelligence-sdk/commit/5741e42b1dad1d61836cfd4e7790f60fd5774ca9))
* fix version string ([#2](https://github.com/IBM/data-intelligence-sdk/issues/2)) ([d672e40](https://github.com/IBM/data-intelligence-sdk/commit/d672e40768419b84a5951af9328da9017c55d6d8))


### BREAKING CHANGES

* Initial release bump version 1.0.0

Signed-off-by: Koichi Nishitani <knish@jp.ibm.com>
