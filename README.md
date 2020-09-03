						PostgreSQL Spatial Data Importer
	Description:
		This tool was built from scratch to support importing data from different file types
		into PostgreSQL databes' tables. 

	How to use:
        	Considering the tool's current state, you simply have to follow the options available in front
        	of you. It's as simple as doing the following:
        		-   Choose file format
        		-   Click browse to navigate to your file
        		-   Select the file you want to import, and click "Open"
        		-   If your file is a CSV or WKT file, you will have only two options:
            			*   Select delimiter
				*   Select Coordinate Reference System (CRS)
				*   Click load
				*   Enter connection details
				*   Click "Run" - if everything is OK, you will find a message in the logger area telling
				    you that the operation succeeded- otherwise, report error will appear,
				    if you think no errors should occur, report the error back to us
				*   If you feel like you messed up, click "Cancel" which will reset the UI for you ;)
			-   And if your file is either 'GeoJSON' or 'Shapefile', you can do much more:
			    *   Change default fields "id, geometry" names
			    *   Select certain fields to import
			    *   Rename selected fields 'should be of the same size as selected fields'
			    *   Select Coordinate Reference System (CRS)
			    *   Generate new IDs
			    *   Skip loading attributes
			    *   Create a table "Drop table that matches table's name"
			    *   Create spatial index
			    *   Override data in target table
			    *   Append data to table 'Preserves sequence and primary key duplication'
			    *   Click load
			    *   Enter connection details
			    *   Click "Run" - if everything is OK, you will find a message in the logger area telling
				    you that the operation succeeded- otherwise, report error will appear,
				    if you think no errors should occur, report the error back to us
			    *   If you feel like you messed up, click "Cancel" which will reset the UI for you ;)

	Features:
	    -   Support for numeric fields
	    -   Supoort for null values
	    -   Support for date values
	    -   Support for removing starting and trailing spaces
	    -   CSV & WKT:
		*   Support for geometries in CSV & WKT formats
	    -   GeoJSON & Shapefile:
		*   Support for GeoJSON & Shapefile geometries
		*   Support to select certain attributes
		*   Support to modify attributes' names before import to DB
		*   Support to generate IDs if not exist in data.json file (Depends on user input)
		*   Support to change the geometry & primary key fields
		*   Support for importing only geometry
		*   Support for creating table (Replace if exists)
		*   Support for creating spatial index
		*   Support for appending data to table

	Planned features:
    		-   Support for more spatial file formats

	Known issues:
	    *   Application freezes while loading data (User should wait until process is finished)
	    *   Mixed Geometries import isn't supported from Shapefiles but is working fine in GeoJSON formats
	    
	Notice:
	    -   We've been actively working on testing the tool, and fixing bugs/issues
		as soon as we find any, but no tool is complete and invulnerable.
		So please report any bug/issue you find while using the tool.
	    -   You can send bugs/issues by mail to one of the Support team or Project manager
