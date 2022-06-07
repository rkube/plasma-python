'''
#########################################################
This file containts classes to handle data processing

Author: Julian Kates-Harbeck, jkatesharbeck@g.harvard.edu

This work was supported by the DOE CSGF program.
#########################################################
'''

import time
import sys
from os import remove, listdir
from os.path import join, isfile

import numpy as np
import multiprocessing as mp

from plasma.utils.processing import append_to_filename
from plasma.primitives.shots import ShotList
from plasma.utils.downloading import mkdirdepth

import logging


class Preprocessor(object):
    """Preprocessor class. """
    def __init__(self, conf, verbose=False):
        """Initializes by storing a copy of the configuration"""
        self.conf = conf
        self.verbose = verbose

    def format_shot_lists(self):
        """Call format_shotlist_twocolumn on a list of shot-lists."""
      
        # Iterate over a list of all directories located in conf['paths']['shot_list_dir']
        # Construct a list of shot lists that are in base_path+shot_list_dir
        shot_list_path = join(self.conf["paths"]["base_path"], self.conf["paths"]["shot_list_dir"])
        all_shot_lists = [join(shot_list_path, f) for f in listdir(shot_list_path) if isfile(join(shot_list_path, f))]
        logging.info(f"all shot_lists = ", all_shot_lists)
        for shot_list in all_shot_lists:
            # Call clean_shot_list for each of these files
            self.format_shotlist(shot_list)

    def format_shotlist(self, path):
        """Re-format a shotlist into two columns.

        Input:
        ------
        path:........str(filename) Data file name 


        Output:
        -------
        None


        Shotlists are in two-column format:
        Shotnr   Tdisrupt
        ======   ========

        Non-disruptive shots have only one column of data. In this case we overwrite
        the datafile with an appended column of -1.
        """
        try:
            data = np.loadtxt(path)
        except BaseException as err:
            logging.error(f"Can't clean shot list for path {path}: {err}. Exiting")
            return

        logging.info(f"Formatting shot list {path}")
        if len(np.shape(data)) < 2:
            # nondisruptive
            new_path = append_to_filename(path, '_clear')
            nd_times = -1.0 * np.ones_like(data)
            data_two_column = np.vstack((data, nd_times)).transpose()
            np.savetxt(new_path, data_two_column, fmt='%d %f')

            logging.info("format_shotlist: renaming {path} -> {new_path}")
            os.remove(path)


    def preprocess_all(self):
        """TODO: Deprecated."""
        err_str = "Preprocess.preprocess_all is deprecated. \n Call instead: \n>"
        err_str += "'preprocess_from_files(conf['paths']['shot_files_all'], conf['data']['use_shots'])'"
        logging.error(err_str)
        raise DeprecationWarning(err_str)
    def preprocess_from_files(self, shot_files, use_shots):
        """Distribute preprocessing of all signals across process pool.

        Input:
        ======
        shot_files...
        use_shots....


        Output:
        =======
        used_shots...


        """
        # New shot list
        shot_list = ShotList()
        # Add the shots to the shotlist object
        for shot in shot_files:
            shot_list.load_from_shot_list_files_object(shot, self.conf["paths"]["all_signals"])
    
        shot_list_picked = shot_list.random_sublist(use_shots)

        # empty
        used_shots = ShotList()

        # TODO(KGF): generalize the follwowing line to perform well on
        # architecutres other than CPUs, e.g. KNLs
        # min( <desired-maximum-process-count>, max(1,mp.cpu_count()-2) )
        use_cores = max(1, mp.cpu_count() - 2)
        pool = mp.Pool(use_cores)
        print('Running in parallel on {} processes'.format(pool._processes))
        start_time = time.time()
        for (i, shot) in enumerate(pool.imap_unordered(
                self.preprocess_single_file, shot_list_picked)):
            # for (i,shot) in
            # enumerate(map(self.preprocess_single_file,shot_list_picked)):
            sys.stdout.write('\r{}/{}'.format(i, len(shot_list_picked)))
            used_shots.append_if_valid(shot)

        pool.close()
        pool.join()
        print('Finished Preprocessing {} files in {} seconds'.format(
            len(shot_list_picked), time.time() - start_time))
        print('Omitted {} shots of {} total.'.format(
            len(shot_list_picked) - len(used_shots), len(shot_list_picked)))
        print('{}/{} disruptive shots'.format(used_shots.num_disruptive(),
                                              len(used_shots)))
        if len(used_shots) == 0:
            print("WARNING: All shots were omitted, please ensure raw data "
                  " is complete and available at {}.".format(
                      self.conf['paths']['signal_prepath']))
        return used_shots

    def preprocess_single_file(self, shot):
        processed_prepath = self.conf['paths']['processed_prepath']
        recompute = self.conf['data']['recompute']
        # print('({}/{}): '.format(num_processed,use_shots))
        if recompute or not shot.previously_saved(processed_prepath):
            shot.preprocess(self.conf)
            shot.save(processed_prepath)
        else:
            try:
                shot.restore(processed_prepath, light=True)
                sys.stdout.write('\r{} exists.'.format(shot.number))
            except BaseException:
                shot.preprocess(self.conf)
                shot.save(processed_prepath)
                sys.stdout.write('\r{} exists but corrupted, resaved.'.format(
                    shot.number))
        shot.make_light()
        return shot

    def get_individual_channel_dirs(self):
        raise DepreciationWarning("replace get_individual_channel_dirs() is conf['paths'][signal_dirs']")
        #return self.conf['paths']['signals_dirs']

    def get_shot_list_path(self):
        raise DepreciationWarning("replace get_shot_list_path() is conf['paths']['saved_shotlist_path']")
        #return self.conf['paths']['saved_shotlist_path']

    def load_shotlists(self):
        path = self.get_shot_list_path()
        data = np.load(self.conf["paths"]["saved_shotlist_path"], 
                       encoding="utf8", allow_pickle=True)
        shot_list_train = data['shot_list_train'][()]
        shot_list_validate = data['shot_list_validate'][()]
        shot_list_test = data['shot_list_test'][()]
        if isinstance(shot_list_train, ShotList):
            return shot_list_train, shot_list_validate, shot_list_test
        else:
            return ShotList(shot_list_train), ShotList(
                shot_list_validate), ShotList(shot_list_test)

    def save_shotlists(self, shot_list_train, shot_list_validate,
                       shot_list_test):
        path = self.get_shot_list_path()
        mkdirdepth(path)
        np.savez(path, shot_list_train=shot_list_train,
                 shot_list_validate=shot_list_validate,
                 shot_list_test=shot_list_test)


def apply_bleed_in(conf, shot_list_train, shot_list_validate, shot_list_test):
    np.random.seed(2)
    num = conf['data']['bleed_in']
    # new_shots = []
    if num > 0:
        shot_list_bleed = ShotList()
        print('applying bleed in with {} disruptive shots\n'.format(num))
        # num_total = len(shot_list_test)
        num_d = shot_list_test.num_disruptive()
        # num_nd = num_total - num_d
        assert num_d >= num, (
            "Not enough disruptive shots {} to cover bleed in {}".format(
                num_d, num))
        num_sampled_d = 0
        num_sampled_nd = 0
        while num_sampled_d < num:
            s = shot_list_test.sample_shot()
            shot_list_bleed.append(s)
            if conf['data']['bleed_in_remove_from_test']:
                shot_list_test.remove(s)
            if s.is_disruptive:
                num_sampled_d += 1
            else:
                num_sampled_nd += 1
        print("Sampled {} shots, {} disruptive, {} nondisruptive".format(
            num_sampled_nd+num_sampled_d, num_sampled_d, num_sampled_nd))
        print("Before adding: training shots: {} validation shots: {}".format(
            len(shot_list_train), len(shot_list_validate)))
        assert(num_sampled_d == num)
        # add bleed-in shots to training and validation set repeatedly
        if conf['data']['bleed_in_equalize_sets']:
            print("Applying equalized bleed in")
            for shot_list_curr in [shot_list_train, shot_list_validate]:
                for i in range(len(shot_list_curr)):
                    s = shot_list_bleed.sample_shot()
                    shot_list_curr.append(s)
        elif conf['data']['bleed_in_repeat_fac'] > 1:
            repeat_fac = conf['data']['bleed_in_repeat_fac']
            print("Applying bleed in with repeat factor {}".format(repeat_fac))
            num_to_sample = int(round(repeat_fac*len(shot_list_bleed)))
            for i in range(num_to_sample):
                s = shot_list_bleed.sample_shot()
                shot_list_train.append(s)
                shot_list_validate.append(s)
        else:  # add each shot only once
            print("Applying bleed in without repetition")
            for s in shot_list_bleed:
                shot_list_train.append(s)
                shot_list_validate.append(s)
        print("After adding: training shots: {} validation shots: {}".format(
            len(shot_list_train), len(shot_list_validate)))
        print("Added bleed in shots to training and validation sets")
        # if num_d > 0:
        #     for i in range(num):
        #         s = shot_list_test.sample_single_class(True)
        #         shot_list_train.append(s)
        #         shot_list_validate.append(s)
        #         if conf['data']['bleed_in_remove_from_test']:
        #             shot_list_test.remove(s)
        # else:
        #     print('No disruptive shots in test set, omitting bleed in')
        # if num_nd > 0:
        #     for i in range(num):
        #         s = shot_list_test.sample_single_class(False)
        #         shot_list_train.append(s)
        #         shot_list_validate.append(s)
        #         if conf['data']['bleed_in_remove_from_test']:
        #             shot_list_test.remove(s)
        # else:
        #     print('No nondisruptive shots in test set, omitting bleed in')
    return shot_list_train, shot_list_validate, shot_list_test


def guarantee_preprocessed(conf, verbose=False):
    pp = Preprocessor(conf)
    
    # TODO: replace function with definitino here
    #def all_are_preprocessed(self):
    #    return os.path.isfile(self.get_shot_list_path())
    if isfile(conf['paths']['saved_shotlist_path']):
        logging.info(f"{self.get_shot_list_path()} exists. Skipping preprocessing")
        shot_list_train, shot_list_validate, shot_list_test = pp.load_shotlists()
    else:
        logging.info("Formatting shots....")
        # Make sure the shot lists are properly formatted
        pp.format_shot_lists()
        # Preprocess all available shots
        logging.info("Preprocessing from files...")
        shot_list = pp.preprocess_from_files(conf["paths"]["shot_files_all"], conf["data"]["use_shots"])
        shot_list.sort()
        shot_list_train, shot_list_test = shot_list.split_train_test(conf)
        # num_shots = len(shot_list_train) + len(shot_list_test)
        validation_frac = conf['training']['validation_frac']
        if validation_frac <= 0.05:
            if verbose:
                g.print_unique('Setting validation to a minimum of 0.05')
            validation_frac = 0.05
        shot_list_train, shot_list_validate = shot_list_train.split_direct(
            1.0-validation_frac, do_shuffle=True)
        pp.save_shotlists(shot_list_train, shot_list_validate, shot_list_test)
    shot_list_train, shot_list_validate, shot_list_test = apply_bleed_in(
        conf, shot_list_train, shot_list_validate, shot_list_test)
    if verbose:
        g.print_unique('validate: {} shots, {} disruptive'.format(
            len(shot_list_validate), shot_list_validate.num_disruptive()))
        g.print_unique('training: {} shots, {} disruptive'.format(
            len(shot_list_train), shot_list_train.num_disruptive()))
        g.print_unique('testing: {} shots, {} disruptive'.format(
            len(shot_list_test), shot_list_test.num_disruptive()))
        g.print_unique("...done")
    #    g.print_unique("...printing test shot list:")
    #    for s in shot_list_test:
    #       g.print_unique(str(s.number))

    select_shot =True
    ss = list(range(153760,153768))+list(range(170865,170897))+list(range(174819,174853))+[166671]
    if select_shot:
       for s in shot_list_train:
            if s.number in ss:
              print('Found in train',s.number)
              shot_list_train.remove(s)
              shot_list_test.append(s)
       for s in shot_list_validate:
            if s.number in ss:
              print('Found in validate',s.number)
              shot_list_validate.remove(s)
              shot_list_test.append(s)
       for s in shot_list_test:
            if s.number in ss:
              print('Found in test',s.number)
    if verbose:
        g.print_unique('validate: {} shots, {} disruptive'.format(
            len(shot_list_validate), shot_list_validate.num_disruptive()))
        g.print_unique('training: {} shots, {} disruptive'.format(
            len(shot_list_train), shot_list_train.num_disruptive()))
        g.print_unique('testing: {} shots, {} disruptive'.format(
            len(shot_list_test), shot_list_test.num_disruptive()))
        g.print_unique("...done")
           
    return shot_list_train, shot_list_validate, shot_list_test
