#!/usr/bin/env python
# Copyright 2014-2018 The PySCF Developers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest
import numpy as np

from pyscf.pbc import gto as pbcgto
from pyscf.pbc import scf as pbcscf
import pyscf.pbc.mp
import pyscf.pbc.mp.kmp2


atom = 'C 0 0 0'
a = np.eye(3) * 5
basis = 'cc-pvdz'
cell = pbcgto.M(atom=atom, basis=basis, a=a).set(precision=1e-12, verbose=4)


class KnownValues(unittest.TestCase):
    def test_mp2(self):
        mf = pbcscf.RHF(cell).density_fit()
        mf.conv_tol = 1e-10
        mf.kernel()
        pt = pyscf.pbc.mp.mp2.RMP2(mf).run()

        self.assertAlmostEqual(pt.e_corr, -0.0634551885557889, 7)
        self.assertAlmostEqual(pt.e_corr_ss, -0.00561754117341521, 7)
        self.assertAlmostEqual(pt.e_corr_os, -0.0578376473823737, 7)

    def test_kmp2(self):
        def run_k(kmesh):
            kpts = cell.make_kpts(kmesh)
            mf = pbcscf.KRHF(cell, kpts).density_fit()
            mf.conv_tol = 1e-10
            mf.kernel()
            pt = pyscf.pbc.mp.kmp2.KMP2(mf).run()
            return pt

        pt = run_k((1,1,1))
        self.assertAlmostEqual(pt.e_corr, -0.0634551885557889, 7)
        self.assertAlmostEqual(pt.e_corr_ss, -0.00561754117341521, 7)
        self.assertAlmostEqual(pt.e_corr_os, -0.0578376473823737, 7)

        pt = run_k((2,1,1))
        self.assertAlmostEqual(pt.e_corr, -0.0640728626841088, 7)
        self.assertAlmostEqual(pt.e_corr_ss, -0.00558491559563941, 7)
        self.assertAlmostEqual(pt.e_corr_os, -0.0584879470884693, 7)

    def test_ksymm(self):
        def run_k(kmesh):
            kpts = cell.make_kpts(kmesh, space_group_symmetry=True)
            mf = pbcscf.KRHF(cell, kpts).density_fit()
            mf.conv_tol = 1e-10
            mf.kernel()
            pt = pyscf.pbc.mp.kmp2_ksymm.KMP2(mf).run()
            return pt

        pt = run_k((1,1,1))
        self.assertAlmostEqual(pt.e_corr, -0.0634551885557889, 7)
        self.assertAlmostEqual(pt.e_corr_ss, -0.00561754117341521, 7)
        self.assertAlmostEqual(pt.e_corr_os, -0.0578376473823737, 7)

        pt = run_k((2,1,1))
        self.assertAlmostEqual(pt.e_corr, -0.0640728626841088, 7)
        self.assertAlmostEqual(pt.e_corr_ss, -0.00558491559563941, 7)
        self.assertAlmostEqual(pt.e_corr_os, -0.0584879470884693, 7)


if __name__ == '__main__':
    print("Full kpoint test")
    unittest.main()
