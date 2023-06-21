from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr_assets as ecr_assets,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns,
    App,
    Stack,
    CfnOutput,
    Duration,
)


class ChatUIStack(Stack):
    def __init__(self, scope: Construct, construct_id: str):
        super().__init__(scope, construct_id)

        # ==============================
        # ======= CFN PARAMETERS =======
        # ==============================
        port = 8501
        name = "chatui"

        # ==================================================
        # ================= IAM ROLE =======================
        # ==================================================
        role = iam.Role(
            scope=self,
            id="TASKROLE",
            assumed_by=iam.ServicePrincipal(service="ecs-tasks.amazonaws.com"),
        )
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonECS_FullAccess")
        )
        role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
        )

        # ==================================================
        # ==================== VPC =========================
        # ==================================================
        vpc = ec2.Vpc(self, "vpc", ip_addresses=ec2.IpAddresses.cidr('10.1.0.0/16'), max_azs=2,)

        # ==================================================
        # =============== FARGATE SERVICE ==================
        # ==================================================
        cluster = ecs.Cluster(scope=self, id="cluster", cluster_name=name, vpc=vpc)

        task_definition = ecs.FargateTaskDefinition(
            scope=self,
            id="taskdefinition",
            task_role=role,
            cpu=4 * 1024,
            memory_limit_mib=8 * 1024,
            runtime_platform=ecs.RuntimePlatform(
                cpu_architecture=ecs.CpuArchitecture.ARM64,
                operating_system_family=ecs.OperatingSystemFamily.LINUX
            )
        )

        container = task_definition.add_container(
            id="Container",
            image=ecs.ContainerImage.from_asset(
                directory="chat_ui",
                platform=ecr_assets.Platform.LINUX_ARM64
            ),
            logging=ecs.LogDriver.aws_logs(stream_prefix=name),
        )
        port_mapping = ecs.PortMapping(
            container_port=port, host_port=port, protocol=ecs.Protocol.TCP
        )
        container.add_port_mappings(port_mapping)

        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            scope=self,
            id="service",
            service_name=name,
            cluster=cluster,
            task_definition=task_definition,
        )

        # Setup security group
        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(port),
            description="Allow inbound from VPC for chatui",
        )

        # Setup autoscaling policy
        scaling = fargate_service.service.auto_scale_task_count(max_capacity=2)
        scaling.scale_on_cpu_utilization(
            id="autoscaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )
        # ==================================================
        # =================== OUTPUTS ======================
        # ==================================================
        CfnOutput(
            scope=self,
            id="LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name,
        )


app = App()
ChatUIStack(app, "ChatUIStack")
app.synth()
