# SDK Test Plugin

A SDK Test Plugin.

## Example/Usage

### Build and Push Image

```bash
$ docker build -t <your-registry-host>/dce/sdk-test .
$ docker push <your-registry-host>/dce/sdk-test
```

### Install Plugin on DCE

Install plugin on DCE with image you have build before.

Then you can enter plugin on DCE navigation bar.

### Test Set Config

```bash
$ curl --insecure -X POST https://<your-DCE-host>/plugin/<plugin-port>/config
{"key": "Hello, World"}
```

### Test Get Config

```bash
$ curl --insecure -X GET https://<your-DCE-host>/plugin/<plugin-port>/config
{"key": "Hello, World"}
```