# -*- coding: utf-8 -*-

"""
Class representations of measurement signals.

"""

from os import remove
from os.path import isfile, join

import logging

import numpy as np

from plasma.utils.processing import get_individual_shot_file
from plasma.utils.downloading import get_missing_value_array
from plasma.utils.hashing import myhash

class Signal():
    """Represents a signal.
    
    """
    def __init__(self, description, paths, machines, tex_label=None,
                 causal_shifts=None, is_ip=False, normalize=True,
                 data_avail_tolerances=None, is_strictly_positive=False,
                 mapping_paths=None):
        """Initialize a signal
        
        Args:
          description: (string) String description of the signal
          paths: (string)
          machines: (machine) Type of machine on which this signal is defined
          tex_label: (string) Label used in plots
          causal_shifts: ???
          is_ip: ???
          normalize: (bool) If true, normalize this data in preprocessing. If False, skip normalization
          data_avail_tolerances:
          is_strictly_positive: (bool): If true, this data can not have negative values
          mapping_paths: ???
        
        """
        assert(len(paths) == len(machines))
        self.description = description
        self.paths = paths
        self.machines = machines  # on which machines is the signal defined
        if causal_shifts is None:
            self.causal_shifts = [0 for m in machines]
        else:
            self.causal_shifts = causal_shifts  # causal shift in ms
        self.is_ip = is_ip
        self.num_channels = 1
        self.normalize = normalize
        if data_avail_tolerances is None:
            data_avail_tolerances = [0 for m in machines]
        self.data_avail_tolerances = data_avail_tolerances
        self.is_strictly_positive = is_strictly_positive       
        self.mapping_paths = mapping_paths

    def is_strictly_positive_fn(self):
        raise DeprecationWarning("use signal.is_strictly_positive")

    def is_ip(self):
        raise DeprecationWarning("use signal.is_ip")

    def get_file_path(self, prepath, machine, shot_number):
        """Loads signal for given machine and shot number.
    
        Args:
        prepath: string, Base path, conf['paths']['base_path']
        machine machine, Type of machine (D3D, NSTX, Jet...)
        shot_number: int, Unique shot identifier

        Returns:
        ???: No idea

        Constructs the filename for a signal. Format:
        prepath/machine.name/signal.dirname/shot_number
        """

        dirname = self.get_path(machine)
        return get_individual_shot_file(join(prepath, 
                                             machine.name, 
                                             dirname), shot_number)

    def is_valid(self, prepath, shot, dtype='float32'):
        t, data, exists = self.load_data(prepath, shot, dtype)
        return exists

    def is_saved(self, prepath, shot):
        file_path = self.get_file_path(prepath, shot.machine, shot.number)
        return isfile(file_path)

    def load_data_from_txt_safe(self, prepath, shot, dtype='float32'):
        """Safely load signal data from a stored txt file.


        Args:
        prepath:  
        shot:
        dtype:


        Returns:
        data: ndarray(float) Signal data 

        """
        file_path = self.get_file_path(prepath, shot.machine, shot.number)
        if not self.is_saved(prepath, shot):
            print(f"Signal {self.description} , shot {shot.number} was never downloaded")
            return None, False

        if os.path.getsize(file_path) == 0:
            print(f"Signal {self.description}, shot {shot.number} was downloaded incorrectly (empty file). Removing.")
            remove(file_path)
            return None, False

        try:
            data = np.loadtxt(file_path, dtype=dtype)
            if np.all(data == get_missing_value_array()):
                print(f"Signal {self.description}, shot {shot.number} contains no data")
                return None, False
        except Exception as e:
            print(e)
            print(f"Couldnt load signal {self.description} shot {shot.number} from {file.path}. Removing")
            remove(file_path)
            return None, False

        return data, True

    def load_data(self, prepath, shot, dtype='float32'):
        data, succ = self.load_data_from_txt_safe(prepath, shot)
        if not succ:
            return None, None, False

        if np.ndim(data) == 1:
            data = np.expand_dims(data, axis=0)

        t = data[:, 0]
        sig = data[:, 1:]

        if self.is_ip:  # restrict shot to current threshold
            region = np.where(np.abs(sig) >= shot.machine.current_threshold)[0]
            if len(region) == 0:
                print(f"shot {shot.number} has no current")
                return None, sig.shape, False
            first_idx = region[0]
            last_idx = region[-1]
            # add 50 ms to cover possible disruption event
            last_time = t[last_idx]+5e-2
            last_indices = np.where(t > last_time)[0]
            if len(last_indices) == 0:
                last_idx = -1
            else:
                last_idx = last_indices[0]
            t = t[first_idx:last_idx]
            sig = sig[first_idx:last_idx, :]

        # make sure shot is not garbage data
        if len(t) <= 1 or (np.max(sig) == 0.0 and np.min(sig) == 0.0):
            if self.is_ip:
                print(f"shot {shot.number} has no current")
            else:
                print(f"Signal {self.description}, shot {shot.number} contains no data")
            return None, sig.shape, False

        # make sure data doesn't contain nan
        if np.any(np.isnan(t)) or np.any(np.isnan(sig)):
            print(f"Signal {self.description}, shot {shot.number}")
            return None, sig.shape, False

        return t, sig, True

    def fetch_data_basic(self, machine, shot_num, c, path=None):
        if path is None:
            path = self.get_path(machine)
        success = False
        mapping = None
        try:
            time, data, mapping, success = machine.fetch_data_fn(
                path, shot_num, c)
        except Exception as e:
            print(e)
            sys.stdout.flush()

        if not success:
            return None, None, None, False

        time = np.array(time) + 1e-3*self.get_causal_shift(machine)
        return time, np.array(data), mapping, success

    def fetch_data(self, machine, shot_num, c):
        return self.fetch_data_basic(machine, shot_num, c)

    def is_defined_on_machine(self, machine):
        return machine in self.machines

    def is_defined_on_machines(self, machines):
        return all([m in self.machines for m in machines])

    def get_path(self, machine):
        idx = self.get_idx(machine)
        return self.paths[idx]

    def get_mapping_path(self, machine):
        if self.mapping_paths is None:
            return None
        else:
            idx = self.get_idx(machine)
            return self.mapping_paths[idx]

    def get_causal_shift(self, machine):
        idx = self.get_idx(machine)
        return self.causal_shifts[idx]

    def get_data_avail_tolerance(self, machine):
        idx = self.get_idx(machine)
        return self.data_avail_tolerances[idx]

    def get_idx(self, machine):
        assert(machine in self.machines)
        idx = self.machines.index(machine)
        return idx

    def description_plus_paths(self):
        return self.description + ' ' + ' '.join(self.paths)

    def __eq__(self, other):
        if other is None:
            return False
        return self.description_plus_paths().__eq__(
            other.description_plus_paths())

    def __ne__(self, other):
        return self.description_plus_paths().__ne__(
            other.description_plus_paths())

    def __lt__(self, other):
        return self.description_plus_paths().__lt__(
            other.description_plus_paths())

    def __hash__(self):
        return myhash(self.description_plus_paths())

    def __str__(self):
        return self.description

    def __repr__(self):
        return self.description


