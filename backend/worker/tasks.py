from backend.worker.scheduler import app

@app.task
def job1():
    print("Deneme123")

