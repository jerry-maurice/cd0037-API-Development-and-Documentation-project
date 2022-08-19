# Trivia App

This project is about a simple trivia application that allows people to bond with each other.

## Description
1. Display questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer.
2. Delete questions.
3. Add questions and require that they include question and answer text.
4. Search for questions based on a text query string.
5. Play the quiz game, randomizing either all questions or within a specific category.

### Install Project Dependecies
```bash
pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py`and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

### Set up the Database

With Postgres running, create a `trivia` database:

```bash
createbd trivia
```

Populate the database using the `trivia.psql` file provided. From the `backend` folder in terminal run:

```bash
psql trivia < trivia.psql
```

### Run the Server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

## API Reference

### Getting Started
* Base URL: At present this app can only be run locally.
* Authentication: This version of the application does not require authentication or API keys

### Error Handling
Error are returned as JSON objects in the following fortmat:
```bash
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
* 400: Bad Request
* 404: Resource Not Found
* 422: Not Processable

## Endpoints
#### GET /categories
* General:
  * Return an object with info about categories, and success value
* Sample: ```curl http://localhost:5000/categories```

```bash
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  }, 
  "success": true
}
```

#### GET /questions
* General:
  * Return a list of question object, categories, success value, and total number of questions
  * Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1
* Sample: ```curl http://localhost:5000/questions```

```bash
{
  "categories": {
    "1": "Science", 
    "2": "Art", 
    "3": "Geography", 
    "4": "History", 
    "5": "Entertainment", 
    "6": "Sports"
  },  
  "currentCategory": "", 
  "questions": [
    {
      "answer": "Apollo 13", 
      "category": 5, 
      "difficulty": 4, 
      "id": 2, 
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
    }, 
    {
      "answer": "Tom Cruise", 
      "category": 5, 
      "difficulty": 4, 
      "id": 4, 
      "question": "What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
    },
    ...
  ], 
  "success": true, 
  "totalQuestions": 19
```

#### DELETE /questions/{question_id}
* General:
  * Deletes the question of the given ID if it exists. Returns the id of the deleted question, and success value
* Sample: ```curl -X DELETE http://localhost:5000/questions/26```

```bash
{
  "deleted": 26, 
  "success": true
}
```

#### POST /questions
* General:
  * Create a new question using the submitted question, answer, category, difficulty
  * Search is also possible if search term is provided, it returns the question object, success, the total questions, and current category
* Sample: ```curl http://localhost:5000/questions -X POST -H "Content-Type: application/json" -d '{"question":"Country with the most won Worl Cup", "answer":"Brasili", "category":4, "difficulty":1}```

Example Search question
```bash
{
  "currentCategory": "Sports", 
  "questions": [
    {
      "answer": "Uruguay", 
      "category": 6, 
      "difficulty": 4, 
      "id": 11, 
      "question": "Which country won the first ever soccer World Cup in 1930?"
    }
  ], 
  "success": true, 
  "totalQuestions": 1
}
```

#### GET /categories/1/questions
* General:
  * Return a list of question object, currentCategories, success value, and total number of questions for that category
  * Results are paginated in groups of 10. 
* Sample: ```curl http://localhost:5000/questions```

```bash
{
  "currentCategory": "Science", 
  "questions": [
    {
      "answer": "The Liver", 
      "category": 1, 
      "difficulty": 4, 
      "id": 20, 
      "question": "What is the heaviest organ in the human body?"
    }, 
    {
      "answer": "Alexander Fleming", 
      "category": 1, 
      "difficulty": 3, 
      "id": 21, 
      "question": "Who discovered penicillin?"
    }, 
    {
      "answer": "Blood", 
      "category": 1, 
      "difficulty": 4, 
      "id": 22, 
      "question": "Hematology is a branch of medicine involving the study of what?"
    }
  ], 
  "success": true, 
  "totalQuestions": 3
}
```

#### POST /quizzes
* General:
  * Randomly generate quiz question
* Sample: ```curl http://localhost:5000/quizzes -X POST -H "Content-Type: application/json" -d '{"previous_questions":[], "quiz_category":{"id":1, "type":"Science"}```

```bash
{
  "currentCategory": "Science", 
  "question": {
    "answer": "Alexander Fleming", 
    "category": 1, 
    "difficulty": 3, 
    "id": 21, 
    "question": "Who discovered penicillin?"
  }, 
  "success": true, 
  "totalQuestions": 3
}
```

## Tests
In order to run test, run the following commands:
```bash
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

## Authors
Jerry Maurice