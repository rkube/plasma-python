# Traverse Tutorial
*Last updated July 2021.*

Building the package
====================

Login to Traverse
-----------------

First, login to Traverse cluster headnode via ssh::

    ssh -XC <yourusername>@traverse.princeton.edu


Note, `-XC` is optional; it is only necessary if you are planning on performing remote
visualization, e.g. the output `.png` files from the below
[section](#Learning-curves-and-ROC-per-epoch). Trusted X11 forwarding can be used with
`-Y` instead of `-X` and may prevent timeouts, but it disables X11 SECURITY extension
controls. Compression `-C` reduces the bandwidth usage and may be useful on slow connections.

Sample installation on Traverse
-------------------------------

Add the following flag to your environment::

    export LD_PRELOAD=/usr/lib64/libpmix.so.2


The recommended way is to edit your `~/.bashrc` and then reload the environment as follows:

    source ~/.bashrc



Next, check out the source code from github:

    git clone https://github.com/PPPLDeepLearning/plasma-python
    cd plasma-python
    git checkout tf2


After that, create an isolated Anaconda environment and load CUDA drivers, an MPI compiler,
and the HDF5 library. The suggested libraries are included with the repository, so simple
sourcing `plasma-python/envs/traverse.cmd` will load these into your path. Traverse uses a
PowerPC arcitecture, which is not as widely supported with many common libraries. The `python=3.6`
option below sets the python version in this anaconda environment to the older python version 3.6,
which will help down the line with installing libraries. ::

    #cd plasma-python
    module load anaconda3
    conda env create --name my_env --file envs/requirements-traverse.yaml python=3.6
    conda activate my_env
`

Go into `envs/traverse.cmd` and modify the `conda activate` command to `conda activate my_env`. Run::


    source envs/traverse.cmd


As of the latest update of this document (Summer 2021), the above modules correspond to the following versions
on the Traverse system, given by `module list`::

    Currently Loaded Modulefiles:
        1) anaconda3/2020.7                 3) cudnn/cuda-9.2/7.6.3             5) hdf5/gcc/openmpi-1.10.2/1.10.0
        2) cudatoolkit/10.2                 4) openmpi/cuda-11.0/gcc/4.0.4/64


Next, install the `plasma-python` package::

    #conda activate my_env
    python setup.py install --user


Common runtime issue: when to load environment and when to call `sbatch`
-----------------------------------------------------------------------
When queueing jobs on Traverse or running slurm managed scripts, *DO NOT* load your anaconda
environment before doing so. This will cause a module loading issue. It is *highly*
suggested that you build `plasma-python` in one terminal witht the anaconda environment
loaded and run it in another without the anaconda environment loaded to avoid this issue.
Alternatively, calling `module purge` before using slurm fixes this issue.

Commond build issue: creating anaconda environment fails
--------------------------------------------------------
On Traverse, pytorch has been observed to not install correctly. By default it is commented out,
but if that's not the case the quick fix is to not intall it by commenting out the line 17 in
`envs/requirements-traverse.yaml`

    7 dependencies:
    8   - python>=3.6.8
    9   - cython
    10   - pip
    11   - scipy
    12   - pandas
    13   - flake8
    14   - h5py<3.0.0
    15   - pyparsing
    16   - pyyaml
    17   #- pytorch>1.3

Commond build issue: `xgboost` not installing
---------------------------------------------

On Traverse, `xgboost` doesn't seem to build right. Just ignore it for now by editing
`setup.py` (comment line 35). Rebuild as above.

    30       install_requires=[
    31           'pathos',
    32           'matplotlib',
    33           'hyperopt',
    34           'mpi4py',
    35           #'xgboost',
    36           'scikit-learn',
    37           'joblib',
    38           ],

Common build issue: cluster's MPI library and `mpi4py`
------------------------------------------------------

Common issue is Intel compiler mismatch in the `PATH` and what you
use in the module. With the modules loaded as above, you should see something like this (as of summer 2021)::

    $ which mpicc
    /usr/local/openmpi/cuda-11.0/4.0.4/gcc/x86_64/bin/mpicc


In both cases, especially note the presence of the CUDA directory in this path. This indicates
that the loaded OpenMPI library is [CUDA-aware](https://www.open-mpi.org/faq/?category=runcuda).

If you `conda activate` the Anaconda environment **after** loading the OpenMPI library, your
application would be built with the MPI library from Anaconda, which has worse performance on
this cluster and could lead to errors.
See [mpi4py on HPC Clusters](https://researchcomputing.princeton.edu/support/knowledge-base/mpi4py)
for a related discussion.


Understanding and preparing the input data
------------------------------------------
"Location of the data on Traverse

Tigress is also avilable on Traverse, so this step is identical to TigerGPU. The JET and D3D
datasets contain multi-modal time series of sensory measurements leading up to deleterious events
called plasma disruptions. The datasets are located in the `/tigress/FRNN` project directory of the
[GPFS](https://www.ibm.com/support/knowledgecenter/en/SSPT3X_3.0.0/com.ibm.swg.im.infosphere.biginsights.product.doc/doc/bi_gpfs_overview.html)
filesystem on Princeton University clusters.

For convenience, create following symbolic links::

    cd /tigress/<netid>
    ln -s /tigress/FRNN/shot_lists shot_lists
    ln -s /tigress/FRNN/signal_data signal_data


"Configuring the dataset
All the configuration parameters are summarised in `examples/conf.yaml`.
In this section, we highlight the important ones used to control the input data.

Currently, FRNN is capable of working with JET and D3D data as well as thecross-machine regime.
The switch is done in the configuration file::

    paths:
        ...
        data: 'jet_0D'


Older yaml files kept for archival purposes will denote this data set as follow::
    paths:
        ...
        data: 'jet_data_0D'

use `d3d_data` for D3D signals, use `jet_to_d3d_data` ir `d3d_to_jet_data` for cross-machine regime.

By default, FRNN will select, preprocess, and normalize all valid signals available in the above dataset.
To chose only specific signals use::

paths:
    ...
    specific_signals: [q95,ip]

if left empty `[]` will use all valid signals defined on a machine. Only set this variable if you need a custom set of signals.

Other parameters configured in the `conf.yaml` include batch size, learning rate, neural network topology and special
conditions for hyperparameter scans.

On Traverse, the data is stored in the `tigress` filesystem. You will probably need to modify
`conf.yaml` to point there by setting::

    fs_path: '/tigress/'
    ...
    fs_path_output: '/tigress/'

This is the end of this file.