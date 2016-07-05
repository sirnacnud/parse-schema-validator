import argparse, copy, json, httplib

api_path = None
connection = None
app_id = None
master_key = None

def add_class(schema_class):
  new_class = {}
  new_class['className'] = schema_class['className']

  new_fields = copy.deepcopy(schema_class['fields'])
  del new_fields['ACL']
  del new_fields['createdAt']
  del new_fields['updatedAt']
  del new_fields['objectId']

  new_class['fields'] = new_fields

  connection.request('POST', api_path + '/' + schema_class['className'], json.dumps(new_class), {
       "X-Parse-Application-Id": app_id,
       "X-Parse-Master-Key": master_key,
       "Content-Type": "application/json"
     })
  response = connection.getresponse()
  if response.status != 200:
    print 'Failed to created class: ' + response.reason
    return False
  else:
    data = response.read()
    print 'Successfully created ' + schema_class['className']
    return True

def add_field(class_name, field_name, field_type):
  update_field = {}
  update_field['className'] = class_name
  update_field['fields'] = {
    field_name: field_type
  }

  connection.request('PUT', api_path + '/' + class_name, json.dumps(update_field), {
       "X-Parse-Application-Id": app_id,
       "X-Parse-Master-Key": master_key,
       "Content-Type": "application/json"
     })
  response = connection.getresponse()
  if response.status != 200:
    print 'Failed to add ' + field_name + ' to ' + class_name + ': ' + response.reason
    return False
  else:
    data = response.read()
    print 'Successfully added ' + field_name + ' to ' + class_name
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
          answer = raw_input('Field ' + schema_field + ' not found on ' + schema_class_name + ', fix (y/n): ')
          if answer == 'y':
            verified = add_field(schema_class_name, schema_field, schema_type)
          else:
            verified = False
        else:
          print 'Field ' + schema_field + ' not found on ' + schema_class_name
          verified = False
      elif schema_type['type'] != parse_field_type['type']:
        print 'Field ' + schema_field + ' type is ' + parse_field_type['type'] + ' when it should be ' + schema_type['type']
        verified = False

  else:
    if fix:
      answer = raw_input('Class ' + schema_class_name + ' not found, fix (y/n): ')
      if answer == 'y':
        verified = add_class(schema_class)
      else:
        verified = False
    else:
      print 'Class ' + schema_class_name + ' not found'
      verified = False

  return verified

def get_arguments():
  arg_parser = argparse.ArgumentParser('Tool for validating and creating Parse Classes on a Parse Server' )
  arg_parser.add_argument('-s', '--schema', help='Json file describing the Parse Classes', required=True)
  arg_parser.add_argument('-m', '--masterKey', help='Parse Server master key', required=True)
  arg_parser.add_argument('-a', '--appId', help='Parse Server app id', required=True)
  arg_parser.add_argument('-n', '--hostName', help='Parse Server host name', required=True)
  arg_parser.add_argument('-p', '--port', help='Parse Server port', default=443)
  arg_parser.add_argument('-r', '--resourcePath', help='Parse Server API resource path')
  arg_parser.add_argument('-f', '--fixInteractive', help='Interactively fix schema validation errors', default=False, action='store_true')
  return arg_parser.parse_args()

def main():
  command_args = get_arguments()

  global connection
  global api_path
  global app_id
  global master_key

  if command_args.port == 443:
    connection = httplib.HTTPSConnection(command_args.hostName, command_args.port)
  else:
    connection = httplib.HTTPConnection(command_args.hostName, command_args.port)

  api_path = ''

  if command_args.resourcePath:
    api_path = command_args.resourcePath

  api_path += '/schemas'
  app_id = command_args.appId
  master_key = command_args.masterKey

  connection.connect()
  connection.request('GET', api_path, '', {
         "X-Parse-Application-Id": app_id,
         "X-Parse-Master-Key": master_key,
         "Content-Type": "application/json"
       })

  response = connection.getresponse()

  if response.status == 200:
    results = json.loads(response.read())
    parse_classes = results['results']

    schema_file = open(command_args.schema, 'r')
    schema_json = schema_file.read()
    schema = json.loads(schema_json)
    for schema_class in schema['classes']:
      verified = process_class(parse_classes, schema_class, command_args.fixInteractive)

      if not verified:
        print 'Failed to verify ' + schema_class['className']
      else:
        print 'Verified ' + schema_class['className']
  else:
    print 'Failed to connect to Parse Server - ' + response.reason

if __name__ == "__main__":
  main()