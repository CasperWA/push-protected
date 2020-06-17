# Push with Status Checks GitHub Action

Push commit(s) to a protected branch by creating a temporary branch, where status checks are run, before pushing into the protected branch and removing the temporary branch.

In order to most easy perform commits prior to the push updates, you should pass a sh script to `changes`.

## Inputs

| Name | Description | Required | Default |
|:---:|:---|:---|:---:|
| **`github_token`** | Token for the repo. Can be passed in using ${{ secrets.GITHUB_TOKEN }}. | `True` | |
| `repository` | Repository name to push to. Default or empty value represents current github repository (${GITHUB_REPOSITORY}). | `False` | `${{ github.repository }}` |
| `branch` | Target branch for the push. | `False` | `master` |
| `changes` | Shell script to run in the target repository root prior to the push. NOTE: Unrelated to prior workflow jobs and steps. MUST be a file in the repository that spawns the workflow. MUST be a relative path from the repository root, e.g., `.github/workflows/changes.sh`. | `False` | `` |

## License

[MIT License](LICENSE)
