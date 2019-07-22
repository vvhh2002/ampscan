import unittest
import os
import sys


class TestBasicFunction(unittest.TestCase):
    ACCURACY = 3  # The number of decimal places to value accuracy for

    def SetUp(self):
        modPath = os.path.abspath(os.getcwd())
        sys.path.insert(0, modPath)
    
    def test_running(self):
        print("Running sample_test.py")
        self.assertTrue(True)
    
    def test_python_imports(self):
        import numpy, scipy, matplotlib, vtk, AmpScan.core
        s = str(type(numpy))
        self.assertEqual(s, "<class 'module'>")
        s = str(type(scipy))
        self.assertEqual(s, "<class 'module'>")
        s = str(type(matplotlib))
        self.assertEqual(s, "<class 'module'>")
        s = str(type(vtk))
        self.assertEqual(s, "<class 'module'>")
        s = str(type(AmpScan.core))
        self.assertEqual(s, "<class 'module'>", "Failed import: AmpScan.core")

    @unittest.expectedFailure
    def test_failure(self):
        s = str(type("string"))
        self.assertEqual(s, "<class 'module'>")

    def test_rotate(self):
        from AmpScan.core import AmpObject
        stlPath = self.get_path("sample_stl_sphere_BIN.stl")
        Amp = AmpObject(stlPath)
        s = str(type(Amp))
        self.assertEqual(s, "<class 'AmpScan.core.AmpObject'>", "Not expected Object")
        with self.assertRaises(TypeError):
            Amp.rotateAng(7)
            Amp.rotateAng({})

    def test_trim(self):
        # a new test for the trim module
        stlPath = self.get_path("sample_stl_sphere_BIN.stl")
        from AmpScan.core import AmpObject
        Amp = AmpObject(stlPath)
        #with self.assertRaises(TypeError):
            #Amp.planarTrim([], plane=[])

    def test_translate(self):
        from AmpScan.core import AmpObject
        stlPath = self.get_path("sample_stl_sphere_BIN.stl")
        amp = AmpObject(stlPath)

        # Check that everything has been translated by 1
        start = amp.vert.mean(axis=0)[:]
        amp.translate([1, -1, 0])
        end = amp.vert.mean(axis=0)[:]
        self.assertAlmostEqual(start[0], end[0]-1, places=TestBasicFunction.ACCURACY)
        self.assertAlmostEqual(start[1], end[1]+1, places=TestBasicFunction.ACCURACY)
        self.assertAlmostEqual(start[2], end[2], places=TestBasicFunction.ACCURACY)

        # Check that translating raises TypeError when translating with an invalid type
        with self.assertRaises(Exception):
            amp.translate("")

        # Check that translating raises ValueError when translating with 2 dimensions
        with self.assertRaises(ValueError):
            amp.translate([0, 0])

        # Check that translating raises ValueError when translating with 4 dimensions
        with self.assertRaises(ValueError):
            amp.translate([0, 0, 0, 0])

    def get_path(self, filename):
        """
        Method to get the absolute path to the testing files

        :param filename: Name of the file in tests folder
        :return: The absolute path to the file
        """

        # Check if the parent directory is tests (this is for Pycharm unittests)
        if os.path.basename(os.getcwd()) == "tests":
            # This is for Pycharm testing
            stlPath = filename
        else:
            # This is for the Gitlab testing
            stlPath = os.path.abspath(os.getcwd()) + "\\tests\\"+filename
        return stlPath
        

if __name__ == '__main__':
    unittest.main()
