# -*- coding: utf-8

import pytest
import logging
import sys
import re

from .rest import RestHelper

@pytest.fixture(scope='session', autouse=True)
def setup_module():
    log_format = "%(asctime)s.%(msecs)03d %(levelname)-06s: %(module)s::%(funcName)s:%(lineno)s: %(message)s"
    log_datefmt = "%m-%dT%H:%M:%S"
    log_formatter = logging.Formatter(log_format, datefmt=log_datefmt)
    logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt=log_datefmt)
    stream_handler = logging.FileHandler('test.log')
    #stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_formatter)
    stream_handler.setLevel('DEBUG')
    logging.getLogger().addHandler(stream_handler)
    logging.getLogger().setLevel('DEBUG')

class Listener(object):
    """
    Monitor current test, implment some other logic, such as file bug automatically, write result to database
    """
    def __init__(self, triage=False):
        self.triage = triage

    def __call__(self, func, *args, **kwargs):
        doc = func.__doc__
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except:
                if self.triage:
                    print '---------Triage Bug----------'
                    print doc
                raise
    
        return wrapper

class TestCase(object):
    """
    Base class of all test, define some generic method or variables
    """
    log = None

    @pytest.fixture(autouse=True)
    def logtest(self, request):
        request.cls.log = logging.getLogger(request.cls.__name__)
        self.log.info('######## Test Begin - %s::%s ###########' % (request.cls.__name__, request.function.__name__))
        def fin():
            self.log.info('######## Test End - %s::%s ###########' % (request.cls.__name__, request.function.__name__))
        request.addfinalizer(fin)

@pytest.fixture(scope='class', autouse=True, params=['https://splunk.mocklab.io'])
def setup(request):
    request.cls.rest = RestHelper(request.param)

class TestSPL(TestCase):
    """
    Tests for APIs: 'POST /movies, GET /movies'
    """
    rest = None

    @pytest.fixture()
    def movies(self, request, logtest):
        self.log.info("Step: Get movies")
        return self.rest.get_movies()
    
    def test_tc_001(self, movies):
        """
        TC1: Call GET movies with name which inclues empty, blanks, special chars, Chinese chars, UTF-8 encoding, unicode encoding
        """
        self.log.info("Step 1: Test name with blanks")
        self.rest.get_movies('batman fight')

        self.log.info("Step 2: Test name with special chars, such as +%\\/@*&")
        self.rest.get_movies('batman@@%+fight')

        self.log.info("Step 3: Test name with Chinese chars")
        self.rest.get_movies('batman\xe4\xb8\xad\xe6\x96\x87')
        self.log.info("Step 4: Test name with different coding, such as UTF-8, Unicode")
        self.rest.get_movies('batman\u4e2d\u6587')

        self.log.info("Step 1: Test name with empty string")
        assert len(self.rest.get_movies('')), 'No movie has title empty'

    def test_tc_002(self, movies):
        """
        TC2: Call GET movies without count, with count=0, count=big number, count=negative number, count=other string
        """
        self.log.info("Step 1: Get all movies without parameter 'count'")
        total = len(self.rest.get_movies())

        self.log.info("Step 2: Get movies with parameter count=0")
        count = len(self.rest.get_movies(count=0))
        assert count == total, "The count of movies is not expected: %s" % total

        if total > 1:
            self.log.info("Step 3: Get movies with parameter count=%s" % (total-1))
            count = len(self.rest.get_movies(count=total-1))

            assert count == total - 1, "The count of movies is not expected: %s" % (total -  1)

        self.log.info("Step 4: Get movies with parameter count=-1")
        count = len(self.rest.get_movies(count=-1))

        self.log.info("Step 5: Get movies with parameter count=str")
        count = len(self.rest.get_movies(count='xx'))

    def test_tc_003(self):
        """
        TC3: Call GET movies with head 'Accept: Application/json', or 'Accept: application/json' or others 'Accept: */*' or without 'Accept' head
        """
        self.log.info("Step 1: Test 'Application/json', which should be case-insensitive")
        count = len(self.rest.get_movies(headers={'Accept': 'Application/json'}))
        assert count > 0, 'The count of movies should be greater than 0'

        self.log.info("Step 2: Test 'application/json'")
        count = len(self.rest.get_movies(headers={'Accept': 'application/json'}))
        assert count > 0, 'The count of movies should be greater than 0'

        self.log.info("Step 3: Test '*/*'")
        count = len(self.rest.get_movies(headers={'Accept': '*/*'}))
        assert count > 0, 'The count of movies should be greater than 0'

    def test_tc_004(self):
        """
        TC4: Call POST movies with name and description with validate words
        """
        self.log.info('Step 1: Test POST movies')
        resp = self.rest.add_movies('movie name', 'movie description')
        self.log.info('Response: %s' % resp)

    def test_tc_005(self):
        """
        TC5: Call POST movies with name and description with validate words, with valid and invalid head 'Content-Type: application/json', 'Accept: */*'
        """
        resp = self.rest.add_movies('xxx', 'movie description', raw=True, content_type='Application/json', headers={'Accept': '*/*'})
        assert resp.status_code == 200, 'Expect succeeding to add moive with Application/json'

        resp = self.rest.add_movies('xxx', 'movie description', raw=True, content_type='Application/json', headers={'Accept': 'Application/xml'})
        assert resp.status_code != 200, 'Expect failing to add moive with Accept: Application/xml'

        resp = self.rest.add_movies('xxx', 'movie description', raw=True, content_type='Application/xml', headers={'Accept': '*/*'})
        assert resp.status_code != 200, 'Expect failing to add moive with Application/xml'

    def test_tc_006(self):
        """
        TC6: Call POST movies with name and description which are empty, blanks, special chars, Chineese chars, UTF-8, unicode encoding
        """
        self.log.info('Step 1: Test POST movies')
        resp = self.rest.add_movies('', 'movie description', raw=True)
        assert resp.status_code != 200, 'Title cannot be empty'

        resp = self.rest.add_movies('  ', 'movie description', raw=True)
        assert resp.status_code != 200, 'Title cannot be empty'

        self.rest.add_movies(' @#" ', 'movie description')
        self.rest.add_movies(' \xe4\xb8\xad\xe6\x96\x87 ', 'movie description')
        self.rest.add_movies(' \u4e2d\u6587 ', 'movie description')

    def test_tc_007(self):
        """
        TC7: Call POST movies with invalid JSON string
        """
        resp = self.rest.request('/movies', 'POST', raw=True, payload='{"name":111, "description":@}')
        assert resp.status_code != 200, 'Payload is not valid JSON'

    def test_tc_008(self):
        """
        TC8: Call POST movies with other fields besides name and description
        """
        resp = self.rest.request('/movies', 'POST', raw=True, payload='{"name":"title", "description":"@", "other":1}')
        assert resp.status_code != 200, 'Payload includes other fields'

    def test_tc_009(self):
        """
        TC9: Call POST movies with name which is number, boolean, json array, json object
        """
        resp = self.rest.request('/movies', 'POST', raw=True, payload='{"name":123, "description":"@"}')
        assert resp.status_code != 200, 'Name is number'

        self.rest.request('/movies', 'POST', raw=True, payload='{"name":true, "description":"@"}')
        assert resp.status_code != 200, 'Name is boolean'

        self.rest.request('/movies', 'POST', raw=True, payload='{"name":["array"], "description":"@"}')
        assert resp.status_code != 200, 'Name is json array'

        self.rest.request('/movies', 'POST', raw=True, payload='{"name":{"key":"object"}, "description":"@"}')
        assert resp.status_code != 200, 'Name is json object'

    ######Business Requirements: - 
    def test_tc_010(self, movies):
        """
        TC10: Call GET movies, make sure there should no two movies hasve the same 'poster_path'
        """
        self.log.info('Step 1: Filter movies whose poster_path is null')
        movies = filter(lambda m: 'poster_path' in m and m['poster_path'], movies)

        self.log.info("Step 2: Get movies' poster_path")
        poster_paths = [m['poster_path'] for m in movies]
        self.log.info('All poster paths: %s' % poster_paths)

        assert len(poster_paths) == len(set(poster_paths)), 'There has duplicated poster_paths'
        self.log.info("All movies' poster path are different")

    def test_tc_011(self, movies):
        """
        TC11: Call GET movies, validate the poster_path can be null, empty(not present), or validte url address(https://..., http://..., or relative path)
        """
        self.log.info('Step 1: Filter movies whose poster_path is null')
        movies = filter(lambda m: 'poster_path' in m and m['poster_path'], movies)

        self.log.info("Step 2: Get movies' poster_path")
        poster_paths = [m['poster_path'] for m in movies]
        self.log.info('All poster paths: %s' % poster_paths)

        self.log.info("Step 3: Check all poster_paths are valid")
        # Path - How to check it is valid: check URL is accessible? (Absolute path, relative path?)
        assert all(map(lambda path: re.match(r'^https?://\S+/.+$', path) != None, poster_paths)), 'Some paths are not valid'
        self.log.info("All movies' poster path are valid")

    def test_tc_012(self, movies):
        """
        TC12: Call GET movies, validate the movies with genre_ids == null should be first in response, and sorted by id(ascending); for movies with non-null genre_ids, the results should be sorted by id(ascending)
        """
        self.log.info('Step 1: Check if movies wich genre_ids were at first and sorted by id ascending')
        idx_without_genre_ids = []
        id_without_genre_ids = []
        for i,movie in enumerate(movies):
            if 'genre_ids' not in movie or not movie['genre_ids']:
                idx_without_genre_ids.append(i)
                id_without_genre_ids.append(movie['id'])
        self.log.info('index of movies without genre_ids: %s' % idx_without_genre_ids)
        self.log.info('id of movies without genre_ids: %s' % id_without_genre_ids)
        if idx_without_genre_ids:
            assert idx_without_genre_ids[0] == 0, 'The index of the first movie without genre_ids should be 0'
            for i in range(1, len(idx_without_genre_ids)):
                assert idx_without_genre_ids[i] == idx_without_genre_ids[i-1] + 1, 'The index of followed movies without genre_ids shoud be continuous'
        
        if id_without_genre_ids:
            for i in range(1, len(id_without_genre_ids)):
                assert id_without_genre_ids[i] > id_without_genre_ids[i-1], 'The id of movies without genre_ids should be sorted by id(ascending)'

    def test_tc_013(self, movies):
        """
        TC13: Call GET movies, validate the number of movies whose sum of 'genre_ids' > 400 should be no more than 7. (Need preprare date and combined the query with count)
        """
        self.log.info('Step 1: Get the sum of genre_ids of movies')
        nums = len(filter(lambda m: 'genre_ids' in m and sum(m['genre_ids']) > 400, movies))
            
        assert nums <= 7, 'The number of movies whose sum of genre_ids > 400 should be less than 7'

    def test_tc_014(self, movies):
        """
        TC14: Call GET movies, validate there is one movie whose title has a palindrome word in it
        """
        self.log.info('Step 1: Check if there is at least one movie whose titile has a palindrome in it')
        def hasParlindrome(title):
            for word in title.split(' '):
                if word == '':
                    continue
                
                if word == word[::-1]:
                    return True
            return False
        
        assert any(filter(lambda m: hasParlindrome(m['title']), movies)), 'There should have at least one move whose title has a palindrome'

    def test_tc_015(self, movies):
        """
        TC15: Call GET movies, validate there are at least two movies whose title contain the tile of anothere movie
        """
        self.log.info("Step 1: Get movies' title")
        titles = [m['title'] for m in movies]
        self.log.info("Movies' title: %s" % titles)

        total = 0
        for i in range(len(movies)):
            for j in range(i+1, len(movies)):
                if movies[j]['title'].find(movies[i]['title']) >= 0:
                    total += 1
        
        self.log.info('There are %s movies whose title contains the title of another movie' % total)
        assert total >= 2, "Expect there are at least 2 movies whose title contain the title of another movie"