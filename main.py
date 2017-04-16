# -*- coding: utf-8 -*-

import xlwt
import vk
import os
from experiment import Experiment
from excel_writer import ExcelWriter
from logs import logger
from vk.exceptions import VkAPIError
import pickle

import string
from users_info_provider import UsersInfoProvider
from personal_info import PersonalInfo
from personal_info import encode_str
from excel_writer import ExcelWriter

def test():
    session = vk.AuthSession(app_id=5966499, scope = 'offline, market', user_login="", user_password="")
    api = vk.API(session, timeout=100)
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
    group_markets = [(104001319, 0)]
    group_ids = ", ".join(map(lambda pair: "\"-" + str(pair[0]) + "\"", group_markets))
    album_ids = map(lambda pair: pair[1], group_markets)
    code = string.Template(code.replace('\n', '')).substitute(group_ids=group_ids, album_ids=album_ids,
                                                              count=len(group_markets))

    response = None
    try:
        response = api.execute(code=code)
    except VkAPIError as err:
        if err.code != 10:
            raise err
    print response



def main():
    session = vk.AuthSession(app_id=5966499, scope = 'offline, market', user_login="79523919471", user_password="software389")
    experiment = Experiment(vk.API(session, timeout=100), group1_id='icommunity', group2_id='0s_android', count_per_group=500, use_cache=True)
    users_data = experiment.fetch_experiment_data()

    output_filename = 'output.xls'
    try:
        os.remove(output_filename)
    except OSError:
        pass

    excel_writer = ExcelWriter(output_filename)
    excel_writer.write_users_to_file(users_data)

    logger.debug("Completed success")


def test2():
    u = PersonalInfo({})
    u.groups_list = 'fsdfsd, fsdfsdf, fsdf'
    u.uid = 111
    u.city_name = 'new'

    u1 = PersonalInfo({})
    u1.groups_list = 'aaa'
    u1.uid = 333
    u1.city_name = 'old'
    try:
        with open('test.pickle', 'wb') as handle:
            pickle.dump([u, u1], handle, protocol=pickle.HIGHEST_PROTOCOL)
    except IOError:
        pass

    try:
        with open('test.pickle', 'rb') as handle:
            res = pickle.load(handle)
            for i in res:
                print i
    except IOError:
        pass

if __name__ == '__main__':
    main()
