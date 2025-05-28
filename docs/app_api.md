# REST API Reference

This document describes the HTTP endpoints provided by the Flask application (`app.py`).

## 1. GET `/`

**Description**: Serves the interactive chessboard UI.

* **Response**: HTML page (`board.html`).

## 2. POST `/validate`

**Description**: Validates a proposed move and applies it if legal.

### Request

* **Content-Type**: `application/json`
* **Body**:

  ```json
  {
    "piece": "wP",   // Piece code: color + type
    "src": 52,        // Source square code (column×10 + row)
    "dst": 53         // Destination square code
  }
  ```

### Response

* **200 OK** (move processed)

  ```json
  {
    "valid": true | false,
    "pieces": { "11": "wR", ... }  // Updated board map if valid
  }
  ```
* **400 Bad Request** (invalid input or out of turn)

  ```json
  { "error": "Invalid input" }
  ```

## 3. POST `/reset`

**Description**: Resets the board to the initial chess starting position.

### Request

* No body required.

### Response

* **200 OK**

  ```json
  {
    "status": "success",
    "pieces": { "11": "wR", ... }  // Starting position map
  }
  ```

## Error Handling

* All endpoints return JSON.
* **500 Internal Server Error** in case of unexpected exceptions:

  ```json
  { "error": "Internal server error" }
  ```

## Example Usage with `curl`

```bash
# Validate a move
echo '{"piece":"wP","src":52,"dst":54}' \
  | curl -H "Content-Type: application/json" -d @- http://127.0.0.1:5000/validate

# Reset the board
curl -X POST http://127.0.0.1:5000/reset
```


