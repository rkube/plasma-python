#!/usr/bin/env python

"""
This file contains helper functions to print only on certain
ranks when running with MPI
"""

def pprint_unique(obj):
    from pprint import pprint
    if task_index == 0:
        pprint(obj)


def print_unique(print_output, end='\n', flush=False):
    """Wrapper function to print but only MPI rank 0 calls print().
    """
    # TODO(KGF): maybe only allow end='','\r','\n' to prevent bugs?
    if task_index == 0:
        print(print_output, end=end, flush=flush)


def write_unique(write_str):
    """Only master MPI rank 0 writes to and flushes stdout.

    A specialized case of print_unique(). Unlike print(), sys.stdout.write():
    - Must pass a string; will not cast argument
    - end='\n' kwarg of print() is not available
    (often the argument here is prepended with \r=carriage return in order to
    simulate a terminal output that overwrites itself)
    """
    # TODO(KGF): \r carriage returns appear as ^M in Unix-encoded .out files
    # from non-interactive Slurm batch jobs. Convert these to true Unix
    # line feeds / newlines (^J, \n) when we can detect such a stdout
    if task_index == 0:
        sys.stdout.write(write_str)
        sys.stdout.flush()


def write_all(write_str):
    """All MPI ranks write to stdout, appending [rank].

    No MPI barriers, no guaranteed ordering of output.
    """
    if comm is not None:
        sys.stdout.write('[{}] '.format(task_index) + write_str)
    else:
        sys.stdout.write(write_str)
    sys.stdout.flush()


def flush_all_inorder(stdout=True, stderr=True):
    """Force each MPI rank to flush its buffered writes.
    
    Flushes to one or both of the standard streams, in order of rank.
    """
    for i in range(num_workers):
        comm.Barrier()
        if i == task_index:
            if stdout:
                sys.stdout.flush()
            if stderr:
                sys.stderr.flush()
    comm.Barrier()


# End of file mpi_print.py
