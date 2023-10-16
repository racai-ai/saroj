# Example __init__.py file for a unit testing package

# Import necessary modules for unit testing
import unittest
from .test_entityMapping_process import TestReadReplacementDictionary
from .test_entityMapping_process import TestUpdateMappingFile
from .test_entityMapping_process import TestProcessEntityInstI


from entityMapping_process import *

from WebServiceModules.EntityMapping.entityMapping_process import *

# Create a test suite that includes all test cases
test_suite = unittest.TestSuite()



# Define the package's public API
__all__ = ['test_suite']

# This code will run when the package is imported for testing
print("Initializing test_package")
# WebServiceModules/EntityMapping
# WebServiceModules/EntityMapping/tests
# WebServiceModules/EntityMapping/tests/__init__.py
# WebServiceModules/EntityMapping/tests/test_entityMapping_process.py
# WebServiceModules/EntityMapping/__init__.py
# WebServiceModules/EntityMapping/dictionar.txt
# WebServiceModules/EntityMapping/entityMapping_api.py
# WebServiceModules/EntityMapping/entityMapping_process.py