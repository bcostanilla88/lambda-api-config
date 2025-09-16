from typing import Optional


from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext


logger = Logger()


@logger.inject_lambda_context
def dummy_handler(event, context):
    logger.debug("Lambda app start")
    return 
