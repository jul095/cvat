To deploy this model at first you need the nuctl cli.

Execute following command
```
cd ../.. && nuctl deploy --project-name cvat \                                                                       
    --path serverless/polygon-reidentification/nuclio \
    --volume $(pwd)/serverless/openvino/common:/opt/nuclio/common \
    --platform local
```