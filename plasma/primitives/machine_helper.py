#!/usr/bin/env python

"""Helper functions for machine classes."""

def create_missing_value_filler():
    """Common filler for missing values.

    Missing values are to be filled with a time-range and corresponding values of zero.
    Time range is 0...100
    Values are 0
    """
    time = np.linspace(0, 100, 100)
    vals = np.zeros_like(time)
    return time, vals


def get_tree_and_tag(path):
    """Fetch tree and tag from a path."""
    spl = path.split('/')
    tree = spl[0]
    tag = '\\' + spl[1]
    return tree, tag


def get_tree_and_tag_no_backslash(path):
    """Fetch tree and tag from path, removing backslash"""
    spl = path.split('/')
    tree = spl[0]
    tag = spl[1]
    return tree, tag 
