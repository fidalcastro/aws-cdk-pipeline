import os
from aws_cdk import (
	core, 
	aws_codepipeline,
	aws_codepipeline_actions,
	aws_codebuild,
	aws_codecommit,
	aws_iam
)
from aws_cdk.aws_lambda import InlineCode

class Pipeline(core.Stack):

	def __init__(self, scope: core.App, id: str, **kwargs) -> None:
		super().__init__(scope, id, **kwargs)
		# IAM Policies
		
		# CodeBuild Build Project
		sam_build = aws_codebuild.PipelineProject(self, "Sam Build", 
			build_spec=aws_codebuild.BuildSpec.from_source_filename("pipeline/buildspec.yml"),
			environment=aws_codebuild.BuildEnvironment(build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0)
		)
		for statement in self.get_iam_policies():
			sam_build.add_to_role_policy(statement)

		sam_deploy = aws_codebuild.PipelineProject(self, "Sam Deploy",
			build_spec=aws_codebuild.BuildSpec.from_source_filename("pipeline/deployspec.yml"),
			environment=aws_codebuild.BuildEnvironment(build_image=aws_codebuild.LinuxBuildImage.STANDARD_5_0)
		)
		for statement in self.get_iam_policies():
			sam_deploy.add_to_role_policy(statement)

		# Creating a pipeline
		pipeline = aws_codepipeline.Pipeline(self, "Pipeline", pipeline_name='hello-world-pipeline')

		# stage
		source_stage  = pipeline.add_stage(stage_name='Source')
		approve_stage = pipeline.add_stage(stage_name='Approve')
		build_stage   = pipeline.add_stage(stage_name='Build')
		deploy_stage  = pipeline.add_stage(stage_name='Deploy')

		# actions
		source_ouput_artifact = aws_codepipeline.Artifact("SourceArtifact")
		source_stage.add_action(aws_codepipeline_actions.CodeCommitSourceAction(
			action_name="Source",
			repository=aws_codecommit.Repository.from_repository_name(self, "Get Repo", "cdk-demo"),
			branch="main",
			output= source_ouput_artifact
		))

		approve_stage.add_action(aws_codepipeline_actions.ManualApprovalAction(
			action_name="Approve"
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

	def get_iam_policies(self):
		return [
			aws_iam.PolicyStatement(
				sid='CloudFormationTemplate',
				actions=['cloudformation:CreateChangeSet'],
				effect=aws_iam.Effect.ALLOW,
				resources=["arn:aws:cloudformation:*:aws:transform/Serverless-2016-10-31"]
			),
			aws_iam.PolicyStatement(
				sid='CloudFormationStack',
				actions=[
					"cloudformation:CreateChangeSet",
					"cloudformation:DeleteStack",
					"cloudformation:DescribeChangeSet",
					"cloudformation:DescribeStackEvents",
					"cloudformation:DescribeStacks",
					"cloudformation:ExecuteChangeSet",
					"cloudformation:GetTemplateSummary"
            	],
				resources=["*"],
				effect=aws_iam.Effect.ALLOW,
			),
			aws_iam.PolicyStatement(
				sid='S3',
				actions=[
					"s3:CreateBucket",
					"s3:GetObject",
					"s3:PutObject"
            	],
				resources=["arn:aws:s3:::*/*"],
				effect=aws_iam.Effect.ALLOW,
			),
			aws_iam.PolicyStatement(
				sid='Lambda',
				actions=[
					"lambda:AddPermission",
					"lambda:CreateFunction",
					"lambda:DeleteFunction",
					"lambda:GetFunction",
					"lambda:GetFunctionConfiguration",
					"lambda:ListTags",
					"lambda:RemovePermission",
					"lambda:TagResource",
					"lambda:UntagResource",
					"lambda:UpdateFunctionCode",
					"lambda:UpdateFunctionConfiguration"
            	],
				resources=["*"],
				effect=aws_iam.Effect.ALLOW,
			),
			aws_iam.PolicyStatement(
				sid='IAM',
				actions=[
					"iam:CreateRole",
					"iam:AttachRolePolicy",
					"iam:DeleteRole",
					"iam:DetachRolePolicy",
					"iam:GetRole",
					"iam:PassRole",
					"iam:TagRole"
            	],
				resources=["*"],
				effect=aws_iam.Effect.ALLOW,
			),
			aws_iam.PolicyStatement(
				sid='APIGateway',
				actions=[
					"apigateway:DELETE",
					"apigateway:GET",
					"apigateway:PATCH",
					"apigateway:POST",
					"apigateway:PUT"
            	],
				resources=["arn:aws:apigateway:*::*"],
				effect=aws_iam.Effect.ALLOW,
			)
		]