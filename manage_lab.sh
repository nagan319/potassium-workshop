#!/bin/bash

# List of UCSB-AMO repositories
REPOS=(
    "spcm"
    "k-exp"
    "artiq"
    "k-amo"
    "pyLabLib"
    "wax"
)

# Per-repo branch overrides (default: clone the repo's default branch)
declare -A REPO_BRANCH
REPO_BRANCH["artiq"]="release-8-ucsb"
BASE_URL="https://github.com/ucsb-amo"
LOG_FILE="last_sync_report.txt"

echo "--- Starting Lab Sync $(date) ---" > $LOG_FILE

for repo in "${REPOS[@]}"; do
    if [ -d "$repo" ]; then
        echo "Checking $repo for updates..."
        cd "$repo"
        
        # Get the current ID before updating
        OLD_REV=$(git rev-parse --short HEAD)
        git pull origin $(git branch --show-current) > /dev/null 2>&1
        NEW_REV=$(git rev-parse --short HEAD)

        if [ "$OLD_REV" != "$NEW_REV" ]; then
            echo "[UPDATE] $repo changed: $OLD_REV -> $NEW_REV" >> ../$LOG_FILE
            # Capture the commit messages for Claude to read
            git log "$OLD_REV..$NEW_REV" --oneline >> ../$LOG_FILE
        else
            echo "[STABLE] $repo is up to date." >> ../$LOG_FILE
        fi
        cd ..
    else
        echo "First time setup: Cloning $repo..."
        if [ -n "${REPO_BRANCH[$repo]}" ]; then
            git clone -b "${REPO_BRANCH[$repo]}" "$BASE_URL/$repo.git"
        else
            git clone "$BASE_URL/$repo.git"
        fi
        echo "[NEW] Cloned $repo" >> $LOG_FILE
    fi
done

echo "Sync complete. Report saved to $LOG_FILE"

