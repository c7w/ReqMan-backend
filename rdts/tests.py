import imp
from django.test import TestCase
from rms.models import *
from ums.models import *
from ums.tests import *
from rms.tests import *

class RDTS_Tests(TestCase):
    def setUp(self):
        self.rms=RMS_Tests()
        self.rms.setUp()
        
