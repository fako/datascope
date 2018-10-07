Future Fashion
==============

Future Fashion explores ways in which second hand clothing sales can be stimulated.

Installation
------------

Run the following commands to install an inventory to use with Future Fashion:
* Download the inventory files from Google Drive
* Place these files inside of ```future_fashion/data/media/future_fashion``` under a unique name
* Make sure that you run the image_recognition service under ```localhost:2001``` with the ```clothing_type``` project
* Now run ```./manage.py grow_community InventoryCommunity -a <unique-name>```
* Still command will take a while
* To use the service now run ```./manage.py store_clothing_frames```

After these commands you should be able to call the service under 
```/data/v1/future-fashion/service/<unique-name>/?<colors-by-type>```. 
[Like this localhost example](http://localhost:8000/data/v1/future-fashion/service/pilot/?$top=228,85,52&$bottom=108,25,63&$accessories=164,192,217).



Deploy
------

Before you import Future Fashion for a deploy make sure to run: ```./manage.py dump_community InventoryCommunity -a pilot```. 
This ensures that the data will become available on the server.
After installation but before deploy run ```./manage.py load_community InventoryCommunity -a pilot```
on the server to load the data.
