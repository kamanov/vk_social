# -*- coding: utf-8 -*-

from logs import logger
from users_info_provider import UsersInfoProvider
from user_groups_provider import UserGroupsProvider
from personal_info import PersonalInfo
from itertools import cycle


class Experiment:
    def __init__(self, api, group1_id, group2_id, count_per_group):
        self.api = api
        self.group1_id = group1_id
        self.group2_id = group2_id
        self.count_per_group = count_per_group

    def fetch_experiment_data(self):
        logger.debug("Experiment fetch with  group1=%s, groupd2=%s, count_per_group=%s", self.group1_id, self.group2_id, self.count_per_group)

        user_groups_provider = UserGroupsProvider(self.api)
        users1_ids = user_groups_provider.get_user_ids_for_group_id(self.group1_id)
        logger.debug("Fetched first group with actual count=%s", len(users1_ids))
        users2_ids = user_groups_provider.get_user_ids_for_group_id(self.group2_id)
        logger.debug("Fetched second group with actual count=%s", len(users2_ids))

        # remove duplicates
        if len(users1_ids) > len(users2_ids):
            users1_ids = list(set(users1_ids) - set(users2_ids))
        else:
            users2_ids = list(set(users2_ids) - set(users1_ids))

        users_provider = UsersInfoProvider(self.api, self.count_per_group, self.experiment_rating_for_user, self.max_rating)
        users1 = users_provider.fetch_info_for_user_ids(users1_ids)
        users2 = users_provider.fetch_info_for_user_ids(users2_ids)

        min_count = min(len(users1), len(users2))
        logger.debug("Actual experiment count=%s", min_count)
        for user in users1:
            user.experiment_group_id = self.group1_id

        for user in users2:
            user.experiment_group_id = self.group2_id

        return users1 + users2

    @staticmethod
    def experiment_rating_for_user(user):
        class Nonlocal:
            def __init__(self):
                pass
            rating = 0

        def acc_field(field, weight):
            Nonlocal.rating += weight if field else 0

        acc_field(user.age, weight=3)
        acc_field(user.occupation_type, weight=2)
        acc_field(user.relation, weight=2)
        acc_field(user.country_id, weight=2)
        acc_field(user.city_id, weight=2)
        acc_field(user.university_name, weight=1)
        acc_field(user.political, weight=1)
        acc_field(user.people_main, weight=1)
        acc_field(user.life_main, weight=1)
        acc_field(user.smoking, weight=1)
        acc_field(user.alcohol, weight=1)
        return Nonlocal.rating

    max_rating = 17
