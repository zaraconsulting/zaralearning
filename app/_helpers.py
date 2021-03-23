import glob, os, boto3
from flask import current_app as app

def clear_temp_dir():
    files = glob.glob('/temp/*')
    for f in files:
        os.remove(f)
    print('temp folder cleared')

def save_to_s3_bucket(credentials, image=None, video=None, thumbnail=None, folder=None):
    app.config.get('BASEDIR')
    if folder is None:
        print(folder)
        print('You must pass a valid folder')
    if not isinstance(credentials, dict):
        print(credentials)
        print('Your credentials must be a dictionary')
    if filename is None:
        print(filename)
        print('You must pass a valid filename.')

    s3_client = boto3.client('s3', aws_access_key_id=app.config.get('AWS_ACCESS_KEY_ID'), aws_secret_access_key=app.config.get('AWS_SECRET_ACCESS_KEY'))
    s3_client.upload_fileobj(open(f'temp/{filename_img}', 'rb'), app.config.get('AWS_S3_BUCKET'), 'courses/categories/' + filename_img, ExtraArgs={ 'ACL': 'public-read' })