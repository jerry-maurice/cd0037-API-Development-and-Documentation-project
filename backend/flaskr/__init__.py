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
    Create an endpoint to handle GET requests
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
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
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
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)

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
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
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
                    abort(404)
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
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
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
            "totalQuestions": len(Question.query.all()),
            "currentCategory": category.type
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def create_quiz_questions():
        body = request.get_json()

        previous_questions = body.get("previous_questions", None)
        quiz_category = body.get("quiz_category", None)
        print(previous_questions)
        print("testing quiz", quiz_category["id"])
        if previous_questions is None or quiz_category is None:
            abort(404)
        try:
            if quiz_category["id"] == 0:
                category = "All"
                question = Question.query.order_by(func.random()).filter(
                    Question.id.notin_(previous_questions)
                )
                num = question.count()
                question = question.first()

            else:
                category = (Category.query.get(quiz_category["id"])).type
                question = Question.query.order_by(func.random()).filter(
                    Question.category == quiz_category["id"]
                ).filter(
                    Question.id.notin_(previous_questions)
                )
                num = question.count()
                question = question.first()

            return jsonify({
                "success": True,
                "question": question.format(),
                "totalQuestions": num,
                "currentCategory": category,
            })
        except:
            abort(404)


    """
    @TODO:
    Create error handlers for all expected errors
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
