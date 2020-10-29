#!/usr/bin/env bash
set -e

echo -e "\n### Setting commit user ###"
git config --local user.email "casper+github@welzel.nu"
git config --local user.name "CasperWA"

echo -e "\n### Update version in README ###"
invoke update-version --version="${GITHUB_REF#refs/tags/}"

echo -e "\n### Commit update ###"
git commit -am "Release ${GITHUB_REF#refs/tags/}"

echo -e "\n### Create new full version (v<MAJOR>.<MINOR>.<PATCH>) tag ###"
TAG_MSG=.github/static/release_tag_msg.txt
sed -i "s|TAG_NAME|${GITHUB_REF#refs/tags/}|g" "${TAG_MSG}"

git tag -af -F "${TAG_MSG}" ${GITHUB_REF#refs/tags/}

echo -e "\n### Move/update v<MAJOR> tag ###"
MAJOR_VERSION=$( echo ${GITHUB_REF#refs/tags/v} | cut -d "." -f 1 )
TAG_MSG=.github/static/major_version_tag_msg.txt
sed -i "s|MAJOR|${MAJOR_VERSION}|g" "${TAG_MSG}"

git tag -af -F "${TAG_MSG}" v${MAJOR_VERSION}
