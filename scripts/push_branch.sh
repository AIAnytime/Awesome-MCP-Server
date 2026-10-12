#!/usr/bin/env bash
# Publish a directory as the single commit of a branch (used for gh-pages and status-data).
# usage: push_branch.sh <directory> <branch> <commit message>
set -euo pipefail

dir=$1 branch=$2 message=$3
remote=${REMOTE:-$(git remote get-url origin)}
name=$(git config user.name || echo "github-actions[bot]")
email=$(git config user.email || echo "41898282+github-actions[bot]@users.noreply.github.com")

cd "$dir"
rm -rf .git
git init -q -b "$branch"
git add -A
git -c user.name="$name" -c user.email="$email" commit -q -m "$message"
git push -q --force "$remote" "$branch"
rm -rf .git
