# Overseer

Tool to extract many-to-many relationships from a junction table and add them to the data.
**Very specific to Cluster data.**

### What does it do?
For example:

Table 1 - Mitglieder

|id| name|
|---|----|
|0| Immanuel |


Table 2 - Projekte

|id| name|
|---|----|
|1| ID-Lab|

JunctionTable

|page1| page2|
|---|----|
|0| 1|

Results

Table 1 - Mitglieder

|id| name| projekte|
|---|----|---|
|0| Thomas| **ID-Lab**|

Table 2 - Projekte

|id| name| mitglieder|
|---|----|---|
|1| ID-Lab| **Immanuel**|

### Usage

This program only works with the data from the cluster homepage as json formatted files (Like the ones Housekeeper generates). Using it outside of this context requires manual changes to the code.

`python3 main.py --source inputFolder --output outputFolder`
