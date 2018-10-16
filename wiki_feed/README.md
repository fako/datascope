Wiki Feed
=========

A project to allow editors to create customized feeds about Wikipedia pages.

Manual deploy
-------------

Because of infratructure changes the deploy process has to be done manually.
Follow these steps after uploading the artefacts:

```bash
cp /home/fako/uploads/datascope/<version> /data/project/algo-news/artefacts/datascope/

```

Now become the tool and take control of the upload.

```bash
become algo-news
take artefacts/datascope/<version>
```

Then login to a Kubernetes pod an go to the installation directory with:

```bash
webservice --backend kubernetes python shell
cd artefacts/datascope/<version>
```

Time to make the installation:

```bash
deactivate
source env/bin/activate
```
