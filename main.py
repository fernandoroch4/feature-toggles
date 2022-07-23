import os
import logging
from xml.sax.handler import feature_validation

from in_memory_cache import InMemoryFeatureTogglesCache
from errors import NotFoundNamespaceFeatureException

import boto3

LOG_LEVEL = int(os.getenv('LOG_LEVEL', 20))  # 20 -> info
EXPIRES_CACHE_IN_SECONDS = 300  # 5 minutes

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(LOG_LEVEL)


class FeatureToggles:

    ssm = boto3.client('ssm', region_name='us-east-1', endpoint_url='http://localhost:4566')
    cache: InMemoryFeatureTogglesCache
    validations: list = []
    namespace: str = None
    feature: str = None
    log: logging

    def __init__(self, namespace: str, validations: list, log: logging = logger) -> None:
        self.log = log
        self.namespace = namespace
        self.validations = validations
        self.cache = InMemoryFeatureTogglesCache(logger, namespace)
        self.log.info(f'starting FeatureToggles for namespace "{namespace}" and validation "{validations}"')

    def _retrieve_namespace_features(self) -> list:
        self.log.info(f'retrieving features for namespace "{self.namespace}"')
        response = self.ssm.get_parameters_by_path(
            Path=self.namespace,
            Recursive=True
        )

        if len(response['Parameters']) == 0:
            raise NotFoundNamespaceFeatureException(f'Not found namespace features "{self.namespace}"')

        parameters = {}
        for parameter in response['Parameters']:
            idx = parameter['Name'].split(f'{self.namespace}/')[1]
            parameters[idx] = parameter['Value']

        self.log.info(f"list of features retrieved '{parameters}'")

        return parameters

    def is_authorize(self, feature: str) -> bool:
        feature_validations = []

        in_cache = self.cache.get_cache(feature)
        if len(in_cache) > 0:
            feature_validations = in_cache
        else:
            feature_validations = self._retrieve_namespace_features()
            self.cache.set_cache(feature_validations)

        if feature in feature_validations:
            self.log.info(f'authorized to access feature "{feature}"')
            return True

        self.log.info(f'unauthorized to access feature "{feature}"')
        return False
