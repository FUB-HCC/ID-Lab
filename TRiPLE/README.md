# TRiPLE - To RDF PipelinE

TRiPLE is a number of tools to clean an convert CSV data to RDF. It is specifically designed to handle the BWG data.

- Housekeeper - PHP based HTTP API for cleaning csv files for usage in RDF
- Overseer - Python based tool for integrating content linked by junction tables into json files
- PublicationConverter - PHP based script to convert the Cluster citation format to bibtex using grobid
- RMLMaker - Python based guided script for generating RML from arbitrary json files 


### Install

1. Clone this project using 
`git clone --recursive https://github.com/FUB-HCC/ID-Lab/tree/master/TRiPLE`.
2. Run `git submodule update --init --recursive`.
3. Using your shell go to `./RML-Mapper/` and run `mvn clean install`. You will need [Maven](http://maven.apache.org/download.cgi) and Java 1.7.
4. Install all Python dependencies using `pip install requests psycopg2 pandas`

This code uses Python 3.


### Usage

You can either import a folder of csv files or directly connect to a PostgreSQL database containing the BWG website SQL dump. It is located under `./output`. **If your Python command prompt is not `python3` please change it in the settings (See Settings).***

#### Option 1: Input from folder
`python3 main.py --source folder --inputFolder input`
"input" is seen relative to the TRiPE folder, eg: /`Users/You/TRiPLE/input`

#### Option 2: Input from database
`python3 main.py --source sql --ip localhost --user username --dbName cluster --password ifNeededPasswordHere`

**When finished (with both options!), do not forget to execute the displayed command manually.** Read the propmt in your shell.

##### Keeping files
You can use the `--keepFolders 1` parameter to keep all temp files, which would normally be removed before every run.

### Settings

At the top of main.py you will find a commented "Settings" section. There you can add desired settings. 

##### Housekeeper settings
Just add the desired parameters as defined in the [Housekeeper Readme](https://github.com/FUB-HCC/ID-Lab/blob/master/TRiPLE/Housekeeper/README.md).
It defaults to:

```
housekeeperParams = {
    'outputType': 'json' # This needs to be json
}
```
##### Python command

Here you can change your Python command. For example yours may be `python` and not `python3`.

```
pythonCommand = "python3"
```

##### Useless files
When using the database option it converts all tables to csv files. Some of them should be deleted because they are useless to the rest of the process and some of them for privacy reasons. You can add or remove files from that list using the "uselessFiles" array. It defaults to:

```
uselessFiles = ["auth_user","django_content_type","home_homepage","taggit_taggeditem","wagtailcore_page","wagtailcore_site","wagtailimages_filter"]

```
##### RDF output format
This value defines the output format for rdf.
```
rdfFormat = "rdfxml"
``` 

It can be changed to the following values: turtle, ntriples, nquads, rdfxml, rdfjson or jsonld. 
