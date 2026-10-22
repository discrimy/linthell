#!/bin/sh
# Mirror branches and tags of linthell from GitHub to GitLab.
#
# Keeps a bare clone in $CACHE_DIR, so each run fetches only new objects.
# Safe to run from cron: concurrent runs are serialized with flock.
#
# Environment:
#   SRC_URL       source repository (default: GitHub)
#   DST_URL       destination repository (default: git.medrocket.ru)
#   CACHE_DIR     bare clone location (default: ~/.cache/linthell-mirror.git)
#   GITLAB_TOKEN  token with write_repository scope, used for HTTPS pushes;
#                 leave empty when DST_URL is SSH or credentials are set up elsewhere
#   GITLAB_USER   username sent with GITLAB_TOKEN (default: oauth2; gitlab-ci-token for CI_JOB_TOKEN)
#
# Example crontab entry (every 15 minutes):
#   */15 * * * * GITLAB_TOKEN=... /path/to/mirror.sh >>/var/log/linthell-mirror.log 2>&1
set -eu

SRC_URL=${SRC_URL:-https://github.com/discrimy/linthell.git}
DST_URL=${DST_URL:-https://git.medrocket.ru/public_packages/linthell.git}
CACHE_DIR=${CACHE_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/linthell-mirror.git}
GITLAB_TOKEN=${GITLAB_TOKEN:-}
GITLAB_USER=${GITLAB_USER:-oauth2}
export GITLAB_TOKEN GITLAB_USER

# Only branches and tags: GitHub also exposes refs/pull/*, which do not belong in the mirror.
REFSPECS='+refs/heads/*:refs/heads/* +refs/tags/*:refs/tags/*'

# Re-exec under an exclusive lock so overlapping cron runs do not collide.
if [ -z "${MIRROR_LOCKED:-}" ]; then
    mkdir -p "$(dirname "$CACHE_DIR")"
    MIRROR_LOCKED=1 exec flock --nonblock --conflict-exit-code 0 "$CACHE_DIR.lock" "$0" "$@"
fi

log() { echo "$(date '+%Y-%m-%dT%H:%M:%S%z') $*"; }

if [ ! -d "$CACHE_DIR" ]; then
    log "initializing cache in $CACHE_DIR"
    git init --quiet --bare "$CACHE_DIR"
fi

git -C "$CACHE_DIR" config remote.origin.url "$SRC_URL"
git -C "$CACHE_DIR" config --unset-all remote.origin.fetch || true
for spec in $REFSPECS; do
    git -C "$CACHE_DIR" config --add remote.origin.fetch "$spec"
done

log "fetching $SRC_URL"
git -C "$CACHE_DIR" fetch --quiet --prune origin

# The token is read from the environment by the credential helper at run time,
# so it never appears in the process list or in the git config.
log "pushing to $DST_URL"
# shellcheck disable=SC2016,SC2086
git -C "$CACHE_DIR" \
    -c credential.helper= \
    -c credential.helper='!f() { test -n "$GITLAB_TOKEN" && echo "username=$GITLAB_USER" && echo "password=$GITLAB_TOKEN"; }; f' \
    push --quiet --prune "$DST_URL" $REFSPECS

log "done"
