#!/usr/bin/env bash
case ${INPUT_DEBUG} in
    y | Y | yes | Yes | YES | true | True | TRUE | on | On | ON)
        set -x
        ;;
    n | N | no | No | NO | false | False | FALSE | off | Off | OFF)
        ;;
    *)
        ;;
esac

set -e

# Utility functions
unprotect () {
    case ${INPUT_UNPROTECT_REVIEWS} in
        y | Y | yes | Yes | YES | true | True | TRUE | on | On | ON)
            if [ -n "${PUSH_PROTECTED_CHANGED_BRANCH}" ] && [ -n "${PUSH_PROTECTED_PROTECTED_BRANCH}" ]; then
                echo -e "\nRemove '${INPUT_BRANCH}' pull request review protection ..."
                push-action --token "${INPUT_TOKEN}" --ref "${INPUT_BRANCH}" --temp-branch "${PUSH_PROTECTED_TEMPORARY_BRANCH}" -- unprotect_reviews
                echo "Remove '${INPUT_BRANCH}' pull request review protection ... DONE!"
            fi
            ;;
        n | N | no | No | NO | false | False | FALSE | off | Off | OFF)
            ;;
        *)
            echo -e "\nNon-valid input for 'unprotect_review': ${INPUT_UNPROTECT_REVIEWS}. Will use default (false)."
            ;;
    esac
}
protect () {
    case ${INPUT_UNPROTECT_REVIEWS} in
        y | Y | yes | Yes | YES | true | True | TRUE | on | On | ON)
            if [ -n "${PUSH_PROTECTED_CHANGED_BRANCH}" ] && [ -n "${PUSH_PROTECTED_PROTECTED_BRANCH}" ]; then
                echo -e "\nRe-add '${INPUT_BRANCH}' pull request review protection ..."
                push-action --token "${INPUT_TOKEN}" --ref "${INPUT_BRANCH}" --temp-branch "${PUSH_PROTECTED_TEMPORARY_BRANCH}" -- protect_reviews
                echo "Re-add '${INPUT_BRANCH}' pull request review protection ... DONE!"
            fi
            ;;
        n | N | no | No | NO | false | False | FALSE | off | Off | OFF)
            ;;
        *)
            echo -e "\nNon-valid input for 'unprotect_review': ${INPUT_UNPROTECT_REVIEWS}. Will use default (false)."
            ;;
    esac
}
wait_for_checks() {
    if [ -n "${PUSH_PROTECTED_CHANGED_BRANCH}" ] && [ -n "${PUSH_PROTECTED_PROTECTED_BRANCH}" ]; then
        echo -e "\nWaiting for status checks to finish for '${PUSH_PROTECTED_TEMPORARY_BRANCH}' ..."
        # Sleep for 5 seconds to let the workflows start
        sleep ${INPUT_SLEEP}
        push-action --token "${INPUT_TOKEN}" --ref "${INPUT_BRANCH}" --temp-branch "${PUSH_PROTECTED_TEMPORARY_BRANCH}" --wait-timeout "${INPUT_TIMEOUT}" --wait-interval "${INPUT_INTERVAL}" -- wait_for_checks
        echo "Waiting for status checks to finish for '${PUSH_PROTECTED_TEMPORARY_BRANCH}' ... DONE!"
    fi
}
remove_remote_temp_branch() {
    if [ -n "${PUSH_PROTECTED_CHANGED_BRANCH}" ] && [ -n "${PUSH_PROTECTED_PROTECTED_BRANCH}" ]; then
        echo -e "\nRemoving temporary branch '${PUSH_PROTECTED_TEMPORARY_BRANCH}' ..."
        push-action --token "${INPUT_TOKEN}" --ref "${INPUT_BRANCH}" --temp-branch "${PUSH_PROTECTED_TEMPORARY_BRANCH}" -- remove_temp_branch
        echo "Removing temporary branch '${PUSH_PROTECTED_TEMPORARY_BRANCH}' ... DONE!"
    fi
}
push_tags() {
    if [ -n "${PUSH_PROTECTED_PUSH_TAGS}" ]; then
        echo -e "\nPushing tags ..."
        git push --tags ${PUSH_PROTECTED_FORCE_PUSH}
        echo "Pushing tags ... DONE!"
    fi
}
push_to_target() {
    git checkout -f ${INPUT_BRANCH}
    git reset --hard ${PUSH_PROTECTED_TEMPORARY_BRANCH}
    git push ${PUSH_PROTECTED_FORCE_PUSH}
}

# Enter chosen working directory
if [ -n "${INPUT_PATH}" ]; then
    cd ${INPUT_PATH}
fi

# Determine branch
if [ -n "${INPUT_REF}" ]; then
    if [ -n "${INPUT_BRANCH}" ]; then
        echo -e "\nInputs 'branch' and 'ref' are mutually exclusive; please only define one."
        exit 1
    else
        # Only `ref` is defined - use it to define `INPUT_BRANCH`, which is used throughout the workflow.
        INPUT_BRANCH=${INPUT_REF#refs/heads/}
        unset INPUT_REF
    fi
elif [ -z "${INPUT_BRANCH}" ]; then
    # Neither `ref` or `branch` are defined - use default: `branch: "main"`.
    INPUT_BRANCH=main
fi

# Due to multi-user vulnerabilities (between Docker user and host user), we need to add a safe directory
# In a GitHub Action, the Actions workspace from the host is mounted at `/github/workspace` within the container.
# This path should also be the current working directory, however, to be sure the current working directory is
# added to the safe.directory configuration as well. If it's the same, it shouldn't matter.
git config --global --add safe.directory /github/workspace
git config --global --add safe.directory ${PWD}

# Retrieve target repository
echo -e "\nFetching the latest information from '${GITHUB_REPOSITORY}' ..."
git config --local --name-only --get-regexp "http\.https\:\/\/github\.com\/\.extraheader" && git config --local --unset-all "http.https://github.com/.extraheader" || :
git submodule foreach --recursive 'git config --local --name-only --get-regexp "http\.https\:\/\/github\.com\/\.extraheader" && git config --local --unset-all "http.https://github.com/.extraheader" || :'
git remote set-url origin https://${GITHUB_ACTOR}:${INPUT_TOKEN}@github.com/${GITHUB_REPOSITORY}.git
git fetch --unshallow -tp origin || :
echo "Fetching the latest information from '${GITHUB_REPOSITORY}' ... DONE!"

# Check target branch exists
echo -e "\nCheck target branch '${INPUT_BRANCH}' exists ..."
if [ -z "$(git branch -a | grep -E ^.*remotes/origin/${INPUT_BRANCH}$ )" ]; then
    # Branch does not exist on remote
    # If branch was set to the default (`main`) try the current standard `git` default branch name: `master`
    if [ "${INPUT_BRANCH}" = "main" ] && [ -n "$(git branch -a | grep -E ^.*remotes/origin/master$ )" ]; then
        # `master` exists - use it as the fallback default instead of the non-existing `main`
        INPUT_BRANCH=master
        echo "Changed target branch from 'main' to '${INPUT_BRANCH}'."
    else
        echo -e "Branch '${INPUT_BRANCH}' cannot be found in the '${GITHUB_REPOSITORY}' repository !\nExiting."
        exit 1
    fi
fi
echo "Check target branch '${INPUT_BRANCH}' exists ... DONE!"

# Check whether there are newer commits on current branch compared to target branch
if [ "$(git rev-parse HEAD)" != "$(git rev-parse origin/${INPUT_BRANCH})" ]; then
    PUSH_PROTECTED_CHANGED_BRANCH=yes
fi

# Check whether target branch is protected
# This will only be non-empty if the branch IS protected
PUSH_PROTECTED_PROTECTED_BRANCH=$(push-action --token "${INPUT_TOKEN}" --ref "${INPUT_BRANCH}" --temp-branch "null" -- protected_branch)

# Create new temporary branch
PUSH_PROTECTED_TEMPORARY_BRANCH="push-action/${GITHUB_RUN_ID}/${RANDOM}-${RANDOM}-${RANDOM}"
echo -e "\nCreating temporary branch '${PUSH_PROTECTED_TEMPORARY_BRANCH}' ..."
git checkout -f -b ${PUSH_PROTECTED_TEMPORARY_BRANCH}  # throws away any local un-committed changes
if [ -n "${PUSH_PROTECTED_CHANGED_BRANCH}" ] && [ -n "${PUSH_PROTECTED_PROTECTED_BRANCH}" ]; then
    git push -f origin ${PUSH_PROTECTED_TEMPORARY_BRANCH}
fi
echo "Creating temporary branch '${PUSH_PROTECTED_TEMPORARY_BRANCH}' ... DONE!"

# --force
case ${INPUT_FORCE} in
    y | Y | yes | Yes | YES | true | True | TRUE | on | On | ON)
        echo -e "\nWill force push!"
        PUSH_PROTECTED_FORCE_PUSH="--force"
        ;;
    n | N | no | No | NO | false | False | FALSE | off | Off | OFF)
        ;;
    *)
        echo -e "\nNon-valid input for 'force': ${INPUT_FORCE}. Will use default (false)."
        ;;
esac

# --tags
case ${INPUT_TAGS} in
    y | Y | yes | Yes | YES | true | True | TRUE | on | On | ON)
        echo -e "\nWill push tags!"
        PUSH_PROTECTED_PUSH_TAGS="--tags"
        ;;
    n | N | no | No | NO | false | False | FALSE | off | Off | OFF)
        ;;
    *)
        echo -e "\nNon-valid input for 'tags': ${INPUT_TAGS}. Will use default (false)."
        ;;
esac

{
    # Possibly wait for status checks to complete
    wait_for_checks &&

    # Unprotect target branch for pull request reviews (if desired)
    unprotect &&

    # Push to target branch
    echo -e "\nPushing '${PUSH_PROTECTED_TEMPORARY_BRANCH}' -> 'origin/${INPUT_BRANCH}' ..." &&
    push_to_target &&
    push_tags &&
    echo "Pushing '${PUSH_PROTECTED_TEMPORARY_BRANCH}' -> 'origin/${INPUT_BRANCH}' ... DONE!" &&

    # Re-protect target branch for pull request reviews (if desired)
    protect &&

    # Remove temporary branch
    remove_remote_temp_branch
} || {
    # Remove temporary branch
    remove_remote_temp_branch &&
    exit 1
}
