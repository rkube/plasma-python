# -*- coding: utf-8 -*-

import re
from plasma.primitives.signal import Signal

class ChannelSignal(Signal):
    """A signal best represented by a number of channels."""
    def __init__(self, description, paths, machines, tex_label=None,
                 causal_shifts=None, data_avail_tolerances=None,
                 is_strictly_positive=False, mapping_paths=None):
        super(ChannelSignal, self).__init__(
            description, paths, machines, tex_label, causal_shifts,
            is_ip=False, data_avail_tolerances=data_avail_tolerances,
            is_strictly_positive=is_strictly_positive,
            mapping_paths=mapping_paths)
        nums, new_paths = self.get_channel_nums(paths)
        self.channel_nums = nums
        self.paths = new_paths

    def get_channel_nums(self, paths):
        regex = re.compile(r'channel\d+')
        regex_int = re.compile(r'\d+')
        nums = []
        new_paths = []
        for p in paths:
            assert(p[-1] != '/')
            elements = p.split('/')
            res = regex.findall(elements[-1])
            assert(len(res) < 2)
            if len(res) == 0:
                nums.append(None)
                new_paths.append(p)
            else:
                nums.append(int(regex_int.findall(res[0])[0]))
                new_paths.append("/".join(elements[:-1]))
        return nums, new_paths

    def get_channel_num(self, machine):
        idx = self.get_idx(machine)
        return self.channel_nums[idx]

    def fetch_data(self, machine, shot_num, c):
        time, data, mapping, success = self.fetch_data_basic(
            machine, shot_num, c)
        mapping = None  # we are not interested in the whole profile
        channel_num = self.get_channel_num(machine)
        if channel_num is not None and success:
            if np.ndim(data) != 2:
                print("Channel Signal {} expected 2D array for shot {}".format(
                    self, self.shot_number))
                success = False
            else:
                data = data[channel_num, :]  # extract channel of interest
        return time, data, mapping, success

    def get_file_path(self, prepath, machine, shot_number):
        dirname = self.get_path(machine)
        num = self.get_channel_num(machine)
        if num is not None:
            dirname += "/channel{}".format(num)
        return get_individual_shot_file(prepath + '/' + machine.name + '/'
                                        + dirname + '/', shot_number)



