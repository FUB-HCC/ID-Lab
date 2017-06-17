# PublicationConverter

Converts Cluster publication references to bibtex.

## Install

You will need a running Grobid instance. 

1. Install [Grobid](http://grobid.readthedocs.io/en/latest/Install-Grobid/)
2. Put `./Grobid training data/citation/cluster.xml` into `/grobid-master/grobid-trainer/resources/dataset/citation/corpus` and run `mvn generate-resources -Ptrain_name_citation -e` inside ./grobid-trainer ([Help](http://grobid.readthedocs.io/en/latest/Training-the-models-of-Grobid/))
3. Put the resulting model into `/grobid-master/grobid-home/models/citation`
4. Put `./Grobid training data/name/cluster.xml` into `/grobid-master/grobid-trainer/resources/dataset/name/citation/corpus` and run `mvn generate-resources -Ptrain_citation -e` inside ./grobid-trainer ([Help](http://grobid.readthedocs.io/en/latest/Training-the-models-of-Grobid/))
5. Put the resulting model into `/grobid-master/grobid-home/models/name/citation`
6. Make sure to have the Grobid service running (http://grobid.readthedocs.io/en/latest/Grobid-service/). Change ip in $requestURL in ./Grobit script/citation_parser.php if not 0.0.0.0:8080. If you have problems with wapiti corruption try using the [docker container](http://grobid.readthedocs.io/en/latest/Grobid-docker/). 


## Usage:

- Check // Settings variables in citation_parser.php. You can change the imported file with the $filename variable.
- Run PHP development server inside ./Grobid script: `php -S 0.0.0.0:8080`
- GET to localhost:8080/citation_parser.php (for example using your browser)
- Results will appear in $outFilenameBib file
- Move that file to ./BibtexToRdf and run `java -jar bibtex2rdf.jar -schema config.properties $outFilenameBib.bib results.rdf`