
from uuid import uuid4
import os


class JobCallback:
    def __init__(self, callback, kwargs = None):
        self.callback = callback
        self.kwargs = kwargs
        
    def run(self):
        self.callback(**self.kwargs)

class JobPrompt:
    def __init__(self, text = None, responses = None, ctx = None, callback = None):
        self.text = text
        self.responses = responses
        self.ctx = ctx
        self.response = None
        self.callback = callback

class JobFile:
    def __init__(self, label, filePath, autoDelete = False):
        self.label = label
        self.path = filePath
        self.autoDelete = autoDelete

    def toDict(self):
        return {
            "label": self.label,
            "path": self.path,
            "autoDelete": self.autoDelete,
            "exists": os.path.exists(self.path)
        }

class Job:
    def __init__(self, ctx = {}):
        self.uuid = str(uuid4())
        self.totalTasks = None
        self.completedTasks = None 
        self.status = None
        self.prompt : JobPrompt = None
        self.ctx = ctx
        self.statusCallbacks = {}
        self.log = []
        self.files: list[JobFile] = []

    def updateStatus(self, status):

        self.status = status
        self.log.append(status)
        if status in self.statusCallbacks:
            print("Running status callback for ", status)
            self.statusCallbacks[status].run()

    def addFile(self, file: JobFile):
        
        for f in self.files:
            if f.label == file.label:
                print(f"File with label {file.label} already exists")
                return False
        
        self.files.append(file)
        return True

    def getFile(self, key):
        for f in self.files:
            if f.label == key:
                return f
        return None
        

    def addStatusCallback(self, status, callback, kwargs = None):
        self.statusCallbacks[status] = JobCallback(callback, kwargs)


    def setPrompt(self, text, responses, ctx):
        self.prompt = JobPrompt(text, responses, ctx)

    def respond(self, response):
        self.prompt.response = response
        if self.prompt.callback:
            self.prompt.callback(response)

    def toDict(self):
        data =  {
            "uuid": self.uuid,
            "totalTasks": self.totalTasks,
            "completedTasks": self.completedTasks,
            "status": self.status,
            "ctx": self.ctx,
            "log": self.log,
        }

        if self.prompt:
            data["prompt"] = {
                "text": self.prompt.text,
                "responses": self.prompt.responses,
                "ctx": self.prompt.ctx,
                "response": self.prompt.response
        }
            
        if len(self.files) > 0:
            data["files"] = [f.toDict() for f in self.files]

        return data

class JobQueue:
    def __init__(self):
        self.queue: dict[int, list[Job]] = {}
    
    def createJob(self, conatinerId=0) -> Job:
        job = Job()
        self.addJob(conatinerId, job)
        return job

    def addJob(self, job: Job, containerId = 0):
        if containerId in self.queue:
            self.queue[containerId].append(job)
        else:
            self.queue[containerId] = [job]

    def getJobs(self, conatinerId =0) -> list[Job]:

        if conatinerId in self.queue:
            self.queue[conatinerId]
        else:
            return []
        
    def getJob(self, jobId, containerId=0) -> Job:
        if containerId in self.queue:
            for job in self.queue[containerId]:
                if job.uuid == jobId:
                    return job
        return None
    
    def removeJob(self,  jobId, containerId=0):
        if containerId in self.queue:  
            for job in self.queue[containerId]:
                if job.uuid == jobId:
                    for f in job.files:
                        if f.autoDelete and os.path.exists(f.path):
                            os.remove(f.path)

            self.queue[containerId] = [job for job in self.queue[containerId] if job.uuid != jobId]
        return None
    
    
