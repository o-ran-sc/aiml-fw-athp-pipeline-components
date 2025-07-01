# AIML Pipeline Components

This repository provides a set of **reusable Kubeflow pipeline components** for building end-to-end AI/ML workflows. Each component is designed to perform a specific task in the pipeline and can be independently developed, tested, and reused across different pipelines and projects.

## Key Concepts

- **Component**: A self-contained, reusable unit of computation (e.g., feature extraction, model training, model storage, metrics storage).
- **Pipeline**: An assembly of components, orchestrated to solve a specific ML use case.

## Available Components

- **Feature Extraction**  
  Extracts features from data sources and stores them for downstream tasks.  
  See: [`feature_extraction/feature_extraction_component.py`](components/feature_extraction/feature_extraction/feature_extraction_component.py)

- **Model Training**  
  Trains a machine learning model using the extracted features.  
  See: [`model_training/model_training_component.py`](components/model_training/model_training/model_training_component.py)

- **Model Storage**  
  Registers and uploads trained models to a model registry or storage backend.  
  See: [`model_storage/model_storage_component.py`](components/model_storage/model_storage/model_storage_component.py)

- **Metrics Store**  
  Stores evaluation metrics for trained models.  
  See: [`metrics_store/metrics_store_component.py`](components/metrics_store/metrics_store/metrics_store_component.py)

Each component is implemented as a Kubeflow pipeline component and can be built and pushed as a container image using the provided [Makefile](components/Makefile).

## Reusing Components

You can reuse these components in your own Kubeflow pipelines by importing them and assembling them as needed. The components are designed to be modular and configurable, making it easy to plug them into different workflows.

### Example: Assembling a Pipeline

The file [`pipeline/pipeline.py`](pipeline/pipeline.py) demonstrates how to assemble the reusable components into a complete Kubeflow pipeline:

- Import each component at the top of the pipeline function.
- Instantiate and connect the components, passing outputs from one as inputs to the next.
- Use Kubeflow DSL and Kubernetes helpers to manage resources (e.g., PVCs).

**Excerpt from [`pipeline/pipeline.py`](pipeline/pipeline.py):**

````python
from feature_extraction.feature_extraction_component import download_features
from model_training.model_training_component import model_training
from model_storage.model_storage_component import model_storage
from metrics_store.metrics_store_component import metrics_store

@dsl.pipeline
def pipeline():
    # ... set up configs ...
    comp1 = download_features(...)
    comp2 = model_training(...)
    comp3 = model_storage(modelpath=comp2.outputs['path'], ...)
    comp4 = metrics_store(metrics={"accuracy": comp2.outputs['accuracy']})
    # ... manage dependencies and resources ...