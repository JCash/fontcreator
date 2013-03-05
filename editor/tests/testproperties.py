
import sys, os, unittest, traceback

sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

from properties.propertyclass import property_class
from properties.propertytypes import PropertyValidateError, Property, IntProperty, StringProperty


def assertRaises(testcase, exc, instance, name, value):
    try:
        setattr(instance, name, value)
        print getattr(instance, name)
    except exc:
        return
    except Exception:
        traceback.print_exc()
    testcase.fail('Test did not raise ' + str(exc))


class Test(unittest.TestCase):

    def test_property(self):
        self.assertRaises(AssertionError, Property)

        # Make sure it doesn't assert
        p = Property(default='', name='foo')

        self.assertRaises(PropertyValidateError, p.validate, '')

    def test_propertyclass(self):
        @property_class()
        class TestObject(object):
            test_int = IntProperty(0)

            def validateTestInt(self, value):
                if value == 20:
                    raise PropertyValidateError('foo')

        o1 = TestObject()
        o2 = TestObject()

        self.assertEqual(0, o1.test_int)
        self.assertEqual(0, o2.test_int)

        o1.test_int = 7
        o2.test_int = 6

        self.assertEqual(7, o1.test_int)
        self.assertEqual(6, o2.test_int)

        # test range [0,100]
        self.assertRaises(PropertyValidateError, o1.validate, 'test_int', 170)
        # test custom validate func
        self.assertRaises(PropertyValidateError, o2.validate, 'test_int', 20)

    def test_numeric_property(self):

        @property_class()
        class TestObject(object):
            test_int = IntProperty(0)

        o = TestObject()

        self.assertEqual(0, o.test_int)

        o.test_int = 7
        self.assertEqual(7, o.test_int)

        assertRaises(self, PropertyValidateError, o, 'test_int', 200)
        assertRaises(self, PropertyValidateError, o, 'test_int', -1)

        o2 = TestObject()
        self.assertEqual(7, o.test_int)
        self.assertEqual(0, o2.test_int)

    def test_string_property(self):

        @property_class()
        class TestObject(object):
            test_str = StringProperty('Hello World!')

        o = TestObject()

        self.assertEqual('Hello World!', o.test_str)

        o.test_str = 'foobar'
        self.assertEqual('foobar', o.test_str)

        #assertRaises(self, PropertyValidateError, o, 'test_int', 200)
        #assertRaises(self, PropertyValidateError, o, 'test_int', -1)

        o2 = TestObject()
        self.assertEqual('foobar', o.test_str)
        self.assertEqual('Hello World!', o2.test_str)

    def test_iteritems(self):

        @property_class()
        class TestObject(object):
            int0 = IntProperty(0)
            int1 = IntProperty(1)
            int2 = IntProperty(2)
            int3 = IntProperty(3)

        expectedkeys = [ 'int%d' % i for i in range(4)]
        expectedvalues = range(4)

        o = TestObject()

        result = [ (name, value) for name, value in o.iteritems() ]

        self.assertEqual( zip(expectedkeys, expectedvalues), sorted(result) )

        result = [ name for name in o.iterkeys() ]
        self.assertEqual( expectedkeys, sorted(result) )

        result = [ (name, value) for name, value in o ]
        self.assertEqual( zip(expectedkeys, expectedvalues), sorted(result) )

        self.assertTrue( 'int1' in o )
        self.assertTrue( 'int3' in o )
        self.assertFalse( 'int4' in o )

        self.assertEqual( 4, len(o) )

    def test_inheritance(self):
        # tests basic inheritance between objects

        @property_class()
        class TestObjectA(object):
            int0 = IntProperty(0)
            int1 = IntProperty(1)

        @property_class()
        class TestObjectB(TestObjectA):
            int1 = IntProperty(2)
            int2 = IntProperty(3)

        o = TestObjectB()

        result = [ (name, value) for name, value in o.iteritems() ]

        self.assertEqual( 3, len(result) )
        self.assertEqual( 0, o.int0 )
        self.assertEqual( 2, o.int1 )
        self.assertEqual( 3, o.int2 )

    def test_inheritance_set_get_validate(self):
        # tests inheritance, the functionality of the set, get and validate functions
        """
        A   a   b   c
        B       b   c   d
        C           c
        """

        @property_class()
        class TestObjectA(object):
            int0 = IntProperty(0)
            int1 = IntProperty(1)
            int2 = IntProperty(2)

            # to be tested by c
            int_c_a = IntProperty(0xca)
            int_c_b = IntProperty(0xcb)
            int_c_c = IntProperty(0xcc)

            def setInt0(self, value):
                self._int0 = value*2

            def setInt1(self, value):
                self._int1 = value*2

            def setInt2(self, value):
                self._int2 = value*2

        @property_class()
        class TestObjectB(TestObjectA):
            int2 = IntProperty(3)
            int3 = IntProperty(4)
            int3 = IntProperty(4)

            # to be tested by c
            int_c_b = IntProperty(0xcb0)
            int_c_c = IntProperty(0xcc0)
            int_c_d = IntProperty(0xcd0)

            # Override a value that isn't in this class
            def setInt1(self, value):
                self._int1 = value*3

            def setInt2(self, value):
                self._int2 = value*3

        @property_class()
        class TestObjectC(TestObjectB):
            int2 = IntProperty(3)
            int3 = IntProperty(4)

            # to be tested by c
            int_c_c = IntProperty(0xcc00)

            # Override a value that isn't in this class
            def setInt1(self, value):
                self._int1 = value*3

            def setInt2(self, value):
                self._int2 = value*3

        o = TestObjectB()

        self.assertEqual( 0, o.int0 )
        self.assertEqual( 1, o.int1 )
        self.assertEqual( 3, o.int2 )
        self.assertEqual( 4, o.int3 )

        o.int0 = 10
        o.int1 = 20
        o.int2 = 30
        o.int3 = 40

        self.assertEqual( 20, o.int0 )
        self.assertEqual( 60, o.int1 )
        self.assertEqual( 90, o.int2 )
        self.assertEqual( 40, o.int3 )

        """
        for n,v in o.iteritems():
            print n, v

        import jsonpickle
        s = jsonpickle.encode(o)

        print s

        oo = jsonpickle.decode(s)

        for n,v in oo.iteritems():
            print n, v

        """

        """

        import cStringIO as StringIO
        import pickle
        #s = pickle.dumps(o)

        f = StringIO.StringIO()
        pickler = pickle.Pickler(f)
        pickler.dump(o)

        s = f.getvalue()
        print s
        """


if __name__ == '__main__':
    unittest.main()
