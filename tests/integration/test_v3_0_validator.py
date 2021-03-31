import pytest

from openapi_spec_validator.exceptions import (
    ExtraParametersError, UnresolvableParameterError, OpenAPIValidationError,
    DuplicateOperationIDError,
)


class TestSpecValidatorIterErrors(object):

    @pytest.fixture
    def validator(self, v3_0_validator):
        return v3_0_validator

    def test_empty(self, validator):
        spec = {}

        errors = validator.iter_errors(spec)

        errors_list = list(errors)
        assert errors_list[0].__class__ == OpenAPIValidationError
        assert errors_list[0].message == "'openapi' is a required property"
        assert errors_list[1].__class__ == OpenAPIValidationError
        assert errors_list[1].message == "'info' is a required property"
        assert errors_list[2].__class__ == OpenAPIValidationError
        assert errors_list[2].message == "'paths' is a required property"

    def test_info_empty(self, validator):
        spec = {
            'openapi': '3.0.0',
            'info': {},
            'paths': {},
        }

        errors = validator.iter_errors(spec)

        errors_list = list(errors)
        assert errors_list[0].__class__ == OpenAPIValidationError
        assert errors_list[0].message == "'title' is a required property"

    def test_minimalistic(self, validator):
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Test Api',
                'version': '0.0.1',
            },
            'paths': {},
        }

        errors = validator.iter_errors(spec)

        errors_list = list(errors)
        assert errors_list == []

    def test_same_parameters_names(self, validator):
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Test Api',
                'version': '0.0.1',
            },
            'paths': {
                '/test/{param1}': {
                    'parameters': [
                        {
                            'name': 'param1',
                            'in': 'query',
                            'schema': {
                              'type': 'integer',
                            },
                        },
                        {
                            'name': 'param1',
                            'in': 'path',
                            'schema': {
                              'type': 'integer',
                            },
                            'required': True,
                        },
                    ],
                },
            },
        }

        errors = validator.iter_errors(spec)

        errors_list = list(errors)
        assert errors_list == []

    def test_same_operation_ids(self, validator):
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Test Api',
                'version': '0.0.1',
            },
            'paths': {
                '/test': {
                    'get': {
                        'operationId': 'operation1',
                        'responses': {
                            'default': {
                                'description': 'default response',
                            },
                        },
                    },
                    'post': {
                        'operationId': 'operation1',
                        'responses': {
                            'default': {
                                'description': 'default response',
                            },
                        },
                    },
                },
                '/test2': {
                    'get': {
                        'operationId': 'operation1',
                        'responses': {
                            'default': {
                                'description': 'default response',
                            },
                        },
                    },
                },
            },
        }

        errors = validator.iter_errors(spec)

        errors_list = list(errors)
        assert len(errors_list) == 2
        assert errors_list[0].__class__ == DuplicateOperationIDError
        assert errors_list[1].__class__ == DuplicateOperationIDError

    def test_allow_allof_required_no_properties(self, validator):
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Test Api',
                'version': '0.0.1',
            },
            'paths': {},
            'components': {
                'schemas': {
                    'Credit': {
                        'type': 'object',
                        'properties': {
                            'clientId': {'type': 'string'},
                        }
                    },
                    'CreditCreate': {
                        'allOf': [
                            {
                                '$ref': '#/components/schemas/Credit'
                            },
                            {
                                'required': ['clientId']
                            }
                        ]
                    }
                },
            },
        }

        errors = validator.iter_errors(spec)
        errors_list = list(errors)
        assert errors_list == []

    def test_extra_parameters_in_required(self, validator):
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Test Api',
                'version': '0.0.1',
            },
            'paths': {},
            'components': {
                'schemas': {
                    'testSchema': {
                        'type': 'object',
                        'required': [
                            'testparam1',
                        ]
                    }
                },
            },
        }

        errors = validator.iter_errors(spec)

        errors_list = list(errors)
        assert errors_list[0].__class__ == ExtraParametersError
        assert errors_list[0].message == (
            "Required list has not defined properties: ['testparam1']"
        )

    def test_undocumented_parameter(self, validator):
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Test Api',
                'version': '0.0.1',
            },
            'paths': {
                '/test/{param1}/{param2}': {
                    'get': {
                        'responses': {
                            'default': {
                                'description': 'default response',
                            },
                        },
                    },
                    'parameters': [
                        {
                            'name': 'param1',
                            'in': 'path',
                            'schema': {
                                'type': 'integer',
                            },
                            'required': True,
                        },
                    ],
                },
            },
        }

        errors = validator.iter_errors(spec)

        errors_list = list(errors)
        assert errors_list[0].__class__ == UnresolvableParameterError
        assert errors_list[0].message == (
            "Path parameter 'param2' for 'get' operation in "
            "'/test/{param1}/{param2}' was not resolved"
        )

    def test_default_value_wrong_type(self, validator):
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Test Api',
                'version': '0.0.1',
            },
            'paths': {},
            'components': {
                'schemas': {
                    'test': {
                        'type': 'integer',
                        'default': 'invaldtype',
                    },
                },
            },
        }

        errors = validator.iter_errors(spec)

        errors_list = list(errors)
        assert len(errors_list) == 1
        assert errors_list[0].__class__ == OpenAPIValidationError
        assert errors_list[0].message == (
            "'invaldtype' is not of type integer"
        )

    def test_parameter_default_value_wrong_type(self, validator):
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Test Api',
                'version': '0.0.1',
            },
            'paths': {
                '/test/{param1}': {
                    'get': {
                        'responses': {
                            'default': {
                                'description': 'default response',
                            },
                        },
                    },
                    'parameters': [
                        {
                            'name': 'param1',
                            'in': 'path',
                            'schema': {
                                'type': 'integer',
                                'default': 'invaldtype',
                            },
                            'required': True,
                        },
                    ],
                },
            },
        }

        errors = validator.iter_errors(spec)

        errors_list = list(errors)
        assert len(errors_list) == 1
        assert errors_list[0].__class__ == OpenAPIValidationError
        assert errors_list[0].message == (
            "'invaldtype' is not of type integer"
        )

    def test_parameter_default_value_with_reference(self, validator):
        spec = {
            'openapi': '3.0.0',
            'info': {
                'title': 'Test Api',
                'version': '0.0.1',
            },
            'paths': {
                '/test/': {
                    'get': {
                        'responses': {
                            'default': {
                                'description': 'default response',
                            },
                        },
                        'parameters': [
                            {
                                'name': 'param1',
                                'in': 'query',
                                'schema': {
                                    'allOf': [{
                                        '$ref': '#/components/schemas/type',
                                    }],
                                    'default': 1,
                                },
                            },
                        ],
                    },
                },
            },
            'components': {
                'schemas': {
                    'type': {
                        'type': 'integer',
                    }
                },
            },
        }

        errors = validator.iter_errors(spec)

        errors_list = list(errors)
        assert errors_list == []
