# SAP Race Tracking Analysis

With this project we can download the tracking data from SAP Sailing Analytics, compute new variables and visualize the data in a power bi report

## SQL server
To store the data in this project, an SQL server has been used. This server is hosted by the Sailing Innovation Centre (SIC) and can be accessed using the credentials given in the jupyter notebooks. If you get an error saying that it is not possible to reach the server from your IP address, contact the SIC.


## Getting Started
If it is desired to setup a new database run the jupyter notebook 'src/0_Setup_Table_Structure'. In this notebook a connection can be made with the new server by changing the credentials in the first cell. After that the rest of the notebook creates all tables, indices and foreign keys that are required.



## Add New Races
At the moment there are about 350 races uploaded to the database. If it is desired to add others as well this can be done using the jupyter notebook 'src/1_download_to_sql_server'. Specify which races you desire to download by defining an `eventSelection`, by specifying the what the of name of the regatta and races should contain, in the following way

```
eventSelection = [{'name' :  'www', 'regattaNameContaining': 'WCS 2019 Genoa - 49er', 'raceNameContaining': ''},
         {'name' : 'www', 'regattaNameContaining': 'WCS 2019 Genoa - Nacra', 'raceNameContaining' : ''}
         ]
```
`'name'` represents the name of the server. After some time all the races tracked by SAP will be available using `'www'`, but some events also have their own server on which the data is available sooner. The name of the server can be found when viewing the desired race online at the *SAP Sailing Analytics* web site. For example the [test event in Tokyo](https://tokyo2019.sapsailing.com/gwt/Home.html#/regatta/races/:eventId=6389fb9d-12e1-47ef-9831-ddab8cf9598f&regattaId=Tokyo%202019%20-%2049er%20FX) has it's own url starting with `tokyo2019`. 

By running the whole notebook all the tables will be filled with data regarding the selected races.


## Add New Variables
For some visuals extra variables are needed. These are calculated before uploading the data to power bi to save computation time. This can be done with the jupyter notebook 'src/2_Create_New_Variables'. In the same way as for adding new races, it is possible to select races for which updates are desired.

In every section a part of the variables can be updated. Some depend on another, so it is not always possible to skip to the variable you specifically want to update.

This is the file that should be modified when new variables are desired.


## Working on the Report
In the folder **reports** the *Power BI* files can be found. In the files the data from the sql server is imported. Per table there is a small query to change some formats and make combined id's because *Power BI* cannot deal with multi column foreign keys. 

For the `posititions` table an indexed view is made in the database. If there is new data available that is needed in the report a the view should be renewed.


## Authors

* **Nerine Usman** - *Initial work* - [NerineUsman](https://github.com/NerineUsman)

