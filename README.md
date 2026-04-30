# Django Quiz App

A flexible and user-friendly quiz application built with Django. This project allows users to create, manage, share, and attempt quizzes with different visibility levels and access control.

---

## Features

* Create and manage quiz questions with difficulty levels
* Multiple answer options per question with correct answer validation
* Organize quizzes into categories
* Share quizzes via:

  * Private access
  * Direct link (unlisted)
  * Shared access with specific users
* Track quiz attempts and scores
* Generate shareable result links
* Store quiz snapshots for historical attempts

---

## Project Structure

### Core Models

#### `Question`

Stores quiz questions with difficulty and ownership.

#### `Option`

Represents possible answers, including correct answer flags.

#### `Quiz`

* Combines multiple questions
* Supports categories and visibility levels:

  * `Private`
  * `Unlisted`
  * `Shared`
* Includes secure share tokens

#### `Category`

Groups quizzes.

#### `QuizAccess`

Handles user-based quiz sharing.

#### `QuizAttempt`

Stores results, scores, and snapshots of quiz attempts.

---

## Visibility & Sharing

* **Private** → Only owner can access
* **Unlisted** → Accessible via link
* **Shared** → Accessible to selected users

---

## Installation

You can install this project using either **uv** or **pip**.

---

### Option 1: Using uv

Install uv (if not already installed):

```bash
pip install uv
```

Clone the repository:

```bash
git clone https://github.com/hanneskoessl/quiz-app.git

cd quiz-app
```

Install dependencies:

```bash
uv sync
```

Run migrations:

```bash
uv run python manage.py migrate
```

Create a superuser:

```bash
uv run python manage.py createsuperuser
```

Start the server:

```bash
uv run python manage.py runserver
```

---

### Option 2: Using pip

Clone the repository:

```bash
git clone https://github.com/hanneskoessl/quiz-app.git
cd quiz-app
```

Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Create superuser:

```bash
python manage.py createsuperuser
```

Start the server:

```bash
python manage.py runserver
```

---

## Dependency Management

This project uses:

* `pyproject.toml` → main dependency definition
* `uv.lock` → fully locked dependencies
* `requirements.txt` → compatibility for pip users

To regenerate `requirements.txt`:

```bash
uv export --format requirements-txt > requirements.txt
```

---

## Example Use Cases

* Teachers creating quizzes for students
* Sharing quizzes via links
* Tracking learning progress
* Private study collections

---

## Notes

* Secure sharing via UUID tokens
* JSON snapshots for reproducible quiz attempts
* Clean separation of ownership and access control

---

## Future Improvements

* Timed quizzes
* Leaderboards
* Question randomization
* REST API support
* Frontend integration (React/Vue)

---

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## License

This project is licensed under the MIT License.
See the LICENSE file for details.

---

## Contact

Use GitHub issues for questions or feedback.

---
