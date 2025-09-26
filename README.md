# Composable Pipeline Setup and Running Guide

This document provides a step-by-step guide for setting up the environment, building the pipeline components, and running a composable pipeline.

---

## Table of Contents
1. [Composable Pipeline Setup](#composable-pipeline-setup)
2. [Build Pipeline Components](#build-pipeline-components)
3. [Running the Pipeline](#running-the-pipeline)
4. [Manual Component Build Commands (Alternative)](#manual-component-build-commands-alternative)

---

## Composable Pipeline Setup

Follow these steps to set up your environment for the pipeline components.

1.  **Clone the Repository**
    ```bash
    git clone "https://gerrit.o-ran-sc.org/r/aiml-fw/athp/pipeline-components"
    cd pipeline-components
    ```

2.  **Update System Packages**
    ```bash
    sudo apt update && sudo apt upgrade
    ```

3.  **Install Python Pip**
    ```bash
    sudo apt install python3-pip
    ```

4.  **Install Python Virtual Environment**
    ```bash
    sudo apt install python3.10-venv
    ```
    > **Note:** Ensure `ensure-pip` is enabled. If not, installing `python3.10-venv` as above should resolve it.

5.  **Create and Activate Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

6.  **Install Python Dependencies**
    ```bash
    pip3 install -r requirements.txt
    ```

---

## Build Pipeline Components

This section guides you through building the individual component images and then all components together.

1.  **Navigate to Components Directory**
    ```bash
    cd pipeline-components/components
    ```

2.  **Build and Push Individual Component Images**
    Use the provided Makefile. Before building, **change the target image for all components to your respective IP** (e.g., `192.168.180.70:500/<component_name>:v1`).

    ```bash
    make build-feature-extraction
    make build-metrics-store
    make build-model-storage
    make build-model-training
    ```
    > **Purpose:** This step ensures that the `kfp_config.ini` file is generated for each component. You may ignore any errors raised during this process, but please verify that the configuration files are created.

3.  **Build All Components**
    Once every component has been built separately:
    ```bash
    make build-all
    ```

4.  **Install All Components**
    ```bash
    make install-all
    ```

---

## Running the Pipeline

After setting up and building the components, follow these steps to generate and upload your pipeline.

1.  **Navigate to Pipeline Directory**
    ```bash
    cd pipeline-components/pipeline
    ```

2.  **Generate Pipeline YAML**
    This command creates the `pipeline.yaml` file.
    ```bash
    python3 pipeline.py
    ```

3.  **Download Patch for Upload Pipeline**
    > **Note:** You will need the `upload_pipeline.py` utility file. This is intended to be a separate patch.
    > **Prerequisites:**
    > *   `pip install colorlog requests`
    > *   Update the IP address within the `upload_pipeline.py` script.

4.  **Upload the Pipeline**
    Execute the following command to upload your generated pipeline:
    ```bash
    python3 upload_pipeline.py -f pipeline.yaml -p <pipeline_name>
    ```
    Replace `<pipeline_name>` with your desired name for the pipeline.

---

## Manual Component Build Commands (Alternative)

If you need to build components manually, you can use the following `buildctl` commands. Run these from each component's directory (e.g., `components/model_training/model_training`).

### Model Training
```bash
sudo buildctl --addr=nerdctl-container://buildkitd build --no-cache --frontend dockerfile.v0 --opt filename=Dockerfile --local dockerfile=. --local context=. --output type=oci,name=t25kim/model_training:v5 | sudo nerdctl load --namespace k8s.io
```

### Metrics Store
```bash
sudo buildctl --addr=nerdctl-container://buildkitd build --no-cache --frontend dockerfile.v0 --opt filename=Dockerfile --local dockerfile=. --local context=. --output type=oci,name=t25kim/metrics_store:v5 | sudo nerdctl load --namespace k8s.io
```

### Feature Extraction
```bash
sudo buildctl --addr=nerdctl-container://buildkitd build --no-cache --frontend dockerfile.v0 --opt filename=Dockerfile --local dockerfile=. --local context=. --output type=oci,name=t25kim/feature_extraction:v5 | sudo nerdctl load --namespace k8s.io
```

### Model Storage
```bash
sudo buildctl --addr=nerdctl-container://buildkitd build --no-cache --frontend dockerfile.v0 --opt filename=Dockerfile --local dockerfile=. --local context=. --output type=oci,name=t25kim/model_storage:v5 | sudo nerdctl load --namespace k8s.io
```

---

**Your pipeline is now uploaded!** You can start your model training by providing the **`pipeline_name`** and **`pipeline_version`** when creating a training job.
