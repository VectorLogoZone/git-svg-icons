#!/usr/bin/env bash
#
# build a downloadable archive with all the images
#

set -o errexit
set -o pipefail
set -o nounset

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"
BASE_DIR=$(realpath "${SCRIPT_HOME}/..")

IMGTYPE=${1:-BAD}
if [ "${IMGTYPE}" == "BAD" ]; then
	echo "usage: build-download.sh IMGTYPE"
	echo "       imgtype is [ logos | icons ]"
	exit 1
fi

CACHE_DIR=${CACHE_DIR:-${BASE_DIR}/cache/${IMGTYPE}}
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
	| tar -czvf "${BUILD_DIR}/download-${IMGTYPE}.tgz" --directory "${CACHE_DIR}" --null --files-from - --totals

echo "INFO: completed download build at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
