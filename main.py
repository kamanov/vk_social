# -*- coding: utf-8 -*-

import vk
import os
from experiment import Experiment
from excel_writer import ExcelWriter
from logs import logger



def main():
    session = vk.Session(
                         access_token='') #your vk access token
    experiment = Experiment(vk.API(session, timeout=100), group1_id='icommunity', group2_id='0s_android', count_per_group=500)
    users_data = experiment.fetch_experiment_data()

    output_filename = 'output.xls'
    try:
        os.remove(output_filename)
    except OSError:
        pass

    excel_writer = ExcelWriter(output_filename)
    excel_writer.write_users_to_file(users_data)

    logger.debug("Completed success")


if __name__ == '__main__':
    main()
