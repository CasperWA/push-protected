#!/usr/bin/env bash
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

# Retrieve target repository
echo -e "\nGetting latest commit of ${GITHUB_REPOSITORY}@${INPUT_BRANCH} ..."
git config --local --name-only --get-regexp "http\.https\:\/\/github\.com\/\.extraheader" && git config --local --unset-all "http.https://github.com/.extraheader" || :
git submodule foreach --recursive 'git config --local --name-only --get-regexp "http\.https\:\/\/github\.com\/\.extraheader" && git config --local --unset-all "http.https://github.com/.extraheader" || :'
git remote set-url origin https://${GITHUB_ACTOR}:${INPUT_TOKEN}@github.com/${GITHUB_REPOSITORY}.git
git fetch --unshallow -tp origin || :
echo "Getting latest commit of ${GITHUB_REPOSITORY}@${INPUT_BRANCH} ... DONE!"

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
