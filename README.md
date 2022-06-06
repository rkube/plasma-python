# FRNN 

[![Build Status](https://travis-ci.com/PPPLDeepLearning/plasma-python.svg?branch=master)](https://travis-ci.com/PPPLDeepLearning/plasma-python)
[![Build Status](https://jenkins.princeton.edu/buildStatus/icon?job=FRNM/PPPL)](https://jenkins.princeton.edu/job/FRNM/job/PPPL/)

## Package description

The Fusion Recurrent Neural Net (FRNN) software is a Python package that implements deep learning models for disruption prediction in tokamak fusion plasmas.

It consists of 4 core modules:

- `models`: Python classes necessary to construct, train and optimize deep RNN models. Including a distributed data-parallel synchronous implementation of mini-batch gradient descent. FRNN makes use of MPI for communication and supports TensorFlow via the high-level Keras API. FRNN offers the built-in ability to run hyperparameter search optimizations.

- `preprocessors`: signal preprocessing and normalization classes, including the methods necessary to prepare physical data for stateful LSTM training.

- `primitives`: contains abstractions specific to the domain, implemented as Python classes. For instance, `Shot`: a measurement of plasma current as a function of time. The Shot object contains attributes corresponding to unique identifier of a shot, disruption time in milliseconds, time profile of the shot converted to time-to-disruption values, validity of a shot (whether plasma current reaches a certain value during the shot), etc. Other primitives include `Machines` and `Signals` which carry the relevant information necessary for incorporating physics data into the overall pipeline. Signals know the Machine they live on, their mds+ paths, code for being downloaded, preprocessing approaches, their dimensionality, etc. Machines know which Signals are defined on them, which mds+ server houses the data, etc.

- `utilities`: a set of auxiliary functions for preprocessing, performance evaluation and learning curves analysis.

In addition to the `utilities` FRNN supports TensorBoard scaler variable summaries, histogramms of layers, activations and gradients and graph visualizations.

This is a pure Python implementation for Python versions 3.6+.

## Installation

The package comes with a standard setup script and a list of dependencies which include: mpi4py, TensorFlow, h5py, Pathos. It also requires a standard set of CUDA drivers to run on GPU.

Then checkout the repo and use the setup script:

```bash
git clone https://github.com/PPPLDeepLearning/plasma-python
cd plasma-python
pip install -e .
```

with `sudo` if superuser permissions are needed or `--home=~` to install in a home directory. The latter option requires an appropriate `PYTHONPATH`.

Alternatively run (no need to checkout the repository in that case):
```bash
pip install -i https://testpypi.python.org/pypi plasma
```
optionally add `--user` to install in a home directory.


## Tutorials

For a tutorial, check out: [PrincetonUTutorial.md](docs/PrincetonUTutorial.md)


## Breaking Change introduced by ELMs branch

* The base path for all signals is now `paths.base_path`. This path is directly specified in
  `conf.yaml`

* Renaming clean_shot_list to format_shotlist in Preprocessing

* Removed Preprocess.all_are_preprocessed (one-liner that was called in one line)


