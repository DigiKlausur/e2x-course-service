# e2x Course Service

A JupyterHub service for managing course members in the e2x ecosystem. This service provides a web interface for graders to manage students and other graders in their courses.

## Features

- **Course Management**: View and manage courses you have grader access to
- **Member Management**: Add/remove students and graders from courses
- **JupyterHub Integration**: Automatically create users in JupyterHub when adding course members
- **Role-based Access**: Only graders can manage course membership
- **Web Interface**: Clean, responsive UI built with Grid.js and SweetAlert2

## Installation

```bash
pip install e2x-course-service
```

Or for development:

```bash
git clone https://github.com/Digiklausur/e2x-course-service
cd e2x-course-service
pip install -ve .
```

## Configuration

The service requires the following environment variables:

- `JUPYTERHUB_SERVICE_PREFIX`: The URL prefix for the service
- `JUPYTERHUB_API_TOKEN`: API token for authenticating with JupyterHub

### Course Data Structure

The service expects course data to be organized in the following directory structure:

```
course_base_path/
├── course1/
│   ├── student/
│   │   └── course1-semester1.csv
│   └── grader/
│       └── course1-semester1.csv
└── course2/
    ├── student/
    │   └── course2-semester1.csv
    └── grader/
        └── course2-semester1.csv
```

Each CSV file should contain a `Username` column with the usernames of course members.

## Usage

### Running the Service

```python
from e2x_course_service.app import CourseServiceApp

app = CourseServiceApp()
app.course_base_path = "/path/to/course/data"
app.port = 10101
app.start()
```

### As a JupyterHub Service

Add to your JupyterHub configuration:

```python
c.JupyterHub.services = [
    {
        'name': 'course-service',
        'url': 'http://localhost:10101',
        'command': [
            'python', '-m',
            'e2x_course_service.app',
            '--CourseServiceApp.course_base_path=/path/to/course/data,
            '--CourseServiceApp.port=10101'
        ],
    }
]
```

## Development

### Building the UI

The frontend is built using esbuild:

```bash
cd ui
npm install
npm run build
```

### Code Formatting

```bash
npm run format  # Format JavaScript
ruff check .    # Check Python code
```

## API Endpoints

- `GET /api/courses` - List courses for the current user
- `GET /api/course_members` - Get members of a specific course
- `PUT /api/course_members` - Update course membership
- `DELETE /api/course_members` - Remove members from a course

## License

MIT License - see [LICENSE](LICENSE) for details.