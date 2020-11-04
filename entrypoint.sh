#!/usr/bin/env bash
set -e

# Utility functions
unprotect () {
    case ${INPUT_UNPROTECT_REVIEWS} in
        y | Y | yes | Yes | YES | true | True | TRUE | on | On | ON)
            if [ -n "${PROTECTED_BRANCH}" ]; then
                echo -e "\nRemove '${INPUT_BRANCH}' pull request review protection ..."
                push-action --token "${INPUT_TOKEN}" --ref "${INPUT_BRANCH}" --temp-branch "${TEMPORARY_BRANCH}" -- unprotect_reviews
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
            if [ -n "${PROTECTED_BRANCH}" ]; then
                echo -e "\nRe-add '${INPUT_BRANCH}' pull request review protection ..."
                push-action --token "${INPUT_TOKEN}" --ref "${INPUT_BRANCH}" --temp-branch "${TEMPORARY_BRANCH}" -- protect_reviews
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
    if [ -n "${PROTECTED_BRANCH}" ]; then
        echo -e "\nWaiting for status checks to finish for '${TEMPORARY_BRANCH}' ..."
        # Sleep for 5 seconds to let the workflows start
        sleep ${INPUT_SLEEP}
        push-action --token "${INPUT_TOKEN}" --ref "${INPUT_BRANCH}" --temp-branch "${TEMPORARY_BRANCH}" --wait-timeout "${INPUT_TIMEOUT}" --wait-interval "${INPUT_INTERVAL}" -- wait_for_checks
        echo "Waiting for status checks to finish for '${TEMPORARY_BRANCH}' ... DONE!"
    fi
}
remove_remote_temp_branch() {
    if [ -n "${PROTECTED_BRANCH}" ]; then
        echo -e "\nRemoving temporary branch '${TEMPORARY_BRANCH}' ..."
        push-action --token "${INPUT_TOKEN}" --ref "${INPUT_BRANCH}" --temp-branch "${TEMPORARY_BRANCH}" -- remove_temp_branch
        echo "Removing temporary branch '${TEMPORARY_BRANCH}' ... DONE!"
    fi
}
push_tags() {
    if [ -n "${PUSH_TAGS}" ]; then
        echo -e "\nPushing tags ..."
        git push ${FORCE_PUSH}--tags
        echo "Pushing tags ... DONE!"
    fi
}

# Retrieve target repository
echo -e "\nGetting latest commit of ${GITHUB_REPOSITORY}@${INPUT_BRANCH} ..."
git config --local --name-only --get-regexp "http\.https\:\/\/github\.com\/\.extraheader" && git config --local --unset-all "http.https://github.com/.extraheader" || :
git submodule foreach --recursive 'git config --local --name-only --get-regexp "http\.https\:\/\/github\.com\/\.extraheader" && git config --local --unset-all "http.https://github.com/.extraheader" || :'
git remote set-url origin https://${GITHUB_ACTOR}:${INPUT_TOKEN}@github.com/$GITHUB_REPOSITORY.git
git fetch --unshallow -tpP origin || :
echo "Getting latest commit of ${GITHUB_REPOSITORY}@${INPUT_BRANCH} ... DONE!"

# Check whether target branch is protected
# This will only be non-empty if the branch IS protected
PROTECTED_BRANCH=$(push-action --token "${INPUT_TOKEN}" --ref "${INPUT_BRANCH}" --temp-branch "null" -- protected_branch)

# Create new temporary repository
TEMPORARY_BRANCH="push-action/${GITHUB_RUN_ID}/${RANDOM}-${RANDOM}-${RANDOM}"
echo -e "\nCreating temporary repository '${TEMPORARY_BRANCH}' ..."
git checkout -f -b ${TEMPORARY_BRANCH}
if [ -n "${PROTECTED_BRANCH}" ]; then
    git push -f origin ${TEMPORARY_BRANCH}
fi
echo "Creating temporary repository '${TEMPORARY_BRANCH}' ... DONE!"

# --force
case ${INPUT_FORCE} in
    y | Y | yes | Yes | YES | true | True | TRUE | on | On | ON)
        echo -e "\nWill force push!"
        FORCE_PUSH="--force "
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
        PUSH_TAGS="--tags"
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

    # Merge into target branch
    echo -e "\nMerging (fast-forward) '${TEMPORARY_BRANCH}' -> '${INPUT_BRANCH}' ..." &&
    git checkout ${INPUT_BRANCH} &&
    git reset --hard origin/${INPUT_BRANCH} &&
    git merge --ff-only ${TEMPORARY_BRANCH} &&
    git push ${FORCE_PUSH} &&
    push_tags &&
    echo "Merging (fast-forward) '${TEMPORARY_BRANCH}' -> '${INPUT_BRANCH}' ... DONE!" &&

    # Re-protect target branch for pull request reviews (if desired)
    protect &&

    # Remove temporary repository
    remove_remote_temp_branch
} || {
    # Remove temporary repository
    remove_remote_temp_branch &&
    exit 1
}
