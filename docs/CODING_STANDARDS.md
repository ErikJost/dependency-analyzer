# Coding Standards for Dependency Analyzer MCP Server

This document defines the coding standards, conventions, and best practices for the Dependency Analyzer MCP Server project. Following these standards ensures consistency, maintainability, and interoperability.

## 1. File Organization

### 1.1 Directory Structure

```
dependency-analyzer/
├── server_mcp.py             # HTTP interface implementation
├── stdio_mcp.py              # stdio interface implementation
├── mcp_api.py                # Core MCP API implementation
├── scripts/                  # Analysis scripts
│   ├── enhanced-dependency-analysis.cjs
│   └── ...
├── static/                   # Static web assets
│   ├── css/
│   ├── js/
│   └── images/
├── templates/                # HTML templates
├── docs/                     # Documentation
│   ├── api/
│   ├── examples/
│   └── tutorials/
├── schemas/                  # JSON schemas for validation
│   ├── tools/
│   └── resources/
├── tests/                    # Tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── config/                   # Configuration files
├── projects/                 # Mounted project directory
└── analysis/                 # Analysis results directory
```

### 1.2 File Naming Conventions

- **Python Files**: Use lowercase with underscores (`snake_case`) for filenames.
  - Example: `server_mcp.py`, `mcp_api.py`, `stdio_mcp.py`

- **JavaScript/TypeScript Files**: Use camelCase for filenames.
  - Example: `enhancedDependencyAnalysis.cjs`, `routeComponentVerifier.js`

- **Configuration Files**: Use lowercase with hyphens (`kebab-case`).
  - Example: `docker-compose.yml`, `mcp-config.yml`

- **Documentation Files**: Use UPPERCASE for general documentation.
  - Example: `README.md`, `CONTRIBUTING.md`, `CODING_STANDARDS.md`

- **Test Files**: Prefix or suffix with `test_` or `_test` respectively.
  - Example: `test_server_mcp.py`, `mcp_api_test.py`

## 2. Code Style

### 2.1 Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style.
- Maximum line length: 100 characters.
- Use 4 spaces for indentation (no tabs).
- Use docstrings for all modules, classes, and functions.
- Always include type hints for function parameters and return types.

```python
def process_request(request_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process an MCP request with the given parameters.
    
    Args:
        request_id: The unique identifier for this request
        params: The parameters for the request
    
    Returns:
        A dictionary containing the response data
    
    Raises:
        ValidationError: If the parameters are invalid
    """
    # Function implementation
```

### 2.2 JavaScript/TypeScript Code Style

- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript).
- Maximum line length: 100 characters.
- Use 2 spaces for indentation (no tabs).
- Use JSDoc comments for all functions and classes.

```javascript
/**
 * Analyzes dependencies in a project.
 * 
 * @param {string} rootDir - The root directory of the project
 * @param {Object} options - Analysis options
 * @returns {Object} The dependency analysis results
 */
function analyzeDependencies(rootDir, options = {}) {
  // Function implementation
}
```

### 2.3 Comments and Documentation

- Use meaningful comments that explain "why", not "what".
- Document complex algorithms or non-obvious code behavior.
- Keep comments up-to-date with code changes.
- Use documentation generators compatible with your comments (JSDoc, Sphinx).

## 3. API Design Standards

### 3.1 MCP Tool Design

- Each tool should have a single, well-defined purpose.
- Tool names should be verbs in snake_case (`analyze_dependencies`, `find_orphaned_files`).
- Parameters should be descriptive and use camelCase.
- Each tool must have a JSON schema definition for its parameters.
- Tools should return standardized response objects.

### 3.2 Resource URI Design

- Resource URIs should follow a consistent pattern: `{resource_type}://{resource_id}/{subresource}`.
- Use plural nouns for collections (`projects`) and singular for items (`project`).
- Resource identifiers should be included in the path, not as query parameters.
- Query parameters should only be used for filtering, sorting, or pagination.

### 3.3 Response Format

All API responses must follow this standard format:

```json
{
  "status": "success",
  "data": {
    // Response data specific to the endpoint
  },
  "metadata": {
    // Optional metadata about the response
    "timestamp": "2023-07-01T12:34:56Z",
    "version": "1.0"
  }
}
```

Error responses must follow this format:

```json
{
  "status": "error",
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {
      // Optional additional error details
    }
  }
}
```

## 4. HTTP API Standards

### 4.1 Endpoint Design

- Base URL: `/api`
- API versioning in URL: `/api/v1/tools/{tool_name}`
- Use plural nouns for collections: `/api/v1/projects`
- Use resource IDs in paths: `/api/v1/projects/{project_id}`

### 4.2 HTTP Methods

- `GET`: Retrieve resources
- `POST`: Create resources or execute actions
- `PUT`: Replace resources
- `PATCH`: Update resources partially
- `DELETE`: Remove resources

### 4.3 Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created
- `204 No Content`: Successful request with no response body
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## 5. stdio API Standards

### 5.1 Message Format

All messages must be valid JSON objects on a single line.

Request format:
```json
{
  "request_id": "unique-request-id",
  "tool": "tool_name",
  "parameters": {
    // Tool-specific parameters
  }
}
```

or

```json
{
  "request_id": "unique-request-id",
  "resource": "project://project-id/structure"
}
```

Response format follows the standard response format defined in section 3.3.

### 5.2 Error Handling

- Never allow unhandled exceptions to crash the process.
- Always log errors to stderr.
- Respond with appropriate error responses.
- Include the original request ID in error responses.

### 5.3 Protocol Extensions

- Protocol extensions must be negotiated during handshake.
- Custom extensions should be prefixed with `x-`.
- Extensions must be optional and degrade gracefully if not supported.

## 6. Testing Standards

### 6.1 Unit Tests

- Write unit tests for all functions and classes.
- Use pytest for Python tests.
- Organize tests in a structure mirroring the source code.
- Aim for at least 80% code coverage.

### 6.2 Integration Tests

- Test API endpoints with real HTTP requests.
- Test stdio interface with simulated input/output.
- Use mock data for external dependencies.

### 6.3 End-to-End Tests

- Test complete workflows.
- Include tests for Docker deployment.
- Test multiple project types and sizes.

## 7. Git Workflow

### 7.1 Branching Strategy

- `main`: Stable, production-ready code.
- `develop`: Integration branch for features.
- `feature/*`: Feature branches.
- `bugfix/*`: Bug fix branches.
- `release/*`: Release preparation branches.

### 7.2 Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 7.3 Pull Requests

- Create descriptive PR titles.
- Include a summary of changes.
- Reference related issues with "Fixes #123" or "Relates to #123".
- Require at least one review before merging.
- Squash commits when merging.

## 8. Documentation Standards

### 8.1 Code Documentation

- Use docstrings for all public modules, classes, and functions.
- Include parameter descriptions, return types, and exceptions.
- Provide examples for complex functions.

### 8.2 API Documentation

- Document all API endpoints.
- Include request and response schemas.
- Provide example requests and responses.
- Document error responses.

### 8.3 User Documentation

- Write clear, concise documentation.
- Include step-by-step tutorials for common tasks.
- Provide troubleshooting guides.
- Keep documentation up-to-date with code changes.

## 9. Security Standards

### 9.1 Input Validation

- Validate all user inputs.
- Use JSON Schema for request validation.
- Sanitize inputs to prevent injection attacks.

### 9.2 Dependency Management

- Regularly update dependencies.
- Use a dependency scanning tool.
- Pin dependency versions in requirements.txt.

### 9.3 API Security

- Implement rate limiting.
- Add authentication for production deployments.
- Use HTTPS in production.
- Set appropriate security headers.

## 10. Performance Standards

### 10.1 Response Time

- API endpoints should respond within 500ms for simple requests.
- Long-running operations should use background processing.
- Implement caching for frequently accessed resources.

### 10.2 Resource Usage

- Monitor memory usage in the container.
- Optimize large data processing.
- Implement pagination for large result sets.

## 11. Accessibility and Internationalization

### 11.1 Web Interface

- Follow WCAG 2.1 guidelines.
- Support keyboard navigation.
- Use semantic HTML.

### 11.2 Error Messages

- Use clear, actionable error messages.
- Avoid technical jargon in user-facing messages.
- Prepare for future internationalization.

## Conclusion

These standards are meant to ensure code quality, consistency, and maintainability. They should be followed for all new code and applied to existing code during refactoring.

For questions or suggestions regarding these standards, please open an issue on GitHub.

- Example: Only Dockerfile.sdk_minimal is supported for building the MCP server image. Do not use docker-compose or other Dockerfiles. 