# Changelog

## [v2.10.0](https://github.com/CasperWA/push-protected/tree/v2.10.0) (2022-04-14)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v2.9.0...v2.10.0)

**Fixed bugs:**

- GH GraphQL variable update for auto-merge workflow [\#100](https://github.com/CasperWA/push-protected/issues/100)

**Closed issues:**

- Looks like git update for CVE-2022-24765 broke the action [\#114](https://github.com/CasperWA/push-protected/issues/114)

**Merged pull requests:**

- Add `/github/workspace/ to git safe.directory [\#115](https://github.com/CasperWA/push-protected/pull/115) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#113](https://github.com/CasperWA/push-protected/pull/113) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#112](https://github.com/CasperWA/push-protected/pull/112) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#110](https://github.com/CasperWA/push-protected/pull/110) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#106](https://github.com/CasperWA/push-protected/pull/106) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#104](https://github.com/CasperWA/push-protected/pull/104) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#103](https://github.com/CasperWA/push-protected/pull/103) ([CasperWA](https://github.com/CasperWA))
- Use `ID!` type instead of `String!` [\#101](https://github.com/CasperWA/push-protected/pull/101) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#98](https://github.com/CasperWA/push-protected/pull/98) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#97](https://github.com/CasperWA/push-protected/pull/97) ([CasperWA](https://github.com/CasperWA))

## [v2.9.0](https://github.com/CasperWA/push-protected/tree/v2.9.0) (2022-01-17)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v2.8.0...v2.9.0)

**Implemented enhancements:**

- Warn or error upon using token without proper rights [\#94](https://github.com/CasperWA/push-protected/issues/94)
- Add `debug` option [\#93](https://github.com/CasperWA/push-protected/issues/93)

**Closed issues:**

- Not clear which scope should I use to enable `unprotect_reviews` option [\#60](https://github.com/CasperWA/push-protected/issues/60)

**Merged pull requests:**

- Check permission [\#95](https://github.com/CasperWA/push-protected/pull/95) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#92](https://github.com/CasperWA/push-protected/pull/92) ([CasperWA](https://github.com/CasperWA))

## [v2.8.0](https://github.com/CasperWA/push-protected/tree/v2.8.0) (2022-01-03)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v2.7.0...v2.8.0)

**Implemented enhancements:**

- Update this repository's default branch to `main` [\#84](https://github.com/CasperWA/push-protected/issues/84)
- Change default branch name to match GitHub [\#80](https://github.com/CasperWA/push-protected/issues/80)

**Fixed bugs:**

- Force pushing tags when updating `master` [\#88](https://github.com/CasperWA/push-protected/issues/88)
- Problem with CI [\#86](https://github.com/CasperWA/push-protected/issues/86)

**Merged pull requests:**

- Force update `master` tag [\#89](https://github.com/CasperWA/push-protected/pull/89) ([CasperWA](https://github.com/CasperWA))
- Fix CI runs for `main` updates [\#87](https://github.com/CasperWA/push-protected/pull/87) ([CasperWA](https://github.com/CasperWA))
- Finish update to `main` with `master` tag [\#85](https://github.com/CasperWA/push-protected/pull/85) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#82](https://github.com/CasperWA/push-protected/pull/82) ([CasperWA](https://github.com/CasperWA))
- Use `main` as default `branch` value instead of `master` [\#81](https://github.com/CasperWA/push-protected/pull/81) ([CasperWA](https://github.com/CasperWA))

## [v2.7.0](https://github.com/CasperWA/push-protected/tree/v2.7.0) (2021-12-15)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v2.6.0...v2.7.0)

**Implemented enhancements:**

- Consider adding `ref` [\#61](https://github.com/CasperWA/push-protected/issues/61)

**Fixed bugs:**

- Finding the "previous version" for adding changelog info to release not working [\#77](https://github.com/CasperWA/push-protected/issues/77)

**Merged pull requests:**

- Add `ref` argument [\#79](https://github.com/CasperWA/push-protected/pull/79) ([CasperWA](https://github.com/CasperWA))
- Exclude `ci_test` and vMAJOR tags for changelog gen [\#78](https://github.com/CasperWA/push-protected/pull/78) ([CasperWA](https://github.com/CasperWA))

## [v2.6.0](https://github.com/CasperWA/push-protected/tree/v2.6.0) (2021-12-08)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v2.5.0...v2.6.0)

**Implemented enhancements:**

- Immediately show print statements [\#75](https://github.com/CasperWA/push-protected/pull/75) ([CasperWA](https://github.com/CasperWA))
- Update pre-commit [\#58](https://github.com/CasperWA/push-protected/pull/58) ([CasperWA](https://github.com/CasperWA))
- Automate dependabot more [\#57](https://github.com/CasperWA/push-protected/pull/57) ([CasperWA](https://github.com/CasperWA))

**Fixed bugs:**

- Correct target branch for dependabot [\#71](https://github.com/CasperWA/push-protected/issues/71)
- `actions/checkout@v1` still checking out wrong commit SHA [\#67](https://github.com/CasperWA/push-protected/issues/67)
- Not properly reset to HEAD commit of remote branch [\#63](https://github.com/CasperWA/push-protected/issues/63)
- unprotect\_reviews not doing its job [\#54](https://github.com/CasperWA/push-protected/issues/54)

**Closed issues:**

- Not able to use your action due to a fatal error [\#59](https://github.com/CasperWA/push-protected/issues/59)
- Update README - user admin rights [\#55](https://github.com/CasperWA/push-protected/issues/55)

**Merged pull requests:**

- Update dependencies [\#76](https://github.com/CasperWA/push-protected/pull/76) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#73](https://github.com/CasperWA/push-protected/pull/73) ([CasperWA](https://github.com/CasperWA))
- Change dependabot PRs target to ci/dependabot-updates [\#72](https://github.com/CasperWA/push-protected/pull/72) ([CasperWA](https://github.com/CasperWA))
- Use v1 for resetting in v1 CI section [\#68](https://github.com/CasperWA/push-protected/pull/68) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#66](https://github.com/CasperWA/push-protected/pull/66) ([CasperWA](https://github.com/CasperWA))
- Use GITHUB\_REF instead of github.sha [\#65](https://github.com/CasperWA/push-protected/pull/65) ([CasperWA](https://github.com/CasperWA))
- Solve issue with checkout v1 action [\#64](https://github.com/CasperWA/push-protected/pull/64) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#62](https://github.com/CasperWA/push-protected/pull/62) ([CasperWA](https://github.com/CasperWA))
- Extend scope and rights mentions in README [\#56](https://github.com/CasperWA/push-protected/pull/56) ([CasperWA](https://github.com/CasperWA))

## [v2.5.0](https://github.com/CasperWA/push-protected/tree/v2.5.0) (2021-10-13)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v2.4.1...v2.5.0)

**Implemented enhancements:**

- Respect local changes [\#52](https://github.com/CasperWA/push-protected/issues/52)

**Merged pull requests:**

- Respect local state [\#53](https://github.com/CasperWA/push-protected/pull/53) ([CasperWA](https://github.com/CasperWA))

## [v2.4.1](https://github.com/CasperWA/push-protected/tree/v2.4.1) (2021-10-04)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v2.4.0...v2.4.1)

**Implemented enhancements:**

- Use more action-specific local bash variable names [\#50](https://github.com/CasperWA/push-protected/issues/50)

**Merged pull requests:**

- Action-specific variable names [\#51](https://github.com/CasperWA/push-protected/pull/51) ([CasperWA](https://github.com/CasperWA))
- Update pre-commit requirement from ~=2.13 to ~=2.15 [\#49](https://github.com/CasperWA/push-protected/pull/49) ([CasperWA](https://github.com/CasperWA))

## [v2.4.0](https://github.com/CasperWA/push-protected/tree/v2.4.0) (2021-08-04)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v2.3.0...v2.4.0)

**Closed issues:**

- This triggers another on.push action [\#42](https://github.com/CasperWA/push-protected/issues/42)

**Merged pull requests:**

- Test the `tags` option [\#46](https://github.com/CasperWA/push-protected/pull/46) ([CasperWA](https://github.com/CasperWA))
- Fixing issue that tags are removed before they can be pushed [\#45](https://github.com/CasperWA/push-protected/pull/45) ([THuppke](https://github.com/THuppke))
- Update requests requirement from ~=2.25 to ~=2.26 [\#44](https://github.com/CasperWA/push-protected/pull/44) ([dependabot[bot]](https://github.com/apps/dependabot))
- Update invoke requirement from ~=1.5 to ~=1.6 [\#43](https://github.com/CasperWA/push-protected/pull/43) ([dependabot[bot]](https://github.com/apps/dependabot))
- Update pre-commit requirement from ~=2.12 to ~=2.13 [\#41](https://github.com/CasperWA/push-protected/pull/41) ([dependabot[bot]](https://github.com/apps/dependabot))
- Update GH actions + pre-commit [\#40](https://github.com/CasperWA/push-protected/pull/40) ([CasperWA](https://github.com/CasperWA))
- Update pre-commit requirement from ~=2.10 to ~=2.12 [\#37](https://github.com/CasperWA/push-protected/pull/37) ([dependabot[bot]](https://github.com/apps/dependabot))

## [v2.3.0](https://github.com/CasperWA/push-protected/tree/v2.3.0) (2021-03-01)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v2.2.0...v2.3.0)

**Fixed bugs:**

- GitHub Actions checks not recognized as such [\#34](https://github.com/CasperWA/push-protected/issues/34)

**Merged pull requests:**

- Loosen determination if a branch is protected + up default sleep [\#35](https://github.com/CasperWA/push-protected/pull/35) ([CasperWA](https://github.com/CasperWA))
- Update pre-commit requirement from ~=2.9 to ~=2.10 [\#33](https://github.com/CasperWA/push-protected/pull/33) ([dependabot[bot]](https://github.com/apps/dependabot))
- Update dependencies [\#32](https://github.com/CasperWA/push-protected/pull/32) ([CasperWA](https://github.com/CasperWA))
- Update requests requirement from ~=2.24 to ~=2.25 [\#29](https://github.com/CasperWA/push-protected/pull/29) ([dependabot[bot]](https://github.com/apps/dependabot))

## [v2.2.0](https://github.com/CasperWA/push-protected/tree/v2.2.0) (2020-11-05)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v2.1.1...v2.2.0)

**Implemented enhancements:**

- Don't push branch if there's no new commits [\#27](https://github.com/CasperWA/push-protected/issues/27)

**Merged pull requests:**

- Ensure no push if there are no changes [\#28](https://github.com/CasperWA/push-protected/pull/28) ([CasperWA](https://github.com/CasperWA))

## [v2.1.1](https://github.com/CasperWA/push-protected/tree/v2.1.1) (2020-11-04)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v2.1.0...v2.1.1)

**Fixed bugs:**

- Space missing [\#24](https://github.com/CasperWA/push-protected/issues/24)

**Merged pull requests:**

- Fix line, inserting necessary space [\#25](https://github.com/CasperWA/push-protected/pull/25) ([CasperWA](https://github.com/CasperWA))
- Update pre-commit requirement from ~=2.7 to ~=2.8 [\#23](https://github.com/CasperWA/push-protected/pull/23) ([dependabot[bot]](https://github.com/apps/dependabot))

## [v2.1.0](https://github.com/CasperWA/push-protected/tree/v2.1.0) (2020-10-29)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v2.0.0...v2.1.0)

**Fixed bugs:**

- `tags` option doesn't also push commits [\#18](https://github.com/CasperWA/push-protected/issues/18)

**Merged pull requests:**

- Remove use of `global` [\#22](https://github.com/CasperWA/push-protected/pull/22) ([CasperWA](https://github.com/CasperWA))
- Update names for checkout@v1 CI tests [\#21](https://github.com/CasperWA/push-protected/pull/21) ([CasperWA](https://github.com/CasperWA))
- New release workflow [\#20](https://github.com/CasperWA/push-protected/pull/20) ([CasperWA](https://github.com/CasperWA))
- Move pushing tags to Bash function [\#19](https://github.com/CasperWA/push-protected/pull/19) ([CasperWA](https://github.com/CasperWA))

## [v2.0.0](https://github.com/CasperWA/push-protected/tree/v2.0.0) (2020-10-29)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v1.0.1...v2.0.0)

**Implemented enhancements:**

- Utilize that the workdir is the current checked out repository [\#15](https://github.com/CasperWA/push-protected/issues/15)

**Merged pull requests:**

- Update to v2 [\#17](https://github.com/CasperWA/push-protected/pull/17) ([CasperWA](https://github.com/CasperWA))
- Utilize local changes instead of downloading external script [\#16](https://github.com/CasperWA/push-protected/pull/16) ([CasperWA](https://github.com/CasperWA))

## [v1.0.1](https://github.com/CasperWA/push-protected/tree/v1.0.1) (2020-09-15)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/v1.0.0...v1.0.1)

**Fixed bugs:**

- unprotect\_reviews: false not respected [\#8](https://github.com/CasperWA/push-protected/issues/8)

**Merged pull requests:**

- Update to v1.0.1 [\#14](https://github.com/CasperWA/push-protected/pull/14) ([CasperWA](https://github.com/CasperWA))
- Mention unconditional push triggers [\#13](https://github.com/CasperWA/push-protected/pull/13) ([CasperWA](https://github.com/CasperWA))
- Update dependencies [\#12](https://github.com/CasperWA/push-protected/pull/12) ([CasperWA](https://github.com/CasperWA))
- Handle unprotect\_reviews with case [\#9](https://github.com/CasperWA/push-protected/pull/9) ([CasperWA](https://github.com/CasperWA))

## [v1.0.0](https://github.com/CasperWA/push-protected/tree/v1.0.0) (2020-07-21)

[Full Changelog](https://github.com/CasperWA/push-protected/compare/d79a86d6ef61f063da2b56916508adb63c3836cd...v1.0.0)

**Merged pull requests:**

- Update README and dependencies [\#7](https://github.com/CasperWA/push-protected/pull/7) ([CasperWA](https://github.com/CasperWA))
- Add `sleep` option [\#6](https://github.com/CasperWA/push-protected/pull/6) ([CasperWA](https://github.com/CasperWA))
- Remove filtering for success in util funcs [\#5](https://github.com/CasperWA/push-protected/pull/5) ([CasperWA](https://github.com/CasperWA))
- Sleep 15s prior to waiting [\#4](https://github.com/CasperWA/push-protected/pull/4) ([CasperWA](https://github.com/CasperWA))
- Add 'extra\_data' input [\#3](https://github.com/CasperWA/push-protected/pull/3) ([CasperWA](https://github.com/CasperWA))
- Remove all mentions of initial\_work branch [\#2](https://github.com/CasperWA/push-protected/pull/2) ([CasperWA](https://github.com/CasperWA))
- Initial work [\#1](https://github.com/CasperWA/push-protected/pull/1) ([CasperWA](https://github.com/CasperWA))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
