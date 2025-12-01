#!/usr/bin/env bash
set -e

echo -e "\n### Setting commit user ###"
git config --global user.email "${GIT_USER_EMAIL}"
git config --global user.name "${GIT_USER_NAME}"

ref=${GITHUB_REF#refs/tags/}

echo -e "\n### Update version to ${ref} ###"
invoke update-version --version="${ref}"

echo -e "\n### Commit update ###"
git add push_action/__init__.py
git add CHANGELOG.md
git commit -m "Release ${ref}"

echo -e "\n### Create new full version (v<MAJOR>.<MINOR>.<PATCH>) tag ###"
TAG_MSG=.github/utils/release_tag_msg.txt
sed -i "s|TAG_NAME|${ref}|g" "${TAG_MSG}"

git tag -af -F "${TAG_MSG}" ${ref}

echo -e "\n### Move/update v<MAJOR> tag ###"
MAJOR_VERSION=$( echo ${GITHUB_REF#refs/tags/v} | cut -d "." -f 1 )
TAG_MSG=.github/utils/major_version_tag_msg.txt
sed -i "s|MAJOR|${MAJOR_VERSION}|g" "${TAG_MSG}"

git tag -af -F "${TAG_MSG}" v${MAJOR_VERSION}
