# Trivia API

## Introduction
This API is created to provide client with trivial questions and answers. The API is responsible for providing questions and their answers combined in categories. The API is also responsible to create new questions sent from the client.

## Getting Started

### Base URL
The base url is `/`

## Errors

### `404` Not found
This error occurs when the requested resource doesn't exist. example use cases that leads to this error:
* Trying to access a wrong uri
* Trying to modify a not-existed question
* Trying to get the questions of a category that doesn't exist.

### `422` Request can't be processed
This error occurs when the request body is missing required data or the json keys is mis-spelled. example use cases that leads to this error:
* Trying to create a question without providing a required data. See creating question request below.
* Searching for a question without providing the search term or providing it with a wrong json key

### `500` Server Error
This error occurs when there is a problem in the server is facing a problem while processing your request. In this case, you can try later after the problem is fixed by us.


## API Endpoints
### `GET /questions`
* Gets all the questions paginated with 10 items per page
* Request arguments:
* * page: optional = the requested page
* Request Parameters: None
* Response: A JSON object containing the following:
```
{
    'success': 'Boolean: success status',
    'questions': 'Array: Questions of this page',
    'totalQuestions': 'Integer: Total number of questions',
    'categories': 'Array: All the categories',
    'current_category': 'Array: The categories of the questions in this page'
}
```
### `GET /categories`
* Gets all the categories
* Request arguments: None
* Request Parameters: None
* Response: A JSON object containing the following:
```
{
    'success': 'Boolean: success status',
    'categories': 'Array: All the categories',
    'total_categories': 'Integer: Total number of categories',
}
```
### `DELETE /questions/<int:question_id>`
* Deletes a question with the given ID
* Request arguments: None
* Request Parameters: question_id: The id of the question to delete
* Response: A JSON object containing the following:
```
{
    'success': 'Boolean: success status',
    'question_id': 'Integer: the id of the deleted question'
}
```
### `POST /questions`
* Creates a new question
* Request arguments: None
* Request Parameters: None
* Request body:
```
{
    'question': 'String: The question',
    'answer': 'String: The answer of the question',
    'difficulty': 'Integer: The difulty of the question in the scale from 1 to 10',
    'category': 'The category of the question
}
```
* Response: A JSON object containing the following:
```
{
    'success': 'Boolean: success status',
}
```
### `POST /questions/search`
* Searchs for a question with a given search term
* Request arguments: None
* Request Parameters: None
* Request body:
```
{
    'searchTerm': 'String: The search term'
}
```
* Response: A JSON object containing the following:
```
{
    'success': 'Boolean: success status',
    'questions': 'Array: Questions mathcing the search term',
    'totalQuestions': 'Integer: Total number of result questions',
}
```
### `GET /categories/<int:category_id>/questions`
* Gets the questions of the given category id
* Request arguments: None
* Request Parameters: category_id: The id of the wanted category
* Response: A JSON object containing the following:
```
{
    'success': 'Boolean: success status',
    'questions': 'Array: Questions of this category',
    'totalQuestions': 'Integer: Total number of questions of this category',
    'current_category': 'Integer: The category id'
}
```
### `POST /quizzes`
* Gets a random question that is not included in the previous questions from a chosen category
* Request arguments: None
* Request Parameters: None
* Request body:
```
{
    'previous_questions': 'Array[int]: The questions appeared before in the quiz',
    'quiz_category': { 'id': 'Int: the id of the category', 'type': 'String: the type of the category }
}
```
* Response: A JSON object containing the following:
```
{
    'success': 'Boolean: success status',
    'question': 'Object: A random question that meets the specs',
}
```
