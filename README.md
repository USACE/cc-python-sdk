# cc-python-sdk
The Python SDK for developing plugins for Cloud Compute

## TODO / Questions
1. We need to make the JSON serialzers consistent across all SDKs. Should we use camelCase for all attributes since this is the JavaScript convention?

2. Will we need to support using an S3 data store with files that cannot fit in memory? We could use multipart upload/downloads instead of reading entire files to memory.

3. In the Java sdk, pull/put/get methods seem to be writing to predetermined paths, why do we need source/dest paths in the input? In this sdk I've made them read and write to the supplied paths in the input parameter.

4. Should `put_object()` use source and dest root paths instead of full paths? Currently we are using root paths (directories?) for pull and get

5. Do we want to support directory paths with trailing slashes? It is not supported now.

6. What about files with no extension? We need to remove the "." from paths in that case

7. In writeInputStreamToDisk in the Java SDK, there is a bug if the filepath containes the filename in any parent directory

```Java
        String[] fileparts = outputDestination.split("/");
        String fileName = fileparts[fileparts.length-1];
        String directory = outputDestination.replace(fileName,""); // <- dangerous if any parent directory contains the fileName

        // replace with this
        String outputDestination = "path/to/output/destination";
        String directory = new File(outputDestination).getParent();

        File dir = new File(directory);
        if (!dir.exists()) {
            dir.mkdirs();
        }
```