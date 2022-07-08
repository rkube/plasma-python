#!/usr/bin/env python

from os import listdir, stat
from os.path import join, isfile, isdir
import yaml

from plasma.primitives.shots import ShotListFiles
import plasma.data.user_signals as user_signals
from plasma.utils.hashing import myhash_signals
from plasma.models.targets import (
    HingeTarget, MaxHingeTarget, BinaryTarget,
    FLATTarget, 
    TTDTarget, TTDInvTarget, TTDLinearTarget
    )

import logging


def parse_config(input_file):
    """Parse yaml file of configuration parameters.
    
    Performs various tasks:
    1. Assemble a params['paths']['signal_prepath'] - A list of directories to look for data
    2.   
    
    
    
    """
    with open(input_file, 'r') as yaml_file:
        params = yaml.load(yaml_file, Loader=yaml.SafeLoader)

        # Sets base path for all output.
        # All paths, including
        # * signal_prepath
        # * shot_list_dir
        # * ...
        # are relative to this path
        try: 
            stat(params["paths"]["base_path"])
            logging.info(f"Using base path {params['paths']['base_path']}")
        except FileNotFoundError as err:
            logging.error(f"Can not use {params['paths']['base_path']} as base_path: {err}")
            raise FileNotFoundError


        # Set directory list for signal_prepath
        # paths.signal_prepath is a list of directories that will be searched for data
        if isinstance(params['paths']['signal_prepath'], list):
            # Assemble a list of directories that will be sourced for data
            prepath_list = []
            for path in [join(params['paths']['base_path'], pp) for pp in params['paths']['signal_prepath']]:
                try:
                    stat(path)
                    prepath_list.append(join(params["paths"]["base_path"], path))
                    logging.info(f"Adding data directory {join(params['paths']['base_path'], path)}")
                except FileNotFoundError as err:
                    logging.error(f"Can't use {path} for signal_prepath: {err}")
                    raise(err)

        else:
            # Do the same, but only for the single directory given
            path = join(params["paths"]["base_path"], params["paths"]["signal_prepath"])
            try:
                stat(path)
                logging.info(f"Adding data directory {path}")
            except FileNotFoundError as err:
                logging.error(f"Can't use {path} for signal_prepath: {err}")
                raise(err)
            prepath_list = [path]

        # If somehow prepath_list is still empty we need to abort.
        if(len(prepath_list) == 0):
            raise ValueError("Could not assemble list of prepaths: len(prepath_list) == 0")
        params["paths"]["signal_prepath"] = prepath_list


        # Set shot_list_dir
        path = join(params["paths"]["base_path"], params['paths']['shot_list_dir'])
        try:
            stat(path)
        except FileNotFoundError as err:
            logging.error(err)
            raise err
        params['paths']['shot_list_dir'] = path

            
        # By setting paths.data_collection we define a set of signals that will be loaded during
        # pre-processing. These collections are defined in data/signals.py
        # 
        # In the block below we set a 
        # 1. A data specific hash h
        # 2. Define the named collection in params["paths"]["all_signals_dict"]
        if params['paths']['data'] == 'd3d_data_gar18':
            h = myhash_signals(user_signals.signal_group_gar18.values())
            params['paths']['all_signals_dict'] = user_signals.signal_group_gar18
            params['paths']['use_signals_dict'] = user_signals.signal_group_gar18
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            

        if params['paths']['data'] == 'd3d_data':
            h = myhash_signals(user_signals.signal_group_d3d_all.values())
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = user_signals.signal_group_d3d_all
            params['paths']['all_signals_dict'] = user_signals.signal_group_d3d_all
#

        elif params['paths']['data'] == 'd3d_data_n1rms':
            h = myhash_signals(user_signals.all_signals_n1rms.values())
            params['paths']['all_signals_dict'] = user_signals.all_signals_n1rms
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': user_signals.q95,
                'li': user_signals.li,
                'ip': user_signals.ip,
                'lm': user_signals.lm,
                'betan': user_signals.betan,
                'energy': user_signals.energy,
                'dens': user_signals.dens,
                'pradcore': user_signals.pradcore,
                'pradedge': user_signals.pradedge,
                'pin': user_signals.pin,
                'torquein': user_signals.torquein,
                'ipdirect': user_signals.ipdirect,
                'iptarget': user_signals.iptarget,
                'iperr': user_signals.iperr,
                'etemp_profile': user_signals.etemp_profile,
                'edens_profile': user_signals.edens_profile,
                'n1_rms': user_signals.n1_rms,
                'n1_rms_no_shift': user_signals.n1_rms_no_shift,
            }

        elif params['paths']['data'] == 'd3d_data_fs07':
            h = myhash_signals(user_signals.all_signals_fs07.values())
            params['paths']['all_signals_dict'] = user_signals.all_signals_fs07a
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': user_signals.q95,
                'li': user_signals.li,
                'fs07': user_signals.fs07,
                'ip': user_signals.ip,
                'lm': user_signals.lm,
                'betan': user_signals.betan,
                'energy': user_signals.energy,
                'dens': user_signals.dens,
                'pradcore': user_signals.pradcore,
                'pradedge': user_signals.pradedge,
                'pin': user_signals.pin,
                'torquein': user_signals.torquein,
                'ipdirect': user_signals.ipdirect,
                'iptarget': user_signals.iptarget,
                'iperr': user_signals.iperr,
                'etemp_profile': user_signals.etemp_profile,
                'edens_profile': user_signals.edens_profile,
                'n1_rms': user_signals.n1_rms,
                'n1_rms_no_shift': user_signals.n1_rms_no_shift,
            }


        elif params['paths']['data'] == 'd3d_data_ped':
            h = myhash_signals(user_signals.all_signals_ped.values())
            params['paths']['all_signals_dict'] = user_signals.all_signals_ped
            params['paths']['shot_files'] = [d3d_full_new_2021]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': user_signals.q95,
                #'li': user_signals.li,
                'fs07': user_signals.fs07,
                'neped': user_signals.neped,
                'peped': user_signals.peped,
                'newid': user_signals.newid,
                'teped': user_signals.teped,
                'tewid': user_signals.tewid,
                'ip': user_signals.ip,
                'lm': user_signals.lm,
                'betan': user_signals.betan,
                'energy': user_signals.energy,
                'dens': user_signals.dens,
                'pradcore': user_signals.pradcore,
                'pradedge': user_signals.pradedge,
                'pin': user_signals.pin,
                'torquein': user_signals.torquein,
                #'ipdirect': user_signals.ipdirect,
             #   'iptarget': user_signals.iptarget,
             #   'iperr': user_signals.iperr,
                'etemp_profile': user_signals.etemp_profile,
                'edens_profile': user_signals.edens_profile,
                'n1_rms': user_signals.n1_rms,
                'n2_rms_10': user_signals.n2_rms_10,
                'n3_rms_10': user_signals.n3_rms_10,
            }



        elif params['paths']['data'] == 'd3d_data_ped_spec':
            h = myhash_signals(user_signals.all_signals_ped_spec.values())
            params['paths']['all_signals_dict'] = user_signals.all_signals_ped_spec
            params['paths']['shot_files'] = [d3d_full_new_2021]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': user_signals.q95,
                'qpsi_efitrt1': user_signals.qpsi_efitrt1,
                'fs07': user_signals.fs07,
                'neped': user_signals.neped,
                'peped': user_signals.peped,
                'newid': user_signals.newid,
                'teped': user_signals.teped,
                'tewid': user_signals.tewid,
                'ip': user_signals.ip,
                'lm': user_signals.lm,
                'betan': user_signals.betan,
                'energy': user_signals.energy,
                'dens': user_signals.dens,
                'pradcore': user_signals.pradcore,
                'pradedge': user_signals.pradedge,
                'pin': user_signals.pin,
                'torquein': user_signals.torquein,
                'etemp_profile': user_signals.etemp_profile,
                'edens_profile': user_signals.edens_profile,
                'mpi66m322d_spec_profile': user_signals.mpi66m322d_spec_profile,
                'n1_rms': user_signals.n1_rms,
            }

        elif params['paths']['data'] == 'd3d_data_n1rms_thomson':
            h = myhash_signals(user_signals.all_signals_n1rms_thomson.values())
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95_EFITRT1': user_signals.q95_EFITRT1,
                'li': user_signals.li,
                'ip': user_signals.ip,
                'lm': user_signals.lm,
                'betan': user_signals.betan,
                'energy': user_signals.energy,
                'dens': user_signals.dens,
                'pradcore': user_signals.pradcore,
                'pradedge': user_signals.pradedge,
                'pin': user_signals.pin,
                'torquein': user_signals.torquein,
                'ipdirect': user_signals.ipdirect,
                'iptarget': user_signals.iptarget,
                'iperr': user_signals.iperr,
                'etemp_profile_thomson': user_signals.etemp_profile_thomson,
                'edens_profile_thomson': user_signals.edens_profile_thomson,
                'n1_rms': user_signals.n1_rms,
                'n1_rms_no_shift': user_signals.n1_rms_no_shift,
            }


        elif params['paths']['data'] == 'd3d_data_n1rms_qmin':
            h = myhash_signals(user_signals.all_signals_n1rms_qmin.values())
            params['paths']['all_signals_dict'] = user_signals.all_signals_n1rms_qmin
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': user_signals.q95,
                'qmin': user_signals.qmin,
                'li': user_signals.li,
                'ip': user_signals.ip,
                'lm': user_signals.lm,
                'betan': user_signals.betan,
                'energy': user_signals.energy,
                'dens': user_signals.dens,
                'pradcore': user_signals.pradcore,
                'pradedge': user_signals.pradedge,
                'pin': user_signals.pin,
                'torquein': user_signals.torquein,
                'ipdirect': user_signals.ipdirect,
                'iptarget': user_signals.iptarget,
                'iperr': user_signals.iperr,
                'etemp_profile': user_signals.etemp_profile,
                'edens_profile': user_signals.edens_profile,
                'n1_rms': user_signals.n1_rms,
                'n1_rms_no_shift': user_signals.n1_rms_no_shift,
            }



        elif params['paths']['data'] == 'd3d_data_thomson':
            h = myhash_signals(user_signals.all_signals_thomson.values())
            params['paths']['all_signals_dict'] = user_signals.all_signals_thomson
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95t': user_signals.q95,
                'lit': user_signals.li,
                'ipt': user_signals.ip,
                'lmt': user_signals.lm,
                'betant': user_signals.betan,
                'energyt': user_signals.energy,
                'denst': user_signals.dens,
                'pradcoret': user_signals.pradcore,
                'pradedget': user_signals.pradedge,
                'pint': user_signals.pin,
                'torqueint': user_signals.torquein,
                'ipdirectt': user_signals.ipdirect,
                'iptargett': user_signals.iptarget,
                'iperrt': user_signals.iperr,
                'etemp_profile_thomson': user_signals.etemp_profile_thomson,
                'edens_profile_thomson': user_signals.edens_profile_thomson,
            }
 

        elif params['paths']['data'] == 'd3d_data_garbage':
            h = myhash_signals(user_signals.all_signals_gar18.values())*2
            params['paths']['all_signals_dict'] = user_signals.all_signals_gar18
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95t': user_signals.q95t,
                'lit': user_signals.lit,
                'ipt': user_signals.ipt,
                'lmt': user_signals.lmt,
                'betant': user_signals.betant,
                'energyt': user_signals.energyt,
                'denst': user_signals.denst,
                'pradcoret': user_signals.pradcoret,
                'pradedget': user_signals.pradedget,
                'pint': user_signals.pint,
                'torqueint': user_signals.torqueint,
                'ipdirectt': user_signals.ipdirectt,
                'iptargett': user_signals.iptargett,
                'iperrt': user_signals.iperrt,
                'etemp_profilet': user_signals.etemp_profilet,
                'edens_profilet': user_signals.edens_profilet,
            }

        elif params['paths']['data'] == 'd3d_data_new':
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = [] 
            params['paths']['use_signals_dict'] = {
                'q95': user_signals.q95,
                'li': user_signals.li,
                'ip': user_signals.ip,
                'lm': user_signals.lm,
                'betan': user_signals.betan,
                'energy': user_signals.energy,
                'dens': user_signals.dens,
                'pradcore': user_signals.pradcore,
                'pradedge': user_signals.pradedge,
                'pin': user_signals.pin,
                'torquein': user_signals.torquein,
                'ipdirect': user_signals.ipdirect,
                'iptarget': user_signals.iptarget,
                'iperr': user_signals.iperr,
                'etemp_profile': user_signals.etemp_profile,
                'edens_profile': user_signals.edens_profile,
            }

        elif params['paths']['data'] == 'd3d_data_real_time':
            h = myhash_signals(user_signals.all_signals_real_time.values())
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95_EFITRT1': user_signals.q95_EFITRT1,
                'li': user_signals.li,
                'ip': user_signals.ip,
                'lm': user_signals.lm,
                'betan': user_signals.betan,
                'energy': user_signals.energy,
                'dens': user_signals.dens,
                'pradcore': user_signals.pradcore,
                'pradedge': user_signals.pradedge,
                'pin': user_signals.pin,
                'torquein': user_signals.torquein,
                'ipdirect': user_signals.ipdirect,
                'iptarget': user_signals.iptarget,
                'iperr': user_signals.iperr,
                'etemp_profile': user_signals.etemp_profile,
                'edens_profile': user_signals.edens_profile,
            }
        #params['paths']['all_signals_dict'] = user_signals.all_signals_real_time

        elif params['paths']['data'] == 'd3d_data_real_time_0D':
            h = myhash_signals(user_signals.all_signals_real_time_0D.values())
            params['paths']['all_signals_dict'] = user_signals.all_signals_real_time_0D
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95_EFITRT1': user_signals.q95_EFITRT1,
                'li': user_signals.li,
                'ip': user_signals.ip,
                'lm': user_signals.lm,
                'betan': user_signals.betan,
                'energy': user_signals.energy,
                'dens': user_signals.dens,
                'pin': user_signals.pin,
                'torquein': user_signals.torquein,
                'ipdirect': user_signals.ipdirect,
                'iptarget': user_signals.iptarget,
                'iperr': user_signals.iperr,
            }



        elif params['paths']['data'] == 'd3d_data_ori':
            h = myhash_signals(user_signals.all_signals_ori.values())*2
            params['paths']['all_signals_dict'] = user_signals.all_signals_ori
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': user_signals.q95,
                'li': user_signals.li,
                'ipori': user_signals.ipori,
                'lm': user_signals.lm,
                'betan': user_signals.betan,
                'energy': user_signals.energy,
                'dens': user_signals.dens,
                'pradcore': user_signals.pradcore,
                'pradedge': user_signals.pradedge,
                'pin': user_signals.pin,
                'torquein': user_signals.torquein,
                'ipdirect': user_signals.ipdirect,
                'iptarget': user_signals.iptarget,
                'iperr': user_signals.iperr,
                'etemp_profile': user_signals.etemp_profile,
                'edens_profile': user_signals.edens_profile,
            }

        elif params['paths']['data'] == 'd3d_data_1D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'ipdirect': user_signals.ipdirect,
                'etemp_profile': user_signals.etemp_profile,
                'edens_profile': user_signals.edens_profile,
            }

        elif params['paths']['data'] == 'd3d_data_all_profiles':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'ipdirect': user_signals.ipdirect,
                'etemp_profile': user_signals.etemp_profile,
                'edens_profile': user_signals.edens_profile,
                'itemp_profile': user_signals.itemp_profile,
                'zdens_profile': user_signals.zdens_profile,
                'trot_profile': user_signals.trot_profile,
                'pthm_profile': user_signals.pthm_profile,
                'neut_profile': user_signals.neut_profile,
                'q_profile': user_signals.q_profile,
                'bootstrap_current_profile': user_signals.bootstrap_current_profile,
                'q_psi_profile': user_signals.q_psi_profile,
            }
        elif params['paths']['data'] == 'd3d_data_0D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': user_signals.q95,
                'li': user_signals.li,
                'ip': user_signals.ip,
                'lm': user_signals.lm,
                'betan': user_signals.betan,
                'energy': user_signals.energy,
                'dens': user_signals.dens,
                'pradcore': user_signals.pradcore,
                'pradedge': user_signals.pradedge,
                'pin': user_signals.pin,
                'torquein': user_signals.torquein,
                'ipdirect': user_signals.ipdirect,
                'iptarget': user_signals.iptarget,
                'iperr': user_signals.iperr,
            }
        elif params['paths']['data'] == 'd3d_data_all':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = user_signals.d3d_signals


        else:   
           h = myhash_signals(user_signals.all_signals.values())#+params['data']['T_min_warn'])
           params['paths']['all_signals_dict'] = user_signals.all_signals

        logging.info(f"Hash used: {h}")
        logging.info(f"Using signal dict {params['paths']['data']} with keys: {params['paths']['all_signals_dict'].keys()}")

       
        # 
        params['paths']['global_normalizer_path'] = \
                join(params["paths"]["base_path"], 
                     f"/normalization/normalization_signal_group_{h}.npz")

        if params['training']['hyperparam_tuning']:
            # params['paths']['saved_shotlist_path'] =
            # './normalization/shot_lists.npz'
            params['paths']['normalizer_path'] = f"./normalization/normalization_signal_group_{h}.npz"
            params['paths']['model_save_path'] = "model_checkpoints"
            params['paths']['csvlog_save_path'] = "csv_logs"
            params['paths']['results_prepath'] = "results"
        else:
            # params['paths']['saved_shotlist_path'] = output_path +
            # '/normalization/shot_lists.npz'
            params['paths']['normalizer_path'] = params['paths']['global_normalizer_path']
            params['paths']['model_save_path'] = join(params["paths"]["base_path"], "model_checkpoints")
            params['paths']['csvlog_save_path'] = join(params["paths"]["base_path"], "csv_logs")
            params['paths']['results_prepath'] =  join(params["paths"]["base_path"], "results")

        # TODO: What is this parameter used for?
        params['paths']['saved_shotlist_path'] = join(params["paths"]["base_path"],
                                                      "processed_shotlists_torch")
        #params['paths']['base_path'] + "processed_shotlists_torch"
            #params['paths']['base_path'] + '/../FRNN/gdong-temp/processed_shotlists_torch/'
            #+ params['paths']['data']
            #+ '/shot_lists_signal_group_{}.npz'.format(h))

        params['paths']['processed_prepath'] = \
            join(params["paths"]["base_path"], 
                 "../FRNN/rkube-temp/processed_shots_torch",
                 "signal_group_{h}")

        # ensure shallow model has +1 -1 target.
        if params['model']['shallow'] or params['target'] == 'hinge':
            params['data']['target'] = HingeTarget
        elif params['target'] == 'maxhinge':
            MaxHingeTarget.fac = params['data']['positive_example_penalty']
            params['data']['target'] = MaxHingeTarget
        elif params['target'] == 'binary':
            params['data']['target'] = BinaryTarget
        elif params['target'] == 'ttd':
            params['data']['target'] = TTDTarget
        elif params['target'] == 'ttdinv':
            params['data']['target'] = TTDInvTarget
        elif params['target'] == 'ttdlinear':
            params['data']['target'] = TTDLinearTarget
        elif params['target'] == 'flat':
            params['data']['target'] = FLATTarget
        else:
            logging.error("Unknown type of target: {params['data']['target']}. Exiting")


        if params['paths']['data'] == 'jet_data':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = user_signals.jet_signals
        elif params['paths']['data'] == 'jet_data_0D':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = user_signals.jet_signals_0D
        elif params['paths']['data'] == 'jet_data_1D':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = user_signals.jet_signals_1D
        elif params['paths']['data'] == 'jet_data_late':
            params['paths']['shot_files'] = [jet_iterlike_wall_late]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = user_signals.jet_signals
        elif params['paths']['data'] == 'jet_data_carbon_to_late_0D':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall_late]
            params['paths']['use_signals_dict'] = user_signals.jet_signals_0D
        elif params['paths']['data'] == 'jet_data_temp_profile':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = {
                'etemp_profile': user_signals.etemp_profile}
        elif params['paths']['data'] == 'jet_data_dens_profile':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = {
                'edens_profile': user_signals.edens_profile}
        elif params['paths']['data'] == 'jet_carbon_data':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = user_signals.jet_signals
        elif params['paths']['data'] == 'jet_mixed_data':
            params['paths']['shot_files'] = [jet_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = user_signals.jet_signals
        elif params['paths']['data'] == 'jenkins_jet':
            params['paths']['shot_files'] = [jenkins_jet_carbon_wall]
            params['paths']['shot_files_test'] = [jenkins_jet_iterlike_wall]
            params['paths']['use_signals_dict'] = user_signals.jet_signals
        # jet data but with fully defined signals
        elif params['paths']['data'] == 'jet_data_fully_defined':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = user_signals.fully_defined_signals
        # jet data but with fully defined signals
        elif params['paths']['data'] == 'jet_data_fully_defined_0D':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = user_signals.fully_defined_signals_0D

        elif params['paths']['data'] == 'd3d_data_0D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': user_signals.q95,
                'li': user_signals.li,
                'ip': user_signals.ip,
                'lm': user_signals.lm,
                'betan': user_signals.betan,
                'energy': user_signals.energy,
                'dens': user_signals.dens,
                'pradcore': user_signals.pradcore,
                'pradedge': user_signals.pradedge,
                'pin': user_signals.pin,
                'torquein': user_signals.torquein,
                'ipdirect': user_signals.ipdirect,
                'iptarget': user_signals.iptarget,
                'iperr': user_signals.iperr,
            }
        elif params['paths']['data'] == 'd3d_data_all':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = user_signals.d3d_signals
        elif params['paths']['data'] == 'jenkins_d3d':
            params['paths']['shot_files'] = [d3d_jenkins]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': user_signals.q95,
                'li': user_signals.li,
                'ip': user_signals.ip,
                'lm': user_signals.lm,
                'betan': user_signals.betan,
                'energy': user_signals.energy,
                'dens': user_signals.dens,
                'pradcore': user_signals.pradcore,
                'pradedge': user_signals.pradedge,
                'pin': user_signals.pin,
                'torquein': user_signals.torquein,
                'ipdirect': user_signals.ipdirect,
                'iptarget': user_signals.iptarget,
                'iperr': user_signals.iperr,
                'etemp_profile': user_signals.etemp_profile,
                'edens_profile': user_signals.edens_profile,
            }
        # jet data but with fully defined signals
        elif params['paths']['data'] == 'd3d_data_fully_defined':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = user_signals.fully_defined_signals
        # jet data but with fully defined signals
        elif params['paths']['data'] == 'd3d_data_fully_defined_0D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = user_signals.fully_defined_signals_0D
        elif params['paths']['data'] == 'd3d_data_temp_profile':
            # jet data but with fully defined signals
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'etemp_profile': user_signals.etemp_profile}  # fully_defined_signals_0D
        elif params['paths']['data'] == 'd3d_data_dens_profile':
            # jet data but with fully defined signals
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'edens_profile': user_signals.edens_profile}  # fully_defined_signals_0D

        # cross-machine
        elif params['paths']['data'] == 'jet_to_d3d_data':
            params['paths']['shot_files'] = [jet_full]
            params['paths']['shot_files_test'] = [d3d_full]
            params['paths']['use_signals_dict'] = user_signals.fully_defined_signals
        elif params['paths']['data'] == 'd3d_to_jet_data':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = user_signals.fully_defined_signals
        elif params['paths']['data'] == 'd3d_to_late_jet_data':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [jet_iterlike_wall_late]
            params['paths']['use_signals_dict'] = user_signals.fully_defined_signals
        elif params['paths']['data'] == 'jet_to_d3d_data_0D':
            params['paths']['shot_files'] = [jet_full]
            params['paths']['shot_files_test'] = [d3d_full]
            params['paths']['use_signals_dict'] = user_signals.fully_defined_signals_0D
        elif params['paths']['data'] == 'd3d_to_jet_data_0D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = user_signals.fully_defined_signals_0D
        elif params['paths']['data'] == 'jet_to_d3d_data_1D':
            params['paths']['shot_files'] = [jet_full]
            params['paths']['shot_files_test'] = [d3d_full]
            params['paths']['use_signals_dict'] = user_signals.fully_defined_signals_1D
        elif params['paths']['data'] == 'd3d_to_jet_data_1D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = user_signals.fully_defined_signals_1D

        else:
            logging.error(f"Unknown dataset {params['paths']['data']}")
            exit(1)

        if 'specific_signals' in params['paths'] and len(params['paths']['specific_signals']):
            for s in params['paths']['specific_signals']:
                if s not in params['paths']['use_signals_dict'].keys():
                    logging.info(f"Signal {s} is not fully defined for {params['paths']['data'].split('_')[0]} machine. Skipping.")
            params['paths']['specific_signals'] = list(
                filter(
                    lambda x: x in params['paths']['use_signals_dict'].keys(),
                    params['paths']['specific_signals']))
            selected_signals = {k: params['paths']['use_signals_dict'][k]
                                for k in params['paths']['specific_signals']}

            # 'use_signals' will contain a list of channels, sorted by number
            # of channels
            params["paths"]["use_signals"] = list(selected_signals.values()).sort(key = lambda x:x.num_channels)
        else:
            params["paths"]["use_signals"] = list(params["paths"]["use_signals_dict"].values()).sort(key = lambda x: x.num_channels)

        params["paths"]["all_signals"] = list(params["paths"]["all_signals_dict"].values()).sort(key = lambda x: x.num_channels)

        logging.info(f"Selected signals (determines which signals are used for training):\n{params['paths']['use_signals']}")
        params['paths']['shot_files_all'] = (
            params['paths']['shot_files'] + params['paths']['shot_files_test'])
        params['paths']['all_machines'] = list and(
            set([file.machine for file in params['paths']['shot_files_all']]))

        # type assertations
        assert (isinstance(params['data']['signal_to_augment'], str)
                or isinstance(params['data']['signal_to_augment'], None))
        assert isinstance(params['data']['augment_during_training'], bool)

    return params


