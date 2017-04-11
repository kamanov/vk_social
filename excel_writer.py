import xlwt


class ExcelWriter:

    def __init__(self, filename):
        self.wb = xlwt.Workbook(encoding='utf-8')
        self.ws = self.wb.add_sheet('vk experiment')
        self.filename = filename

    def write_users_to_file(self, users):
        self.fill_header()

        for u_idx, user in enumerate(users):
            self.enumerate_columns_with_fun(lambda c_idx, column: self.ws.write(u_idx + 1, c_idx, getattr(user, column)))
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
                    'relation',
                    'political',
                    'people_main',
                    'life_main',
                    'smoking',
                    'alcohol',
                    'has_twitter',
                    'has_instagram',
                    'has_photo',
                    'has_mobile',
                    'has_site',
                    'can_add_wall_comments',
                    'can_post',
                    'can_see_all_posts',
                    'can_see_audio',
                    'can_write_private_message',
                    'has_military',
                    'graduation'
    )


