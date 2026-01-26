Feature: Todo REST API
  As an application developer
  I want a REST API for managing todos
  So that I can perform CRUD operations on todo items

  Background:
    Given the API is running
    And the database is empty

  # Happy Path Scenarios

  Scenario: Create a new todo with required fields
    When I send a POST request to "/todos" with JSON:
      """
      {
        "title": "Buy groceries",
        "description": "Milk, eggs, and bread"
      }
      """
    Then the response status code should be 201
    And the response should have header "Content-Type" with value "application/json"
    And the response JSON should have field "id"
    And the response JSON field "title" should equal "Buy groceries"
    And the response JSON field "description" should equal "Milk, eggs, and bread"
    And the response JSON field "completed" should equal "false"
    And the response JSON should have field "created_at"
    And the response JSON should have field "updated_at"

  Scenario: Retrieve all todos
    Given the following todos exist:
      | title          | description        | completed |
      | Buy groceries  | Milk and eggs      | false     |
      | Finish project | Complete API tests | true      |
      | Call dentist   |                    | false     |
    When I send a GET request to "/todos"
    Then the response status code should be 200
    And the response should be a JSON array with 3 items
    And the response JSON array should contain an item with "title" equal to "Buy groceries"
    And the response JSON array should contain an item with "title" equal to "Finish project"

  Scenario: Retrieve a specific todo by ID
    Given a todo exists with:
      | title       | Buy groceries      |
      | description | Milk, eggs, bread  |
      | completed   | false              |
    When I send a GET request to "/todos/{id}"
    Then the response status code should be 200
    And the response JSON field "title" should equal "Buy groceries"
    And the response JSON field "description" should equal "Milk, eggs, bread"
    And the response JSON field "completed" should equal "false"

  Scenario: Update a todo completely with PUT
    Given a todo exists with:
      | title       | Old title       |
      | description | Old description |
      | completed   | false           |
    When I send a PUT request to "/todos/{id}" with JSON:
      """
      {
        "title": "Updated title",
        "description": "Updated description",
        "completed": true
      }
      """
    Then the response status code should be 200
    And the response JSON field "title" should equal "Updated title"
    And the response JSON field "description" should equal "Updated description"
    And the response JSON field "completed" should equal "true"
    And the response JSON field "updated_at" should be after "created_at"

  Scenario: Partially update a todo with PATCH
    Given a todo exists with:
      | title       | Original title       |
      | description | Original description |
      | completed   | false                |
    When I send a PATCH request to "/todos/{id}" with JSON:
      """
      {
        "completed": true
      }
      """
    Then the response status code should be 200
    And the response JSON field "title" should equal "Original title"
    And the response JSON field "description" should equal "Original description"
    And the response JSON field "completed" should equal "true"

  Scenario: Delete a todo
    Given a todo exists with:
      | title | Todo to delete |
    When I send a DELETE request to "/todos/{id}"
    Then the response status code should be 204
    And the response body should be empty
    When I send a GET request to "/todos/{id}"
    Then the response status code should be 404

  Scenario: Filter todos by completion status
    Given the following todos exist:
      | title    | completed |
      | Todo 1   | true      |
      | Todo 2   | false     |
      | Todo 3   | true      |
      | Todo 4   | false     |
    When I send a GET request to "/todos?completed=true"
    Then the response status code should be 200
    And the response should be a JSON array with 2 items
    And all items in the response should have "completed" equal to "true"

  # Error Scenarios - Validation

  Scenario: Reject todo creation with empty title
    When I send a POST request to "/todos" with JSON:
      """
      {
        "title": "",
        "description": "This should fail"
      }
      """
    Then the response status code should be 400
    And the response JSON should have field "error"
    And the response JSON field "message" should contain "title"

  Scenario: Reject todo creation with missing title
    When I send a POST request to "/todos" with JSON:
      """
      {
        "description": "No title provided"
      }
      """
    Then the response status code should be 400
    And the response JSON should have field "error"
    And the response JSON field "message" should contain "title"

  Scenario: Reject todo creation with title exceeding maximum length
    When I send a POST request to "/todos" with JSON:
      """
      {
        "title": "This is a very long title that exceeds the maximum allowed length of 200 characters. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
      }
      """
    Then the response status code should be 400
    And the response JSON should have field "error"
    And the response JSON field "message" should contain "title"

  Scenario: Reject todo creation with description exceeding maximum length
    When I send a POST request to "/todos" with JSON:
      """
      {
        "title": "Valid title",
        "description": "<VERY_LONG_STRING_2001_CHARS>"
      }
      """
    Then the response status code should be 400
    And the response JSON should have field "error"
    And the response JSON field "message" should contain "description"

  Scenario: Reject malformed JSON request
    When I send a POST request to "/todos" with body:
      """
      {title: "Missing quotes", invalid json}
      """
    Then the response status code should be 400
    And the response JSON should have field "error"

  # Error Scenarios - Not Found

  Scenario: Return 404 when getting non-existent todo
    When I send a GET request to "/todos/99999"
    Then the response status code should be 404
    And the response JSON should have field "error"
    And the response JSON field "message" should contain "not found"

  Scenario: Return 404 when updating non-existent todo
    When I send a PUT request to "/todos/99999" with JSON:
      """
      {
        "title": "Updated title"
      }
      """
    Then the response status code should be 404
    And the response JSON should have field "error"

  Scenario: Return 404 when patching non-existent todo
    When I send a PATCH request to "/todos/99999" with JSON:
      """
      {
        "completed": true
      }
      """
    Then the response status code should be 404
    And the response JSON should have field "error"

  Scenario: Return 404 when deleting non-existent todo
    When I send a DELETE request to "/todos/99999"
    Then the response status code should be 404
    And the response JSON should have field "error"

  # Error Scenarios - Invalid ID Format

  Scenario: Handle invalid ID format in URL
    When I send a GET request to "/todos/invalid-id"
    Then the response status code should be 400
    And the response JSON should have field "error"
    And the response JSON field "message" should contain "invalid"

  # Edge Cases

  Scenario: Create todo with only required fields
    When I send a POST request to "/todos" with JSON:
      """
      {
        "title": "Minimal todo"
      }
      """
    Then the response status code should be 201
    And the response JSON field "title" should equal "Minimal todo"
    And the response JSON field "description" should equal ""
    And the response JSON field "completed" should equal "false"

  Scenario: Create todo with whitespace-only title
    When I send a POST request to "/todos" with JSON:
      """
      {
        "title": "   "
      }
      """
    Then the response status code should be 400
    And the response JSON should have field "error"

  Scenario: Update todo with empty PATCH request
    Given a todo exists with:
      | title       | Original title |
      | description | Original desc  |
      | completed   | false          |
    When I send a PATCH request to "/todos/{id}" with JSON:
      """
      {}
      """
    Then the response status code should be 200
    And the response JSON field "title" should equal "Original title"
    And the response JSON field "description" should equal "Original desc"
    And the response JSON field "completed" should equal "false"

  Scenario: Retrieve todos from empty database
    When I send a GET request to "/todos"
    Then the response status code should be 200
    And the response should be a JSON array with 0 items

  Scenario: Filter todos with no matches
    Given the following todos exist:
      | title  | completed |
      | Todo 1 | false     |
      | Todo 2 | false     |
    When I send a GET request to "/todos?completed=true"
    Then the response status code should be 200
    And the response should be a JSON array with 0 items

  # Security Edge Cases

  Scenario: Reject SQL injection attempt in title
    When I send a POST request to "/todos" with JSON:
      """
      {
        "title": "'; DROP TABLE todos; --"
      }
      """
    Then the response status code should be 201
    And the response JSON field "title" should equal "'; DROP TABLE todos; --"
    When I send a GET request to "/todos"
    Then the response status code should be 200
    And the response should be a JSON array with at least 1 item

  Scenario: Handle XSS attempt in description
    When I send a POST request to "/todos" with JSON:
      """
      {
        "title": "XSS Test",
        "description": "<script>alert('XSS')</script>"
      }
      """
    Then the response status code should be 201
    And the response JSON field "description" should equal "<script>alert('XSS')</script>"
    And the response header "Content-Type" should contain "application/json"

  # Concurrency Edge Case

  Scenario: Handle concurrent updates to same todo
    Given a todo exists with:
      | title     | Concurrent test |
      | completed | false           |
    When I send a PATCH request to "/todos/{id}" with JSON:
      """
      {
        "completed": true
      }
      """
    And I send a PATCH request to "/todos/{id}" with JSON:
      """
      {
        "title": "Updated title"
      }
      """
    Then the response status code should be 200
    When I send a GET request to "/todos/{id}"
    Then the response JSON field "title" should equal "Updated title"
    And the response JSON field "completed" should equal "true"
