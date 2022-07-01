#!/usr/bin/env python

"""
This file contains pre-defined shot lists.

They were originally placed in plasma/conf_parser.py
"""

from plasma.primitives.shots import ShotListFiles
from plasma.primitives.machine import MachineD3D, MachineJET, MachineNSTX

       
# assert order
# q95, li, ip, lm, betan, energy, dens, pradcore, pradedge, pin,
# pechin, torquein, ipdirect, etemp_profile, edens_profile
"""Commenting this out until I know what this is.
2022-07-01 RK




# shot lists
jet_carbon_wall = ShotListFiles(MachineJET, 
    params['paths']['shot_list_dir'],
    ['CWall_clear.txt', 'CFC_unint.txt'], 'jet carbon wall data')
jet_iterlike_wall = ShotListFiles(MachineJET, 
    params['paths']['shot_list_dir'],
    ['ILW_unint.txt', 'BeWall_clear.txt'], 'jet iter like wall data')

jet_iterlike_wall_late = ShotListFiles(MachineJET, 
    params['paths']['shot_list_dir'],
    ['ILW_unint_late.txt', 'ILW_clear_late.txt'],
    'Late jet iter like wall data')

jenkins_jet_carbon_wall = ShotListFiles(MachineJET,
    params['paths']['shot_list_dir'],
    ['jenkins_CWall_clear.txt', 'jenkins_CFC_unint.txt'],
    'Subset of jet carbon wall data for Jenkins tests')
jenkins_jet_iterlike_wall = ShotListFiles(MachineJET,
    params['paths']['shot_list_dir'],
    ['jenkins_ILW_unint.txt', 'jenkins_BeWall_clear.txt'],
    'Subset of jet iter like wall data for Jenkins tests')

jet_full = ShotListFiles(MachineJET,
    params['paths']['shot_list_dir'],
    ['ILW_unint.txt', 'BeWall_clear.txt', 'CWall_clear.txt',
     'CFC_unint.txt'], 'jet full data')

d3d_full = ShotListFiles(MachineD3D, 
    params['paths']['shot_list_dir'],
    ['d3d_clear_data_avail.txt', 'd3d_disrupt_data_avail.txt'],
    'd3d data since shot 125500')

d3d_full_new = ShotListFiles(MachineD3D, 
    params['paths']['shot_list_dir'],
    ['shots_since_2016_clear.txt','shots_since_2016_disrupt.txt'],
    'd3d data since shot 125500')

d3d_full_new_2021 = ShotListFiles(MachineD3D, 
    params['paths']['shot_list_dir'],
    ['shots_since_2016_clear_temp.txt','shots_since_2016_disrupt.txt'],
    'd3d data since shot 125500')

d3d_jenkins = ShotListFiles(MachineD3D,
    params['paths']['shot_list_dir'],
    ['jenkins_d3d_clear.txt', 'jenkins_d3d_disrupt.txt'],
    'Subset of d3d data for Jenkins test')

"""
