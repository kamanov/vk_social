# -*- coding: utf-8 -*-
import string
from time import sleep

"""   
 def get_user_ids_by_group_id(self, group_id, count):
        response = self.api.groups.getMembers(group_id=group_id, count=count)
        assert isinstance(response, dict), "getMembers should return dictionary"
        return response.get('users', [])
        
"""


class UserGroupsProvider:
    def __init__(self, api):
        self.api = api
        self.requests_count = 0
        self.batch_size = 25000

    def get_user_ids_for_group_id(self, group_id):
        limit = self.batch_size * 6
        offset = 0
        response = self.get_user_ids(group_id, offset)
        result = response
        while response and len(result) < limit:
            offset += len(response)
            response = self.get_user_ids(group_id, offset)
            result += response
        return result

    def get_user_ids(self, group_id, offset):
        self.requests_count += 1
        if self.requests_count % 10 == 0:
            sleep(3)
        code = """
        var response = API.groups.getMembers({\"group_id\": \"$group_id\", \"count\": 1000, \"offset\": $offset});
        var all_count = response.count;
        var local_offset = $offset;
        var limit = local_offset + 24000;
        var result = response.users;
        while (local_offset < all_count && local_offset < limit) {
        result = result + API.groups.getMembers({\"group_id\": \"$group_id\", \"count\": 1000, \"offset\": local_offset}).users;
        local_offset = local_offset + 1000;
        };
        return result;
        """
        code = string.Template(code.replace('\n','')).substitute(group_id=group_id, offset=offset)
        response = self.api.execute(code=code)
        return response

