#!/bin/sh
set -e

# Install requirements
python -m pip install --no-cache -U requests

# Setup git user
git config --system user.email "actions@github.com"
git config --system user.name "${GITHUB_WORKFLOW}"

# Retrieve target repository
mkdir target_repo
cd target_repo
git init
git pull https://${INPUT_GITHUB_TOKEN}:x-oauth-basic@github.com/${INPUT_REPOSITORY}.git

if [ "${GITHUB_SHA}" != "$(git rev-parse HEAD)" ]; then
    git checkout -f "$(python -c "print('/'.join('${GITHUB_REF}'.split('/')[2:]))")"
fi

# Retrieve shell script to run changes
if [ -n "${INPUT_CHANGES}" ]; then
    wget --tries=5 https://raw.githubusercontent.com/${GITHUB_REPOSITORY}/${GITHUB_SHA}/${INPUT_CHANGES}

    FILENAME=$(python -c "import os; print(os.path.basename('${INPUT_CHANGES}'))")
    /bin/sh ${FILENAME}
fi

# Create new temporary repository
TEMPORARY_BRANCH="push-action/temporary/${GITHUB_RUN_ID}"
git checkout -f -b ${TEMPORARY_BRANCH}
git push -f https://${INPUT_GITHUB_TOKEN}:x-oauth-basic@github.com/${INPUT_REPOSITORY}.git ${TEMPORARY_BRANCH}

# Wait for status checks to complete
python ../app/run.sh --token "${INPUT_GITHUB_TOKEN}" --repo "${INPUT_REPOSITORY}" --run-id "${GITHUB_RUN_ID}" --ref "${INPUT_BRANCH}" wait_for_checks

# Merge into target branch
git checkout -f ${INPUT_BRANCH}
git merge --ff-only ${TEMPORARY_BRANCH}
git push https://${INPUT_GITHUB_TOKEN}:x-oauth-basic@github.com/${INPUT_REPOSITORY}.git ${INPUT_BRANCH}

# Remove temporary repository
python ../app/run.sh --token "${INPUT_GITHUB_TOKEN}" --repo "${INPUT_REPOSITORY}" --run-id "${GITHUB_RUN_ID}" --ref "${INPUT_BRANCH}" remove_temp_branch
