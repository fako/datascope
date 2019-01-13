Wiki Feed
=========

A project to allow editors to create customized feeds about Wikipedia pages.

Manual deploy
-------------

Because of infratructure changes the deploy process has to be done manually.
Follow these steps after uploading the artefacts:

```bash
cp -r /home/fako/uploads/datascope/<version> /data/project/algo-news/artefacts/datascope/
cp /data/project/algo-news/artefacts/datascope/<version>/src/datascope/wsgi.py /data/project/algo-news/artefacts/datascope/<version>/src/app.py

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
/usr/bin/python3 -m venv --copies env
source env/bin/activate
pip install --upgrade pip
pip install -r src/datascope/environments/wikipedia_requirements.txt
```

Now we need to setup Django:

```bash
cp src/datascope/environments/wikipedia_settings.py src/datascope/settings.py
echo 'DATASCOPE_VERSION = "<version>"' > src/datascope/bootstrap.py
cat src/datascope/environments/wikipedia_bootstrap.py >> src/datascope/bootstrap.py
cp /data/project/algo-news/secrets.py src/datascope/secrets.py
cd src
python manage.py collectstatic --noinput
cp -r system/files/static ../
```

And last but not least we can deploy once we exit the pod with CTRL-D

```bash
ln -sfn artefacts/datascope/<version> datascope
webservice --backend=kubernetes python stop
webservice --backend=kubernetes python start
kubectl delete deployment algo-news.celery
kubectl create -f /data/project/algo-news/deployment.yaml
```

Once the deployment is made you can control it with:

```bash
kubectl get pods
kubectl logs <name>
kubectl delete deployment algo-news.celery
```
