#!/bin/env bash
set -e

# USAGE:
# COPY .devcontainer/ /app/.devcontainer/
# ARG VSCODE_VERSION=2ccd690cbff1569e4a83d7c43d45101f817401dc
# RUN bash .devcontainer/preinstall-vscode-extensions.sh $VSCODE_VERSION /app/.devcontainer/devcontainer.json
# 
# Preinstall vscode server extensions.
# Uses vscode of provided version (git commit hash) to download extensions inside container
# and deletes installed vscode server. It does it because user's vscode can be a different version,
# so after container start it will install itself inside container, and the container will have
# two different versions of vscode server, and it's bad in terms storage and conflicts.
# Extensions to install are extracted from devcontainer.json file
# 
# IMPORTANT: requires jq and curl to be installed

vscode_commit_sha=$1
devcontainer_path=$2

# Install vscode
ARCH="x64"
U_NAME=$(uname -m)
if [ "${U_NAME}" = "aarch64" ]; then
    ARCH="arm64"
fi
archive="vscode-server-linux-${ARCH}.tar.gz"
vscode_dir="~/.vscode-server/bin/${vscode_commit_sha}"
echo "will attempt to download VS Code Server version = '${vscode_commit_sha}'"
# Download VS Code Server tarball to tmp directory.
curl -L "https://update.code.visualstudio.com/commit:${vscode_commit_sha}/server-linux-${ARCH}/stable" -o "/tmp/${archive}"
# Make the parent directory where the server should live.
# NOTE: Ensure VS Code will have read/write access; namely the user running VScode or container user.
mkdir -vp "$vscode_dir"
# Extract the tarball to the right location.
tar --no-same-owner -xzv --strip-components=1 -C "$vscode_dir" -f "/tmp/${archive}"

# Install extensions from .devcontainer.json
# Exclude comments lines to make file a valid JSON
extensions_list=$(cat "$devcontainer_path" | grep -vE "\s*//" | jq ".customizations.vscode.extensions[]" -r)
for extension in "${extensions_list[@]}"; do 
    "$vscode_dir/bin/code-server" --install-extension $extension; 
done

# Cleanup
rm -rd "$vscode_dir"
rm "/tmp/${archive}"

echo "Done!"