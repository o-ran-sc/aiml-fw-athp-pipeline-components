# Setup Guide for AIMLFW Generic Pipeline
This guide provides step-by-step instructions to set up the environment, prepare private Python packages, build pipeline components, and onboard a pipeline into Kubeflow.

## Prerequisites
Before starting, ensure you have the following installed:

- make
- virtualenv
- Python (3.12 recommended)
- pip
- kfp (Kubeflow Pipelines SDK)
- docker (required for building component images, as KFP only supports Docker)

## Setup Private PyPI Server

We need to host some custom Python packages (`modelmetricsdk` and `featurestoresdk`) need to be hosted on a private PyPI server since version 0.3 is not available on public PyPI.

## Build the packages:

From the repository folder (e.g., model storage or feature store), run:

```
python setup.py sdist bdist_wheel
```

Repeat the process for `feature-store-sdk`.

## Move the packages to the target machine:

Copy the generated `.whl` files from the `dist/ folder` to the machine where AIMLFW is installed:

```bash
$ scp -i ~/os-dev dist/modelmetricsdk-0.3-py3-none-any.whl ubuntu@AIMLFW_HOST_IP:pip-packages
```

Repeat for all required packages.

Deploy a private PyPI server on Kubernetes:
Create a file `pypi-server.yaml` with the following content:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pypi-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pypi
  template:
    metadata:
      labels:
        app: pypi
    spec:
      containers:
      - name: pypi
        image: pypiserver/pypiserver
        args: ["-P", ".", "-a", ".", "/data/packages"]
        ports:
        - containerPort: 8080
        volumeMounts:
        - mountPath: /data/packages
          name: packages-volume
      volumes:
      - name: packages-volume
        hostPath:
          path: /home/ubuntu/pip-packages # contains .whl/.tar.gz files
          type: DirectoryOrCreate
---
apiVersion: v1
kind: Service
metadata:
  name: pypi-service
spec:
  type: NodePort
  selector:
    app: pypi
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
    nodePort: 30080
```
Apply the configuration:
```
kubectl apply -f pypi-server.yaml
```
✅ Your custom Python packages are now hosted at `http://<node-ip>:30080/simple`.

## Build Pipeline Components
Each pipeline component has a Python file ending with `_component.py`. The image name is defined in the `@component` annotation. For example:
```python
@component(
    base_image="python:3.12",
    packages_to_install=[
        "cassandra-driver==3.29.1",
        "pandas",
        "featurestoresdk",
        "modelmetricsdk"
    ],
    target_image="docker_repo_ip:port/feature_extraction:v1", # image name
    pip_index_urls=["https://pypi.org/simple/"],
)
```
Since a private PyPI is used, update the `Dockerfile` as follows:

```
FROM python:3.12
WORKDIR /usr/local/src/kfp/components
# Install standard packages
RUN pip install --index-url https://pypi.org/simple/ --no-cache-dir pandas cassandra-driver==3.29.1 setuptools kfp==2.12.1
# Install from private PyPI
RUN pip install --index-url http://192.168.180.52:30080/simple --trusted-host 192.168.180.52 --no-cache-dir featurestoresdk==0.3 modelmetricsdk==0.3
COPY . .
```
Case A: If you have a Docker repository
Build and push component images using the provided Makefile:
```
cd components
make build-feature-extraction
```
Case B: If you don’t have a Docker repository
Build the component without pushing:
```
kfp component build feature_extraction/ --component-filepattern feature_extraction_component.py --no-push-image
```
Export the image and load it on the target machine:
```
docker save -o feature_extraction.tar 192.168.180.70:5000/feature_extraction:v1
nerdctl load -i feature_extraction.tar
```
Repeat the process for other components:

- model_training
- metrics_store
- model_storage

## Build the Pipeline
Once components are ready, generate the pipeline YAML:
```
cd pipeline
python pipeline.py # generates pipeline.yaml
```

Upload Pipeline to Kubeflow
Push the pipeline to Kubeflow using the following API call:

```
resp = requests.post(
    "http://192.168.180.82:32002/pipelines/{}/upload".format("pipeline_name"),
    files={"file": open("pipeline.yaml", "rb")},
)
```

Once uploaded, the pipeline will appear in the Kubeflow dashboard and can be used for model training.

## Summary
1. Install prerequisites.
2. Set up a private PyPI server with custom packages.
3. Build components (with or without a Docker repository).
4. Generate the pipeline YAML.
5. Upload the pipeline to Kubeflow.
Now you’re ready to run AIMLFW pipelines in your Kubeflow environment! 🎉
