#!/usr/bin/python
# -*- coding: utf-8 -*-
from unittest import TestCase

import compliancelib
import os
import json
import yaml

from compliancelib import SystemCompliance

class SystemComplianceTest(TestCase):
    
    def test(self):
        self.assertTrue(True)

    def test_load_ocfile(self):
        "Test loading of an OpenControl component YAML file"
        ocfileurl = "https://raw.githubusercontent.com/pburkholder/freedonia-compliance/master/AU_policy/component.yaml"
        sp = SystemCompliance()
        # test empty oc
        self.assertTrue(len(sp.ocfiles) == 0)
        # load an OpenControl file
        sp.load_ocfile_from_url(ocfileurl)
        print len(sp.ocfiles)
        print list(sp.ocfiles.keys())
        #  test length of ocfiles
        self.assertTrue(len(sp.ocfiles) == 1)
        # self.assertTrue(sp.list_files() == "https://github.com/pburkholder/freedonia-compliance/blob/master/AU_policy/component.yaml")
        # test not loading same file twice
        sp.load_ocfile_from_url(ocfileurl)
        self.assertTrue(len(sp.ocfiles) == 1)
        # load second file
        ocfileurl2 = 'https://raw.githubusercontent.com/opencontrol/cf-compliance/master/UAA/component.yaml'
        sp.load_ocfile_from_url(ocfileurl2)
        self.assertTrue(len(sp.ocfiles) == 2)
        self.assertTrue(sp.ocfiles.keys() == ['https://raw.githubusercontent.com/opencontrol/cf-compliance/master/UAA/component.yaml', 'https://raw.githubusercontent.com/pburkholder/freedonia-compliance/master/AU_policy/component.yaml'])

    def test_create_system_dictionary(self):
        "Test system dictionary created"
        sp = SystemCompliance()
        # test empty oc
        self.assertTrue(len(sp.ocfiles) == 0)
        # test necessary dictionaries created
        self.assertTrue(sp.system is not None)
        self.assertTrue(sp.system['components'] is not None)

        # test that empty system object exists
        self.assertTrue(sp.system['name'] == "Test System")

    def test_add_component_from_url(self):
        "Test method 'add_component_from_url'"
        sp = SystemCompliance()
        ocfileurl = 'https://raw.githubusercontent.com/pburkholder/freedonia-compliance/master/AU_policy/component.yaml'
        sp.add_component_from_url(ocfileurl)
        print sp.components()
        self.assertTrue(sp.components() == ['Audit Policy'])

    def test_components(self):
        "Test system component dictionary"
        sp = SystemCompliance()
        # test necessary dictionaries created
        self.assertTrue(sp.system is not None)

        # test adding in components
        oc_component_file = os.path.join(os.path.dirname(__file__), '../data/UAA_component.yaml')
        print oc_component_file
        ocfileurl = "file://%s" % oc_component_file
        sp.load_ocfile_from_url(ocfileurl)

        test_component_dict = sp.ocfiles[ocfileurl]
        sp.system_component_add(test_component_dict['name'], test_component_dict)
        print "system components are %s " % sp.system['components'].keys()
        print len(sp.system['components']['User Account and Authentication (UAA) Server']['satisfies'])
        self.assertTrue(sp.system['components'].keys()[0] == "User Account and Authentication (UAA) Server")
        self.assertTrue(len(sp.system['components']['User Account and Authentication (UAA) Server']['satisfies']) == 26)

        # add second component file and test list of components
        oc_component_file = os.path.join(os.path.dirname(__file__), '../data/AU_policy_component.yaml')
        print oc_component_file
        ocfileurl = "file://%s" % oc_component_file
        sp.load_ocfile_from_url(ocfileurl)
        # this is where we add the component dictionary
        sp.system_component_add(sp.ocfiles[ocfileurl]['name'], sp.ocfiles[ocfileurl])

        # test method to get list of system components
        print sp.components()
        self.assertTrue(sp.components() == ['Audit Policy', 'User Account and Authentication (UAA) Server'])
        self.assertFalse(sp.components() == ['User Account and Authentication (UAA) Server', 'Wrong Name'])
        # self.assertTrue(0==1)

    def test_standards(self):
        "Test system standards dictionary"
        sp = SystemCompliance()
        # testing adding a standard
        standard_name = "FRIST-800-53"
        standard_dict = {"name": "FRIST-800-53", "other_key": "some value"}
        sp.add_system_dict('standards', standard_name, standard_dict)
        self.assertTrue(sp.standards() == ["FRIST-800-53"])
        # To do test for exception case of non-existent dictionary type

    def test_certifications(self):
        "Test system certifications dictionary"
        sp = SystemCompliance()
        # testing adding a certification
        name = "FRed-RAMP-Low"
        my_dict = {"name": "FRed-RAMP-Low", "other_key": "some value"}
        sp.add_system_dict('certifications', name, my_dict)
        self.assertTrue(sp.certifications() == ["FRed-RAMP-Low"])
        # To do test for exception case of non-existent dictionary type 

    def test_roles(self):
        "Test system roles dictionary"
        sp = SystemCompliance()
        # testing adding a role
        name = "SOME VALUE"
        my_dict = {"name": "SOME VALUE", "other_key": "some value"}
        sp.add_system_dict('roles', name, my_dict)
        self.assertTrue(sp.roles() == ["SOME VALUE"])
        # To do test for exception case of non-existent dictionary type

    def test_summary(self):
        "Test outputting basic system compliance profile"
        sp = SystemCompliance()
        # set system name
        sp.system['name'] = "GovReady WordPress Dashboard"
        # add system components
        my_components = ['../data/UAA_component.yaml', '../data/AU_policy_component.yaml']
        [sp.add_component_from_url("file://%s" % os.path.join(os.path.dirname(__file__), ocfileurl)) for ocfileurl in my_components]
        
        # add system standard
        standard_name = "FRIST-800-53"
        standard_dict = {"name": "FRIST-800-53", "other_key": "some value"}
        sp.add_system_dict('standards', standard_name, standard_dict)

        # add system certifications
        name = "FRed-RAMP-Low"
        my_dict = {"name": "FRed-RAMP-Low", "other_key": "some value"}
        sp.add_system_dict('certifications', name, my_dict)

        # Test system compliance profile
        print "System compliance summary %s" % sp.summary()
        self.assertTrue(sp.summary() == {'stanards': ['FRIST-800-53'], 'certifications': ['FRed-RAMP-Low'], 'name': 'GovReady WordPress Dashboard', 'components': ['Audit Policy', 'User Account and Authentication (UAA) Server']})

    def test_control(self):
        "Test the control implementation object"
        # We assume just NIST 800-53 controls for time being
        sp = SystemCompliance()
        # set system name
        sp.system['name'] = "GovReady WordPress Dashboard"
        # add system components
        my_components = ['../data/UAA_component.yaml', '../data/AU_policy_component.yaml']
        [sp.add_component_from_url("file://%s" % os.path.join(os.path.dirname(__file__), ocfileurl)) for ocfileurl in my_components]
        # add system standard
        standard_name = "FRIST-800-53"
        standard_dict = {"name": "FRIST-800-53", "other_key": "some value"}
        sp.add_system_dict('standards', standard_name, standard_dict)
        # add system certifications
        name = "FRed-RAMP-Low"
        my_dict = {"name": "FRed-RAMP-Low", "other_key": "some value"}
        sp.add_system_dict('certifications', name, my_dict)

        #
        # System instantiated, let's test displaying control information
        #

        # report when a control is not found
        ck = "AC-200" # no such control
        ci = sp.control(ck)
        print "%s info is %s " % (ck, ci.title)
        print "\n"

        # report when a control is  found
        ck = "AC-4"
        ci = sp.control(ck)
        print ci.id
        print ci.title
        print ci.description
        print "\nSystem control implmentation details"
        print "-------------------------------------"
        print ci.components
        print ci.narrative

        # test control enhancement id
        ck = "AC-2 (1)"
        ci = sp.control(ck)
        print ci.id
        print ci.title
        print ci.description
        print "\nSystem control implmentation details"
        print "-------------------------------------"
        print ci.components
        print ci.narrative

        self.assertTrue( 0 == 1 )

if __name__ == "__main__":
    unittest.main()