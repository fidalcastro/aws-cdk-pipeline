import os
from aws_cdk import (
	core, 
	aws_codepipeline,
	aws_codepipeline_actions,
	aws_codebuild,
	aws_codecommit
)
from aws_cdk.aws_lambda import InlineCode

class Pipeline(core.Stack):

	def __init__(self, scope: core.App, id: str, **kwargs) -> None:
		super().__init__(scope, id, **kwargs)
		# CodeBuild Build Project
		sam_build = aws_codebuild.PipelineProject(self, "Sam Build", 
			build_spec=aws_codebuild.BuildSpec.from_source_filename("pipeline/buildspec.yml")
		)

		sam_deploy = aws_codebuild.PipelineProject(self, "Sam Deploy",
			build_spec=aws_codebuild.BuildSpec.from_source_filename("pipeline/deployspec.yml")
		)

		# Creating a pipeline
		pipeline = aws_codepipeline.Pipeline(self, "Pipeline", pipeline_name='hello-world-pipeline')

		# stage
		source_stage = pipeline.add_stage(stage_name='Source')
		build_stage  = pipeline.add_stage(stage_name='Build')
		deploy_stage = pipeline.add_stage(stage_name='Deploy')

		# actions
		source_ouput_artifact = aws_codepipeline.Artifact("SourceArtifact")
		source_stage.add_action(aws_codepipeline_actions.CodeCommitSourceAction(
			action_name="Source",
			repository=aws_codecommit.Repository.from_repository_name(self, "Get Repo", "cdk-demo"),
			branch="main",
			output= source_ouput_artifact
		))

		build_output_artifact = aws_codepipeline.Artifact("BuildArtifact")
		build_stage.add_action(aws_codepipeline_actions.CodeBuildAction(
			action_name="SamBuild",
			input=source_ouput_artifact,
			outputs=[build_output_artifact],
			project=sam_build
		))

		deploy_stage.add_action(aws_codepipeline_actions.CodeBuildAction(
			action_name="SamDeploy",
			input=build_output_artifact,
			project=sam_deploy
		))