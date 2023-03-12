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


Installation
------------

After cloning this repo to the machine you want to install Data Scope on. 
Activate the environment where you want to install Data Scope into. 
Then go into the repo directory and run the following for a local installation.

```bash
pip install -r datascope/environments/development.txt
```

After this you need to set up the services used by Datascope through Docker. You can run:

```bash
docker-compose up --build
```

When the services are created by Docker for the first time
you can run the following docker-compose command to restart services.

```bash
docker-compose up
```


Roadmap
=======

The roadmap can be followed by keeping an eye on the project boards of this repo on GitHub.
