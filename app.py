import os

from flask import Flask, render_template, flash, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from src.patent_fetcher import (
    conduct_search, download_patents,
    get_sample_images, extract_images, display)

load_dotenv()

ALLOWED_EXTENSIONS = {'png', 'bmp', 'tif', 'jpg', 'jpeg'}
# Should specify a maximum content length for file uploads


app = Flask(__name__, template_folder='./src/templates')
app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER")
app.config['DOWNLOAD_FOLDER'] = os.getenv("DOWNLOAD_FOLDER")
app.static_folder = os.getenv("STATIC_FOLDER")



def allowed_file(filename: str):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template('home.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/search/")
@app.route("/search")
def user_query():
    return render_template('form.html', title="Patent Search")


@app.route("/search/<string:patent_title>")
def patent_search(patent_title):
    """ Let the user search for a patent by title directly

    Need to figure out how to implement two word searches, e.g. automotive camera
    """

    # Create sub-folder to store images
    if " " in patent_title:
        dir_name = f'./src/downloads/{patent_title.replace(" ", "")}/'
    else:
        dir_name = f'./src/downloads/{patent_title}/'

    # Make new folder if folder doesn't exist already
    try:
        os.makedirs(dir_name)
    except FileExistsError:
        print("Folder already exists, continuing.")

    # Conduct Patent Search
    patent_results = conduct_search(patent_title, limit=10)

    if not patent_results:
        # TODO: if this is unexpected use a flask abort(400) or something?
        print(f'how in the world did we wind up here?!?!? patents={len(patent_results)}')
        images = [f"{app.static_folder}/patent_image_not_available.png"] * len(patent_results)
        return render_template('search_results.html', category=patent_title, patents=patent_results,
                                images=images)

    # Download patent drawings to new folder
    drawing_files = download_patents(patent_results, destination=dir_name)

    # Extract images from patents' prior art
    sample_images = get_sample_images(
        drawing_files, app.static_folder)

    return render_template('search_results.html', category=patent_title,
                            patents=patent_results, images=sample_images)


if __name__ == '__main__':
    app.run()
