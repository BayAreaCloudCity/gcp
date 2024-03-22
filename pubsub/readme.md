# PubSub

This folder contains the schema definitions used for Pub/Sub (which is further passed into BigQuery). 
You'll need to have a [ProtoBuf](https://github.com/protocolbuffers/protobuf) compiler in order to run the following commands.


## BigQuery

To generate the schema for BigQuery, install [protoc-gen-bq-schema](https://github.com/GoogleCloudPlatform/protoc-gen-bq-schema), add
`option (gen_bq_schema.bigquery_opts).table_name = "table_name";`
`import "bq_table.proto"; import "bq_field.proto";`
and run
```bash
protoc --proto_path=/path/to/protoc-gen-bq-schema --proto_path=. --bq-schema_out=. xxxx.proto
```

After the schema has been generated, you may need to add 4 more PubSub metadata fields. You can find them at the end
of each existing .schema file in this folder.

Note: For optimized performance and cost, please set up partitioning on the `publish_time` column.

## Cloud Function

To generate the `*_pb2.py` and `_pb2.pyi` files, run
```bash
protoc --proto_path=. --python_out=. --mypy_out=. --experimental_allow_proto3_optional *.proto
```