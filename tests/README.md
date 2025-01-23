## Tests

We recommend running tests in a docker image. Most of the tests produce images that are compared with
a base snapshot, but sometimes results might be a bit different from machine to machine (e.g.: image might be shifted 1 pixel).

### Using pi-top test runner image

```
$ docker run \
    --rm \
    --volume "$PWD":/src \
    pitop/pt-miniscreen-test-runner:latest
```

### Building the image

Build the image by running:

```
$ docker build -t pt-miniscreen-test-runner tests
```

Then, run the tests with:

```
$ docker run \
    --rm \
    --platform linux/amd64 \
    --volume "$PWD":/src \
    pt-miniscreen-test-runner
```

### Updating base images

Override the entrypoint to access the image using `bash`. Then use `pytest --snapshot-update` to update the snapshots in the tests folder.

```
$ docker run \
    -ti \
    --rm \
    --volume "$PWD":/src \
    --platform linux/amd64 \
    --entrypoint bash \
    pitop/pt-miniscreen-test-runner:latest
```
