#!/bin/sh
set -e

git checkout -b ci_tests
echo "This is a test. ${RANDOM} ${RANDOM}" >> "ci_test_file.txt"
git add ci_test_file.txt
git commit -m "CI tests"
