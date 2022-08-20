import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
from sqlalchemy import func

QUESTIONS_PER_PAGE = 10


def paginated_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    """
    Set up CORS. Allow '*' for origins. 
    """
    CORS(app, resource={"/": {"origins": "*"}})

    """
    Use the after_request decorator to set Access-Control-Allow
    """

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    an endpoint to handle GET requests
    for all available categories.
    """

    @app.route("/categories")
    def retrieve_categories():
        categories = {
            category.id: category.type for category in (Category.query.order_by(Category.id).all())
        }

        print(categories)
        if len(categories) == 0:
            abort(404)
        return jsonify(
            {
                "success": True,
                "categories": categories,
            }
        )

    """
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    """

    @app.route("/questions")
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginated_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        categories = {
            category.id: category.type for category in (Category.query.order_by(Category.id).all())
        }
        return jsonify({
            "success": True,
            "questions": current_questions,
            "totalQuestions": len(Question.query.all()),
            "categories": categories,
            "currentCategory": ""
        })

    """
    an endpoint to DELETE question using a question ID.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(400)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_selection = paginated_questions(request, selection)

            return jsonify({
                "success": True,
                "deleted": question_id,
            })
        except:
            abort(422)

    """
    an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    
    An endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    """

    @app.route("/questions", methods=["POST"])
    def create_questions():
        body = request.get_json()

        question = body.get("question", None)
        answer = body.get("answer", None)
        difficulty = body.get("difficulty", None)
        category = body.get("category", None)
        search = body.get("searchTerm", None)

        verify_submission = question is None or answer is None or difficulty is None or category is None
        try:
            if search:
                categoryValue = ""
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(search))
                )
                num_questions = selection.count()
                current_questions = paginated_questions(request, selection)

                if len(current_questions) == 1:
                    current = current_questions[0]
                    categoryValue = Category.query.get(current["category"]).type

                return jsonify({
                    "success": True,
                    "questions": current_questions,
                    "totalQuestions": num_questions,
                    "currentCategory": categoryValue
                })
            else:
                if verify_submission:
                    abort(400)
                question = Question(question=question, answer=answer,
                                    category=category, difficulty=difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_question = paginated_questions(request, selection)

                return jsonify({
                    "success": True,
                    "created": question.id,
                })
        except:
            abort(422)

    """
    endpoint to get questions based on category.
    """

    @app.route("/categories/<int:category_id>/questions")
    def questions_by_category(category_id):
        category = Category.query.get(category_id)
        if category is None:
            abort(404)
        selection = Question.query.order_by(Question.id).filter(Question.category==category_id)
        current_questions = paginated_questions(request, selection)
        return jsonify({
            "success": True,
            "questions": current_questions,
            "totalQuestions": selection.count(),
            "currentCategory": category.type
        })

    """
    endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """
    @app.route("/quizzes", methods=["POST"])
    def create_quiz_questions():
        body = request.get_json()

        previous_questions = body.get("previous_questions", None)
        quiz_category = body.get("quiz_category", None)

        if previous_questions is None or quiz_category is None:
            abort(400)
        try:
            if quiz_category["id"] == 0:
                question = Question.query.order_by(func.random()).filter(
                    Question.id.notin_(previous_questions)
                )

            else:
                question = Question.query.order_by(func.random()).filter(
                    Question.category == quiz_category["id"]
                ).filter(
                    Question.id.notin_(previous_questions)
                )

            if len(question.all()):
                question = (question.first()).format()
            else:
                question = ""

            return jsonify({
                "success": True,
                "question": question,
            })

        except:
            abort(404)


    """
    error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )

    return app
