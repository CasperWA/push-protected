#!/usr/bin/env bash
set -ex

TAG_NAME=$1

git config --global user.email "casper+github@welzel.nu"
git config --global user.name "Casper Welzel Andersen"

echo "This is a test. ${RANDOM} ${RANDOM}" >> "ci_test_file.txt"
mv -f extra_data_more.md ../
mv -f ci_test_file.txt ../../

git add ../../ci_test_file.txt ../extra_data.log extra_data_more.md
git commit -m "CI tests"

if [ -n "${TAG_NAME}" ]; then
    git tag ${TAG_NAME} -a -m "This is a test tag"
fi
