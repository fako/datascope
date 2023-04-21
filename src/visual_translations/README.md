Union Scope
===========

Union Scope shows how images on the web around the same topic, differ across countries in the European Union. 
We tend to think that words like “pension” or “immigrants” have similar visual representations across Europe. 
Union Scope reveals some striking differences between countries. 
It is an interactive installation where everybody can play with to discover more about Europe.

Installation
------------

For Union Scope to work you'll need to enable websockets.
This can be done by installing the websockets requirements.

```bash
pip install -r datascope/requirements/websockets.txt
```

And then setting USE_WEBSOCKETS to True in  ```datascope/boostrap.py```
 
Getting the data
----------------

You can get a new snapshot of the data through the following steps:
* Up the [Google API limit](https://console.cloud.google.com/apis/api/customsearch.googleapis.com/quotas?project=optical-wall-133808&supportedpurview=project) to a sufficiently high limit per day.
* Run ```./manage.py generate_eu_visual_translations -a <word>``` where <word> is the term you're interested in.
* Use the ```delete_word``` and ```delete_image``` commands to clean the data.
* Run ```./manage.py generate_image_grids -a <word>``` to clean the grid for a term. 
* Lower Google API limit to default when you're done. 
