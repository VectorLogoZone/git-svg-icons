#!/usr/bin/env bash
#
# build the logo data
#

set -o errexit
set -o pipefail
set -o nounset

SCRIPT_HOME="$( cd "$( dirname "$0" )" && pwd )"
BASE_DIR=$(realpath "${SCRIPT_HOME}/..")

#
# load an .env file if it exists
#
ENV_FILE="${BASE_DIR}/.env"
if [ -f "${ENV_FILE}" ]; then
    echo "INFO: loading '${ENV_FILE}'"
    export $(cat "${ENV_FILE}")
fi

IMGTYPE=${1:-BAD}
PROVIDER=${2:-BAD}
if [ "${PROVIDER}" == "BAD" ] || [ "${IMGTYPE}" == "BAD" ]; then
	echo "usage: build-index.sh IMGTYPE PROVIDER"
    echo "       imgtype is [ emoji | icons | logos ]"
	echo "       provider is [ github | gitlab ]"
	exit 1
fi

echo "INFO: starting ${PROVIDER} index build at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

OUTPUT_DIR=${OUTPUT_DIR:-${BASE_DIR}/output/${IMGTYPE}/${PROVIDER}}
if [ ! -d "${OUTPUT_DIR}" ]; then
    echo "INFO: creating output directory ${OUTPUT_DIR}"
    mkdir -p "${OUTPUT_DIR}"
else
    echo "INFO: output to existing directory ${OUTPUT_DIR}"
fi

#
# load all the git repos
#
echo "INFO: loading logos into ${OUTPUT_DIR}"
"${BASE_DIR}/bin/loadrepo.py" \
    --cache "cache/${IMGTYPE}" \
    --input "data/${IMGTYPE}.yaml" \
    --nocopy \
    --output=${OUTPUT_DIR} \
    --provider=${PROVIDER}

# to force it to copy even if no new commits, add:
#    --always \

BUILD_DIR=${BUILD_DIR:-${BASE_DIR}/build}
if [ ! -d "${BUILD_DIR}" ]; then
    echo "INFO: creating build directory ${BUILD_DIR}"
    mkdir -p "${BUILD_DIR}"
else
    echo "INFO: building to existing directory ${BUILD_DIR}"
fi

#
# make the index
#
echo "INFO: building compressed index"
tar cvzf ${BUILD_DIR}/index-${IMGTYPE}-${PROVIDER}.tgz ${OUTPUT_DIR}/*/sourceData.json

echo "INFO: completed ${IMGTYPE} from ${PROVIDER} index build at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
