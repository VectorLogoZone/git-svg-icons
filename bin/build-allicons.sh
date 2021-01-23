#!/usr/bin/env bash
#
# build a downloadable archive with all the icons
#

set -o errexit
set -o pipefail
set -o nounset

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"
BASE_DIR=$(realpath "${SCRIPT_HOME}/..")

CACHE_DIR=${CACHE_DIR:-${BASE_DIR}/cache}
if [ ! -d "${CACHE_DIR}" ]; then
	echo "ERROR: cache directory ${CACHE_DIR} does not exist"
	exit 1
fi

BUILD_DIR=${BUILD_DIR:-${BASE_DIR}/build}
if [ ! -d "${BUILD_DIR}" ]; then
	echo "INFO: creating build directory ${BUILD_DIR}"
	mkdir -p "${BUILD_DIR}"
fi

echo "INFO: starting download build at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

cd "${CACHE_DIR}" && find . -name "*.svg" -type f -print0 \
	| tar -czvf "${BUILD_DIR}/allicons.tgz" --directory "${CACHE_DIR}" --null --files-from - --totals

echo "INFO: completed download build at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
