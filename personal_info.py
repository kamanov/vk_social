# -*- coding: utf-8 -*-

from datetime import datetime


class PersonalInfo:
    def __init__(self, dictionary):
        self.uid = dictionary.get('uid', 0)
        self.sex = self.extract_sex(dictionary)
        self.age = self.extract_age(dictionary)
        self.city_id = dictionary.get('city', 0)
        self.country_id = dictionary.get('country', 0)
        self.university_name = encode_str(dictionary.get('university_name', ''))
        self.followers_count = dictionary.get('followers_count', 0)
        self.occupation_type = encode_str(dictionary.get('occupation', {}).get('type', ''))
        self.relation = self.extract_relation(dictionary)
        about = dictionary.get('personal', {})
        self.political = self.extract_political(about)
        self.people_main = self.extract_people_main(about)
        self.life_main = self.extract_life_main(about)
        self.smoking = self.extract_smoking(about)
        self.alcohol = self.extract_alcohol(about)
        self.can_add_wall_comments = bool_str(dictionary.get('wall_comments'))
        self.can_post = bool_str(dictionary.get('can_post'))
        self.can_see_all_posts = bool_str(dictionary.get('can_see_all_posts'))
        self.can_see_audio = bool_str(dictionary.get('can_see_audio'))
        self.can_write_private_message = bool_str(dictionary.get('can_write_private_message'))
        self.movies = encode_str(dictionary.get('movies', ''))
        self.music = encode_str(dictionary.get('music', ''))
        self.tv = encode_str(dictionary.get('tv', ''))
        self.books = encode_str(dictionary.get('books', ''))
        self.interests = encode_str(dictionary.get('interests', ''))

        self.groups_list = ''
        self.markets_list = ''
        self.country_name = ''
        self.city_name = ''
        self.experiment_group_id = ''

    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}={value}".format(key=key, value=self.__dict__[key]))
        return '\n'.join(sb)

    def __repr__(self):
        return self.__str__()

    def set_country_name(self, country_name):
        self.country_name = encode_str(country_name)

    def set_city_name(self, city_name):
        self.city_name = encode_str(city_name)

    @staticmethod
    def extract_alcohol(dictionary):
        alcohol_map = {
            1: "резко негативное",
            2: "негативное",
            3: "компромиссное",
            4: "нейтральное",
            5: "положительное"
        }
        return alcohol_map.get(dictionary.get('alcohol', 0), '')

    @staticmethod
    def extract_smoking(dictionary):
        smoking_map = {
            1: "резко негативное",
            2: "негативное",
            3: "компромиссное",
            4: "нейтральное",
            5: "положительное"
        }
        return smoking_map.get(dictionary.get('smoking', 0), '')

    @staticmethod
    def extract_life_main(dictionary):
        life_main_map = {
            1: "семья и дети",
            2: "карьера и деньги",
            3: "развлечения и отдых",
            4: "наука и исследования",
            5: "совершенствование мира",
            6: "саморазвитие",
            7: "красота и искусство",
            8: "слава и влияние"
        }
        return life_main_map.get(dictionary.get('life_main', 0), '')

    @staticmethod
    def extract_people_main(dictionary):
        people_main_map = {
            1: "ум и креативность",
            2: "доброта и честность",
            3: "красота и здоровье",
            4: "власть и богатство",
            5: "смелость и упорство",
            6: "юмор и жизнелюбие"
        }
        return people_main_map.get(dictionary.get('people_main', 0), '')

    @staticmethod
    def extract_political(dictionary):
        political_map = {
            1: "коммунистические",
            2: "социалистические",
            3: "умеренные",
            4: "либеральные",
            5: "консервативные",
            6: "монархические",
            7: "ультраконсервативные",
            8: "индифферентные",
            9: "либертарианские"
        }
        return political_map.get(dictionary.get('political', 0), '')

    @staticmethod
    def extract_relation(dictionary):
        relation_map = {
            1: "не женат/не замужем",
            2: "есть друг/подруга",
            3: "помолвлен / помолвлена",
            4: "женат/замужем",
            5: "всё сложно",
            6: "в активном поиске",
            7: "влюблён/влюблена",
            8: "в гражданском браке"
        }
        return relation_map.get(dictionary.get('relation', 0), '')

    @staticmethod
    def extract_sex(dictionary):
        sex_map = {
            1: 'женский',
            2: 'мужской'
        }
        return sex_map.get(dictionary.get('sex', 0), '')

    @staticmethod
    def extract_age(dictionary):
        def calculate_age(born):
            today = date.today()
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

        date_str = dictionary.get('bdate', '')
        date = None
        try:
            date = datetime.strptime(date_str, '%d.%m.%Y')
        except:
            pass

        if date:
            return calculate_age(date)
        else:
            return 0

    @staticmethod
    def requared_request_fields():
        fields = [
            'sex',
            'bdate',
            'city',
            'country',
            'contacts',
            'education',
            'followers_count',
            'occupation',
            'relation',
            'personal',
            'wall_comments',
            'can_post',
            'can_see_all_posts',
            'can_see_audio',
            'can_write_private_message',
            'movies',
            'music',
            'tv',
            'books',
            'interests'
        ]
        return ", ".join(map(lambda x: "\"" + x + "\"", fields))


def encode_str(string):
    return string


def bool_str(value):
    return 'Да' if value else 'Нет'