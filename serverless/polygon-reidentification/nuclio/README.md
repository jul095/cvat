To deploy this model at first you need the nuctl cli.

Before you have to create a nuclio project
```
nuctl create project cvat
```

Execute following command
```
nuctl deploy --project-name cvat --path . \
    --volume $(pwd)/serverless/openvino/common:/opt/nuclio/common \
    --platform local
```