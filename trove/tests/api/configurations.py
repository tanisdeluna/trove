# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Rackspace
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import json
from datetime import datetime
from proboscis import SkipTest
from proboscis import test
from proboscis import before_class
from proboscis.asserts import *
from proboscis.decorators import time_out
from trove.tests.api.instances import assert_unprocessable
from trove.tests.api.instances import InstanceTestInfo
from trove.tests.api.instances import instance_info
from trove.tests.api.instances import WaitForGuestInstallationToFinish
from trove.tests.config import CONFIG
from trove.tests.util import create_dbaas_client
from trove.tests.util import poll_until
from trove.tests.util import test_config
from trove.tests.util.check import AttrCheck
from trove.tests.util.mysql import create_mysql_connection
from trove.tests.util.users import Requirements
from troveclient.compat import exceptions


GROUP = "dbaas.api.configurations"
CONFIG_NAME = "test_configuration"
CONFIG_DESC = "configuration description"

configuration_info = None
configuration_href = None
configuration_instance = InstanceTestInfo()
configuration_instance_id = None
sql_variables = [
    'key_buffer_size',
    'connect_timeout',
    'join_buffer_size',
]
parameters_booleans = [
    'innodb_file_per_table',
    'autocommit',
    'local_infile'
]
parameters_integers = [
    'key_buffer_size',
    'join_buffer_size',
    'sort_buffer_size',
    'innodb_buffer_pool_size',
    'innodb_flush_log_at_trx_commit',
    'innodb_log_buffer_size',
    'innodb_log_file_size',
    'innodb_open_files',
    'innodb_thread_concurrency',
    'sync_binlog',
    'auto_increment_increment',
    'auto_increment_offset',
    'bulk_insert_buffer_size',
    'expire_logs_days',
    'ft_min_word_len',
    'connect_timeout',
    'interactive_timeout',
    'max_allowed_packet',
    'max_connect_errors',
    'max_connections',
    'max_heap_table_size',
    'tmp_table_size',
    'myisam_sort_buffer_size',
    'thread_cache_size',
    'query_cache_size',
    'table_open_cache',
    'table_definition_cache',
    'open_files_limit',
    'max_user_connections',
    'server_id',
    'wait_timeout'
]
parameters_strings =[
    'character_set_client',
    'character_set_connection',
    'character_set_database',
    'character_set_filesystem',
    'character_set_results',
    'character_set_server',
    'collation_connection',
    'collation_database',
    'collation_server',
    'ft_stopword_file',
    'default_time_zone'
]
parameters_all = parameters_booleans + parameters_integers + parameters_strings
parameters_non_dynamic_booleans = ['local_infile', 'innodb_file_per_table']
parameters_non_dynamic_integers = [
    'innodb_buffer_pool_size',
    'innodb_log_buffer_size',
    'innodb_log_file_size',
    'innodb_open_files',
    'ft_min_word_len',
    'open_files_limit',
    'server_id'
]
parameters_non_dynamic_strings = ['ft_stopword_file']
parameters_non_dynamic_all = parameters_non_dynamic_booleans + \
    parameters_non_dynamic_integers + parameters_non_dynamic_strings
parameters_dynamic_all = [x for x in parameters_all if x not in parameters_non_dynamic_all]
parameters_file = json.loads('{ "configuration-parameters": [ { "name": "innodb_file_per_table", "dynamic": false, "max": 1, "min": 0, "type": "boolean" }, { "name": "autocommit", "dynamic": true, "max": 1, "min": 0, "type": "boolean" }, { "name": "local_infile", "dynamic": true, "max": 1, "min": 0, "type": "boolean" }, { "name": "key_buffer_size", "dynamic": true, "max": 4294967296, "min": 0, "type": "integer" }, { "name": "connect_timeout", "dynamic": true, "max": 65535, "min": 1, "type": "integer" }, { "name": "join_buffer_size", "dynamic": true, "max": 4294967296, "min": 0, "type": "integer" }, { "name": "sort_buffer_size", "dynamic": true, "max": 18446744073709547520, "min": 32768, "type": "integer" }, { "name": "innodb_buffer_pool_size", "dynamic": false, "max": 68719476736, "min": 0, "type": "integer" }, { "name": "innodb_flush_log_at_trx_commit", "dynamic": true, "max": 2, "min": 0, "type": "integer" }, { "name": "innodb_log_buffer_size", "dynamic": false, "max": 4294967296, "min": 1048576, "type": "integer" }, { "name": "innodb_open_files", "dynamic": false, "max": 4294967296, "min": 10, "type": "integer" }, { "name": "innodb_thread_concurrency", "dynamic": true, "max": 1000, "min": 0, "type": "integer" }, { "name": "sync_binlog", "dynamic": true, "max": 18446744073709547520, "min": 0, "type": "integer" }, { "name": "auto_increment_increment", "dynamic": true, "max": 65535, "min": 1, "type": "integer" }, { "name": "auto_increment_offset", "dynamic": true, "max": 65535, "min": 1, "type": "integer" }, { "name": "bulk_insert_buffer_size", "dynamic": true, "max": 18446744073709547520, "min": 0, "type": "integer" }, { "name": "expire_logs_days", "dynamic": true, "max": 65535, "min": 1, "type": "integer" }, { "name": "connect_timeout", "dynamic": true, "max": 65535, "min": 1, "type": "integer" }, { "name": "interactive_timeout", "dynamic": true, "max": 65535, "min": 1, "type": "integer" }, { "name": "max_allowed_packet", "dynamic": true, "max": 1073741824, "min": 1024, "type": "integer" }, { "name": "max_connect_errors", "dynamic": true, "max": 18446744073709547520, "min": 1, "type": "integer" }, { "name": "max_connections", "dynamic": true, "max": 65535, "min": 1, "type": "integer" }, { "name": "myisam_sort_buffer_size", "dynamic": true, "max": 18446744073709547520, "min": 4, "type": "integer" }, { "name": "max_user_connections", "dynamic": true, "max": 100000, "min": 1, "type": "integer" }, { "name": "server_id", "dynamic": false, "max": 100000, "min": 1, "type": "integer" }, { "name": "wait_timeout", "dynamic": true, "max": 31536000, "min": 1, "type": "integer" }, { "name": "character_set_client", "dynamic": true, "type": "string" }, { "name": "character_set_connection", "dynamic": true, "type": "string" }, { "name": "character_set_database", "dynamic": true, "type": "string" }, { "name": "character_set_filesystem", "dynamic": true, "type": "string" }, { "name": "character_set_results", "dynamic": true, "type": "string" }, { "name": "character_set_server", "dynamic": true, "type": "string" }, { "name": "collation_connection", "dynamic": true, "type": "string" }, { "name": "collation_database", "dynamic": true, "type": "string" }, { "name": "collation_server", "dynamic": true, "type": "string" } ] }')["configuration-parameters"]
#parameters_file["configuration-parameters"]

# helper methods to validate configuration is applied to instance
def _execute_query(host, user_name, password, query):
    with create_mysql_connection(host, user_name, password) as db:
        result = db.execute(query)
        return result
    assert_true(False, "something went wrong in the sql connection")


def _get_address(instance_id):
    result = instance_info.dbaas_admin.mgmt.instances.show(instance_id)
    return result.ip[0]


def _test_configuration_is_applied_to_instance(instance, configuration_id):
    instance_test = instance_info.dbaas.instances.get(instance.id)
    assert_equal(configuration_id, instance_test.configuration['id'])
    testconfig_info = instance_info.dbaas.configurations.get(configuration_id)
    config_instance_ids = [inst['id'] for inst in testconfig_info.instances]
    assert_true(instance_test.id in config_instance_ids)
    cfg_names = []
    for cfg in testconfig_info.values.iterkeys():
        cfg_names.append(cfg)

    host = _get_address(instance.id)
    for user in instance.users:
        username = user['name']
        password = user['password']
        concat_variables = "','".join(cfg_names)
        query = ("show variables where Variable_name "
                 "in ('%s');" % concat_variables)
        actual_values = _execute_query(host, username, password, query)
    print(actual_values)
    print(testconfig_info.values)
    assert_true(len(actual_values) == len(cfg_names))

    # check the configs exist
    attrcheck = AttrCheck()
    expected_attrs = [actual_key for actual_key, actual_value in actual_values]
    attrcheck.attrs_exist(testconfig_info.values, expected_attrs,
                          msg="Configurations parameters")

    # check the config values are correct
    for expected_key, expected_value in testconfig_info.values.iteritems():
        expected = (str(expected_key), str(expected_value))
        assert_true(expected in actual_values)


@test(depends_on_classes=[WaitForGuestInstallationToFinish], groups=[GROUP])
class CreateConfigurations(object):

    #todo(cp16net): this is a silly hack to get the session alive need to
    # take out the lazying loading of instances in the mapping of configuration
    @before_class
    def test_setup(self):
        results = instance_info.dbaas.instances.list()
        for instance in results:
            instance_info.dbaas.instances.get(instance.id)
        results = instance_info.dbaas.configurations.list()
        for cfg in results:
            instance_info.dbaas.configurations.get(cfg.id)

    @test
    def test_expected_configurations_parameters(self):
        """test get expected configurations parameters"""
        expected_attrs = ["configuration-parameters"]
        instance_info.dbaas.configurations_parameters.parameters()
        resp, body = instance_info.dbaas.client.last_response
        attrcheck = AttrCheck()
        config_parameters_dict = json.loads(body)
        attrcheck.attrs_exist(config_parameters_dict, expected_attrs,
                              msg="Configurations parameters")
        # sanity check that a few options are in the list
        config_params_list = config_parameters_dict['configuration-parameters']
        config_params_keys = []
        for param in config_params_list:
            config_params_keys.append(param['name'])
        expected_config_params = ['key_buffer_size', 'connect_timeout']
        for expected_config_item in expected_config_params:
            assert_true(expected_config_item in config_params_keys)

    #qe: modified by adding parameters_all
    @test
    def test_expected_configurations_parameters_all(self):
        """test get expected configurations parameters, all"""
        expected_attrs = ["configuration-parameters"]
        instance_info.dbaas.configurations_parameters.parameters()
        resp, body = instance_info.dbaas.client.last_response
        attrcheck = AttrCheck()
        config_parameters_dict = json.loads(body)
        attrcheck.attrs_exist(config_parameters_dict, expected_attrs,
                              msg="Configurations parameters")
        #go beyond the sanity check. check all parameters, hardcoded above
        config_params_list = config_parameters_dict['configuration-parameters']
        config_params_keys = []
        for param in config_params_list:
            config_params_keys.append(param['name'])
        #expected_config_params = ['key_buffer_size', 'connect_timeout']
        #the only real change here is replacing the previous with the following
        expected_config_params = parameters_all
        for expected_config_item in expected_config_params:
            assert_true(expected_config_item in config_params_keys)

    @test
    def test_expected_get_configuration_parameter(self):
        # tests get on a single parameter to verify it has expected attributes
        param = 'key_buffer_size'
        expected_config_params = ['name', 'dynamic', 'max', 'min', 'type']
        instance_info.dbaas.configurations_parameters.get_parameter(param)
        resp, body = instance_info.dbaas.client.last_response
        print(resp)
        print(body)
        attrcheck = AttrCheck()
        config_parameter_dict = json.loads(body)
        print(config_parameter_dict)
        attrcheck.attrs_exist(config_parameter_dict, expected_config_params,
                              msg="Get Configuration parameter")
        assert_equal(param, config_parameter_dict['name'])

    #qe
    @test
    def test_expected_get_configuration_parameter_integers(self):
        # tests GET configurations/parameters on many parameters to verify it
        # has expected attributes
        for param in parameters_integers:
            #param = 'key_buffer_size'
            expected_config_params = ['name', 'dynamic', 'max', 'min', 'type']
            instance_info.dbaas.configurations_parameters.get_parameter(param)
            resp, body = instance_info.dbaas.client.last_response
            print(resp)
            print(body)
            config_parameter_dict = json.loads(body)
            print(config_parameter_dict)
            attrcheck = AttrCheck()
            attrcheck.attrs_exist(config_parameter_dict,
                expected_config_params,
                msg="Get Configuration parameter")
            assert_equal(param, config_parameter_dict['name'])
            assert_equal('integer', config_parameter_dict['type'])

    #qe
    @test
    def test_expected_get_configuration_parameter_strings(self):
        # tests GET configurations/parameters on many parameters to verify it
        # has expected attributes
        for param in parameters_strings:
            #param = 'key_buffer_size'
            expected_config_params = ['name', 'dynamic', 'type']
            instance_info.dbaas.configurations_parameters.get_parameter(param)
            resp, body = instance_info.dbaas.client.last_response
            print(resp)
            print(body)
            config_parameter_dict = json.loads(body)
            print(config_parameter_dict)
            attrcheck = AttrCheck()
            attrcheck.attrs_exist(config_parameter_dict,
                expected_config_params,
                msg="Get Configuration parameter")
            assert_equal(param, config_parameter_dict['name'])
            assert_equal('string', config_parameter_dict['type'])

    # #qe
    # @test
    # def test_expected_get_configuration_parameter_booleans(self):
    #     # tests GET configurations/parameters on many parameters to verify it
    #     # has expected attributes
    #     for param in parameters_booleans:
    #         #param = 'key_buffer_size'
    #         expected_config_params = ['name', 'dynamic', 'type']
    #         instance_info.dbaas.configurations_parameters.get_parameter(param)
    #         resp, body = instance_info.dbaas.client.last_response
    #         print(resp)
    #         print(body)
    #         config_parameter_dict = json.loads(body)
    #         print(config_parameter_dict)
    #         attrcheck = AttrCheck()
    #         attrcheck.attrs_exist(config_parameter_dict,
    #             expected_config_params,
    #             msg="Get Configuration parameter")
    #         assert_equal(param, config_parameter_dict['name'])
    #         assert_equal('boolean', config_parameter_dict['type'])

    #qe
    @test
    def test_configurations_create_name_too_long(self):
        """test create configuration with name too long"""
        values = '{"connect_timeout": 120, "key_buffer_size": 52428800}'
        assert_unprocessable(instance_info.dbaas.configurations.create,
            "A" * 1024, values, CONFIG_DESC)

    #qe
    @test
    def test_configurations_create_description_too_long(self):
        """test create configuration with description too long"""
        values = '{"connect_timeout": 120, "key_buffer_size": 52428800}'
        assert_unprocessable(instance_info.dbaas.configurations.create,
            CONFIG_NAME, values, "A" * 1024)

    #qe
    @test
    def test_configurations_create_key_value_pairs_too_long(self):
        """test create configuration with key-value pairs too long"""
        values = '{"connect_timeout": 120, "key_buffer_size": 52428800}' * 1024
        assert_unprocessable(instance_info.dbaas.configurations.create,
            CONFIG_NAME, values, CONFIG_DESC)

    @test
    def test_configurations_create_invalid_values(self):
        """test create configurations with invalid values"""
        values = '{"this_is_invalid": 123}'
        assert_unprocessable(instance_info.dbaas.configurations.create,
                             CONFIG_NAME, values, CONFIG_DESC)

    @test
    def test_configurations_create_invalid_value_type(self):
        """test create configuration with invalild value type"""
        values = '{"key_buffer_size": "this is a string not int"}'
        assert_unprocessable(instance_info.dbaas.configurations.create,
                             CONFIG_NAME, values, CONFIG_DESC)

    @test
    def test_configurations_create_value_out_of_bounds(self):
        """test create configuration with value out of bounds"""
        values = '{"connect_timeout": 1000000}'
        assert_unprocessable(instance_info.dbaas.configurations.create,
                             CONFIG_NAME, values, CONFIG_DESC)
        values = '{"connect_timeout": -10}'
        assert_unprocessable(instance_info.dbaas.configurations.create,
                             CONFIG_NAME, values, CONFIG_DESC)

    #qe
    # ??????????????
    @test
    def test_configurations_create_value_out_of_bounds_many(self):
        """test create configuration with value out of bounds"""
        #this becomes a list of dictionaries, where each dictionary is:
        #   name:, min:, max:
        #the string dictionaries ask: null permissiable?
        #booleans do not have out of bounds, but should be tested as invalid 
        #types.
        values = '{"connect_timeout": 1000000}'
        assert_unprocessable(instance_info.dbaas.configurations.create,
            CONFIG_NAME, values, CONFIG_DESC)
        values = '{"connect_timeout": -10}'
        assert_unprocessable(instance_info.dbaas.configurations.create,
            CONFIG_NAME, values, CONFIG_DESC)

    @test
    def test_valid_configurations_create(self):
        # create a configuration with valid parameters
        values = '{"connect_timeout": 120, "key_buffer_size": 52428800}'
        expected_values = json.loads(values)
        result = instance_info.dbaas.configurations.create(CONFIG_NAME,
                                                           values,
                                                           CONFIG_DESC)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 200)
        global configuration_info
        configuration_info = result
        assert_equal(configuration_info.name, CONFIG_NAME)
        assert_equal(configuration_info.description, CONFIG_DESC)
        assert_equal(configuration_info.values, expected_values)

    @test(runs_after=[test_valid_configurations_create])
    def test_appending_to_existing_configuration(self):
        # test being able to update and insert new parameter name and values
        # to an existing configuration
        values = '{"join_buffer_size": 1048576, "connect_timeout": 60}'
        instance_info.dbaas.configurations.edit(configuration_info.id,
                                                values)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 200)


@test(depends_on=[CreateConfigurations], groups=[GROUP])
class AfterConfigurationsCreation(object):

    @test
    def test_assign_configuration_to_invalid_instance(self):
        # test assigning to an instance that does not exist
        invalid_id = "invalid-inst-id"
        try:
            instance_info.dbaas.instances.modify(invalid_id,
                                                 configuration_info.id)
        except exceptions.NotFound:
            resp, body = instance_info.dbaas.client.last_response
            assert_equal(resp.status, 404)

    @test
    def test_assign_configuration_to_valid_instance(self):
        # test assigning a configuration to an instance
        print("instance_info.id: %s" % instance_info.id)
        print("configuration_info: %s" % configuration_info)
        print("configuration_info.id: %s" % configuration_info.id)
        config_id = configuration_info.id
        instance_info.dbaas.instances.modify(instance_info.id,
                                             configuration_ref=config_id)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 202)

    @test(depends_on=[test_assign_configuration_to_valid_instance])
    @time_out(10)
    def test_get_configuration_details_from_instance_validation(self):
        # validate that the configuraiton was applied correctly to the instance
        if CONFIG.fake_mode:
            raise SkipTest("configuration from sql does not work in fake mode")
        inst = instance_info.dbaas.instances.get(instance_info.id)
        configuration_id = inst.configuration['id']
        _test_configuration_is_applied_to_instance(instance_info,
                                                   configuration_id)


@test(depends_on=[AfterConfigurationsCreation], groups=[GROUP])
class ListConfigurations(object):

    @test
    def test_configurations_list(self):
        # test listing configurations show up
        result = instance_info.dbaas.configurations.list()
        exists = [config for config in result if
                  config.id == configuration_info.id]
        assert_equal(1, len(exists))
        configuration = exists[0]
        assert_equal(configuration.id, configuration_info.id)
        assert_equal(configuration.name, configuration_info.name)
        assert_equal(configuration.description, configuration_info.description)

    @test
    def test_configurations_list_for_instance(self):
        # test getting an instance shows the configuration assigned shows up
        instance = instance_info.dbaas.instances.get(instance_info.id)
        assert_equal(instance.configuration['id'], configuration_info.id)
        assert_equal(instance.configuration['name'], configuration_info.name)
        # expecting two things in links, href and bookmark
        assert_equal(2, len(instance.configuration['links']))
        link = instance.configuration['links'][0]
        global configuration_href
        configuration_href = link['href']

    @test
    def test_configurations_get(self):
        # test that the instance shows up on the assigned configuration
        result = instance_info.dbaas.configurations.get(configuration_info.id)
        assert_equal(configuration_info.id, result.id)
        assert_equal(configuration_info.name, result.name)
        assert_equal(configuration_info.description, result.description)
        conf_instances = result.instances
        # this is for debuging
        print(conf_instances)
        print(conf_instances[0])
        print(conf_instances[0]['id'])
        print(conf_instances[0]['name'])
        assert_equal(conf_instances[0]['id'], instance_info.id)
        assert_equal(conf_instances[0]['name'], instance_info.name)

        # Test to make sure that another user is not able to GET this config
        reqs = Requirements(is_admin=False)
        test_auth_user = instance_info.user.auth_user
        other_user = CONFIG.users.find_user(reqs, black_list=[test_auth_user])
        other_user_tenant_id = other_user.tenant_id
        client_tenant_id = instance_info.user.tenant_id
        if other_user_tenant_id == client_tenant_id:
            other_user = CONFIG.users.find_user(reqs,
                                                black_list=[
                                                instance_info.user.auth_user,
                                                other_user])
        print(other_user)
        print(other_user.__dict__)
        other_client = create_dbaas_client(other_user)
        assert_raises(exceptions.NotFound, other_client.configurations.get,
                      configuration_info.id)

    @test
    def test_get_default_configuration_on_instance(self):
        # test the api call to get the default template of an instance exists
        result = instance_info.dbaas.instances.configuration(instance_info.id)
        assert_not_equal(None, result.configuration)

    @test
    def test_changing_configuration_with_nondynamic_parameter(self):
        # test that changing a non-dynamic parameter is applied to instance
        # and show that the instance requires a restart
        values = ('{"join_buffer_size": 1048576, '
                  '"innodb_buffer_pool_size": 57671680}')
        instance_info.dbaas.configurations.update(configuration_info.id,
                                                  values)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 202)

        instance_info.dbaas.configurations.get(configuration_info.id)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 200)

        def result_is_not_active():
            instance = instance_info.dbaas.instances.get(
                instance_info.id)
            if instance.status == "ACTIVE":
                return False
            else:
                return True
        poll_until(result_is_not_active)

        instance = instance_info.dbaas.instances.get(instance_info.id)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 200)
        print(instance.status)
        assert_equal('RESTART_REQUIRED', instance.status)

    @test(depends_on=[test_changing_configuration_with_nondynamic_parameter])
    def test_restart_service_should_return_active(self):
        # test that after restarting the instance it becomes active
        instance_info.dbaas.instances.restart(instance_info.id)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 202)

        def result_is_active():
            instance = instance_info.dbaas.instances.get(
                instance_info.id)
            if instance.status == "ACTIVE":
                return True
            else:
                assert_equal("REBOOT", instance.status)
                return False
        poll_until(result_is_active)

    @test(depends_on=[test_restart_service_should_return_active])
    @time_out(10)
    def test_get_configuration_details_from_instance_validation(self):
        # validate that the configuraiton was applied correctly to the instance
        if CONFIG.fake_mode:
            raise SkipTest("configuration from sql does not work in fake mode")
        inst = instance_info.dbaas.instances.get(instance_info.id)
        configuration_id = inst.configuration['id']
        _test_configuration_is_applied_to_instance(instance_info,
                                                   configuration_id)


@test(depends_on=[ListConfigurations], groups=[GROUP])
class StartInstanceWithConfiguration(object):

    @test
    def test_start_instance_with_configuration(self):
        # test that a new instance will apply the configuration on create
        if test_config.auth_strategy == "fake":
            raise SkipTest("Skipping instance start with configuration "
                           "test for fake mode.")
        global configuration_instance
        databases = []
        databases.append({"name": "firstdbconfig", "character_set": "latin2",
                          "collate": "latin2_general_ci"})
        databases.append({"name": "db2"})
        configuration_instance.databases = databases
        users = []
        users.append({"name": "liteconf", "password": "liteconfpass",
                      "databases": [{"name": "firstdbconfig"}]})
        configuration_instance.users = users
        configuration_instance.name = "TEST_" + str(datetime.now()) + "_config"
        flavor_href = instance_info.dbaas_flavor_href
        configuration_instance.dbaas_flavor_href = flavor_href
        configuration_instance.volume = instance_info.volume

        result = instance_info.dbaas.instances.create(
            configuration_instance.name,
            configuration_instance.dbaas_flavor_href,
            configuration_instance.volume,
            configuration_instance.databases,
            configuration_instance.users,
            availability_zone="nova",
            configuration_ref=configuration_href)
        assert_equal(200, instance_info.dbaas.last_http_code)
        assert_equal("BUILD", result.status)
        configuration_instance.id = result.id


@test(depends_on_classes=[StartInstanceWithConfiguration], groups=[GROUP])
class WaitForConfigurationInstanceToFinish(object):

    @test
    @time_out(60 * 7)
    def test_instance_with_configuration_active(self):
        # wait for the instance to become active
        if test_config.auth_strategy == "fake":
            raise SkipTest("Skipping instance start with configuration "
                           "test for fake mode.")

        def result_is_active():
            instance = instance_info.dbaas.instances.get(
                configuration_instance.id)
            if instance.status == "ACTIVE":
                return True
            else:
                assert_equal("BUILD", instance.status)
                return False

        poll_until(result_is_active)

    @test(depends_on=[test_instance_with_configuration_active])
    @time_out(10)
    def test_get_configuration_details_from_instance_validation(self):
        # validate that the configuraiton was applied correctly to the instance
        if CONFIG.fake_mode:
            raise SkipTest("configuration from sql does not work in fake mode")
        inst = instance_info.dbaas.instances.get(configuration_instance.id)
        configuration_id = inst.configuration['id']
        _test_configuration_is_applied_to_instance(configuration_instance,
                                                   configuration_id)


#qe
@test(runs_after=[WaitForConfigurationInstanceToFinish], groups=[GROUP])
class MoreConfigurations(object):

    #qe
    @test
    def test_changing_configuration_with_dynamic_parameter(self):
        # update a configuration group with only dynamic variables
        # apply the configuration group to the instance
        # no restart should be required
        values = ('{"max_connections": 4444}')
        instance_info.dbaas.configurations.update(configuration_info.id,
                                                  values)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 202)

        instance_info.dbaas.configurations.get(configuration_info.id)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 200)

        def result_is_active():
            instance = instance_info.dbaas.instances.get(
                instance_info.id)
            if instance.status == "ACTIVE":
                return True
            else:
                return False
        poll_until(result_is_active)

        instance = instance_info.dbaas.instances.get(instance_info.id)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 200)
        print(instance.status)
        assert_equal('ACTIVE', instance.status)

    #qe
    #probably don't need this here at all.
    #there is no need to restart the instance after applying dynamic only
    # @test(depends_on=[test_changing_configuration_with_nondynamic_parameter])
    # def test_restart_service_should_return_active(self):
    #     # test that after restarting the instance it becomes active
    #     instance_info.dbaas.instances.restart(instance_info.id)
    #     resp, body = instance_info.dbaas.client.last_response
    #     assert_equal(resp.status, 202)

    #     def result_is_active():
    #         instance = instance_info.dbaas.instances.get(
    #             instance_info.id)
    #         if instance.status == "ACTIVE":
    #             return True
    #         else:
    #             assert_equal("REBOOT", instance.status)
    #             return False
    #     poll_until(result_is_active)

    #qe
    @test
    def test_changing_configuration_with_dynamic_and_nondynamic(self):
        # test that changing a non-dynamic parameter is applied to instance
        # and show that the instance requires a restart
        # A dynamic variable is included in the list of configurations
        values = ('{"join_buffer_size": 1048576, '
                  '"innodb_buffer_pool_size": 57671680, '
                  '"max_connections": 4444}') #max_connections is dynamic

        instance_info.dbaas.configurations.update(configuration_info.id,
                                                  values)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 202)

        instance_info.dbaas.configurations.get(configuration_info.id)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 200)

        def result_is_not_active():
            instance = instance_info.dbaas.instances.get(
                instance_info.id)
            if instance.status == "ACTIVE":
                return False
            else:
                return True
        poll_until(result_is_not_active)

        instance = instance_info.dbaas.instances.get(instance_info.id)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 200)
        print(instance.status)
        assert_equal('RESTART_REQUIRED', instance.status)

    @test(depends_on=[test_changing_configuration_with_dynamic_and_nondynamic])
    def test_resize_service_should_return_active_again(self):
        # test that after restarting the instance it becomes active
        # This test is also 
        #HEY, TODO, TO DO, etc: is this the correct call to flavor?
        instance_info.dbaas.instances.resize_instance(instance_info.id, 3)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 202)

        def result_is_active():
            instance = instance_info.dbaas.instances.get(
                instance_info.id)
            if instance.status == "ACTIVE":
                return True
            else:
                assert_equal("RESIZE", instance.status)
                return False
        poll_until(result_is_active)

    @test(depends_on=[test_resize_service_should_return_active_again])
    @time_out(10)
    def test_get_configuration_details_from_instance_validation_again(self):
        # validate that the configuraiton was applied correctly to the instance
        if CONFIG.fake_mode:
            raise SkipTest("configuration from sql does not work in fake mode")
        inst = instance_info.dbaas.instances.get(instance_info.id)
        configuration_id = inst.configuration['id']
        _test_configuration_is_applied_to_instance(instance_info,
                                                   configuration_id)


@test(depends_on_classes=[MoreConfigurations], groups=[GROUP])
class WaitForConfigurationInstanceToFinishAgain(object):

    @test
    @time_out(60 * 7)
    def test_instance_with_configuration_active(self):
        # wait for the instance to become active
        if test_config.auth_strategy == "fake":
            raise SkipTest("Skipping instance start with configuration "
                           "test for fake mode.")

        def result_is_active():
            instance = instance_info.dbaas.instances.get(
                configuration_instance.id)
            if instance.status == "ACTIVE":
                return True
            else:
                assert_equal("BUILD", instance.status)
                return False

        poll_until(result_is_active)

    @test(depends_on=[test_instance_with_configuration_active])
    @time_out(10)
    def test_get_configuration_details_from_instance_validation(self):
        # validate that the configuraiton was applied correctly to the instance
        if CONFIG.fake_mode:
            raise SkipTest("configuration from sql does not work in fake mode")
        inst = instance_info.dbaas.instances.get(configuration_instance.id)
        configuration_id = inst.configuration['id']
        _test_configuration_is_applied_to_instance(configuration_instance,
                                                   configuration_id)













@test(runs_after=[WaitForConfigurationInstanceToFinish], groups=[GROUP])
class DeleteConfigurations(object):

    @test
    def test_delete_invalid_configuration_not_found(self):
        # test deleting a configuration that does not exist throws exception
        invalid_configuration_id = "invalid-config-id"
        assert_raises(exceptions.NotFound,
                      instance_info.dbaas.configurations.delete,
                      invalid_configuration_id)

    @test
    def test_unable_delete_instance_configurations(self):
        # test deleting a configuration that is assigned to
        # an instance is not allowed.
        assert_raises(exceptions.BadRequest,
                      instance_info.dbaas.configurations.delete,
                      configuration_info.id)

    @test(runs_after=[test_unable_delete_instance_configurations])
    def test_unassign_configuration_from_instances(self):
        # test to unassign configuration from instance
        instance_info.dbaas.instances.modify(configuration_instance.id,
                                             configuration_ref="")
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 202)
        instance_info.dbaas.instances.modify(instance_info.id,
                                             configuration_ref="")
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 202)

    @test(runs_after=[test_unassign_configuration_from_instances])
    def test_delete_configuration_instance(self):
        # test that we can delete the instance even though there is a
        # configuration applied to the instance
        instance_info.dbaas.instances.delete(configuration_instance.id)
        assert_equal(202, instance_info.dbaas.last_http_code)

        def instance_is_gone():
            try:
                instance_info.dbaas.instances.get(configuration_instance.id)
                return False
            except exceptions.NotFound:
                return True

        poll_until(instance_is_gone)
        assert_raises(exceptions.NotFound, instance_info.dbaas.instances.get,
                      configuration_instance.id)

    @test(depends_on=[test_delete_configuration_instance])
    def test_no_instances_on_configuration(self):
        # test there is no configuration on the instance after unassigning
        result = instance_info.dbaas.configurations.get(configuration_info.id)
        assert_equal(configuration_info.id, result.id)
        assert_equal(configuration_info.name, result.name)
        assert_equal(configuration_info.description, result.description)
        print(configuration_instance.id)
        print(instance_info.id)
        assert_equal(0, len(result.instances))

    @test(depends_on=[test_unassign_configuration_from_instances])
    def test_delete_unassigned_configuration(self):
        # test that we can delete the configuration after no instances are
        # assigned to it any longer
        instance_info.dbaas.configurations.delete(configuration_info.id)
        resp, body = instance_info.dbaas.client.last_response
        assert_equal(resp.status, 202)
