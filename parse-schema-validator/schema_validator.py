import argparse
import copy
import json
from parse_connection import ParseConnection

api_path = None
connection = None


def add_class(schema_class):
    new_class = {}
    new_class['className'] = schema_class['className']

    new_fields = copy.deepcopy(schema_class['fields'])
    del new_fields['ACL']
    del new_fields['createdAt']
    del new_fields['updatedAt']
    del new_fields['objectId']

    new_class['fields'] = new_fields

    response = connection.perform_request(
        'POST',
        api_path +
        '/' +
        schema_class['className'],
        json.dumps(new_class))
    if response.status != 200:
        print('Failed to created class: ' + response.reason)
        return False
    else:
        data = response.read()
        print('Successfully created ' + schema_class['className'])
        return True


def add_field(class_name, field_name, field_type):
    update_field = {}
    update_field['className'] = class_name
    update_field['fields'] = {
        field_name: field_type
    }

    response = connection.perform_request(
        'PUT', api_path + '/' + class_name, json.dumps(update_field))
    if response.status != 200:
        print('Failed to add ' + field_name + ' to ' +
              class_name + ': ' + response.reason)
        return False
    else:
        data = response.read()
        print('Successfully added ' + field_name + ' to ' + class_name)
        return True


def process_class(parse_classes, schema_class, fix):
    verified = True
    schema_class_name = schema_class['className']
    parse_class = None

    for iter_parse_class in parse_classes:
        if iter_parse_class['className'] == schema_class_name:
            parse_class = iter_parse_class
            break

    if parse_class:
        parse_class_fields = parse_class['fields']
        schema_class_fields = schema_class['fields']
        for schema_field, schema_type in schema_class_fields.iteritems():
            parse_field_type = parse_class_fields.get(schema_field)

            if not parse_field_type:
                if fix:
                    answer = raw_input(
                        'Field ' +
                        schema_field +
                        ' not found on ' +
                        schema_class_name +
                        ', fix (y/n): ')
                    if answer == 'y':
                        verified = add_field(
                            schema_class_name, schema_field, schema_type)
                    else:
                        verified = False
                else:
                    print(
                        'Field ' +
                        schema_field +
                        ' not found on ' +
                        schema_class_name)
                    verified = False
            elif schema_type['type'] != parse_field_type['type']:
                print(
                    'Field ' +
                    schema_field +
                    ' type is ' +
                    parse_field_type['type'] +
                    ' when it should be ' +
                    schema_type['type'])
                verified = False

    else:
        if fix:
            answer = raw_input(
                'Class ' +
                schema_class_name +
                ' not found, fix (y/n): ')
            if answer == 'y':
                verified = add_class(schema_class)
            else:
                verified = False
        else:
            print('Class ' + schema_class_name + ' not found')
            verified = False

    return verified


def get_arguments():
    arg_parser = argparse.ArgumentParser(
        'Tool for validating Parse Classes on a Parse Server')
    arg_parser.add_argument(
        '-s',
        '--schema',
        help='Json file describing the Parse Classes')
    arg_parser.add_argument(
        '-m',
        '--masterKey',
        help='Parse Server master key',
        required=True)
    arg_parser.add_argument(
        '-a',
        '--appId',
        help='Parse Server app id',
        required=True)
    arg_parser.add_argument(
        '-n',
        '--hostName',
        help='Parse Server host name',
        required=True)
    arg_parser.add_argument(
        '-p',
        '--port',
        help='Parse Server port',
        default=443)
    arg_parser.add_argument(
        '-r',
        '--resourcePath',
        help='Parse Server API resource path')
    arg_parser.add_argument(
        '-f',
        '--fixInteractive',
        help='Interactively fix schema validation errors',
        default=False,
        action='store_true')
    arg_parser.add_argument(
        '-d',
        '--dump',
        help='Dump json to standard out of the current parse schema',
        default=False,
        action='store_true')
    return arg_parser.parse_args()


def run():
    global api_path
    global connection

    api_path = ''

    command_args = get_arguments()

    if command_args.resourcePath:
        api_path = command_args.resourcePath

    api_path += '/schemas'
    host = command_args.hostName
    port = command_args.port
    app_id = command_args.appId
    master_key = command_args.masterKey

    connection = ParseConnection(host, port, app_id, master_key)
    connection.connect()
    response = connection.perform_request('GET', api_path, '')

    if response.status == 200:
        results = json.loads(response.read())
        parse_classes = results['results']

        if command_args.dump:
            for item in parse_classes:
                del item['classLevelPermissions']
            print(json.dumps({'classes': parse_classes},
                             indent=2, sort_keys=True))
        elif command_args.schema:
            schema_file = open(command_args.schema, 'r')
            schema_json = schema_file.read()
            schema = json.loads(schema_json)
            for schema_class in schema['classes']:
                verified = process_class(
                    parse_classes, schema_class, command_args.fixInteractive)

                if not verified:
                    print('Failed to validate ' + schema_class['className'])
                else:
                    print('Validated ' + schema_class['className'])
        else:
            print('Error: schema file required to verify')
    else:
        print('Failed to connect to Parse Server - ' + response.reason)
