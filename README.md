
Install the dependencies:

```bash
pip install -r requirements.txt
```

4. **Install Chrome Headless**:
Ensure Google Chrome or Chromium is installed. On Debian-based systems, you can install it with:

```bash
sudo apt-get update
sudo apt-get install google-chrome-stable
```

5. **Configure Redis**:
Ensure Redis is running locally or adjust the `CELERY_BROKER_URL` in `app.py` to point to your Redis server.

Start Redis:

```bash
redis-server
```

## Usage

### Running the Services
The API, Celery worker, and Redis can be managed using provided shell scripts (`start.sh`, `stop.sh`, `restart.sh`).

1. **Start all services**:
```bash
./start.sh
```

This will launch Redis, Celery worker, and Flask API in the background, with logs stored in the `logs` directory.

2. **Stop all services**:
```bash
./stop.sh
```

3. **Restart all services**:
```bash
./restart.sh
```

### Testing the API
Use `curl` or any HTTP client to interact with the API. Ensure the services are running before testing.

Example using `curl`:

```bash
# Convert a webpage to PDF
curl -X POST "http://127.0.0.1:5000/convert" -H "Content-Type: application/json" -d '{"url": "https://developer.chrome.com/"}'

# Check task status
curl -X GET "http://127.0.0.1:5000/status/<task_id>"

# Download the PDF
curl -X GET "http://127.0.0.1:5000/download/<task_id>" -o output.pdf

# List all tasks
curl -X GET "http://127.0.0.1:5000/tasks"
```

## API Endpoints

### 1. Convert Webpage to PDF (`/convert`)
- **Method**: POST
- **Request Body**:
- `url` (string, required): The URL of the webpage to convert.
- **Response**:
- Success (200):
 ```json
 {
     "task_id": "abcdef12345",
     "status": "queued"
 }
 ```
- Error (400):
 ```json
 {
     "error": "Missing URL"
 }
 ```

### 2. Check Task Status (`/status/<task_id>`)
- **Method**: GET
- **URL Parameters**:
- `task_id` (string, required): The ID of the task.
- **Response**:
- 200:
 - Queued:
   ```json
   {
       "status": "queued"
   }
   ```
 - Completed:
   ```json
   {
       "status": "completed",
       "pdf_path": "pdf_output/abcdef12345.pdf"
   }
   ```
 - Failed:
   ```json
   {
       "status": "failed",
       "error": "Error message"
   }
   ```

### 3. Download PDF (`/download/<task_id>`)
- **Method**: GET
- **URL Parameters**:
- `task_id` (string, required): The ID of the task.
- **Response**:
- Success (200): Returns the PDF file as an attachment.
- Error:
 - 404:
```json
   {
       "error": "Task not found or invalid task ID"
   }
```
 - 400:
```json
   {
       "error": "Task failed"
   }
```
 - 202:
```json
   {
       "error": "Task is not completed yet"
   }
```

### 4. List All Tasks (`/tasks`)
- **Method**: GET
- **Response**:
- 200:
 ```json
 {
     "tasks": [
         {
             "task_id": "abcdef12345",
             "status": "SUCCESS",
             "worker": "celery@hostname"
         },
         {
             "task_id": "xyz789",
             "status": "PENDING",
             "worker": "celery@hostname"
         }
     ]
 }
 ```

## Scripts

- **`start.sh`**: Starts Redis, Celery, and Flask in the background with logging.
- **`stop.sh`**: Stops all running services safely.
- **`restart.sh`**: Stops and then restarts all services.

Ensure these scripts have execute permissions:

```bash
chmod +x *.sh
```

## Future Work

- **Scaling**: Implement Docker containers and Kubernetes for production deployment.
- **Security**: Add API authentication, rate limiting, and HTTPS support.
- **Error Handling**: Enhance error logging and alerting for failed conversions.
- **Performance**: Optimize Chrome Headless performance and add caching for frequent requests.
- **Monitoring**: Integrate with monitoring tools like Prometheus and Grafana.
- **Storage**: Use cloud storage (e.g., AWS S3) for PDF files instead of local storage.

## Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
