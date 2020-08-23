#!/bin/bash
#
# run locally for dev
#

set -o errexit
set -o pipefail
set -o nounset

#
# load an .env file if it exists
#
ENV_FILE="${1:-./.env}"
if [ -f "${ENV_FILE}" ]; then
    echo "INFO: loading '${ENV_FILE}'"
    export $(cat "${ENV_FILE}")
fi

OUTPUT_DIR=${OUTPUT_DIR:-./local}

#
# representative subset of repos
#
#DEV_REPO="${DEV_REPO:-adamfairhead,brandicons,bestofjs,vlz-ar21,svgporn}"
DEV_REPO=${DEV_REPO:-}

#
# LATER: make dir if it doesn't exist
#

#
# load a few so there is some data
#
echo "INFO: loading ${DEV_REPO//,/ } logos into ${OUTPUT_DIR}"
./bin/loadrepo.py \
    --always \
    --output=${OUTPUT_DIR} \
    ${DEV_REPO//,/ }

# to force it to refresh local dir add:
#	--always \

#
# make the index
#
echo "INFO: building index"
tar cvzf ${OUTPUT_DIR}/sourceData.tgz ${OUTPUT_DIR}/*/sourceData.json
