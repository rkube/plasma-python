#!/usr/bin/env python
import sys

# global variable defaults for non-MPI runs
comm = None
task_index = 0
num_workers = 1
NUM_GPUS = 0
MY_GPU = 0
# TODO(KGF): remove this (and all?) references to Keras backend
backend = ''
backendpackage = ''
bfloat16= ''
tf_ver = None
conf_file = None


def init_MPI():
    from mpi4py import MPI
    global comm, task_index, num_workers
    comm = MPI.COMM_WORLD
    task_index = comm.Get_rank()
    num_workers = comm.Get_size()


def init_GPU_backend(conf):
    global NUM_GPUS, MY_GPU, backend, backendpackage, bfloat16
    NUM_GPUS = conf['num_gpus']
    MY_GPU = task_index % NUM_GPUS
    backend = conf['model']['backend']

    # KGF: added via Subrata patch in April 2021 specific to tf2 branch
    # (neither of the following options are in the default conf.yaml)
    try:
        backendpackage = conf['model']['backendpackage']
    except KeyError as ex:
        backendpackage = backend

    try:
        bfloat16 = conf['model']['bfloat16']
    except KeyError as ex:
        bfloat16 = ''

# End of file global_vars.py
