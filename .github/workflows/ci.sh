#!/bin/sh
set -e

git checkout -b ci_tests
echo "This is a test. ${RANDOM} ${RANDOM}" >> "ci_test_file.txt"
mv -f extra_data_more.md .github/
git add ci_test_file.txt extra_data.log .github/extra_data_more.md Workflow_file.txt
git commit -m "CI tests"
