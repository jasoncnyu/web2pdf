from flask import Flask, request, jsonify, send_file
from celery import Celery
import subprocess
import os

app = Flask(__name__)

# Configure Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

OUTPUT_DIR = "pdf_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@celery.task(bind=True)
def convert_to_pdf(self, url):
    pdf_filename = f"{OUTPUT_DIR}/{self.request.id}.pdf"
    try:
        command = [
            "google-chrome", "--no-sandbox", "--disable-gpu", "--headless",
            "--print-to-pdf=" + pdf_filename, url
        ]
        subprocess.run(command, check=True)

        if not os.path.exists(pdf_filename) or os.path.getsize(pdf_filename) == 0:
            raise Exception("PDF generation failed")

        return {"status": "completed", "pdf_path": pdf_filename}
    except subprocess.CalledProcessError:
        return {"status": "failed"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@app.route('/convert', methods=['POST'])
def convert():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "Missing URL"}), 400

    task = convert_to_pdf.apply_async(args=[url])
    return jsonify({"task_id": task.id, "status": "queued"})

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    task = convert_to_pdf.AsyncResult(task_id)
    if task.state == "PENDING":
        return jsonify({"status": "queued"})
    elif task.state == "SUCCESS":
        return jsonify({"status": "completed", "pdf_path": task.result['pdf_path']})
    elif task.state == "FAILURE":
        return jsonify({"status": "failed", "error": task.result.get('error', 'Unknown error')})
    return jsonify({"status": task.state})

@app.route('/download/<task_id>', methods=['GET'])
def download_pdf(task_id):
    task = convert_to_pdf.AsyncResult(task_id)
    
    if task.status == 'PENDING' or task.status == 'UNKNOWN':
        return jsonify({"error": "Task not found or invalid task ID"}), 404
    
    if task.status == 'FAILURE':
        return jsonify({"error": "Task failed"}), 400
    
    if task.status != 'SUCCESS':
        return jsonify({"error": "Task is not completed yet"}), 202
    
    pdf_path = task.result['pdf_path']
    if not os.path.exists(pdf_path):
        return jsonify({"error": "PDF file not found"}), 404
    
    return send_file(pdf_path, as_attachment=True)

@app.route('/tasks', methods=['GET'])
def list_tasks():
    inspector = celery.control.inspect()
    active_tasks = inspector.active() or {}
    scheduled_tasks = inspector.scheduled() or {}
    reserved_tasks = inspector.reserved() or {}

    tasks = []
    for worker, tasks_list in list(active_tasks.items()) + list(scheduled_tasks.items()) + list(reserved_tasks.items()):
        for task in tasks_list:
            task_id = task['id']
            result = convert_to_pdf.AsyncResult(task_id)
            tasks.append({
                "task_id": task_id,
                "status": result.status,
                "worker": worker
            })

    return jsonify({"tasks": tasks})

if __name__ == "__main__":
    app.run(debug=True)
