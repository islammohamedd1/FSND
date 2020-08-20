import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            'islam', '123123', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

            new_category = Category('Science')
            self.db.session.add(new_category)
            new_question = Question(
                question='a', answer='b', category='1', difficulty=1)
            self.db.session.add(new_question)
            new_question = Question(
                question='b', answer='c', category='1', difficulty=1)
            self.db.session.add(new_question)
            new_question = Question(
                question='c', answer='d', category='1', difficulty=1)
            self.db.session.add(new_question)
            self.db.session.commit()

    def tearDown(self):
        """Executed after reach test"""
        self.db = SQLAlchemy()
        with self.app.app_context():
            self.db.init_app(self.app)
            self.db.drop_all()

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertTrue(data['success'])
        self.assertTrue(data['total_categories'])

    def test_get_all_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertTrue(data['success'])
        self.assertTrue(data['totalQuestions'])

    def test_delete_question_valid(self):
        question_id = Question.query.first().id
        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        self.assertTrue(data['success'])

    def test_delete_question_invalid(self):
        res = self.client().delete('/questions/123123124123124')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])

    def test_submit_question_valid(self):
        req_data = {
            'question': 'test question 122131214124',
            'answer': 'b',
            'difficulty': 2,
            'category': 1
        }
        res = self.client().post('/questions', data=json.dumps(req_data),
                                 content_type='application/json')
        res_data = json.loads(res.data)
        self.assertTrue(res_data['success'])

    def test_submit_question_invalid(self):
        req_data = {
            'question': 'test question 122131214124',
            'difficulty': 2,
            'category': 1
        }
        res = self.client().post('/questions', data=json.dumps(req_data),
                                 content_type='application/json')
        res_data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertFalse(res_data['success'])

    def test_search_question_valid(self):
        req_data = {'searchTerm': 'a'}
        res = self.client().post('/questions/search', data=json.dumps(req_data),
                                 content_type='application/json')

        res_data = json.loads(res.data)
        self.assertTrue(res_data['success'])

    def test_search_question_invalid(self):
        req_data = {'sdasdasdasd': 'a'}
        res = self.client().post('/questions/search', data=json.dumps(req_data),
                                 content_type='application/json')

        res_data = json.loads(res.data)
        self.assertFalse(res_data['success'])
        self.assertEqual(res.status_code, 422)

    def test_get_category_questions_valid(self):
        res = self.client().get('/categories/1/questions')
        res_data = json.loads(res.data)

        for q in res_data['questions']:
            self.assertEqual(q['category'], 1)

        self.assertTrue(res_data['success'])

    def test_get_category_questions_invalid(self):
        res = self.client().get('/categories/12312451324135123123123123/questions')
        res_data = json.loads(res.data)

        self.assertFalse(res_data['success'])
        self.assertEqual(res.status_code, 404)

    def test_quizzes(self):
        req_data = {
            'previous_questions': [1],
            'quiz_category': {'id': '1'}
        }

        res = self.client().post('/quizzes', data=json.dumps(req_data),
                                 content_type='application/json')
        res_data = json.loads(res.data)

        self.assertTrue(res_data['success'])
        self.assertIsNotNone(res_data['question'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
