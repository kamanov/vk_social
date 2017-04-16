import xlwt


class ExcelWriter:

    def __init__(self, filename):
        self.wb = xlwt.Workbook(encoding='utf-8')
        self.ws = self.wb.add_sheet('vk experiment')
        self.filename = filename

    def write_users_to_file(self, users):
        self.fill_header()

        for u_idx, user in enumerate(users):
            def write_fun(c_idx, column):
                data = getattr(user, column)
                if isinstance(data, str) or isinstance(data, unicode) and len(data) >= 32767:
                    data = data[0:32764] + '...'
                self.ws.write(u_idx + 1, c_idx, data)
            self.enumerate_columns_with_fun(write_fun)
        self.wb.save(self.filename)

    def fill_header(self):
        self.enumerate_columns_with_fun(lambda idx, column: self.ws.write(0, idx, column))

    def enumerate_columns_with_fun(self, fun):
        for idx, column in enumerate(self.table_columns):
            fun(idx, column)

    table_columns = (
                    'experiment_group_id',
                    'sex',
                    'age',
                    'country_name',
                    'city_name',
                    'university_name',
                    'followers_count',
                    'occupation_type',
                    'groups_list',
                    'markets_list',
                    'movies',
                    'music',
                    'tv',
                    'books',
                    'interests',
                    'relation',
                    'political',
                    'people_main',
                    'life_main',
                    'smoking',
                    'alcohol',
                    'can_add_wall_comments',
                    'can_post',
                    'can_see_all_posts',
                    'can_see_audio',
                    'can_write_private_message'
    )


