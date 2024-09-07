from flask import Flask, render_template, request, redirect, url_for, flash, Markup, send_file, Response
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
from datetime import datetime
import subprocess
import nbformat
from nbconvert import PythonExporter
from nbconvert.preprocessors import ExecutePreprocessor
from jupyter_client import kernelspec
from jupyter_client.kernelspec import KernelSpecManager
import shutil
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'

source_folder = "D:/nokia/python_project"
destination_folder = "D:/nokia/python_project/static/outputs"

# Function to check if a file has a valid Python or Jupyter Notebook extension
def allowed_file(filename):
    return '.' in filename and (filename.rsplit('.', 1)[1].lower() in ['py', 'ipynb'])

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

def convert_ipynb_to_py(ipynb_file):
    with open(ipynb_file, 'r') as nb_file:
        notebook = nbformat.read(nb_file, as_version=4)
    
    exporter = PythonExporter()
    py_script, _ = exporter.from_notebook_node(notebook)
    return py_script

def execute_python_script(script_path):
    try:
        output = subprocess.check_output(['python', script_path], universal_newlines=True, stderr=subprocess.STDOUT)
        return output
    except subprocess.CalledProcessError as e:
        return 'An error occurred:\n' + e.output

def execute_ipynb_script(ipynb_path):
    with open(ipynb_path, 'r') as nb_file:
        notebook = nbformat.read(nb_file, as_version=4)

    # Find the kernel specification for Python
    kernel_spec_manager = KernelSpecManager()
    kernel_name = kernel_spec_manager.get_kernel_spec('python3').argv[0]

    # Create a kernel manager and a kernel client
    preprocessor = ExecutePreprocessor(kernel_name=kernel_name)
    preprocessor.preprocess(notebook, {'metadata': {'path': ''}})

    # Export the notebook to a Python script
    exporter = PythonExporter()
    py_script, _ = exporter.from_notebook_node(notebook)

    # Execute the generated Python script
    output = subprocess.check_output(['python', '-c', py_script], universal_newlines=True, stderr=subprocess.STDOUT)

    return output

def move_txt_files(source_folder, destination_folder, input_file_name):
    try:
        # List all .txt files in the source folder
        txt_files = [f for f in os.listdir(source_folder) if f.endswith('.txt')]

        # If no files found.
        if len(txt_files) == 0:
            print("No etra files creted.")
            return

        i = 0
        # Move each .txt file to the destination folder
        for txt_file in txt_files:
            i+=1
            source_path = os.path.join(source_folder, txt_file)
            destination_path = os.path.join(destination_folder, input_file_name+"-"+str(i)+"_output.txt")
            shutil.move(source_path, destination_path)

        print('Files moved successfully!')
    except Exception as e:
        print(f'Error moving files: {str(e)}')

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = UploadFileForm()
    output_content = None

    if form.validate_on_submit():
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Execute the uploaded Python script or Jupyter Notebook and capture its output
            if filename.endswith('.ipynb'):
                output = execute_ipynb_script(file_path)
            else:
                output = execute_python_script(file_path)

            # Save the output to a file in the output folder
            f = filename.rsplit('.', 1)
            output_filename = secure_filename(f[0] + '_output.txt')
            output_file_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
            with open(output_file_path, 'w') as output_file:
                output_file.write(output)

            # Read the content of the output file
            with open(output_file_path, 'r') as output_file:
                output_content = Markup(output_file.read())  # Use Markup to render HTML content safely

            # To copy any multiple fies generated
            move_txt_files(source_folder, destination_folder, f[0]) 



    return render_template('index.html', form=form, output_content=output_content)

# Rest of your code for downloading and serving files remains the same
@app.route('/download')
def download():
    output_folder = os.path.join(app.root_path, app.config['OUTPUT_FOLDER'])
    file_list = []

    for filename in os.listdir(output_folder):
        input_filename1 = filename.replace('_output.txt', '')  # Assuming input files have a similar naming convention
        input_filename = input_filename1.split("-")[0]+'.py'
        timestamp = os.path.getmtime(os.path.join(output_folder, filename))
        timestamp_formatted = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %I:%M %p')
        file_info = {
            'input_filename': input_filename,
            'output_filename': filename,
            'timestamp': timestamp_formatted,
        }
        file_list.append(file_info)

    return render_template('download.html', files=file_list)

@app.route('/download/<filename>')
def download_file(filename):
    output_folder = os.path.join(app.root_path, app.config['OUTPUT_FOLDER'])
    file_path = os.path.join(output_folder, filename)
    
    # Check if the file exists
    if os.path.exists(file_path):
        # Open the file in binary mode and set the 'Content-Disposition' header
        with open(file_path, 'rb') as file:
            response = Response(file.read(), content_type='application/octet-stream')
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    else:
        flash('File not found', 'error')
        return redirect(url_for('download'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    app.run(debug=True)