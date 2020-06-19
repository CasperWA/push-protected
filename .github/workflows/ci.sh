#!/bin/sh
set -e

git checkout -b ci_tests
echo "This is a test. ${RANDOM} ${RANDOM}" >> "ci_test_file.txt"
mv -f extra_data_more.md .github/

echo "Test installing Ruby"
apt-get update
apt-get install ruby-full build-essential zlib1g-dev
export GEM_HOME="$HOME/gems"
export PATH="$GEM_HOME/bin:$PATH"

echo "Test installing gem"
gem install jekyll

git add ci_test_file.txt extra_data.log .github/extra_data_more.md
git commit -m "CI tests"
