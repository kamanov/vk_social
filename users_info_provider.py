# -*- coding: utf-8 -*-
from __future__ import division
from personal_info import PersonalInfo
from time import sleep
import string
from logs import logger


class SortedList:

    def __init__(self, sort_predicate, limit):
        self.inner_list = []
        self.sort_predicate = sort_predicate
        self.limit = limit

    def insort(self, x):
        lo = 0
        hi = len(self.inner_list)
        while lo < hi:
            mid = (lo + hi) // 2
            if self.sort_predicate(self.inner_list[mid]) < self.sort_predicate(x):
                hi = mid
            else:
                lo = mid + 1
        self.inner_list.insert(lo, x)

    def append(self, added_list):
        sorted_list = sorted(added_list, key=lambda i: self.sort_predicate(i), reverse=True)
        for item in sorted_list:
            if len(self.inner_list) == self.limit and self.sort_predicate(item) < self.sort_predicate(self.inner_list[-1]):
                break
            self.insort(item)
        if len(self.inner_list) > self.limit:
            self.inner_list = self.inner_list[:self.limit]


class UsersInfoProvider:
    def __init__(self, api, result_limit, rating_predicate, max_rating):
        self.api = api
        self.rating_predicate = rating_predicate
        self.result_limit = result_limit
        self.requests_count = 0
        self.batch_size = 2000
        self.max_rating = max_rating

    def fetch_info_for_user_ids(self, user_ids):
        assert user_ids, "User ids should be valid"
        logger.debug("Start fetch info for users with count =%s", len(user_ids))
        result = SortedList(self.rating_predicate, self.result_limit)
        offset = 0
        last_percent_complete = 0
        while offset < len(user_ids):
            users = self.get_info_for_user_ids(user_ids[offset:offset+self.batch_size])
            result.append(users)
            offset += self.batch_size

            percent_complete = (offset / len(user_ids)) * 100
            if abs(last_percent_complete - percent_complete) > 5:
                last_percent_complete = percent_complete
                logger.debug("Fetch in progress : %s%%", last_percent_complete)

            if len(result.inner_list) == self.result_limit and self.rating_predicate(result.inner_list[-1]) == self.max_rating:
                break

        self.resolve_city_and_country_names_for_users(result.inner_list)
        logger.debug("Users info fetched with min rating %s", self.rating_predicate(result.inner_list[-1]))
        return result.inner_list

    def resolve_city_and_country_names_for_users(self, users):
        city_ids_to_resolve = map(lambda info: info.city_id, users)
        city_id_to_name = self.get_city_names_by_ids(city_ids_to_resolve)
        country_ids_to_resolve = map(lambda info: info.country_id, users)
        country_id_to_name = self.get_country_names_by_ids(country_ids_to_resolve)
        for user in users:
            user.set_country_name(country_id_to_name.get(user.country_id, ''))
            user.set_city_name(city_id_to_name.get(user.city_id, ''))

    def get_city_names_by_ids(self, city_ids):
        response = self.api.database.getCitiesById(city_ids=set(city_ids))
        result = {}
        for dictionary in response:
            city_id = dictionary.get('cid', 0)
            name = dictionary.get('name', '')
            result.update({city_id: name})
        return result

    def get_country_names_by_ids(self, city_ids):
        response = self.api.database.getCountriesById(country_ids=set(city_ids))
        result = {}
        for dictionary in response:
            country_id = dictionary.get('cid', 0)
            name = dictionary.get('name', '')
            result.update({country_id: name})
        return result

    def get_personal_info_for_user_ids(self, user_ids):
        response = self.api.users.get(user_ids=user_ids, fields=PersonalInfo.requared_request_fields())
        assert isinstance(response, list), "get users should return list of ids"
        return map(lambda dictionary: PersonalInfo(dictionary), response)

    def get_info_for_user_ids(self, user_ids):
        assert len(user_ids) <= self.batch_size, "It should be less than batch size"
        self.requests_count += 1
        if self.requests_count % 10 == 0:
            sleep(3)
        code = """
        var ids = $user_ids;
        var count = $count;
        var offset = 0;
        var result = [];
        while (offset < count) {
        result = result + API.users.get({\"user_ids\": ids.slice(offset, offset + 1000), \"fields\": [$fields]});
        offset = offset + 1000;
        };
        return result;
        """
        code = string.Template(code.replace('\n', '')).substitute(user_ids=user_ids, count=len(user_ids), fields=PersonalInfo.requared_request_fields())
        response = self.api.execute(code=code)
        assert isinstance(response, list), "get users should return list of ids"
        return map(lambda dictionary: PersonalInfo(dictionary), response)

