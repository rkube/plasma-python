#!/usr/bin/env python

from os import listdir, stat
from os.path import join, isfile, isdir
import yaml

from plasma.primitives.shots import ShotListFiles
import plasma.data.signals as sig
from plasma.utils.hashing import myhash_signals
from plasma.models.targets import (
    HingeTarget, MaxHingeTarget, BinaryTarget,
    FLATTarget, 
    TTDTarget, TTDInvTarget, TTDLinearTarget
    )

import logging


def parse_config(input_file):
    """Parse yaml file of configuration parameters."""
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

        else:
            # Do the same, but only for the single directory given
            path = join(params["paths"]["base_path"], params["paths"]["signal_prepath"])
            try:
                stat(path)
                prepath_list = [path]
                prepath_list.append(path)
                logging.info(f"Adding data directory {path}")
            except FileNotFoundError as err:
                logging.error(f"Can't use {path} for signal_prepath: {err}")

        if(len(prepath_list) == 0):
            raise ValueError("len(prepath_list) == 0")

        params["paths"]["signal_prepath"] = prepath_list

        # Set directory for shot_list_dir
        try:
            path = join(params["paths"]["base_path"], params['paths']['shot_list_dir'])

            stat(path)
            params['paths']['shot_list_dir'] = path
        except FileNotFoundError as err:
            logging.error(err)
            raise err
            
        # By setting paths.data_collection we define a set of signals that will be loaded during
        # pre-processing. These collections are defined in data/signals.py
        # 
        # In the block below we set a 
        # 1. A data specific hash h
        # 2. Define the named collection in params["paths"]["all_signals_dict"]
        if params['paths']['data'] == 'd3d_data_gar18':
            h = myhash_signals(sig.all_signals_gar18.values())
            params['paths']['all_signals_dict'] = sig.all_signals_gar18
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95t': sig.q95t,
                'lit': sig.lit,
                'ipt': sig.ipt,
                'lmt': sig.lmt,
                'betant': sig.betant,
                'energyt': sig.energyt,
                'denst': sig.denst,
                'pradcoret': sig.pradcoret,
                'pradedget': sig.pradedget,
                'pint': sig.pint,
                'torqueint': sig.torqueint,
                'ipdirectt': sig.ipdirectt,
                'iptargett': sig.iptargett,
                'iperrt': sig.iperrt,
                'etemp_profilet': sig.etemp_profilet,
                'edens_profilet': sig.edens_profilet,
            }
        if params['paths']['data'] == 'd3d_data':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': sig.q95,
                'li': sig.li,
                'ip': sig.ip,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pradcore': sig.pradcore,
                'pradedge': sig.pradedge,
                'pin': sig.pin,
                'torquein': sig.torquein,
                'ipdirect': sig.ipdirect,
                'iptarget': sig.iptarget,
                'iperr': sig.iperr,
                'etemp_profile': sig.etemp_profile,
                'edens_profile': sig.edens_profile,
            }
#

        elif params['paths']['data'] == 'd3d_data_n1rms':
            h = myhash_signals(sig.all_signals_n1rms.values())
            params['paths']['all_signals_dict'] = sig.all_signals_n1rms
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': sig.q95,
                'li': sig.li,
                'ip': sig.ip,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pradcore': sig.pradcore,
                'pradedge': sig.pradedge,
                'pin': sig.pin,
                'torquein': sig.torquein,
                'ipdirect': sig.ipdirect,
                'iptarget': sig.iptarget,
                'iperr': sig.iperr,
                'etemp_profile': sig.etemp_profile,
                'edens_profile': sig.edens_profile,
                'n1_rms': sig.n1_rms,
                'n1_rms_no_shift': sig.n1_rms_no_shift,
            }

        elif params['paths']['data'] == 'd3d_data_fs07':
            h = myhash_signals(sig.all_signals_fs07.values())
            params['paths']['all_signals_dict'] = sig.all_signals_fs07a
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': sig.q95,
                'li': sig.li,
                'fs07': sig.fs07,
                'ip': sig.ip,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pradcore': sig.pradcore,
                'pradedge': sig.pradedge,
                'pin': sig.pin,
                'torquein': sig.torquein,
                'ipdirect': sig.ipdirect,
                'iptarget': sig.iptarget,
                'iperr': sig.iperr,
                'etemp_profile': sig.etemp_profile,
                'edens_profile': sig.edens_profile,
                'n1_rms': sig.n1_rms,
                'n1_rms_no_shift': sig.n1_rms_no_shift,
            }


        elif params['paths']['data'] == 'd3d_data_ped':
            h = myhash_signals(sig.all_signals_ped.values())
            params['paths']['all_signals_dict'] = sig.all_signals_ped
            params['paths']['shot_files'] = [d3d_full_new_2021]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': sig.q95,
                #'li': sig.li,
                'fs07': sig.fs07,
                'neped': sig.neped,
                'peped': sig.peped,
                'newid': sig.newid,
                'teped': sig.teped,
                'tewid': sig.tewid,
                'ip': sig.ip,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pradcore': sig.pradcore,
                'pradedge': sig.pradedge,
                'pin': sig.pin,
                'torquein': sig.torquein,
                #'ipdirect': sig.ipdirect,
             #   'iptarget': sig.iptarget,
             #   'iperr': sig.iperr,
                'etemp_profile': sig.etemp_profile,
                'edens_profile': sig.edens_profile,
                'n1_rms': sig.n1_rms,
                'n2_rms_10': sig.n2_rms_10,
                'n3_rms_10': sig.n3_rms_10,
            }



        elif params['paths']['data'] == 'd3d_data_ped_spec':
            h = myhash_signals(sig.all_signals_ped_spec.values())
            params['paths']['all_signals_dict'] = sig.all_signals_ped_spec
            params['paths']['shot_files'] = [d3d_full_new_2021]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': sig.q95,
                'qpsi_efitrt1': sig.qpsi_efitrt1,
                'fs07': sig.fs07,
                'neped': sig.neped,
                'peped': sig.peped,
                'newid': sig.newid,
                'teped': sig.teped,
                'tewid': sig.tewid,
                'ip': sig.ip,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pradcore': sig.pradcore,
                'pradedge': sig.pradedge,
                'pin': sig.pin,
                'torquein': sig.torquein,
                'etemp_profile': sig.etemp_profile,
                'edens_profile': sig.edens_profile,
                'mpi66m322d_spec_profile': sig.mpi66m322d_spec_profile,
                'n1_rms': sig.n1_rms,
            }

        elif params['paths']['data'] == 'd3d_data_n1rms_thomson':
            h = myhash_signals(sig.all_signals_n1rms_thomson.values())
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95_EFITRT1': sig.q95_EFITRT1,
                'li': sig.li,
                'ip': sig.ip,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pradcore': sig.pradcore,
                'pradedge': sig.pradedge,
                'pin': sig.pin,
                'torquein': sig.torquein,
                'ipdirect': sig.ipdirect,
                'iptarget': sig.iptarget,
                'iperr': sig.iperr,
                'etemp_profile_thomson': sig.etemp_profile_thomson,
                'edens_profile_thomson': sig.edens_profile_thomson,
                'n1_rms': sig.n1_rms,
                'n1_rms_no_shift': sig.n1_rms_no_shift,
            }


        elif params['paths']['data'] == 'd3d_data_n1rms_qmin':
            h = myhash_signals(sig.all_signals_n1rms_qmin.values())
            params['paths']['all_signals_dict'] = sig.all_signals_n1rms_qmin
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': sig.q95,
                'qmin': sig.qmin,
                'li': sig.li,
                'ip': sig.ip,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pradcore': sig.pradcore,
                'pradedge': sig.pradedge,
                'pin': sig.pin,
                'torquein': sig.torquein,
                'ipdirect': sig.ipdirect,
                'iptarget': sig.iptarget,
                'iperr': sig.iperr,
                'etemp_profile': sig.etemp_profile,
                'edens_profile': sig.edens_profile,
                'n1_rms': sig.n1_rms,
                'n1_rms_no_shift': sig.n1_rms_no_shift,
            }



        elif params['paths']['data'] == 'd3d_data_thomson':
            h = myhash_signals(sig.all_signals_thomson.values())
            params['paths']['all_signals_dict'] = sig.all_signals_thomson
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95t': sig.q95,
                'lit': sig.li,
                'ipt': sig.ip,
                'lmt': sig.lm,
                'betant': sig.betan,
                'energyt': sig.energy,
                'denst': sig.dens,
                'pradcoret': sig.pradcore,
                'pradedget': sig.pradedge,
                'pint': sig.pin,
                'torqueint': sig.torquein,
                'ipdirectt': sig.ipdirect,
                'iptargett': sig.iptarget,
                'iperrt': sig.iperr,
                'etemp_profile_thomson': sig.etemp_profile_thomson,
                'edens_profile_thomson': sig.edens_profile_thomson,
            }
 

        elif params['paths']['data'] == 'd3d_data_garbage':
            h = myhash_signals(sig.all_signals_gar18.values())*2
            params['paths']['all_signals_dict'] = sig.all_signals_gar18
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95t': sig.q95t,
                'lit': sig.lit,
                'ipt': sig.ipt,
                'lmt': sig.lmt,
                'betant': sig.betant,
                'energyt': sig.energyt,
                'denst': sig.denst,
                'pradcoret': sig.pradcoret,
                'pradedget': sig.pradedget,
                'pint': sig.pint,
                'torqueint': sig.torqueint,
                'ipdirectt': sig.ipdirectt,
                'iptargett': sig.iptargett,
                'iperrt': sig.iperrt,
                'etemp_profilet': sig.etemp_profilet,
                'edens_profilet': sig.edens_profilet,
            }

        elif params['paths']['data'] == 'd3d_data_new':
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = [] 
            params['paths']['use_signals_dict'] = {
                'q95': sig.q95,
                'li': sig.li,
                'ip': sig.ip,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pradcore': sig.pradcore,
                'pradedge': sig.pradedge,
                'pin': sig.pin,
                'torquein': sig.torquein,
                'ipdirect': sig.ipdirect,
                'iptarget': sig.iptarget,
                'iperr': sig.iperr,
                'etemp_profile': sig.etemp_profile,
                'edens_profile': sig.edens_profile,
            }

        elif params['paths']['data'] == 'd3d_data_real_time':
            h = myhash_signals(sig.all_signals_real_time.values())
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95_EFITRT1': sig.q95_EFITRT1,
                'li': sig.li,
                'ip': sig.ip,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pradcore': sig.pradcore,
                'pradedge': sig.pradedge,
                'pin': sig.pin,
                'torquein': sig.torquein,
                'ipdirect': sig.ipdirect,
                'iptarget': sig.iptarget,
                'iperr': sig.iperr,
                'etemp_profile': sig.etemp_profile,
                'edens_profile': sig.edens_profile,
            }
          params['paths']['all_signals_dict'] = sig.all_signals_real_time

        elif params['paths']['data'] == 'd3d_data_real_time_0D':
            h = myhash_signals(sig.all_signals_real_time_0D.values())
            params['paths']['all_signals_dict'] = sig.all_signals_real_time_0D
            params['paths']['shot_files'] = [d3d_full_new]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95_EFITRT1': sig.q95_EFITRT1,
                'li': sig.li,
                'ip': sig.ip,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pin': sig.pin,
                'torquein': sig.torquein,
                'ipdirect': sig.ipdirect,
                'iptarget': sig.iptarget,
                'iperr': sig.iperr,
            }



        elif params['paths']['data'] == 'd3d_data_ori':
            h = myhash_signals(sig.all_signals_ori.values())*2
            params['paths']['all_signals_dict'] = sig.all_signals_ori
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': sig.q95,
                'li': sig.li,
                'ipori': sig.ipori,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pradcore': sig.pradcore,
                'pradedge': sig.pradedge,
                'pin': sig.pin,
                'torquein': sig.torquein,
                'ipdirect': sig.ipdirect,
                'iptarget': sig.iptarget,
                'iperr': sig.iperr,
                'etemp_profile': sig.etemp_profile,
                'edens_profile': sig.edens_profile,
            }

        elif params['paths']['data'] == 'd3d_data_1D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'ipdirect': sig.ipdirect,
                'etemp_profile': sig.etemp_profile,
                'edens_profile': sig.edens_profile,
            }

        elif params['paths']['data'] == 'd3d_data_all_profiles':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'ipdirect': sig.ipdirect,
                'etemp_profile': sig.etemp_profile,
                'edens_profile': sig.edens_profile,
                'itemp_profile': sig.itemp_profile,
                'zdens_profile': sig.zdens_profile,
                'trot_profile': sig.trot_profile,
                'pthm_profile': sig.pthm_profile,
                'neut_profile': sig.neut_profile,
                'q_profile': sig.q_profile,
                'bootstrap_current_profile': sig.bootstrap_current_profile,
                'q_psi_profile': sig.q_psi_profile,
            }
        elif params['paths']['data'] == 'd3d_data_0D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': sig.q95,
                'li': sig.li,
                'ip': sig.ip,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pradcore': sig.pradcore,
                'pradedge': sig.pradedge,
                'pin': sig.pin,
                'torquein': sig.torquein,
                'ipdirect': sig.ipdirect,
                'iptarget': sig.iptarget,
                'iperr': sig.iperr,
            }
        elif params['paths']['data'] == 'd3d_data_all':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = sig.d3d_signals


        else:   
           h = myhash_signals(sig.all_signals.values())#+params['data']['T_min_warn'])
           params['paths']['all_signals_dict'] = sig.all_signals

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
            params['paths']['use_signals_dict'] = sig.jet_signals
        elif params['paths']['data'] == 'jet_data_0D':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = sig.jet_signals_0D
        elif params['paths']['data'] == 'jet_data_1D':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = sig.jet_signals_1D
        elif params['paths']['data'] == 'jet_data_late':
            params['paths']['shot_files'] = [jet_iterlike_wall_late]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = sig.jet_signals
        elif params['paths']['data'] == 'jet_data_carbon_to_late_0D':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall_late]
            params['paths']['use_signals_dict'] = sig.jet_signals_0D
        elif params['paths']['data'] == 'jet_data_temp_profile':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = {
                'etemp_profile': sig.etemp_profile}
        elif params['paths']['data'] == 'jet_data_dens_profile':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = {
                'edens_profile': sig.edens_profile}
        elif params['paths']['data'] == 'jet_carbon_data':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = sig.jet_signals
        elif params['paths']['data'] == 'jet_mixed_data':
            params['paths']['shot_files'] = [jet_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = sig.jet_signals
        elif params['paths']['data'] == 'jenkins_jet':
            params['paths']['shot_files'] = [jenkins_jet_carbon_wall]
            params['paths']['shot_files_test'] = [jenkins_jet_iterlike_wall]
            params['paths']['use_signals_dict'] = sig.jet_signals
        # jet data but with fully defined signals
        elif params['paths']['data'] == 'jet_data_fully_defined':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = sig.fully_defined_signals
        # jet data but with fully defined signals
        elif params['paths']['data'] == 'jet_data_fully_defined_0D':
            params['paths']['shot_files'] = [jet_carbon_wall]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = sig.fully_defined_signals_0D
#        elif params['paths']['data'] == 'd3d_data_ori':
#            params['paths']['shot_files'] = [d3d_full]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'q95': sig.q95,
#                'li': sig.li,
#                'ipori': sig.ipori,
#                'lm': sig.lm,
#                'betan': sig.betan,
#                'energy': sig.energy,
#                'dens': sig.dens,
#                'pradcore': sig.pradcore,
#                'pradedge': sig.pradedge,
#                'pin': sig.pin,
#                'torquein': sig.torquein,
#                'ipdirect': sig.ipdirect,
#                'iptarget': sig.iptarget,
#                'iperr': sig.iperr,
#                'etemp_profile': sig.etemp_profile,
#                'edens_profile': sig.edens_profile,
#            }
#
#        elif params['paths']['data'] == 'd3d_data':
#            params['paths']['shot_files'] = [d3d_full]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'q95': sig.q95,
#                'li': sig.li,
#                'ip': sig.ip,
#                'lm': sig.lm,
#                'betan': sig.betan,
#                'energy': sig.energy,
#                'dens': sig.dens,
#                'pradcore': sig.pradcore,
#                'pradedge': sig.pradedge,
#                'pin': sig.pin,
#                'torquein': sig.torquein,
#                'ipdirect': sig.ipdirect,
#                'iptarget': sig.iptarget,
#                'iperr': sig.iperr,
#                'etemp_profile': sig.etemp_profile,
#                'edens_profile': sig.edens_profile,
#            }
#        elif params['paths']['data'] in ['d3d_data_gar18','d3d_data_garbage']:
#            params['paths']['shot_files'] = [d3d_full_new]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'q95t': sig.q95t,
#                'lit': sig.lit,
#                'ipt': sig.ipt,
#                'lmt': sig.lmt,
#                'betant': sig.betant,
#                'energyt': sig.energyt,
#                'denst': sig.denst,
#                'pradcoret': sig.pradcoret,
#                'pradedget': sig.pradedget,
#                'pint': sig.pint,
#                'torqueint': sig.torqueint,
#                'ipdirectt': sig.ipdirectt,
#                'iptargett': sig.iptargett,
#                'iperrt': sig.iperrt,
#                'etemp_profilet': sig.etemp_profilet,
#                'edens_profilet': sig.edens_profilet,
#            }

#        elif params['paths']['data'] in ['d3d_data_thomson']:
#            params['paths']['shot_files'] = [d3d_full_new]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'q95t': sig.q95,
#                'lit': sig.li,
#                'ipt': sig.ip,
#                'lmt': sig.lm,
#                'betant': sig.betan,
#                'energyt': sig.energy,
#                'denst': sig.dens,
#                'pradcoret': sig.pradcore,
#                'pradedget': sig.pradedge,
#                'pint': sig.pin,
#                'torqueint': sig.torquein,
#                'ipdirectt': sig.ipdirect,
#                'iptargett': sig.iptarget,
#                'iperrt': sig.iperr,
#                'etemp_profile_thomson': sig.etemp_profile_thomson,
#                'edens_profile_thomson': sig.edens_profile_thomson,
#            }
#        
#        elif params['paths']['data'] in ['d3d_data_n1rms_qmin']:
#            params['paths']['shot_files'] = [d3d_full_new]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'q95': sig.q95,
#                'qmin': sig.qmin,
#                'li': sig.li,
#                'ip': sig.ip,
#                'lm': sig.lm,
#                'betan': sig.betan,
#                'energy': sig.energy,
#                'dens': sig.dens,
#                'pradcore': sig.pradcore,
#                'pradedge': sig.pradedge,
#                'pin': sig.pin,
#                'torquein': sig.torquein,
#                'ipdirect': sig.ipdirect,
#                'iptarget': sig.iptarget,
#                'iperr': sig.iperr,
#                'etemp_profile': sig.etemp_profile,
#                'edens_profile': sig.edens_profile,
#                'n1_rms': sig.n1_rms,
#                'n1_rms_no_shift': sig.n1_rms_no_shift,
#            }
#

#        elif params['paths']['data'] in ['d3d_data_n1rms_thomson']:
#            params['paths']['shot_files'] = [d3d_full_new]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'q95_EFITRT1': sig.q95_EFITRT1,
#                'li': sig.li,
#                'ip': sig.ip,
#                'lm': sig.lm,
#                'betan': sig.betan,
#                'energy': sig.energy,
#                'dens': sig.dens,
#                'pradcore': sig.pradcore,
#                'pradedge': sig.pradedge,
#                'pin': sig.pin,
#                'torquein': sig.torquein,
#                'ipdirect': sig.ipdirect,
#                'iptarget': sig.iptarget,
#                'iperr': sig.iperr,
#                'etemp_profile_thomson': sig.etemp_profile_thomson,
#                'edens_profile_thomson': sig.edens_profile_thomson,
#                'n1_rms': sig.n1_rms,
#                'n1_rms_no_shift': sig.n1_rms_no_shift,
#            }
#
#        elif params['paths']['data'] in ['d3d_data_fs07']:
#            params['paths']['shot_files'] = [d3d_full_new]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'q95': sig.q95,
#                'li': sig.li,
#                'fs07': sig.fs07,
#                'ip': sig.ip,
#                'lm': sig.lm,
#                'betan': sig.betan,
#                'energy': sig.energy,
#                'dens': sig.dens,
#                'pradcore': sig.pradcore,
#                'pradedge': sig.pradedge,
#                'pin': sig.pin,
#                'torquein': sig.torquein,
#                'ipdirect': sig.ipdirect,
#                'iptarget': sig.iptarget,
#                'iperr': sig.iperr,
#                'etemp_profile': sig.etemp_profile,
#                'edens_profile': sig.edens_profile,
#                'n1_rms': sig.n1_rms,
#                'n1_rms_no_shift': sig.n1_rms_no_shift,
#            }

#        elif params['paths']['data'] in ['d3d_data_ped_spec']:
#            params['paths']['shot_files'] = [d3d_full_new_2021]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'q95': sig.q95,
#                'qpsi_efitrt1': sig.qpsi_efitrt1,
#              #  'pres_prime_profile': sig.pres_prime_profile,
#                #'li': sig.li,
#                'fs07': sig.fs07,
#                'neped': sig.neped,
#                'peped': sig.peped,
#                'newid': sig.newid,
#                'teped': sig.teped,
#                'tewid': sig.tewid,
#                'ip': sig.ip,
#                'lm': sig.lm,
#                'betan': sig.betan,
#                'energy': sig.energy,
#                'dens': sig.dens,
#                'pradcore': sig.pradcore,
#                'pradedge': sig.pradedge,
#                'pin': sig.pin,
#                'torquein': sig.torquein,
#                #'ipdirect': sig.ipdirect,
#             #   'iptarget': sig.iptarget,
#             #   'iperr': sig.iperr,
#                'etemp_profile': sig.etemp_profile,
#                'edens_profile': sig.edens_profile,
#                'mpi66m322d_spec_profile': sig.mpi66m322d_spec_profile,
#                'n1_rms': sig.n1_rms,
#            #    'n2_rms_10': sig.n2_rms_10,
#            #    'n3_rms_10': sig.n3_rms_10,
#            }

#        elif params['paths']['data'] in ['d3d_data_ped']:
#            params['paths']['shot_files'] = [d3d_full_new_2021]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'q95': sig.q95,
#                #'li': sig.li,
#                'fs07': sig.fs07,
#                'neped': sig.neped,
#                'peped': sig.peped,
#                'newid': sig.newid,
#                'teped': sig.teped,
#                'tewid': sig.tewid,
#                'ip': sig.ip,
#                'lm': sig.lm,
#                'betan': sig.betan,
#                'energy': sig.energy,
#                'dens': sig.dens,
#                'pradcore': sig.pradcore,
#                'pradedge': sig.pradedge,
#                'pin': sig.pin,
#                'torquein': sig.torquein,
#                #'ipdirect': sig.ipdirect,
#             #   'iptarget': sig.iptarget,
#             #   'iperr': sig.iperr,
#                'etemp_profile': sig.etemp_profile,
#                'edens_profile': sig.edens_profile,
#                'n1_rms': sig.n1_rms,
#                'n2_rms_10': sig.n2_rms_10,
#                'n3_rms_10': sig.n3_rms_10,
#            }


#        elif params['paths']['data'] in ['d3d_data_n1rms']:
#            params['paths']['shot_files'] = [d3d_full_new]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'q95': sig.q95,
#                'li': sig.li,
#                'ip': sig.ip,
#                'lm': sig.lm,
#                'betan': sig.betan,
#                'energy': sig.energy,
#                'dens': sig.dens,
#                'pradcore': sig.pradcore,
#                'pradedge': sig.pradedge,
#                'pin': sig.pin,
#                'torquein': sig.torquein,
#                'ipdirect': sig.ipdirect,
#                'iptarget': sig.iptarget,
#                'iperr': sig.iperr,
#                'etemp_profile': sig.etemp_profile,
#                'edens_profile': sig.edens_profile,
#                'n1_rms': sig.n1_rms,
#                'n1_rms_no_shift': sig.n1_rms_no_shift,
#            }

#        elif params['paths']['data'] == 'd3d_data_new':
#            params['paths']['shot_files'] = [d3d_full_new]
#            params['paths']['shot_files_test'] = [] 
#            params['paths']['use_signals_dict'] = {
#                'q95': sig.q95,
#                'li': sig.li,
#                'ip': sig.ip,
#                'lm': sig.lm,
#                'betan': sig.betan,
#                'energy': sig.energy,
#                'dens': sig.dens,
#                'pradcore': sig.pradcore,
#                'pradedge': sig.pradedge,
#                'pin': sig.pin,
#                'torquein': sig.torquein,
#                'ipdirect': sig.ipdirect,
#                'iptarget': sig.iptarget,
#                'iperr': sig.iperr,
#                'etemp_profile': sig.etemp_profile,
#                'edens_profile': sig.edens_profile,
#            }
#        elif params['paths']['data'] == 'd3d_data_real_time':
#            params['paths']['shot_files'] = [d3d_full_new]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'q95_EFITRT1': sig.q95_EFITRT1,
#                'li': sig.li,
#                'ip': sig.ip,
#                'lm': sig.lm,
#                'betan': sig.betan,
#                'energy': sig.energy,
#                'dens': sig.dens,
#                'pradcore': sig.pradcore,
#                'pradedge': sig.pradedge,
#                'pin': sig.pin,
#                'torquein': sig.torquein,
#                'ipdirect': sig.ipdirect,
#                'iptarget': sig.iptarget,
#                'iperr': sig.iperr,
#                'etemp_profile': sig.etemp_profile,
#                'edens_profile': sig.edens_profile,
#            }
#        elif params['paths']['data'] == 'd3d_data_real_time_0D':
#            params['paths']['shot_files'] = [d3d_full_new]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'q95_EFITRT1': sig.q95_EFITRT1,
#                'li': sig.li,
#                'ip': sig.ip,
#                'lm': sig.lm,
#                'betan': sig.betan,
#                'energy': sig.energy,
#                'dens': sig.dens,
#                'pin': sig.pin,
#            #    'vd': sig.vd,
#                'torquein': sig.torquein,
#                'ipdirect': sig.ipdirect,
#                'iptarget': sig.iptarget,
#                'iperr': sig.iperr,
#            }



#        elif params['paths']['data'] == 'd3d_data_1D':
#            params['paths']['shot_files'] = [d3d_full]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'ipdirect': sig.ipdirect,
#                'etemp_profile': sig.etemp_profile,
#                'edens_profile': sig.edens_profile,
#            }
#        elif params['paths']['data'] == 'd3d_data_all_profiles':
#            params['paths']['shot_files'] = [d3d_full]
#            params['paths']['shot_files_test'] = []
#            params['paths']['use_signals_dict'] = {
#                'ipdirect': sig.ipdirect,
#                'etemp_profile': sig.etemp_profile,
#                'edens_profile': sig.edens_profile,
#                'itemp_profile': sig.itemp_profile,
#                'zdens_profile': sig.zdens_profile,
#                'trot_profile': sig.trot_profile,
#                'pthm_profile': sig.pthm_profile,
#                'neut_profile': sig.neut_profile,
#                'q_profile': sig.q_profile,
#                'bootstrap_current_profile': sig.bootstrap_current_profile,
#                'q_psi_profile': sig.q_psi_profile,
#            }
        elif params['paths']['data'] == 'd3d_data_0D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': sig.q95,
                'li': sig.li,
                'ip': sig.ip,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pradcore': sig.pradcore,
                'pradedge': sig.pradedge,
                'pin': sig.pin,
                'torquein': sig.torquein,
                'ipdirect': sig.ipdirect,
                'iptarget': sig.iptarget,
                'iperr': sig.iperr,
            }
        elif params['paths']['data'] == 'd3d_data_all':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = sig.d3d_signals
        elif params['paths']['data'] == 'jenkins_d3d':
            params['paths']['shot_files'] = [d3d_jenkins]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'q95': sig.q95,
                'li': sig.li,
                'ip': sig.ip,
                'lm': sig.lm,
                'betan': sig.betan,
                'energy': sig.energy,
                'dens': sig.dens,
                'pradcore': sig.pradcore,
                'pradedge': sig.pradedge,
                'pin': sig.pin,
                'torquein': sig.torquein,
                'ipdirect': sig.ipdirect,
                'iptarget': sig.iptarget,
                'iperr': sig.iperr,
                'etemp_profile': sig.etemp_profile,
                'edens_profile': sig.edens_profile,
            }
        # jet data but with fully defined signals
        elif params['paths']['data'] == 'd3d_data_fully_defined':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = sig.fully_defined_signals
        # jet data but with fully defined signals
        elif params['paths']['data'] == 'd3d_data_fully_defined_0D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = sig.fully_defined_signals_0D
        elif params['paths']['data'] == 'd3d_data_temp_profile':
            # jet data but with fully defined signals
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'etemp_profile': sig.etemp_profile}  # fully_defined_signals_0D
        elif params['paths']['data'] == 'd3d_data_dens_profile':
            # jet data but with fully defined signals
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = []
            params['paths']['use_signals_dict'] = {
                'edens_profile': sig.edens_profile}  # fully_defined_signals_0D

        # cross-machine
        elif params['paths']['data'] == 'jet_to_d3d_data':
            params['paths']['shot_files'] = [jet_full]
            params['paths']['shot_files_test'] = [d3d_full]
            params['paths']['use_signals_dict'] = sig.fully_defined_signals
        elif params['paths']['data'] == 'd3d_to_jet_data':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = sig.fully_defined_signals
        elif params['paths']['data'] == 'd3d_to_late_jet_data':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [jet_iterlike_wall_late]
            params['paths']['use_signals_dict'] = sig.fully_defined_signals
        elif params['paths']['data'] == 'jet_to_d3d_data_0D':
            params['paths']['shot_files'] = [jet_full]
            params['paths']['shot_files_test'] = [d3d_full]
            params['paths']['use_signals_dict'] = sig.fully_defined_signals_0D
        elif params['paths']['data'] == 'd3d_to_jet_data_0D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = sig.fully_defined_signals_0D
        elif params['paths']['data'] == 'jet_to_d3d_data_1D':
            params['paths']['shot_files'] = [jet_full]
            params['paths']['shot_files_test'] = [d3d_full]
            params['paths']['use_signals_dict'] = sig.fully_defined_signals_1D
        elif params['paths']['data'] == 'd3d_to_jet_data_1D':
            params['paths']['shot_files'] = [d3d_full]
            params['paths']['shot_files_test'] = [jet_iterlike_wall]
            params['paths']['use_signals_dict'] = sig.fully_defined_signals_1D

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


