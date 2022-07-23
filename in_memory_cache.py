import os
import logging
from datetime import datetime, timedelta

EXPIRES_CACHE_IN_SECONDS = int(os.getenv('LOG_LEVEL', 300))


class InMemoryFeatureTogglesCache:

    log: logging = None
    feature_namespace: str = None
    feature_namespace_cached: object = {}
    expires_at: datetime = datetime.fromtimestamp(0)

    def __init__(self, log: logging, feature_namespace: str) -> None:
        self.log = log
        self.feature_namespace = feature_namespace
        self.feature_namespace_cached[feature_namespace] = {}

    def _expired_cache(self) -> bool:
        if self.expires_at == datetime.fromtimestamp(0):
            self.log.info(f'cache: miss for feature namespace "{self.feature_namespace}"')
            return True

        if datetime.now() >= self.expires_at:
            self.log.info(f'cache: expired, reseting cache for feature namespace "{self.feature_namespace}"')
            self.feature_namespace_cached[self.feature_namespace] = []
            return True
        return False

    def _set_exprires(self, date_to_expires: datetime) -> None:
        self.log.info(f'cache: setting cache to expires at "{date_to_expires}"')
        self.expires_at = date_to_expires

    def set_cache(self, features: object, expires_in_seconds: int = EXPIRES_CACHE_IN_SECONDS) -> None:
        for feature in features:
            self.log.info(f'cache: setting cache for namespace "{self.feature_namespace}" and feature "{feature}" with values "{features[feature]}"')
            self.feature_namespace_cached[self.feature_namespace][feature] = features[feature]
        self._set_exprires(datetime.now() + timedelta(seconds=expires_in_seconds))

    def get_cache(self, feature) -> list:
        if self._expired_cache():
            return []

        feature_values = self.feature_namespace_cached[self.feature_namespace].get(feature, [])
        if len(feature_values) == 0:
            self.log.info(f'cache: miss for namespace "{self.feature_namespace}" and feature "{feature}"')
            return []

        self.log.info(f'cache: hit for namespace "{self.feature_namespace}" and feature "{feature}"')
        return feature_values
