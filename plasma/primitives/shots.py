'''
#########################################################
This file containts classes to handle data processing

Author: Julian Kates-Harbeck, jkatesharbeck@g.harvard.edu

This work was supported by the DOE CSGF program.
#########################################################
'''

import os
import random 

import numpy as np
import logging

from plasma.primitives.machine import Machine, MachineD3D, MachineJET, MachineNSTX

from plasma.utils.processing import train_test_split, cut_and_resample_signal
from plasma.utils.downloading import makedirs_process_safe
from plasma.utils.find_elms import *
from plasma.utils.find_rational import *

from plasma.data.user_data import bad_shot_list_d3d


class BadShotException(Exception):
    """Raised when a bad shot is processed."""
    pass


class ShotListFiles(object):
    """Representation of a list of shot files."""
    def __init__(self, machine, basepath, filelist, description=None):
        """Initializes ShotListFiles


        Input:
          machine (machine), type of tokamak device
          basepath (string) Absolute path where the shot lists are located
          filelist (list, shots) List of shots
          description..:

        """
        self.machine = machine
        self.basepath = basepath
        self.filelist = filelist
        self.description = description

        # Ensure that all files exist in basepath
        for fname in filelist:
            try:
                os.stat(os.path.join(basepath, fname))
            except OSError as err:
                logging.error(f"ShotListFiles: file{os.path.join(basepath, fname)} does not exist. Exiting")
                raise(err)

        logging.info(f"ShotListFiles.__init__: machine={self.machine}, prepath={self.prepath}, paths={self.paths}, description={self.description}")

    def __str__(self):
        return f"machine: {self.machine.__str__}\n {self.description}"

    def __repr__(self):
        return self.__str__()

    def get_single_shot_numbers_and_disruption_times(self, full_path):
        data = np.loadtxt(full_path, ndmin=1, dtype={
                'names': (
                    'num', 'disrupt_times'), 'formats': (
                    'i4', 'f4')})
        shots = np.array(list(zip(*data))[0])
        disrupt_times = np.array(list(zip(*data))[1])
        return shots, disrupt_times

    def get_shot_numbers_and_disruption_times(self):
        all_shots = []
        all_disruption_times = []
        # all_machines_arr = []
        for fname in self.filelist:
            full_path = os.path.join(self.basepath, fname)
            shots, disruption_times = (
                self.get_single_shot_numbers_and_disruption_times(full_path))
            all_shots.append(shots)
            all_disruption_times.append(disruption_times)
        return np.concatenate(all_shots), np.concatenate(all_disruption_times)


class ShotList(object):
    """ 
    A wrapper class around list of Shot objects, providing utilities to
    extract, load and transform Shots before passing them to an estimator.

    During distributed training, shot lists are split into sublists.
    A sublist is a ShotList object having num_at_once shots. The ShotList
    contains an entire dataset as specified in the configuration file.
    """

    def __init__(self, shots=None):
        '''
        A ShotList is a list of 2D Numpy arrays.
        '''
        self.shots = []
        if shots is not None:
            assert(all([isinstance(shot, Shot) for shot in shots]))
            self.shots = [shot for shot in shots]

    def load_from_shot_list_files_object(self, shot_list_files_object, signals):
        """Appends a shot_list to the list of shots.

        Arguments:
          shot_list_files_object:
          signals:

        Returns:
            nothing

   
        """

        print("Called load_from_shot_list_files_object: ", type(shot_list_files_object), shot_list_files_object)
        shot_numbers, disruption_times = shot_list_files_object.get_shot_numbers_and_disruption_times()
        for number, t in list(zip(shot_numbers, disruption_times)):
            self.shots.append(Shot(number=number, t_disrupt=t, machine=shot_list_files_object.machine,
                                   signals=[s for s in signals if s.is_defined_on_machine(machine)]))

    def split_train_test(self, conf):
        # shot_list_dir = conf['paths']['shot_list_dir']
        shot_files = conf['paths']['shot_files']
        shot_files_test = conf['paths']['shot_files_test']
        train_frac = conf['training']['train_frac']
        shuffle_training = conf['training']['shuffle_training']
        use_shots = conf['data']['use_shots']
        all_signals = conf['paths']['all_signals']
        # split randomly
        use_shots_train = int(round(train_frac*use_shots))
        use_shots_test = int(round((1-train_frac)*use_shots))
        if len(shot_files_test) == 0:
            shot_list_train, shot_list_test = train_test_split(
                self.shots, train_frac, shuffle_training)
        # train and test list given
        else:
            shot_list_train = ShotList()
            shot_list_train.load_from_shot_list_files_objects(
                shot_files, all_signals)

            shot_list_test = ShotList()
            shot_list_test.load_from_shot_list_files_objects(
                shot_files_test, all_signals)

        shot_numbers_train = [shot.number for shot in shot_list_train]
        shot_numbers_test = [shot.number for shot in shot_list_test]
        print(len(shot_numbers_train), len(shot_numbers_test))
        # make sure we only use pre-filtered valid shots
        shots_train = self.filter_by_number(shot_numbers_train)
        shots_test = self.filter_by_number(shot_numbers_test)
        return shots_train.random_sublist(
            use_shots_train), shots_test.random_sublist(use_shots_test)

    def split_direct(self, frac, do_shuffle=True):
        shot_list_one, shot_list_two = train_test_split(
            self.shots, frac, do_shuffle)
        return ShotList(shot_list_one), ShotList(shot_list_two)

    def filter_by_number(self, numbers):
        new_shot_list = ShotList()
        numbers = set(numbers)
        for shot in self.shots:
            if shot.number in numbers:
                new_shot_list.append(shot)
        return new_shot_list

    def set_weights(self, weights):
        assert(len(weights) == len(self.shots))
        for (i, w) in enumerate(weights):
            self.shots[i].weight = w

    def sample_weighted_given_arr(self, p):
        p = p/np.sum(p)
        idx = np.random.choice(range(len(self.shots)), p=p)
        return self.shots[idx]

    def sample_shot(self):
        idx = np.random.choice(range(len(self.shots)))
        return self.shots[idx]

    def sample_weighted(self):
        p = np.array([shot.weight for shot in self.shots])
        return self.sample_weighted_given_arr(p)

    def sample_single_class(self, disruptive):
        weights_d = 0.0
        weights_nd = 1.0
        if disruptive:
            weights_d = 1.0
            weights_nd = 0.0
        p = np.array([weights_d if shot.is_disruptive_shot()
                      else weights_nd for shot in self.shots])
        return self.sample_weighted_given_arr(p)

    def sample_equal_classes(self):
        weights_d, weights_nd = self.get_weights_d_nd()
        p = np.array([weights_d if shot.is_disruptive_shot()
                      else weights_nd for shot in self.shots])
        return self.sample_weighted_given_arr(p)

    def get_weights_d_nd(self):
        num_total = len(self)
        num_d = self.num_disruptive()
        num_nd = num_total - num_d
        if num_nd == 0 or num_d == 0:
            weights_d = 1.0
            weights_nd = 1.0
        else:
            weights_d = 1.0*num_nd
            weights_nd = 1.0*num_d
        max_weight = np.maximum(weights_d, weights_nd)
        return weights_d/max_weight, weights_nd/max_weight

    def num_timesteps(self, prepath):
        ls = [shot.num_timesteps(prepath) for shot in self.shots]
        timesteps_total = sum(ls)
        timesteps_d = sum([ts for (i, ts) in enumerate(
            ls) if self.shots[i].is_disruptive_shot()])
        timesteps_nd = timesteps_total-timesteps_d
        return timesteps_total, timesteps_d, timesteps_nd

    def num_disruptive(self):
        return len([shot for shot in self.shots if shot.is_disruptive_shot()])

    def __len__(self):
        return len(self.shots)

    def __str__(self):
        return str([s.number for s in self.shots])

    def __iter__(self):
        return self.shots.__iter__()

    def next(self):
        return self.__iter__().next()

    def __add__(self, other_list):
        return ShotList(self.shots + other_list.shots)

    def index(self, item):
        return self.shots.index(item)

    def __getitem__(self, key):
        return self.shots[key]

    def random_sublist(self, num):
        num = min(num, len(self))
        shots_picked = np.random.choice(self.shots, size=num, replace=False)
        return ShotList(shots_picked)

    def sublists(self, num, do_shuffle=True, equal_size=False):
        lists = []
        if do_shuffle:
            self.shuffle()
        for i in range(0, len(self), num):
            subl = self.shots[i:i+num]
            while equal_size and len(subl) < num:
                subl.append(random.choice(self.shots))
            lists.append(subl)
        return [ShotList(l) for l in lists]

    def shuffle(self):
        np.random.shuffle(self.shots)

    def sort(self):
        self.shots.sort()  # will sort based on machine and number

    def as_list(self):
        return self.shots

    def append(self, shot):
        assert(isinstance(shot, Shot))
        self.shots.append(shot)

    def remove(self, shot):
        assert(shot in self.shots)
        self.shots.remove(shot)
        assert(shot not in self.shots)

    def make_light(self):
        for shot in self.shots:
            shot.make_light()

    def append_if_valid(self, shot):
        if shot.valid:
            self.append(shot)
            return True
        else:
            # print('Warning: shot {} not valid, omitting'.format(shot.number))
            return False


class Shot(object):
    """A class representing a shot. 

    Each shot is a measurement of plasma properties (current, locked mode
    amplitude, etc.) as a function of time.

    For 0D time-series data, each shot is modeled as a 2D Numpy array - time vs a plasma
    property.
    """

    def __init__(self, number=None, machine=None, signals=None, signals_dict=None,
                 ttd=None, valid=None, is_disruptive=None, t_disrupt=None):
        """Initializes a shot object.

        Shot objects contain following attributes:

         - number.........: integer, unique identifier of a shot
         - t_disrupt......: double, disruption time in milliseconds (second column in
                            the shotlist input file)
         - ttd............: Numpy array of doubles, time profile of the shot converted to
                             time-to-disruption values
         - valid..........: boolean flag indicating whether plasma property
                            (specifically, current) reaches a certain value during the shot
         - is_disruptive..: boolean flag indicating whether a shot is disruptive
        """
        self.number = number               # Shot identifier
        self.machine = machine             # machine on which the shot is defined
        self.signals = signals             # List of signals available in the shot
        self.signals_dict = signals_dict   # Dictionary of signals
        self.ttd = ttd                     # Timebase of the shot. Approaches zero for disruption
        self.valid = valid                 # Valid. True if the shot shold be used for training
        self.is_disruptive = is_disruptive # True if the shot disrupts, false otherwise
        self.t_disrupt = t_disrupt         # Time of the disruption
        self.weight = 1.0
        self.augmentation_fn = None

        if t_disrupt is not None:
            self.is_disruptive = Shot.is_disruptive_given_disruption_time(
                t_disrupt)
        else:
            logging.info('Warning, disruption time (disruptivity) not set! ',
                  'Either set t_disrupt or is_disruptive')


        # The DIII-D shots below 
        if machine == MachineD3D and self.number in bad_shot_list_d3d:
            raise BadShotException(f"Shot.__init__(): Shot {self.number} on D3D is not good.")

    def get_id_str(self):
        return f"{self.machine} : {self.number}"

    def __lt__(self, other):
        return self.get_id_str().__lt__(other.get_id_str())

    def __eq__(self, other):
        return self.get_id_str().__eq__(other.get_id_str())

    def __hash__(self):
        import hashlib
        return int(
            hashlib.md5(
                self.get_id_str().encode('utf-8')).hexdigest(),
            16)

    def __str__(self):
        """String representation of the shot"""
        string = f"number: {self.number}\n"
        string += "machine: {self.machine}\n"
        string += "signals: {self.signal}\n"
        string += "signals_dict: {signals_dict}\n"
        string += "ttd: {self.ttd}\n"
        string += "valid: {self.valid}\n"
        string += "is_disruptive: {self.is_disruptive}\n"
        string += "t_disrupt: {self.t_disrupt}\n"
        return string

    def num_timesteps(self, prepath):
        self.restore(prepath)
        ts = self.ttd.shape[0]
        self.make_light()
        return ts

    def get_number(self):
        raise DeprecationWarning("Replace shot.get_number() with shot.number")

    def get_signals(self):
        raise DeprecationWarning("Replace shot.get_signals() with shot.signals")

    def is_valid(self):
        raise DeprecationWarning("Replace shot.is_valid() with shot.valid")

    def is_disruptive_shot(self):
        raise DeprecationWarning("Replace shot.is_disruptive_shot() with shot.is_disruptive")


    def get_data_arrays(self, use_signals, dtype=np.float32, cont_signal=None,
                        cont_value=None):
        """Allocates a numpy array for signals in this shot.

        Allocate a 2d array with dimensions length(time) * sum signal.num_channels.

        If the optional parameter contaminate_signal is equals the description of a 
        existing signal in self.signals_dict, the values of that signal will be replace with
        cont_value

        Parameters:
          use_signals: list(signals) List of signals to use for data allocation
          dtype: (datatype) Data type to use for the array. Default=float32
          cont_signal: (string) Description of the signal that will be contaminated
          cont_value: (float) New value of the contamination signals


        Output:
          t_array: ndarray(float)  Time base array
          signal_array: ndarray(float)  Array with one signal per column
        """


        # Pre-allocate numpy array
        signal_array = np.zeros((len(self.ttd), 
                                 sum([sig.num_channels for sig in use_signals])),
                                dtype=dtype)

        # Iteratively copy all signal data into the allocated array
        curr_idx = 0
        for sig in use_signals:
            signal_array[:, curr_idx:curr_idx + sig.num_channels] = self.signals_dict[sig]
            if sig.description == cont_signal:
              logging.info(f"Contaminating {sig.description} ..Artificially.............................")
              signal_array[:,curr_idx:curr_idx+sig.num_channels] = cont_value
            curr_idx += sig.num_channels
        return self.ttd, signal_array


    def get_data_arrays_lmtarget(self, use_signals, dtype='float32',predict_mode='shift_target',predict_time=0,target_description='Locked mode amplitude'):
        def derivative_lm(arr):
            if len(arr)<3:
               return arr
            else:
               res=[0]
               for i in range(1,len(arr)):
                 res.append(arr[i]-arr[i-1])
               return np.array(res)
        def derivative_lm_norm(arr):
            if len(arr)<3:
               return arr
            else:
               res=[0]
               for i in range(1,len(arr)):
                 res.append((arr[i]-arr[i-1])/(arr[i-1]+0.01))
               return np.array(res)
        def ttelm(arr):
            if len(arr)<3:
                return [10,10,10]
            else:
                _,tar = find_elm_events_tar(np.arange(0,len(arr)),arr)
                cutting_time = 100
                tar[np.argwhere(tar>cutting_time)] = cutting_time
                tar = tar*0.1
            return tar

        def smooth_lm(arr,window=50):
             #print('smooth_lm_arr_shape:',arr.shape,arr[0])
             window=window//2
             if len(arr)==0:
                return []
             pad=[]
             for i in range(window):
                 pad.append(arr[0])
             pad=np.array(pad)
             arr_pad=np.concatenate((np.array(pad),arr))
             arr_pad=np.concatenate((arr_pad,np.array([arr[-1]]*window)))
             ress=[]
             for i in range(window,len(arr)+window):
                ress.append(sum(arr_pad[i-window:i+window])/(window*2))
             return np.array(ress)

        predict_time=predict_time+1
        t_array = self.ttd
        signal_array = np.zeros(
            (len(t_array), sum([sig.num_channels for sig in use_signals])+2*128),
            dtype=dtype)
        curr_idx = 0
        lm=self.ttd
        res=[]
        for sig in self.signals:
            if sig.description in target_description and len(t_array)>predict_time:
               #print('TargetDescription:',target_description) 
               #print(len(t_array),predict_time)
               lm=self.ttd.copy()
               lm[:-predict_time]=np.reshape(self.signals_dict[sig][predict_time:],(-1))
               lm[-predict_time:]=self.signals_dict[sig][-predict_time][0]
               res.append(lm)
        #       self.signals_dict[sig]=0.0
            if sig in use_signals:
              signal_array[:, curr_idx:curr_idx
                         + sig.num_channels] = self.signals_dict[sig]
              curr_idx += sig.num_channels
              if sig.description == "q profile efitrt1":
                print(self.number)
                n_mode,m_mode = get_rational(self.signals_dict[sig],self.number,saving = True)
                signal_array[:, curr_idx:curr_idx
                         + sig.num_channels] = n_mode
                curr_idx += sig.num_channels
                signal_array[:, curr_idx:curr_idx
                         + sig.num_channels] = m_mode
                curr_idx += sig.num_channels

           #   else:
           #     signal_array[:, curr_idx:curr_idx
           #              + sig.num_channels] = self.signals_dict[sig]

        if predict_mode=='smooth_target':
            for i in range(len(res)):
                res[i]=smooth_lm(res[i],window=50)
        if predict_mode=='derivative_target':
            for i in range(len(res)):
                res[i]=derivative_lm(res[i])
        if predict_mode=='derivative_target_norm':
            for i in range(len(res)):
                res[i]=derivative_lm_norm(res[i])
        if predict_mode=='ttelm_target':
            for i in range(len(res)):
                res[i]=ttelm(res[i])
        return np.transpose(np.array(res)), signal_array


    def get_individual_signal_arrays(self):
        # guarantee ordering
        return [self.signals_dict[sig] for sig in self.signals]

    def preprocess(self, conf):
        logging.info(f"Preprocessing shot {self.number}")
        # get minmax times
        time_arrays, signal_arrays, t_min, t_max, valid = (
            self.get_signals_and_times_from_file(conf))
        self.valid = valid
        print(f'Shot {self.number}, valid={self.valid} ......................')
        # cut and resample
        if self.valid == True:
            try:
                self.cut_and_resample_signals(
                   time_arrays, signal_arrays, t_min, t_max, conf)
            except:
                self.valid=False


    def get_signals_and_times_from_file(self, conf):
        """Load signals and time bases for a given shot.

        This method loads all signal data and time bases from text files.
        Used keys from conf:
        conf["paths"]["data"] - ???
        conf["data"]["floatx"] - Datatype, either float32 or float64
        conf["paths"]["signal_prepath"] - ???

        Parameters:
          conf (dict) global configuration


        Output:
          time_arrays: List of time bases for the specified signals
          signal_arrays: List of ndarrays for the specified signals
          t_min: Min time of all time bases
          t_max: Max time in all time bases
          valid: True: Good shot. False: Bad shot

        """
        valid = True            # valid specifies whether we got a good shot or nog
        t_min = -np.Inf         #
        t_max = np.Inf          #
        # t_thresh = -1
        signal_arrays = []      # To be populated with a list of ndarrays with shot data
        time_arrays = []        # To be populated with a list of ndarrays, containing time bases 
        garbage = False
        
        if conf['paths']['data'] =='d3d_data_garbage':
            garbage=True
        elif conf['paths']['data'] == 'd3d_data_n1rms_gar' :
            garbage=True
        non_valid_signals = 0 # Counts the number of invalid signals for this shot

        signal_prepath = conf['paths']['signal_prepath']

        # Iterate over all signals and extract data
        for(i, signal) in enumerate(self.signals):
            # In case of a list, handle each signal individually
            if isinstance(signal_prepath, list):
                for prepath in signal_prepath:
                    t, sig, valid_signal = signal.load_data(prepath, self, conf['data']['floatx'])
            else:
                t, sig, valid_signal = signal.load_data(signal_prepath, self, conf['data']['floatx'])

            if not valid_signal:
                if signal.is_ip or ('n1' in signal.description) or garbage==False or sig==None:
                   ########################Not allow a shot if it is missing plasma current information, or q95 is missing 
                   return None, None, None, None, False
                else:
                   t=np.arange(0,20,0.001)
                   sig=np.zeros((t.shape[0],sig[1]))
                   non_valid_signals+=1
                   signal_arrays.append(sig)
                   time_arrays.append(t)
            else:
                assert(len(sig.shape) == 2)
                assert(len(t.shape) == 1)
                assert(len(t) > 1)
                t_min = max(t_min, np.min(t))
                signal_arrays.append(sig)
                time_arrays.append(t)
                
                if self.is_disruptive and self.t_disrupt > np.max(t):
                    t_max_total = (
                        np.max(t) + signal.get_data_avail_tolerance(
                            self.machine)
                    )
                    if (self.t_disrupt > t_max_total):
                        if garbage==False:
                            print('Shot {}: disruption event '.format(self.number),
                              'is not contained in valid time region of ',
                              'signal {} by {}s, omitting.'.format(
                                  self.number, signal,
                                  self.t_disrupt - np.max(t)))
                            valid = False
                        else:
                            non_valid_signals+=1
                            t=np.arange(0,20,0.001)
                            sig=np.zeros((t.shape[0],sig.shape[1]))
                            #Setting the entire channel to zero to prevent any peeking into possible disruptions from this early ended channel
                    else:
                        t_max = np.max(
                            t) + signal.get_data_avail_tolerance(self.machine)
                else:
                    t_max = min(t_max, np.max(t))

        # make sure the shot is long enough.
        dt = conf['data']['dt']
        if (t_max - t_min)/dt <= (2*conf['model']
                                  ['length']+conf['data']['T_min_warn']):
            logging.error(f"Shot {self.number} contains insufficient data, omitting.")
            valid = False

        assert(t_max > t_min or not valid), f"t max: {t_max}, t_min: {_min}"

        if self.is_disruptive:
            assert(self.t_disrupt <= t_max or not valid)
            t_max = self.t_disrupt
        if non_valid_signals>2:
            logging.warning(f"Shot {self.number} >=3 channels are contaminated...")
            valid=False

        return time_arrays, signal_arrays, t_min, t_max, valid

    def cut_and_resample_signals(
            self,
            time_arrays,
            signal_arrays,
            t_min,
            t_max,
            conf):
        dt = conf['data']['dt']
        signals_dict = dict()
        print('resampling..',self.number)
        # resample signals
        assert((len(signal_arrays) == len(time_arrays)
                == len(self.signals)) and len(signal_arrays) > 0)
        tr = 0
        for (i, signal) in enumerate(self.signals):
            print(signal)
            tr, sigr = cut_and_resample_signal(
                time_arrays[i], signal_arrays[i], t_min, t_max, dt,
                conf['data']['floatx'])
            signals_dict[signal] = sigr

        ttd = self.convert_to_ttd(tr, conf)
        self.signals_dict = signals_dict
        self.ttd = ttd

    def convert_to_ttd(self, tr, conf):
        T_max = conf['data']['T_max']
        dt = conf['data']['dt']
        if self.is_disruptive:
            ttd = max(tr) - tr
            ttd = np.clip(ttd, 0, T_max)
        else:
            ttd = T_max*np.ones_like(tr)
        ttd = np.log10(ttd + 1.0*dt/10)
        return ttd

    def save(self, prepath):
        makedirs_process_safe(prepath)
        save_path = self.get_save_path(prepath)
        np.savez(save_path, valid=self.valid, is_disruptive=self.is_disruptive,
                 signals_dict=self.signals_dict, ttd=self.ttd)
        print('...saved shot {}'.format(self.number))

    def get_save_path(self, prepath):
        return get_individual_shot_file(prepath, self.number, '.npz')

    def restore(self, prepath, light=False):
        assert self.previously_saved(prepath), 'shot was never saved'
        save_path = self.get_save_path(prepath)
        dat = np.load(save_path, encoding="latin1", allow_pickle=True)

        self.valid = dat['valid'][()]
        self.is_disruptive = dat['is_disruptive'][()]

        if light:
            self.signals_dict = None
            self.ttd = None
        else:
            self.signals_dict = dat['signals_dict'][()]
            self.ttd = dat['ttd']

    def previously_saved(self, prepath):
        save_path = self.get_save_path(prepath)
        return os.path.isfile(save_path)

    def make_light(self):
        self.signals_dict = None
        self.ttd = None

    @staticmethod
    def is_disruptive_given_disruption_time(t):
        return t >= 0

# it used to be in utilities, but can't import globals in multiprocessing

def get_individual_shot_file(prepath, shot_num, ext='.txt'):
    return prepath + str(shot_num) + ext
