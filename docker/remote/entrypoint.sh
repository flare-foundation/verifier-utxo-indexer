#!/usr/bin/env bash

set -eu

dirs=(
    "/appdata/static"
    "/appdata/media"
)

if [[ ${USER_UID:+x} != "x" ]] || [[ ${USER_GID:+x} != "x" ]]; then
    echo "Running with current user, USER_UID or USER_GID is unset"
    echo "Running 'exec $@'"
    exec "$@"
else
    echo "Running with user and group ${USER_UID}:${USER_GID}"
    for d in ${dirs[@]}; do
        if [[ -d "$d" ]] && [[ "$(stat -c '%u:%g' $d)" != "$USER_UID:$USER_GID" ]]; then
            echo "Found not owned directory '$d'. Running 'chown $USER_UID:$USER_GID $d'"
            chown "$USER_UID:$USER_GID" "$d"
        elif ! [[ -d "$d" ]]; then
            echo "Specified directory '$d' not found"
        fi
    done

    echo "Running 'exec gosu $USER_UID:$USER_GID $@'"
    exec gosu "$USER_UID:$USER_GID" "$@"
fi

