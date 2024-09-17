# Development

## Using a separate computer

1. Turn ssh on

2. Authorize computer so password is not required when using ssh

- ssh into pi
- create the file `~/.ssh/authorized_keys`
- copy development machine's `id_rsa.pub` into pi's `authorized_keys` file

3. When in repo root run `./dev/sync.sh pi@xxx.xxx.xx.x`

This syncs the folder to the pi in the home directory: `~/pi-top-4-Miniscreen`.
It also watches this repo for any file changes and resyncs.

4. On the pi run `sudo pip3 install -e ~/pi-top-4-Miniscreen`

This installs the local version of `pt_miniscreen`.

5. On the pi run `sudo python3 ~/pi-top-4-Miniscreen/dev-start.py`

This starts the miniscreen with logging to stdout.

### Notes

- you need `fswatch` for `sync.sh` to work. Use `sync-once.sh` if that is not an option.

- Syncing takes around a second. You need to wait for it to finish before running.

- Sometimes it helps to stop the running miniscreen `systemctl stop pt-miniscreen.service`

## Tests

We recommend running tests in a docker image. Most of the tests produce images that are compared with
a base, but sometimes results might be a bit different from machine to machine (e.g.: image might be shifted 1 pixel).

A `Dockerfile` can be found in the `tests` folder to build the image locally.
We also provide images you can use to run the tests directly.


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
    --volume "$PWD":/src \
    pt-miniscreen-test-runner
```
