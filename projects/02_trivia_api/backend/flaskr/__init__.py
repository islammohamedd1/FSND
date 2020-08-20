from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r'/*': {'origins': '*'}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Origin-Allow-Headers',
                             'Content-Type')
        response.headers.add('Access-Origin-Allow-Methods',
                             'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    @app.route('/categories')
    def get_categories():
        categories = [category.type for category in Category.query.all()]
        return jsonify({
            'success': True,
            'categories': categories,
            'total_categories': len(categories)
        })

    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, type=int)
        start = (page - 1)
        end = (page - 1) + QUESTIONS_PER_PAGE
        questions = [q.format() for q in Question.query.all()]
        categories = [category.type for category in Category.query.all()]

        res = {
            'success': True,
            'questions': questions[start:end],
            'totalQuestions': len(questions),
            'categories': categories,
            'current_category': [q['category'] for q in questions[start:end]]
        }

        return jsonify(res)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        if question is None:
            return abort(404)
        try:
            question.delete()
        except:
            abort(500)
        return jsonify({
            'success': True,
            'question_id': question_id
        })

    @app.route('/questions', methods=['POST'])
    def submit_question():
        data = request.get_json()
        try:
            new_question = Question(question=data['question'],
                                    answer=data['answer'],
                                    difficulty=data['difficulty'],
                                    category=data['category'])
        except KeyError:  # The sent data isn't full or right
            return abort(422)

        new_question.insert()

        return jsonify({'success': True})

    @app.route('/questions/search', methods=['POST'])
    def search_question():
        data = request.get_json()

        try:
            questions = [q.format() for q in Question.query.filter(
                Question.question.ilike('%{}%'.format(data['searchTerm']))).all()]
        except KeyError:
            return abort(422)

        res = {
            'success': True,
            'questions': questions,
            'totalQuestions': len(questions)
        }
        return jsonify(res)

    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        category = Category.query.get(category_id)
        if category is None:
            return abort(404)
        questions = [q.format()
                     for q in Question.query.filter_by(category=category_id)]
        res = {
            'success': True,
            'questions': questions,
            'totalQuestions': len(questions),
            'current_category': category_id
        }
        return jsonify(res)

    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        data = request.get_json()
        previous_questions = data['previous_questions']
        category = int(data['quiz_category']['id'])
        questions = Question.query.filter_by(category=category).all()
        if not len(questions):
            return abort(404)
        question_id = random.sample(
            [q.id for q in questions if q.id not in previous_questions], 1)[0]

        result_question = Question.query.get(question_id)
        res = {
            'success': True,
            'question': result_question.format()
        }
        return jsonify(res)

    @app.errorhandler(404)
    def not_found_handler(error):
        res = {
            'success': False,
            'message': 'Resource not found!'
        }
        return jsonify(res), 404

    @app.errorhandler(422)
    def unprocessable_hanlder(error):
        res = {
            'success': False,
            'message': 'The request cannot be processed. Please modify it.'
        }
        return jsonify(res), 422

    @app.errorhandler(500)
    def server_error_hanlder(error):
        res = {
            'success': False,
            'message': 'We are facing an issue processing your request. Please try again later.'
        }
        return jsonify(res), 500

    return app
