#RMLMaker
Tool to create RML from json files.
Features:

- Global mappings (Not for single class, but for all of them)
- Local Mappings
- Simple literal relationships
- Parent triples map
- Template generation for cyclic data

###Usage
```
python3 main.py -s sourceFolder/ -m mapping.json -o results.rml.ttl
``` 
**Use trailing / for folders.** Then follow prompts in console. 

If you only want your mappings to be applied, you can disable checking for mappings with the `--checkMappings 0` argument. Checking for new files can be disabled using the `--checkFiles 0` argument. E.g:

```
python3 main.py -s sourceFolder/ -m mapping.json -o results.rml.ttl --checkMappings 0 --checkFiles 0
```


To make changes to mappings you will need to edit it manually inside `./mappings.json`.

#### mappings.json

Add prefixes to the "prefixes" array in mappings.json. The "slugs" object points filenames to their slug. If those should change in the future, you will have to change them here