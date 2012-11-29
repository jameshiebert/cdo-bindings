import unittest,os,tempfile
from stat import *
from cdo import *

class CdoTest(unittest.TestCase):

    def testCDO(self):
        cdo = Cdo()
        newCDO="/usr/bin/cdo"
        if os.path.isfile(newCDO):
            cdo.setCdo(newCDO)
            self.assertEqual(newCDO,cdo.getCdo())
            cdo.setCdo('cdo')

    def testDbg(self):
        cdo = Cdo()
        self.assertEqual(False,cdo.debug)
        cdo.debug = True
        self.assertEqual(True,cdo.debug)
        cdo.debug = False

    def testOps(self):
        cdo = Cdo()
        self.assertIn("sinfov",cdo.operators)
        self.assertIn("for",cdo.operators)
        self.assertIn("mask",cdo.operators)
        self.assertIn("studentt",cdo.operators)

    def test_getOperators(self):
        cdo = Cdo()
        for op in ['random','stdatm','for','cdiwrite','info','showlevel','sinfo','remap','geopotheight','mask','topo','thicknessOfLevels']:
            if 'thicknessOfLevels' != op:
                self.assertIn(op,cdo.operators)
            else:
                self.assertIn(op,dir(cdo))

    def test_listAllOperators(self):
        cdo = Cdo()
        operators = cdo.operators
        operators.sort()
        #print "\n".join(operators)

    def test_simple(self):
        cdo = Cdo()
        cdo.debug = True
        s   = cdo.sinfov(input="-topo",options="-f nc")
        s   = cdo.sinfov(input="-remapnn,r36x18 -topo",options="-f nc")
        f   = 'ofile.nc'
        cdo.expr("'z=log(abs(topo+1))*9.81'",input="-topo",output = f,options="-f nc")
        s   = cdo.infov(input=f)
        cdo.stdatm("0",output=f,options="-f nc")

    def test_outputOperators(self):
        cdo = Cdo()
        levels = cdo.showlevel(input = "-stdatm,0")
        info   = cdo.sinfo(input = "-stdatm,0")
        self.assertEqual([0,0],map(float,levels))
        self.assertEqual("File format: GRIB",info[0])

        values = cdo.outputkey("value",input="-stdatm,0")
        self.assertEqual(["1013.25", "288"],values)
        values = cdo.outputkey("value",input="-stdatm,0,10000")
        self.assertEqual(["1013.25", "271.913", "288", "240.591"],values)
        values = cdo.outputkey("level",input="-stdatm,0,10000")
        self.assertEqual(["0", "10000","0", "10000"],values)

    def test_bndLevels(self):
        cdo = Cdo()
        ofile = cdo.stdatm(25,100,250,500,875,1400,2100,3000,4000,5000,options = "-f nc")
        self.assertEqual([0, 50.0, 150.0, 350.0, 650.0, 1100.0, 1700.0, 2500.0, 3500.0, 4500.0, 5500.0],
                    cdo.boundaryLevels(input = "-selname,T " + ofile))
        self.assertEqual([50.0, 100.0, 200.0, 300.0, 450.0, 600.0, 800.0, 1000.0, 1000.0, 1000.0],
                     cdo.thicknessOfLevels(input = ofile))

    def test_CDO_options(self):
        cdo = Cdo()
        names = cdo.showname(input = "-stdatm,0",options = "-f nc")
        self.assertEqual(["P T"],names)
        ofile = cdo.topo(options = "-z szip")
        self.assertEqual(["GRIB SZIP"],cdo.showformat(input = ofile))

    def test_chain(self):
        cdo = Cdo()
        ofile = cdo.setname("veloc", input=" -copy -random,r1x1",options = "-f nc")
        self.assertEqual(["veloc"],cdo.showname(input = ofile))

    def test_diff(self):
        cdo = Cdo()
        cdo.debug = True
        diffv = cdo.diffn(input = "-random,r1x1 -random,r1x1")
        print diffv
        self.assertEqual(diffv[1].split(' ')[-1],"random")
        self.assertEqual(diffv[1].split(' ')[-3],"0.53060")
        diff  = cdo.diff(input = "-random,r1x1 -random,r1x1")
        self.assertEqual(diff[1].split(' ')[-3],"0.53060")

    def test_returnCdf(self):
        cdo = Cdo()
        ofile = tempfile.NamedTemporaryFile(delete=True,prefix='cdoPy').name
        press = cdo.stdatm("0",output=ofile,options="-f nc")
        self.assertEqual(ofile,press)
        a = cdo.readCdf(press)
        variables = cdo.stdatm("0",options="-f nc",returnCdf=True).variables
        print(variables)
        press = cdo.stdatm("0",options="-f nc",returnCdf=True).variables['P'][:]
        self.assertEqual(1013.25,press.min())
        press = cdo.stdatm("0",output=ofile,options="-f nc")
        self.assertEqual(ofile,press)
        cdo.setReturnArray()
        outfile = 'test.nc'
        press = cdo.stdatm("0",output=outfile,options="-f nc").variables["P"][:]
        self.assertEqual(1013.25,press.min())
        cdo.unsetReturnArray()
        press = cdo.stdatm("0",output=outfile,options="-f nc")
        self.assertEqual(press,outfile)
        press = cdo.stdatm("0",output=outfile,options="-f nc",returnCdf=True).variables["P"][:]
        self.assertEqual(1013.25,press.min())
        print("press = "+press.min().__str__())
        cdo.unsetReturnArray()
        press = cdo.stdatm("0",output=ofile,options="-f nc")
        self.assertEqual(ofile,press)


    def test_forceOutput(self):
        cdo =Cdo()
        cdo.debug = True
        outs = []
        # tempfiles
        outs.append(cdo.stdatm("0,10,20"))
        outs.append(cdo.stdatm("0,10,20"))
        self.assertNotEqual(outs[0],outs[1])
        outs = []

        # deticated output, force = true (=defaut setting)
        ofile = 'test_force'
        outs.append(cdo.stdatm("0,10,20",output = ofile))
        mtime0 = os.stat(ofile).st_mtime
        outs.append(cdo.stdatm("0,10,20",output = ofile))
        mtime1 = os.stat(ofile).st_mtime
        self.assertNotEqual(mtime0,mtime1)
        self.assertEqual(outs[0],outs[1])
        os.remove(ofile)
        outs = []
 
        # dedicated output, force = false
        ofile = 'test_force_false'
        outs.append(cdo.stdatm("0,10,20",output = ofile,force=False))
        mtime0 = os.stat(outs[0]).st_mtime
        outs.append(cdo.stdatm("0,10,20",output = ofile,force=False))
        mtime1 = os.stat(outs[1]).st_mtime
        self.assertEqual(mtime0,mtime1)
        self.assertEqual(outs[0],outs[1])
        os.remove(ofile)
        outs = []

        # dedicated output, global force setting
        ofile = 'test_force_global'
        cdo.forceOutput = False
        outs.append(cdo.stdatm("0,10,20",output = ofile))
        mtime0 = os.stat(outs[0]).st_mtime
        outs.append(cdo.stdatm("0,10,20",output = ofile))
        mtime1 = os.stat(outs[1]).st_mtime
        self.assertEqual(mtime0,mtime1)
        self.assertEqual(outs[0],outs[1])
        os.remove(ofile)
        outs = []

    def test_combine(self):
        cdo = Cdo()
        cdo.debug = True
        stdatm  = cdo.stdatm("0",options = "-f nc")
        stdatm_ = cdo.stdatm("0",options = "-f nc")
        print(cdo.diff(input=stdatm + " " + stdatm_))
        sum = cdo.fldsum(input = stdatm)
        sum = cdo.fldsum(input = cdo.stdatm("0",options="-f nc"),returnCdf=True)
        self.assertEqual(288.0,sum.variables["T"][:])

    def test_cdf(self):
        cdo = Cdo()
        self.assertNotIn("cdf",cdo.__dict__)
        cdo.setReturnArray()
        self.assertIn("cdf",cdo.__dict__)
        cdo.setReturnArray(False)
        sum = cdo.fldsum(input = cdo.stdatm("0",options="-f nc"),returnCdf=True)
        self.assertEqual(1013.25,sum.variables["P"][:])
        cdo.unsetReturnArray()

    def test_cdf_mod(self):
        cdo =Cdo()
        cdo.setReturnArray()
        print('cdo.cdfMod:' + cdo.cdfMod)
        self.assertEqual(cdo.cdfMod,"scipy")
    def test_thickness(self):
        cdo = Cdo()
        levels            = "25 100 250 500 875 1400 2100 3000 4000 5000".split(' ')
        targetThicknesses = [50.0,  100.0,  200.0,  300.0,  450.0,  600.0,  800.0, 1000.0, 1000.0, 1000.0]
        self.assertEqual(targetThicknesses, cdo.thicknessOfLevels(input = "-selname,T -stdatm,"+ ','.join(levels)))

    def test_showlevels(self):
        cdo = Cdo()
        sourceLevels = "25 100 250 500 875 1400 2100 3000 4000 5000".split()
        self.assertEqual(' '.join(sourceLevels), 
                        cdo.showlevel(input = "-selname,T " + cdo.stdatm(','.join(sourceLevels),options = "-f nc"))[0]) 

    def test_verticalLevels(self):
        cdo = Cdo()
        # check, if a given input files has vertival layers of a given thickness array
        targetThicknesses = [50.0,  100.0,  200.0,  300.0,  450.0,  600.0,  800.0, 1000.0, 1000.0, 1000.0]
        sourceLevels = "25 100 250 500 875 1400 2100 3000 4000 5000".split()
        thicknesses = cdo.thicknessOfLevels(input = "-selname,T " + cdo.stdatm(','.join(sourceLevels),options = "-f nc")) 
        self.assertEqual(targetThicknesses,thicknesses)


    def test_returnArray(self):
        cdo = Cdo()
        temperature = cdo.stdatm(0,options = '-f nc', returnCdf = True).variables['T'][:]
        self.assertEqual(False, cdo.stdatm(0,options = '-f nc',returnArray = 'TT'))
        temperature = cdo.stdatm(0,options = '-f nc',returnArray = 'T')
        self.assertEqual(288.0,temperature.flatten()[0])
        pressure = cdo.stdatm("0,1000",options = '-f nc -b F64',returnArray = 'P')
        self.assertEqual("[ 1013.25         898.54345604]",pressure.flatten().__str__())

    if 'thingol' == os.popen('hostname').read().strip():
        def testCall(self):
            cdo = Cdo()
            print cdo.sinfov(input='/home/ram/data/icon/oce.nc')
        def test_readCdf(self):
            cdo = Cdo()
            input= "-settunits,days  -setyear,2000 -for,1,4"
            cdfFile = cdo.copy(options="-f nc",input=input)
            cdf     = cdo.readCdf(cdfFile)
            self.assertEqual(['lat','lon','for','time'],cdf.variables.keys())

        def testTmp(self):
            cdo = Cdo()
            import glob
            tempfilesStart = glob.glob('/tmp/cdoPy*')
            tempfilesStart.sort()
            tempfilesEnd   = glob.glob('/tmp/cdoPy**')
            tempfilesEnd.sort()
            self.assertEqual(tempfilesStart,tempfilesEnd)

            self.test_combine()
            tempfilesEnd = glob.glob('/tmp/cdoPy**')
            tempfilesEnd.sort()
            self.assertEqual(tempfilesStart,tempfilesEnd)
        def test_readArray(self):
            cdo = Cdo()
            ifile = '/home/ram/data/examples/EH5_AMIP_1_TSURF_1991-1995.nc'
            self.assertEqual((10, 96, 192),
                cdo.readArray(cdo.seltimestep('1/10',
                  input=ifile),
                  'tsurf').shape)

        def test_error(self):
            cdo = Cdo()
            print cdo.stdatm(0,10,input="",output="")

if __name__ == '__main__':
    unittest.main()

# vim:sw=2
