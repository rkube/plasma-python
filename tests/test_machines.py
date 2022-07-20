import unittest

from plasma.primitives.machine import MachineNSTX, MachineJET, MachineD3D


class TestMachines(unittest.TestCase):
    """Test routines for machines."""
    def test_machine_nstx(self):
        """Test whether we can instantiate NSTX machine"""
        my_machine = MachineNSTX()

    def test_machine_jet(self):
        """Test whether we can instantiate JET machine"""
        my_machine = MachineJET()

    def test_machine_d3d(self):
        """Test whether we can instantiate D3D machine"""
        my_machine = MachineD3D()



if __name__ == "__main__":
    unittest.main()
