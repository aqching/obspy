#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
The gse2.core test suite.
"""

from obspy.core import Stream, Trace, UTCDateTime, read
import inspect
import os
import unittest
import copy
import numpy as np


class CoreTestCase(unittest.TestCase):
    """
    Test cases for libgse2 core interface
    """
    def setUp(self):
        # directory where the test files are located
        self.path = os.path.dirname(inspect.getsourcefile(self.__class__))

    def tearDown(self):
        pass

    def test_readViaObspy(self):
        """
        Read files via L{obspy.Trace}
        """
        gse2file = os.path.join(self.path, 'data', 'loc_RJOB20050831023349.z')
        testdata = [12, -10, 16, 33, 9, 26, 16, 7, 17, 6, 1, 3, -2]
        # read
        st = read(gse2file)
        st._verify()
        tr = st[0]
        self.assertEqual(tr.stats['station'], 'RJOB ')
        self.assertEqual(tr.stats.npts, 12000)
        self.assertEqual(tr.stats['sampling_rate'], 200)
        self.assertEqual(tr.stats.get('channel'), '  Z')
        self.assertEqual(tr.stats.gse2.get('vang'), -1.0)
        self.assertEqual(tr.stats.gse2.get('calper'), 1.0)
        self.assertAlmostEqual(tr.stats.gse2.get('calib'), 9.49e-02)
        self.assertEqual(tr.stats.starttime.timestamp, 1125455629.849998)
        self.assertEqual(tr.data[0:13].tolist(), testdata)

    def test_readHeadViaObspy(self):
        """
        Read header of files via L{obspy.Trace}
        """
        gse2file = os.path.join(self.path, 'data', 'loc_RJOB20050831023349.z')
        # read
        st = read(gse2file, headonly = True)
        tr = st[0]
        self.assertEqual(tr.stats['station'], 'RJOB ')
        self.assertEqual(tr.stats.npts, 12000)
        self.assertEqual(tr.stats['sampling_rate'], 200)
        self.assertEqual(tr.stats.get('channel'), '  Z')
        self.assertEqual(tr.stats.gse2.get('vang'), -1.0)
        self.assertEqual(tr.stats.gse2.get('calper'), 1.0)
        self.assertAlmostEqual(tr.stats.gse2.get('calib'), 9.49e-02)
        self.assertEqual(tr.stats.starttime.timestamp, 1125455629.849998)
        self.assertEqual(str(tr.data), '[]')

    def test_readAndWriteViaObspy(self):
        """
        Read and Write files via L{obspy.Trace}
        """
        tempfile = os.path.join(self.path, 'data', 'temp1.gse2')
        gse2file = os.path.join(self.path, 'data', 'loc_RNON20040609200559.z')
        # read trace
        st1 = read(gse2file)
        st1._verify()
        tr1 = st1[0]
        # write comparison trace
        st2 = Stream()
        st2.traces.append(Trace())
        tr2 = st2[0]
        tr2.data = copy.deepcopy(tr1.data)
        tr2.stats = copy.deepcopy(tr1.stats)
        st2.write(tempfile, format = 'GSE2')
        # read comparison trace
        st3 = read(tempfile)
        os.remove(tempfile)
        st3._verify()
        tr3 = st3[0]
        # check if equal
        self.assertEqual(tr3.stats['station'], tr1.stats['station'])
        self.assertEqual(tr3.stats.npts, tr1.stats.npts)
        self.assertEqual(tr3.stats['sampling_rate'],
                         tr1.stats['sampling_rate'])
        self.assertEqual(tr3.stats.get('channel'),
                         tr1.stats.get('channel'))
        self.assertEqual(tr3.stats.get('starttime'),
                         tr1.stats.get('starttime'))
        self.assertEqual(tr3.stats.gse2.get('vang'),
                         tr1.stats.gse2.get('vang'))
        self.assertEqual(tr3.stats.gse2.get('calper'),
                         tr1.stats.gse2.get('calper'))
        self.assertEqual(tr3.stats.gse2.get('calib'),
                         tr1.stats.gse2.get('calib'))
        np.testing.assert_equal(tr3.data, tr1.data)

    def test_readAndWriteStreamsViaObspy(self):
        """
        Read and Write files containing multiple GSE2 parts via L{obspy.Trace}
        """
        # setup test
        tmpfile1 = os.path.join(self.path, 'data', 'tmp1.gse2')
        tmpfile2 = os.path.join(self.path, 'data', 'tmp2.gse2')
        files = [os.path.join(self.path, 'data', 'loc_RNON20040609200559.z'),
                 os.path.join(self.path, 'data', 'loc_RJOB20050831023349.z')]
        testdata = [12, -10, 16, 33, 9, 26, 16, 7, 17, 6, 1, 3, -2]
        # write test file containing multiple GSE2 parts
        f = open(tmpfile1, 'wb')
        for i in xrange(2):
            f1 = open(files[i], 'rb')
            f.write(f1.read())
            f1.close()
        f.close()
        # read
        st1 = read(tmpfile1)
        st1._verify()
        self.assertEqual(len(st1), 2)
        tr11 = st1[0]
        tr12 = st1[1]
        self.assertEqual(tr11.stats['station'], 'RNON ')
        self.assertEqual(tr12.stats['station'], 'RJOB ')
        self.assertEqual(tr12.data[0:13].tolist(), testdata)
        # write and read
        st1.write(tmpfile2, format = 'GSE2')
        st2 = read(tmpfile2)
        st2._verify()
        self.assertEqual(len(st2), 2)
        tr21 = st1[0]
        tr22 = st1[1]
        self.assertEqual(tr21.stats['station'], 'RNON ')
        self.assertEqual(tr22.stats['station'], 'RJOB ')
        self.assertEqual(tr22.data[0:13].tolist(), testdata)
        np.testing.assert_equal(tr21.data, tr11.data)
        np.testing.assert_equal(tr22.data, tr12.data)
        os.remove(tmpfile1)
        os.remove(tmpfile2)

    def test_writeIntegersViaObsPy(self):
        """
        Write file test via L{obspy.Trace}.
        """
        tempfile = os.path.join(self.path, 'data', 'temp2.gse2')
        npts = 1000
        # data cloud of integers - float won't work!
        data = np.random.randint(-1000, 1000, npts)
        stats = {'network': 'BW', 'station': 'TEST', 'location':'',
                 'channel': 'EHE', 'npts': npts, 'sampling_rate': 200.0}
        start = UTCDateTime(2000, 1, 1)
        stats['starttime'] = start
        stats['endtime'] = start + (npts - 1) * 0.005
        tr = Trace(data = data, header = stats)
        tr._verify()
        st = Stream([tr])
        st._verify()
        # write
        st.write(tempfile, format = "GSE2")
        # read again
        stream = read(tempfile)
        os.remove(tempfile)
        stream._verify()
        np.testing.assert_equal(data, stream[0].data)
        # test default attributes
        self.assertEqual('CM6', stream[0].stats.gse2.datatype)
        self.assertEqual(-1, stream[0].stats.gse2.vang)
        self.assertEqual(1.0, stream[0].stats.gse2.calper)
        self.assertEqual(1.0, stream[0].stats.gse2.calib)

    def test_tabCompleteStats(self):
        """
        Read files via L{obspy.Trace}
        """
        gse2file = os.path.join(self.path, 'data', 'loc_RJOB20050831023349.z')
        # read
        tr = read(gse2file)[0]
        self.assertTrue('station' in dir(tr.stats))
        self.assertTrue('npts' in dir(tr.stats))
        self.assertTrue('sampling_rate' in dir(tr.stats))
        self.assertEqual(tr.stats['station'], 'RJOB ')
        self.assertEqual(tr.stats.npts, 12000)
        self.assertEqual(tr.stats['sampling_rate'], 200)


def suite():
    return unittest.makeSuite(CoreTestCase, 'test')


if __name__ == '__main__':
    unittest.main(defaultTest = 'suite')
