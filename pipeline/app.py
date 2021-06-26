from aws_cdk import (
        core
)

from Pipeline import Pipeline

app = core.App()
pipeline = Pipeline(app, "hello-world-pipeline")
app.synth()
