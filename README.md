# Push to Status Check-Protected Branches - GitHub Action

Push commit(s) to a branch protected by required status checks by creating a temporary branch, where status checks are run, before fast-forward merging it into the protected branch, finally removing the temporary branch.

In order to perform commits prior to the push updates, you should pass a sh script to `changes`.
The name should be a complete relative path from the root of the repository (on GitHub) to the file.
See below for an example.

## Update your workflow

To successfully have the required status checks run on the temporary branch, you need to add it to the workflow(s) that is/are responsible for the required status checks.

In order to not have to continuously update the yml file(s), the temporary branches all have the same prefix: `push-action/`.
The complete name is `push-action/<RUN_ID>/<UUID>`, where `<RUN_ID>` is the unique GitHub Actions run ID for the current workflow run, and the `<UUID>` is generated using `uuidgen` from the `uuid-runtime` library.

Getting back to adding the temporary branch(es) to your workflow's yml file, it can be done like so:

```yml
on:
  push:
    branches:
      - 'push-action/**'
```

An example can also be seen in this workflow's own [test workflow](.github/workflows/test_status_checks.yml).

## Notes on `token`

If you are using this action to push to a GitHub [protected branch](https://help.github.com/en/github/administering-a-repository/about-protected-branches), you _need_ to pass a [personal access token (PAT)](https://help.github.com/en/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line), preferrably as a [secret](https://help.github.com/en/actions/configuring-and-managing-workflows/creating-and-storing-encrypted-secrets), to the `token` input.
This can be done as such:

```yml
name: Pushing to a protected branch
uses: CasperWA/push-protected@v1
with:
  token: '${{ secrets.PUSH_TO_PROTECTED_BRANCH }}'
  branch: 'protected'
  changes: .github/workflows/update_changelog.sh
```

**Note**: If you are _not_ pushing to a protected branch, you can instead use the [`GITHUB_TOKEN`](https://help.github.com/en/actions/configuring-and-managing-workflows/authenticating-with-the-github_token) secret, which is auto-generated when you use GitHub Actions.

The reason why you can not use the `GITHUB_TOKEN` secret when pushing to a branch that is protected by required status checks, is that using this as authentication does not trigger any webhook events, such as 'push', 'pull_request', etc.
This event trigger is a **MUST** for starting the required status checks on the temporary branch, which are necessary to run in order to be able to push the changes into the desired branch.

The PAT should have a scope appropriate to your repository:

- Private: _repo_
- Public: *public_repo*

It is recommended to not add unneccessary scopes to a PAT that are not needed for its intended purpose.

## Inputs

| Name | Description | Required | Default |
|:---:|:---|:---|:---:|
| **`token`** | Token for the repo. Used for authentication and starting 'push' hooks. See above for notes on this input. | `True` | |
| `repository` | Repository name to push to. Default or empty value represents current github repository (${GITHUB_REPOSITORY}). | `False` | `${{ github.repository }}` |
| `branch` | Target branch for the push. | `False` | `master` |
| `changes` | Shell script to run in the target repository root prior to the push. NOTE: Unrelated to prior workflow jobs and steps. MUST be a file in the repository that spawns the workflow. MUST be a relative path from the repository root, e.g., `.github/workflows/changes.sh`. | `False` | `` |
| `interval` | Time interval (in seconds) between each new check, when waiting for status checks to complete. | `False` | `30` |
| `timeout` | Time (in minutes) of how long the action should run before timing out, waiting for status checks to complete. | `False` | `15` |

## License

[MIT License](LICENSE)
