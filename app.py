from pathlib import Path
import os

from flask import (Flask, render_template, flash, request,
                   redirect, url_for, send_from_directory)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from src.patent_fetcher import (conduct_search, download_patents,
                                get_sample_images)

from src.reverse_image_search import identify_results

load_dotenv()

ALLOWED_EXTENSIONS = {'png', 'bmp', 'tif', 'jpg', 'jpeg'}
# Should specify a maximum content length for file uploads

template_folder = os.getenv("TEMPLATES_FOLDER")
app = Flask(__name__, template_folder=template_folder)
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

            # I changed this for now
            # filename = secure_filename(file.filename)

            filename = "search_image.png"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return render_template('home.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route("/search/", methods=["POST", "GET"])
@app.route("/search", methods=["POST", "GET"])
def user_query():
    if request.method == "GET":
        return render_template('form.html', title="Patent Search")
    else:
        title = request.form["title"]
        author = request.form["author"]
        status = request.form["status"]
        return redirect(url_for("patent_search", patent_title=title, author=author, status=status))


def _create_folder(dir_name):
    try:
        os.makedirs(dir_name)
    except FileExistsError:
        print("Folder already exists, continuing.")


@app.route("/search/<string:patent_title>")
def patent_search(patent_title, author=False, status=False):
    """ Let the user search for a patent by title directly

    Need to figure out how to implement two word searches,
    e.g. automotive camera
    """
    title = patent_title.replace(" ", "")
    dir_name = str(Path(app.config['DOWNLOAD_FOLDER']) / title)

    _create_folder(dir_name)

    patent_results = conduct_search(patent_title, lim=10)

    if not patent_results:
        return render_template('search_results.html', category=patent_title,
                               patents=[], error="No patents found")

    # Download patent drawings to new folder
    drawing_files = download_patents(patent_results, destination=dir_name)

    # Extract images from patents' prior art
    sample_images = get_sample_images(drawing_files, app.static_folder)

    return render_template('search_results.html', category=patent_title,
                           patents=patent_results, images=sample_images,
                           error=None)


@app.route("/done")
def most_similar_patent():
    print("Computing Most Similar Patent")
    image_list = [i for i in os.listdir("src/static/images") if i[-4:] == ".png" if "image" not in i]
    imgs, apps = identify_results(image_list)
    return render_template("results.html", images=imgs, applications=apps)


if __name__ == '__main__':
    app.run()
