# -*- coding: utf-8 -*-
from __future__ import division
from personal_info import PersonalInfo
from personal_info import encode_str
from time import sleep
import string
from logs import logger
from vk.exceptions import VkAPIError


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

    def fetch_info_for_user_ids(self, user_ids, save_selected_ids_cache_block):
        assert user_ids, "User ids should be valid"
        logger.debug("Start fetch info for users with count =%s", len(user_ids))
        result = SortedList(self.rating_predicate, self.result_limit)
        offset = 0
        last_percent_complete = 0
        while offset < len(user_ids):
            users = self.get_info_for_user_ids(user_ids[offset:offset+self.batch_size])
            result.append(users)
            offset += self.batch_size

            percent_complete = (min(offset, len(user_ids)) / len(user_ids)) * 100
            if abs(last_percent_complete - percent_complete) > 5:
                last_percent_complete = percent_complete
                logger.debug("Fetch personal info in progress : %s%%", last_percent_complete)

            if len(result.inner_list) == self.result_limit and self.rating_predicate(result.inner_list[-1]) == self.max_rating:
                break
        save_selected_ids_cache_block(map(lambda user:user.uid, result.inner_list))
        self.resolve_city_and_country_names_for_users(result.inner_list)
        self.fill_groups_and_markets_for_users(result.inner_list)
        logger.debug("Users info fetched with min rating %s and max rating %s", self.rating_predicate(result.inner_list[-1]), self.max_rating)
        return result.inner_list

    def fill_groups_and_markets_for_users(self, users):
        group_list_batch_size = 25
        offset = 0
        last_percent_complete = 0

        while offset < len(users):
            percent_complete = (min(offset, len(users)) / len(users)) * 100
            if abs(last_percent_complete - percent_complete) > 5:
                last_percent_complete = percent_complete
                logger.debug("Fetch groups and markets in progress : %s%%", last_percent_complete)

            batch_users = users[offset: offset+group_list_batch_size]
            uid_to_groups = self.fetch_group_list_for_user_ids(map(lambda user: user.uid, batch_users))
            self.fill_group_list_for_users(batch_users, uid_to_groups)
            self.fill_markets_for_users(batch_users, uid_to_groups)
            offset += group_list_batch_size
        return users

    def fill_markets_for_users(self, users, uid_to_groups):
        for user in users:
            groups = uid_to_groups.get(user.uid, [])
            group_markets = []
            for group in groups:
                gid = group.get('gid', 0)
                market = group.get('market', {})
                if market.get('enabled', False):
                    market_id = market.get('main_album_id', 0)
                    group_markets.append((gid, market_id))
            if group_markets:
                markets_info = self.fetch_markets_info(group_markets)
                user.markets_list = ', '.join(map(lambda market: encode_str(market), markets_info))

    def fetch_markets_info(self, group_markets):
        self.normalize_request_speed()

        markets_max_size = 25
        group_markets = group_markets[0:markets_max_size]
        code = """
        var group_ids = [$group_ids];
        var album_ids = $album_ids;
        var count = $count;
        var offset = 0;
        var result = [];
        while (offset < count) {
        var gid = group_ids[offset];
        var album_id = album_ids[offset];
        var g = API.market.get({\"owner_id\": gid, \"album_id\": album_id});
        if (g) {
        result = result + g.slice(1, g[0])@.category@.section@.name;
        }
        offset = offset + 1;
        };
        return result;
        """
        group_ids = ", ".join(map(lambda pair: "\"-" + str(pair[0]) + "\"", group_markets))
        album_ids = map(lambda pair: pair[1], group_markets)
        code = string.Template(code.replace('\n', '')).substitute(group_ids=group_ids, album_ids=album_ids,
                                                                  count=len(group_markets))

        response = []
        try:
            response = self.api.execute(code=code)
        except VkAPIError as err:
            logger.error("Load market error")
            if err.code != 10:
                raise err
        return list(set(response))


    def fill_group_list_for_users(self, users, uid_to_groups):
        for user in users:
            groups = uid_to_groups.get(user.uid, [])
            user.groups_list = ', '.join(map(lambda dictionary: encode_str(dictionary.get('name', '')), groups))

    def fetch_group_list_for_user_ids(self, user_ids):
        self.normalize_request_speed()
        code = """
        var ids = $user_ids;
        var count = $count;
        var offset = 0;
        var result = {};
        while (offset < count) {
        var uid = ids[offset];
        var g = API.groups.get({\"user_id\": uid, \"extended\": 1, \"fields\": [$fields]});
        if (g) {
        var res = g.slice(1, g[0]);
        result.push([uid, res]);
        }
        offset = offset + 1;
        };
        return result;
        """
        code = string.Template(code.replace('\n', '')).substitute(user_ids=user_ids, count=len(user_ids),
                                                                  fields='\"name\", \"market\"')
        response = self.api.execute(code=code)
        return dict(response)

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

    def normalize_request_speed(self):
        self.requests_count += 1
        if self.requests_count % 5 == 0:
            sleep(3)

    def get_personal_info_for_user_ids(self, user_ids):
        response = self.api.users.get(user_ids=user_ids, fields=PersonalInfo.requared_request_fields())
        assert isinstance(response, list), "get users should return list of ids"
        return map(lambda dictionary: PersonalInfo(dictionary), response)

    def get_info_for_user_ids(self, user_ids):
        assert len(user_ids) <= self.batch_size, "It should be less than batch size"
        self.normalize_request_speed()
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

