# huwebshop
Git for the HU Webshop project.

## How to run

### Libraries
To run this code, you need to have the following programs and libraries installed:

Python 3 (website: https://www.python.org/). This code was developed using Python 3.7. Some of the libraries used here use methods that are set to become deprecated in Python 3.8; when using any version beyond 3.7, be sure to use the most recent versions possible.

MongoDB Community Edition (webpage: https://docs.mongodb.com/manual/administration/install-community/). This allows you to run a MongoDB database locally; almost all students will want to do this. It is strongly advised to also include MongoDB Compass (an option that comes up during the installation wizard).

Flask (command line: pip install Flask). This code was developed using Flask 1.0.3, and automatically included Jinja2 v. 2.10.1 and Werkzeug v. 0.15.4, amongst other things.

Pymongo (command line: pip install pymongo). This code was developed using Pymongo 3.8.0.

Flask-RESTful (command line: pip install flask-restful). This code was developed using Flask Restful 0.3.7. This library allows you to run the dummy recommendation service locally; almost all students will want to do this, at least to start out with.

Python-Dotenv (command line: pip install python-dotenv). This code was developed using Python-Dotenv 0.10.3.

Requests (command line: pip install requests). This code was developed using Requests 2.22.0.

Psycopg2 (command line: pip install psycopg2). This code was developed using Requests 2.8.6.

### Creating database tables
Start by opening the project in PyCharm.

Then you will need to setup your connection with your PostgreSQL database and your Mongo; In the ``controller`` folder you need to create a file named: ``db_auth.py``. In this file you need to paste the following and adjust the strings to your Postgres and Mongo credentials: 
````
def getPostgreSQLConnection(psycopg2):
    connection = psycopg2.connect(user="<<your user>>",
                                  password="<<your password>>",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="<<your database name>>")
    return connection

def getMongoDatabase(client):
    return client.<<your mongo database name>>

````
And we account for the documents names to be `products`, `sessions` and `visitors` in mongoDB.

Once this is done we can start creating a Flask Run Configuration in PyCharm. Start by opening the dropdown in your top-right and click on `Edit configurations`

![image](https://user-images.githubusercontent.com/42800737/113844086-6a576b00-9794-11eb-8e0b-fad3fffdb5fd.png)


Once this is open, click op de `+` on your top-left and select the `Flask Server`.

![image](https://user-images.githubusercontent.com/42800737/113844297-9ffc5400-9794-11eb-8149-2e0d4218a6ee.png)


Change `Target type` to `Script path`

![image](https://user-images.githubusercontent.com/42800737/113844564-e9e53a00-9794-11eb-998b-51b669ec23ad.png)


Enter the target path of the `huw.py`. This can be done by clicking the folder icon and navigating to `huw.py` in your project-directory.

Select the python interpreter which has all the libraries installed

![image](https://user-images.githubusercontent.com/42800737/113845245-97584d80-9795-11eb-8cb9-664f29966a05.png)


Now on the bottom-right you can click `apply` and then `ok` to save and exit out of the dialog.

![image](https://user-images.githubusercontent.com/42800737/113845370-bb1b9380-9795-11eb-9a73-d02849ace216.png)


You may run the flask project by clicking on the green play button on the top-right of your screen

![image](https://user-images.githubusercontent.com/42800737/113845550-eef6b900-9795-11eb-8510-80328e1a6966.png)


This will (if done correctly) create all the database tables you will need and startup the application. 
We now need to fill the database which can be done in using 2 different methods, 1 being quick and easy but loading will take long (through Python), and 1 being very quick to install but may be more complicated (Through database). For the latter please scroll down to the secion `Filling database through PgAdmin or DBeaver`

## Filling database through python
Navigate to the file `database controller` and uncomment all the lines in the function `instantiate`. It should look something like:
````
def instantiate(products, sessions, visitors):

    print('Database tables aan het aanmaken')
    create_tables()
    print('Database tables zijn aangemaakt!')

    print('Database producten worden gevuld.. Dit kan even duren')
    fill_db(products, sessions, visitors)
    print('Database producten zijn gevuld!')
    
    print('Relaties worden toegekend')
    assign_relations()
    print('Relaties zijn toegekend!')
    
    print('Recommendations worden gemaakt..')
    cursor, connection = open_db_connection()
    property_matching.fill_table_property_matching(cursor, connection)
    most_bought_together_algorithm.fill_table_most_bought_together(cursor, connection)
    simple.run(cursor, connection)
    close_db_connection(cursor, connection)

    print('Recommendations zijn gemaakt!')
````
If you now Run the Flask App again is will slowly but surely fill the database with all the necessary data.

## Filling database through PgAdmin or DBeaver
Download the CSV from this link: https://wetransfer.com/downloads/2c0cfdffa74cb21d9dce4f090965462520210407080434/642865
Extract the files to a folder of your choosing.

If you are using DBeaver please take the following steps.
### DBeaver
Once in DBeaver, start a connection to your (localhost) database. If there isn't a schema called `public`, please create one using the following sql statement: 
`create schema public.`. You can open an SQL editor by navigating to `SQL Editor` -> `New SQL Editor` or by using the shortcut `CTRL + ]`.

![image](https://user-images.githubusercontent.com/42800737/113847396-bb1c9300-9797-11eb-80aa-652bd9ecc39b.png)


Once created, right-click on the `tables` folder in the `Database navigator` on the left and select `Import Data`.

![image](https://user-images.githubusercontent.com/42800737/113847661-fd45d480-9797-11eb-8f05-e0d18367837d.png)


Select `CSV | Import from CSV file(s)` and click `next`.

![image](https://user-images.githubusercontent.com/42800737/113847983-4b5ad800-9798-11eb-8d4e-806c274bee6f.png)


Now select all the CSV that you had downloaded and extracted and click `open` on your bottom-right:

![image](https://user-images.githubusercontent.com/42800737/113848128-75ac9580-9798-11eb-9232-26be002bd5b5.png)


Now it is very important that you have the same exact settings as shown in this picture:

![image](https://user-images.githubusercontent.com/42800737/113848278-98d74500-9798-11eb-8fdb-1f2508e9f1b2.png)
So you need to:
 - Change the `Column delimiter` to a pipe, which is: |
 - Change `NULL value mark` to `null`
 - Change the `Set empty string to NULL` chechbox to checked

Then click `next`.


You will now see this screen:

![image](https://user-images.githubusercontent.com/42800737/113848673-01262680-9799-11eb-9023-7a190ed8aae4.png)

Make sure that everything under the column `Mapping` is set to `existing`. This will make sure you wont create any new tables because the Flask app should have created those for you.


If this is correct click `next`.

You will now see this screen:

![image](https://user-images.githubusercontent.com/42800737/113848923-43e7fe80-9799-11eb-98e9-4f3b3edba979.png)

Click `next`.


![image](https://user-images.githubusercontent.com/42800737/113854432-2a49b580-979f-11eb-9b49-6abd631bb3e9.png)

You may now click start and Dbeaver will Import the data into your database.



#### You can now run the webshop!



