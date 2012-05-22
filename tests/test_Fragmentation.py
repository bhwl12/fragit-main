"""
**********************************************************************
tests/test_Fragmentation.py - test functionality of Fragmentation
                              module

Copyright (C) 2011 Casper Steinmann

This file is part of the FragIt project.

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
***********************************************************************/
"""
import unittest
import openbabel

from fragmentation import Fragmentation
from util import is_dictionary, lenOfLists

class TestFragmentationModule(unittest.TestCase):

    def setUp(self):
        self.filename_pdb = "1UAO.pdb"

        # for testing, use OpenBabel functionality directly
        self.molecule = openbabel.OBMol()
        self.conversion = openbabel.OBConversion()
        self.conversion.SetInFormat("pdb")
        self.conversion.ReadFile(self.molecule, self.filename_pdb)

        self.fragmentation = Fragmentation(self.molecule)

    def tearDown(self):
        pass

    def test_FragmentationDefaultParameters(self):
        frg = self.fragmentation
        self.assertEqual(frg.mol != None, True)
        #self.assertEqual(frg.protected_atoms, list())
        #self.assertEqual(frg.explicit_protected_atoms, list())
        #self.assertEqual(frg.explicit_frag_pairs, list())
        #self.assertEqual(frg.smartBreakPatterns, {"peptide": "[$(CN)][$(C(=O)NCC(=O))]"})
        #self.assertEqual(frg.smartProtectPatterns, ["[$([NH2]),$([NH3]),$([NH][CH2][CH2]),$([NH2][CH2]C)]CC(=O)[$(NCC=O)]"])
        #self.assertEqual(frg.fragmentGrouping, 1)
        #self.assertEqual(frg.minFragSize, None)
        #self.assertEqual(frg.maxFragSize, 50)
        #self.assertEqual(frg.boundaries, [])
        #self.assertEqual(frg.centralpoint, None)
        #self.assertEqual(frg.centralfragment, None)
        #self.assertEqual(frg.active_fragments, [])
        #self.assertEqual(frg.residue_names, None)
        #self.assertEqual(frg.atom_pairs, [])
        #self.assertEqual(frg.getFragments(), [])
        #self.assertEqual(frg.rejoined_atoms, [])
        #self.assertEqual(frg.formalCharges, [])
        #self.assertEqual(frg.total_charge, 0)
        #self.assertEqual(frg.fragmentCharge, [])

    def test_FragmentationSetActiveFragments(self):
        self.fragmentation.setActiveFragments([1, 2, 3])
        self.assertEqual(self.fragmentation.active_fragments, [1, 2, 3])

    def test_FragmentationApplySmartProtectPatterns(self):
        self.fragmentation.applySmartProtectPatterns()
        self.assertEqual(self.fragmentation.getExplicitlyProtectedAtoms(), [1, 2, 3, 4, 10])

    def test_FragmentationDetermineFormalCharges(self):
        self.fragmentation.determineFormalCharges()
        self.assertAlmostEqual(sum(self.fragmentation.formalCharges), -2)

    def test_FragmentationGetProtectedAtoms(self):
        self.assertEqual(self.fragmentation.getExplicitlyProtectedAtoms(), [])

    def test_FragmentationAddProtectedAtomsAfterProtect(self):
        self.fragmentation.setProtectedAtoms()
        self.fragmentation.addExplicitlyProtectedAtoms([44, 55, 67])
        #self.assertEqual(self.fragmentation.explicit_protected_atoms, [44, 55, 67])
        self.assertEqual(self.fragmentation.getExplicitlyProtectedAtoms(), [1, 2, 3, 4, 10, 44, 55, 67])

    def test_FragmentationAddBrokenBond(self):
        #self.assertEqual(self.fragmentation.getExplicitlyBreakAtomPairs(), [])
        #self.fragmentation.addBrokenBond((1, 4))
        #self.assertEqual(self.fragmentation.getExplicitlyBreakAtomPairs(), [(1, 4)])
	pass

    def test_FragmentationIsBondProtected(self):
        bond_pair = (2, 3)
        self.assertEqual(self.fragmentation.isBondProtected(bond_pair), False)
        self.fragmentation.addExplicitlyProtectedAtoms([2])
        self.assertEqual(self.fragmentation.isBondProtected(bond_pair), True)

    def test_FragmentationRealBondBreakerNoProtect(self):
        bond_atoms = (2, 3)
        self.fragmentation.realBondBreaker("peptide", bond_atoms)
        self.assertEqual(self.fragmentation.getExplicitlyBreakAtomPairs(), [(2, 3)])

    def test_FragmentationIsValidExplicitBond(self):
        self.assertRaises(ValueError, self.fragmentation.isValidExplicitBond, (1, 1))
        self.assertRaises(ValueError, self.fragmentation.isValidExplicitBond, (2, 4))

    def test_FragmentationBreakBondsWithNoProtect(self):
        self.fragmentation.breakBonds()
        self.assertEqual(len(self.fragmentation.getExplicitlyBreakAtomPairs()), 9)

    def test_FragmentationBreakBondsExplcitWithNoProtect(self):
        self.fragmentation.addExplicitlyBreakAtomPairs([(111, 112)])
        self.fragmentation.breakBonds()
        self.assertEqual(len(self.fragmentation.getExplicitlyBreakAtomPairs()), 10)

    def test_FragmentationBreakBondsWithProtect(self):
        self.fragmentation.setProtectedAtoms()
        self.fragmentation.breakBonds()
        self.assertEqual(len(self.fragmentation.getExplicitlyBreakAtomPairs()), 8)

    def test_FragmentationBreakBondsExplcitWithProtect(self):
        self.fragmentation.setProtectedAtoms()
        self.fragmentation.addExplicitlyBreakAtomPairs([(111, 112)])
        self.fragmentation.breakBonds()
        self.assertEqual(len(self.fragmentation.getExplicitlyBreakAtomPairs()), 9)

    def test_FragmentationDetermineFragmentsNoBreaking(self):
        self.assertRaises(ValueError, self.fragmentation.determineFragments)

    def test_FragmentationDetermineFragmentsWithBreaking(self):
        self.fragmentation.breakBonds()
        self.fragmentation.determineFragments()
        self.assertEqual(lenOfLists(self.fragmentation.getFragments()), [7, 21, 12, 14, 15, 14, 7, 14, 24, 10])

    def test_FragmentationDetermineFragmentsWithBreakingAndGrouping(self):
        self.fragmentation.setFragmentGroupCount(2)
        self.fragmentation.breakBonds()
        self.fragmentation.determineFragments()
        self.fragmentation.doFragmentGrouping()
        self.assertEqual(lenOfLists(self.fragmentation.getFragments()), [28, 26, 29, 21, 34])

    def test_FragmentationDetermineFragmentsWithBreakingAndGroupingTriple(self):
        self.fragmentation.setFragmentGroupCount(3)
        self.fragmentation.breakBonds()
        self.fragmentation.determineFragments()
        self.fragmentation.doFragmentGrouping()
        self.assertEqual(lenOfLists(self.fragmentation.getFragments()), [40, 43, 45, 10])

    def test_FragmentationFindFragmentsCastErrors(self):
        self.assertRaises(ValueError, self.fragmentation.getAtomsInSameFragment, 1, 1)
        self.assertRaises(ValueError, self.fragmentation.getAtomsInSameFragment, "")

    def test_FragmentationFindFragmentsNoGrouping(self):
        self.fragmentation.breakBonds()
        self.fragmentation.determineFragments()
        self.assertEqual(self.fragmentation.getAtomsInSameFragment(11, 0), [3, 4, 10, 11, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30])
        self.assertEqual(self.fragmentation.getAtomsInSameFragment(12, 0), [12, 13, 31, 32] + range(35, 43))

    def test_FragmentationFindFragmentsNoGroupingWithProtect(self):
        self.fragmentation.setProtectedAtoms()
        self.fragmentation.breakBonds()
        self.fragmentation.determineFragments()
        self.assertEqual(self.fragmentation.getAtomsInSameFragment(11, 0), range(1, 12)+range(14, 31))
        self.assertEqual(self.fragmentation.getAtomsInSameFragment(12, 0), [12, 13, 31, 32] + range(35, 43))

    def test_FragmentationFragmentChargeAfterFragment(self):
        self.fragmentation.determineFormalCharges()
        self.fragmentation.breakBonds()
        self.fragmentation.determineFragments()
        self.fragmentation.determineFragmentCharges()
        self.assertEqual(self.fragmentation.getFragmentCharges(), [ 1, 0, -1, 0, -1, 0, 0, 0, 0, -1])

    def test_FragmentationFragmentChargeAfterProtectAndFragment(self):
        self.fragmentation.setProtectedAtoms()
        self.fragmentation.determineFormalCharges()
        self.fragmentation.breakBonds()
        self.fragmentation.determineFragments()
        self.fragmentation.determineFragmentCharges()
        self.assertEqual(self.fragmentation.getFragmentCharges(), [1, -1, 0, -1, 0, 0, 0, 0, -1])

    def test_FragmentationFragmentChargeAfterFragmentAndGroup(self):
        self.fragmentation.determineFormalCharges()
        self.fragmentation.breakBonds()
        self.fragmentation.determineFragments()
        self.fragmentation.setFragmentGroupCount(2)
        self.fragmentation.doFragmentGrouping()
        self.fragmentation.determineFragmentCharges()
        self.assertEqual(self.fragmentation.getFragmentCharges(), [1, -1, -1, 0, -1])

    def test_FragmentationFragmentChargeAfterProtectFragmentAndGroup(self):
        self.fragmentation.setProtectedAtoms()
        self.fragmentation.determineFormalCharges()
        self.fragmentation.breakBonds()
        self.fragmentation.determineFragments()
        self.fragmentation.setFragmentGroupCount(2)
        self.fragmentation.doFragmentGrouping()
        self.fragmentation.determineFragmentCharges()
        self.assertEqual(self.fragmentation.getFragmentCharges(), [0, -1, 0, 0, -1])

    def test_FragmentationGetOBAtom(self):
        test_atom = self.fragmentation.getOBAtom(1)
        self.assertEqual(type(test_atom), type(openbabel.OBAtom()))

    def test_FragmentationNameFragments(self):
        self.fragmentation.breakBonds()
        self.fragmentation.determineFragments()
        self.fragmentation.nameFragments()
        self.assertEqual(self.fragmentation.getFragmentNames(), ["NH3+", "AMINO", "AMINO", "AMINO", "AMINO", "AMINO", "AMINO", "AMINO", "AMINO", "AMINO"])

    def test_FragmentationNameFragmentsProtect(self):
        self.fragmentation.setProtectedAtoms()
        self.fragmentation.breakBonds()
        self.fragmentation.determineFragments()
        self.fragmentation.nameFragments()
        self.assertEqual(self.fragmentation.getFragmentNames(), ["AMINO", "AMINO", "AMINO", "AMINO", "AMINO", "AMINO", "AMINO", "AMINO", "AMINO"])

    def test_FragmentationNameFragmentsGroupByTwo(self):
        self.fragmentation.breakBonds()
        self.fragmentation.setFragmentGroupCount(2)
        self.fragmentation.determineFragments()
        self.fragmentation.doFragmentGrouping()
        self.fragmentation.nameFragments()
        self.assertEqual(self.fragmentation.getFragmentNames(), ["AMINO", "AMINO", "AMINO", "AMINO", "AMINO"])

def suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(TestFragmentationModule))
    return s

if __name__ == '__main__':
    unittest.main()
