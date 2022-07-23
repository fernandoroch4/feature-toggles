import os
import logging
from datetime import date, datetime, timedelta

import boto3

LOG_LEVEL = int(os.getenv('LOG_LEVEL', 20))
EXPIRES_CACHE_IN_SECONDS = 300

logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(LOG_LEVEL)


class NotFoundNamespaceFeatureException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FeatureToggles:

    ssm = boto3.client('ssm', region_name='us-east-1', endpoint_url='http://localhost:4566')
    namespace_features_cached: object = {}
    expires_at: datetime = datetime.fromtimestamp(0)
    namespace: str = None
    feature: str = None
    validations: list = []
    log: logging

    def __init__(self, nasmespace: str, validations: list, log: logging = logger) -> None:
        self.log = log
        self.namespace = nasmespace
        self.validations = validations

        self.log.info(f'starting FeatureToggles for namespace "{self.namespace}" and validation "{self.validations}"')

    def _set_cache(self, nasmespace_features) -> None:

        self.log.info(f'cache: setting cache for namespace "{self.namespace}" with values "{nasmespace_features}"')

        self.namespace_features_cached[self.namespace] = nasmespace_features
        self.expires_at = datetime.now() + timedelta(seconds=EXPIRES_CACHE_IN_SECONDS)

        self.log.info(f'cache: setting cache to expires at "{self.expires_at}"')

    def _get_cache(self, full_feature_name) -> list:
        if self._expired_cache():
            self.namespace_features_cached[self.namespace] = []
            return []

        for _feature in self.namespace_features_cached[self.namespace]:
            if _feature['Name'] == full_feature_name:
                value = _feature['Value'] if isinstance(_feature['Value'], list) else [_feature['Value']]

                self.log.info(f'cache: hit for namespace "{self.namespace}" and feature "{full_feature_name}"')

                return value

        self.log.info(f'cache: miss for namespace "{self.namespace}" and feature "{full_feature_name}"')

        return []

    def _expired_cache(self) -> bool:
        if self.expires_at == datetime.fromtimestamp(0):
            self.log.info(f'cache: miss for namespace "{self.namespace}"')
            return True

        if datetime.now() >= self.expires_at:

            self.log.info(f'cache: miss for namespace "{self.namespace}"')
            self.log.info(f'cache: clearning for namespace "{self.namespace}"')

            return True
        return False

    def _retrieve_namespace_features(self) -> list:

        self.log.info(f'retrieving features for namespace "{self.namespace}"')

        response = self.ssm.get_parameters_by_path(
            Path=self.namespace,
            Recursive=True
        )

        if len(response['Parameters']) == 0:
            raise NotFoundNamespaceFeatureException(f'Not found namespace features "{self.namespace}"')

        self.log.info(f"list of features retrieved '{response['Parameters']}'")

        parameters = []
        for parameter in response['Parameters']:
            parameters.append({
                'Name': parameter['Name'],
                'Value': parameter['Value']
            })
        return parameters

    def has_access(self, feature: str) -> bool:
        namespace_features = []
        full_feature_name = f'{self.namespace}/{feature}'
        values_in_cache = self._get_cache(full_feature_name)
        if len(values_in_cache) > 0:
            namespace_features = values_in_cache

        namespace_features = self._retrieve_namespace_features()
        self._set_cache(namespace_features)

        for _nf in namespace_features:
            if _nf['Name'] == full_feature_name and _nf['Value'] in self.validations:

                self.log.info(f'authorized access for feature "{feature}"')

                return True

        self.log.info(f'unauthorized access for feature "{feature}"')

        return False
