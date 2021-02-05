#!/bin/bash
QSS3BucketName=$1
QSS3KeyPrefix=$2
SCRIPT_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
pushd $SCRIPT_DIRECTORY > /dev/null
cd src
zip -r newrelic_ct_customization.zip .
popd > /dev/null
aws s3 cp ./src/newrelic_ct_customization.zip  s3://$QSS3BucketName/$QSS3KeyPrefix/newrelic_ct_customization.zip --acl public-read
aws s3 cp ./templates/control-tower-customization.yaml s3://$QSS3BucketName/$QSS3KeyPrefix/control-tower-customization.yaml --acl public-read