Data Scope
==========

Data Scope is a data mashup framework meant to facilitate the execution of complex search queries. 
Think about search queries like: “which websites name at least three experts from field X?”, 
“which websites support stance X?”, “what are iconical images for X in culture A, B & C?” and 
“which people are known for similar reasons that person X is known for?”. 
Data Scope allows a programmer to reach over walled gardens of information that he/she may need and
combine the information into new information. 
Due to its nature Data Scope is very suitable for software that tries to break out of filter bubbels.


Prerequisites
-------------

This is the environment that you should have on your machine before installing Data Scope.

* Docker

Optionally you may also want to install

* PhantomJS (for web scraping)

Installation
------------

After cloning this repo to the machine you want to install Data Scope on. 
Activate the environment where you want to install Data Scope into. 
Then go into the repo directory and run the following for a local install.

```bash
cp datascope/environments/local_bootstrap.py datascope/bootstrap.py
cp datascope/environments/local_settings.py datascope/settings.py
cp datascope/environments/secrets_example.py datascope/secrets.py
pip install -r datascope/environments/local_requirements.txt
```

Alternatively you can change ```local``` in these commands to ```digital-ocean``` or ```wikipedia``` 
for an installation in the Digital Ocean or Wikipedia cloud respectively.

Then edit the ```datascope/bootstrap.py```, ```datascope/settings.py``` and ```datascope/secrets.py``` 
to correct the setup of the machine/cloud.

After this you need to setup the services used by Datascope through Docker. You can run:

```bash
docker volume create --name postgres-data
docker-compose up --build
```

When the services are created by Docker for the first time
you can run the following docker-compose command to restart services.

```bash
docker-compose up
```


Next steps
----------

Depending on which project you're working on you may want to run additional installation steps. 
These steps are outlined in the readme's of these projects. Below are the links to all current projects:

* [Wiki Feed](wiki_feed/README.md)
* [Union Scope](visual_translations/README.md)
* [Robo Roaster](setup_utrecht/README.md)
* [Future Fashion](future_fashion/README.md)

Roadmap
=======

The roadmap can be followed by keeping an eye on the project boards of this repo on GitHub.
