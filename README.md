# parse-schema-validator
Tool for validating Parse classes on a Parse Server

This tool is useful for managing the schema of your Parse classes, as your Parse classes change over the lifetime of an application. The tool provides a way to validate the current schema against a specified schema and offers the option to fix the differences. Keep in mind this is for the schema of the Parse classes, not the schema of the MongoDB collections.

The tool works by using the [Parse REST Schema API](http://parseplatform.github.io/docs/rest/guide/#schema).

## Installing
Instructions coming soon...

## Usage

### Connecting to Parse
You will need to specify parameters for the master key (`-m, --masterKey`), app id (`-a, --appId`), hostname (`-n, --hostName`), and port (`-p, --port`) of your Parse Server to connect to. Port `443` is the default port and will use https. Also, you may need to specify the resource path for your Parse Server endpoint (`-r, --resourcePath`).

Example parameters for Parse Server running on `http://localhost:1337/parse` with master key `myMasterKey` and app id `myAppId`:
```
$ parse-schema-validator -m myMasterKey -a myAppId -n localhost -p 1337 -r /parse
```

### Schema File
To validate the current schema of your Parse classes you will need to specify a schema json file (`-s, --schema`). This file uses the same json structure to define a class and its fields as the [Parse REST Schema API](http://parseplatform.github.io/docs/rest/guide/#schema). The top level property in the schema json file is a property named `classes` with the value of an array of classes.

Example schema file for a Parse class named `City` with fields `name`, `state`, and `country`:
```
{
  "classes":[
    {
      "className": "City",
      "fields": {
        "name": {
          "type": "String"
        },
        "state": {
          "type": "String"
        },
        "country": {
          "type": "String"
        }
      }
    }
  ]
}
```
###Schema Dump
If you have already have some Parse classes created, you can generate the schema json file automatically by specifying (`-d, --dump`). This will dump the schema json to standard out.

```
$ parse-schema-validator -m myMasterKey -a myAppId -n localhost -p 1337 -r /parse -d > current_schema.json
```

###Validating
By default when you run the tool with the Parse connection options and the schema file it will validate the Parse classes against the schema and print to standard out whether the classes failed or succedded.

```
$ parse-schema-validator -m myMasterKey -a myAppId -n localhost -p 1337 -r /parse -s schema.json
```

###Fixing Differences
You can have the tool interactively fix differences between your Parse classes and your schema file using (`-f, --fixInteractive`). The tool will prompt you on each difference whether or not to fix it. At the moment the tool can add only add new classes or fields not present. It doesn't have the ability to change the type of a field or remove classes/fields.

```
$ parse-schema-validator -m myMasterKey -a myAppId -n localhost -p 1337 -r /parse -s schema.json -f
```

## Limitations
* Only https port supported is 443, any other port is considered http.
* Doesn't have support to change field types or to remove classes/fields.

## Author

Copyright (C) 2016 [Duncan Cunningham](https://github.com/sirnacnud)

## License

Distributed under the MIT License. See the [LICENSE](LICENSE) file for more info.
