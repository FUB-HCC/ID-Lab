# Housekeeper

A service to clean data for use in RDF.

Features:

- Removes HTML from Strings
- Removal of Newlines
- Removal of Special Character (e.g. ampersands)
- Slugify of Rows/Properties
- delete complete rows/properties
- Input Format: JSON or CSV
- Output Format: JSON, CSV 


## How to run

In development use PHP development server:
php -S 0.0.0.0:8080 -t public 

## Usage

Responds on /clean to POST with csv or json file as body.

Possible URL Parameters.

- ?slugify=row1;row2
- ?delete=row3 // Rows to delete from data
- ?skip=row1 // Row(s) to skip (no cleansing)
- ?outputType=json // Or csv (case sensitive)
- ?htmlEntities=row1;row2 // Apply 
htmlentities(rowEntry) instead of htmlspecialchars

**POST http://$server/clean?delete=column1,column2&skip=column1,column2&output=json**
