#!/usr/bin/env bash
#
# build the logo data
#

set -o errexit
set -o pipefail
set -o nounset

echo "INFO: starting build at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

#
# load an .env file if it exists
#
ENV_FILE=".env"
if [ -f "${ENV_FILE}" ]; then
    echo "INFO: loading '${ENV_FILE}'"
    export $(cat "${ENV_FILE}")
fi

OUTPUT_DIR=${OUTPUT_DIR:-./output-github}
if [ ! -d "${OUTPUT_DIR}" ]; then
    echo "INFO: creating output directory ${OUTPUT_DIR}"
    mkdir -p "${OUTPUT_DIR}"
fi

#
# load all the git repos
#
echo "INFO: loading logos into ${OUTPUT_DIR}"
./bin/loadrepo.py \
    --nocopy \
    --output=${OUTPUT_DIR} \
    --provider=github

# to force it to copy even if no new commits, add:
#    --always \

BUILD_DIR=${BUILD_DIR:-./build}
if [ ! -d "${BUILD_DIR}" ]; then
    echo "INFO: creating build directory ${BUILD_DIR}"
    mkdir -p "${BUILD_DIR}"
fi

#
# make the index
#
echo "INFO: building compressed index"
tar cvzf ${BUILD_DIR}/sourceData-github.tgz ${OUTPUT_DIR}/*/sourceData.json

echo "INFO: completed build at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
