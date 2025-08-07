.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

.. Copyright (c) 2025 Samsung Electronics Co., Ltd. All Rights Reserved.

User-Guide
==========

.. contents::
   :depth: 3
   :local:


Overview
--------
This repository provides a set of **reusable Kubeflow pipeline components**
for building end-to-end AI/ML workflows. Each component is designed to
perform a specific task in the pipeline and can be independently developed,
tested, and reused across different pipelines and projects.

Key Concepts
------------

- **Component**: A self-contained, reusable unit of computation (e.g.,
  feature extraction, model training, model storage, metrics storage).
- **Pipeline**: An assembly of components, orchestrated to solve a
  specific ML use case.

Available Components
--------------------

- **Feature Extraction** Extracts features from data sources and stores
  them for downstream tasks. See:
  ```feature_extraction/feature_extraction_component.py`` <components/feature_extraction/feature_extraction/feature_extraction_component.py>`__

- **Model Training** Trains a machine learning model using the extracted
  features. See:
  ```model_training/model_training_component.py`` <components/model_training/model_training/model_training_component.py>`__

- **Model Storage** Registers and uploads trained models to a model
  registry or storage backend. See:
  ```model_storage/model_storage_component.py`` <components/model_storage/model_storage/model_storage_component.py>`__

- **Metrics Store** Stores evaluation metrics for trained models. See:
  ```metrics_store/metrics_store_component.py`` <components/metrics_store/metrics_store/metrics_store_component.py>`__

Each component is implemented as a Kubeflow pipeline component and can
be built and pushed as a container image using the provided
`Makefile <components/Makefile>`__.

Reusing Components
------------------

You can reuse these components in your own Kubeflow pipelines by
importing them and assembling them as needed. The components are
designed to be modular and configurable, making it easy to plug them
into different workflows.
