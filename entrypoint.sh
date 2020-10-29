#!/usr/bin/env bash
set -e

# Retrieve target repository
echo "Getting latest commit of ${INPUT_REPOSITORY}@${INPUT_BRANCH} ..."
git clone https://${GITHUB_ACTOR}:${INPUT_TOKEN}@github.com/${INPUT_REPOSITORY}.git target_repo/
cd target_repo

git checkout -f ${INPUT_BRANCH}
echo "Getting latest commit of ${INPUT_REPOSITORY}@${INPUT_BRANCH} ... DONE!"

# Create new temporary repository
TEMPORARY_BRANCH="push-action/${GITHUB_RUN_ID}/$(uuidgen)"
echo "Creating temporary repository '${TEMPORARY_BRANCH}' ..."
git checkout -f -b ${TEMPORARY_BRANCH}
git push -f origin ${TEMPORARY_BRANCH}
echo "Creating temporary repository '${TEMPORARY_BRANCH}' ... DONE!"

# Unprotect/protect functions
unprotect () {
    case ${INPUT_UNPROTECT_REVIEWS} in
        y | Y | yes | Yes | YES | true | True | TRUE | on | On | ON)
            echo "Remove '${INPUT_BRANCH}' pull request review protection ..."
            push-action --token "${INPUT_TOKEN}" --repo "${INPUT_REPOSITORY}" --ref "${INPUT_BRANCH}" --temp-branch "${TEMPORARY_BRANCH}" -- unprotect_reviews
            echo "Remove '${INPUT_BRANCH}' pull request review protection ... DONE!"
            ;;
        n | N | no | No | NO | false | False | FALSE | off | Off | OFF)
            ;;
        *)
            echo "Non-valid input for 'unprotect_review': ${INPUT_UNPROTECT_REVIEWS}. Will use default (false)."
            ;;
    esac
}
protect () {
    case ${INPUT_UNPROTECT_REVIEWS} in
        y | Y | yes | Yes | YES | true | True | TRUE | on | On | ON)
            echo "Re-add '${INPUT_BRANCH}' pull request review protection ..."
            push-action --token "${INPUT_TOKEN}" --repo "${INPUT_REPOSITORY}" --ref "${INPUT_BRANCH}" --temp-branch "${TEMPORARY_BRANCH}" -- protect_reviews
            echo "Re-add '${INPUT_BRANCH}' pull request review protection ... DONE!"
            ;;
        n | N | no | No | NO | false | False | FALSE | off | Off | OFF)
            ;;
        *)
            echo "Non-valid input for 'unprotect_review': ${INPUT_UNPROTECT_REVIEWS}. Will use default (false)."
            ;;
    esac
}

case ${INPUT_FORCE} in
    y | Y | yes | Yes | YES | true | True | TRUE | on | On | ON)
        echo "Will force push!"
        FORCE_PUSH="--force "
        ;;
    n | N | no | No | NO | false | False | FALSE | off | Off | OFF)
        echo "Will NOT force push!"
        ;;
    *)
        echo "Non-valid input for 'force': ${INPUT_FORCE}. Will use default (false)."
        ;;
esac

case ${INPUT_TAGS} in
    y | Y | yes | Yes | YES | true | True | TRUE | on | On | ON)
        echo "Will push tags!"
        PUSH_TAGS="--tags"
        ;;
    n | N | no | No | NO | false | False | FALSE | off | Off | OFF)
        echo "Will NOT push tags!"
        ;;
    *)
        echo "Non-valid input for 'tags': ${INPUT_TAGS}. Will use default (false)."
        ;;
esac

{
    # Wait for status checks to complete
    echo "Waiting for status checks to finish for '${TEMPORARY_BRANCH}' ..." &&
    # Sleep for 5 seconds to let the workflows start
    sleep ${INPUT_SLEEP} &&
    push-action --token "${INPUT_TOKEN}" --repo "${INPUT_REPOSITORY}" --ref "${INPUT_BRANCH}" --temp-branch "${TEMPORARY_BRANCH}" --wait-timeout "${INPUT_TIMEOUT}" --wait-interval "${INPUT_INTERVAL}" -- wait_for_checks &&
    echo "Waiting for status checks to finish for '${TEMPORARY_BRANCH}' ... DONE!" &&

    # Unprotect target branch for pull request reviews (if desired)
    unprotect &&

    # Merge into target branch
    echo "Merging (fast-forward) '${TEMPORARY_BRANCH}' -> '${INPUT_BRANCH}' ..." &&
    git checkout ${INPUT_BRANCH} &&
    git merge --ff-only origin/${TEMPORARY_BRANCH} &&
    git push ${FORCE_PUSH}${PUSH_TAGS} &&
    echo "Merging (fast-forward) '${TEMPORARY_BRANCH}' -> '${INPUT_BRANCH}' ... DONE!" &&

    # Re-protect target branch for pull request reviews (if desired)
    protect &&

    # Remove temporary repository
    echo "Removing temporary branch '${TEMPORARY_BRANCH}' ..." &&
    push-action --token "${INPUT_TOKEN}" --repo "${INPUT_REPOSITORY}" --ref "${INPUT_BRANCH}" --temp-branch "${TEMPORARY_BRANCH}" -- remove_temp_branch &&
    echo "Removing temporary branch '${TEMPORARY_BRANCH}' ... DONE!"
} || {
    # Remove temporary repository
    echo "Removing temporary branch '${TEMPORARY_BRANCH}' ..." &&
    push-action --token "${INPUT_TOKEN}" --repo "${INPUT_REPOSITORY}" --ref "${INPUT_BRANCH}" --temp-branch "${TEMPORARY_BRANCH}" -- remove_temp_branch &&
    echo "Removing temporary branch '${TEMPORARY_BRANCH}' ... DONE!" &&
    exit 1
}
