# -*- coding: utf-8 -*-

from logs import logger
from users_info_provider import UsersInfoProvider
from user_groups_provider import UserGroupsProvider
import pickle


class Experiment:
    def __init__(self, api, group1_id, group2_id, count_per_group, use_cache):
        self.api = api
        self.group1_id = group1_id
        self.group2_id = group2_id
        self.count_per_group = count_per_group
        self.cache = {}
        self.use_cache = use_cache

    def fetch_experiment_data(self):
        logger.debug("Experiment fetch with  group1=%s, groupd2=%s, count_per_group=%s", self.group1_id, self.group2_id, self.count_per_group)
        result = self.try_load_experiment_result()
        if result:
            return result

        users1_ids = []
        users2_ids = []
        if self.use_cache:
            self.load_cache()
            users1_ids = self.cache.get(self.group1_id, [])
            users2_ids = self.cache.get(self.group2_id, [])

        user_groups_provider = UserGroupsProvider(self.api)
        groups_to_update_cache = []

        if not users1_ids:
            groups_to_update_cache.append(self.group1_id)
            users1_ids = user_groups_provider.get_user_ids_for_group_id(self.group1_id)
            logger.debug("Fetched first group with actual count=%s", len(users1_ids))
        if not users2_ids:
            groups_to_update_cache.append(self.group2_id)
            users2_ids = user_groups_provider.get_user_ids_for_group_id(self.group2_id)
            logger.debug("Fetched second group with actual count=%s", len(users2_ids))

        # remove duplicates
        if len(users1_ids) > len(users2_ids):
            users1_ids = list(set(users1_ids) - set(users2_ids))
        else:
            users2_ids = list(set(users2_ids) - set(users1_ids))

        users_provider = UsersInfoProvider(self.api,
                                           self.count_per_group,
                                           self.experiment_rating_for_user,
                                           sum(self.rating_field_to_weight.itervalues()))

        def save_cache_for_group(group):
            def fun(ids):
                if group in groups_to_update_cache:
                    self.cache[group] = ids
            return fun
        users1 = users_provider.fetch_info_for_user_ids(users1_ids, save_cache_for_group(self.group1_id))
        self.save_cache()
        users2 = users_provider.fetch_info_for_user_ids(users2_ids, save_cache_for_group(self.group2_id))
        self.save_cache()

        min_count = min(len(users1), len(users2))
        logger.debug("Actual experiment count=%s", min_count)
        for user in users1:
            user.experiment_group_id = self.group1_id

        for user in users2:
            user.experiment_group_id = self.group2_id
        result = users1 + users2
        self.save_result(result)
        return result

    @staticmethod
    def save_result(result):
        try:
            with open('full_result.pickle', 'wb') as handle:
                pickle.dump(result, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except IOError:
            pass

    @staticmethod
    def try_load_experiment_result():
        try:
            with open('full_result.pickle', 'rb') as handle:
                return pickle.load(handle)
        except IOError:
            pass
        return []

    def save_cache(self):
        try:
            with open('cache.pickle', 'wb') as handle:
                pickle.dump(self.cache, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except IOError:
            pass

    def load_cache(self):
        try:
            with open('cache.pickle', 'rb') as handle:
                self.cache = pickle.load(handle)
        except IOError:
            pass

    @staticmethod
    def experiment_rating_for_user(user):
        rating = 0
        for field, weight in Experiment.rating_field_to_weight.iteritems():
            if getattr(user, field):
                rating += weight
        return rating

    rating_field_to_weight = {
        "age": 100,
        "country_id": 90,
        "city_id": 90,
        "occupation_type": 70,
        "relation": 70,
        "interests": 70,
        "movies": 70,
        "music": 70,
        "tv": 70,
        "books": 70,
        "political": 50,
        "people_main": 50,
        "life_main": 50,
        "smoking": 50,
        "alcohol": 50,
        "university_name": 30
    }
