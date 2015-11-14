from celery import current_app as app


@app.task(name="core.test_task")
def test_task():
    return "test task has run"