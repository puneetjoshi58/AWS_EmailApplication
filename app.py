#!/usr/bin/env python3

import aws_cdk as cdk

from message_scheduling_app.message_scheduling_app_stack import MessageSchedulingAppStack


app = cdk.App()
MessageSchedulingAppStack(app, "message-scheduling-app")

app.synth()
