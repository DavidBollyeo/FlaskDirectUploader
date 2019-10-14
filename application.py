####
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
####


from flask import Flask, render_template, request, redirect, url_for
import os, json, boto3
import pymongo
from dotenv import load_dotenv

load_dotenv()


uri = os.environ.get('MONGODB_URI')
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

print(f'uri: {uri}')

client = pymongo.MongoClient(uri, connect=False)
database = client.get_default_database()
collection = database['stars']



def update_account(username: str, full_name: str, avatar_url: str):
    collection.insert_one(
        {
          'username': username,
          'full_name': full_name,
          'avatar_url': avatar_url
        }
    )


app = Flask(__name__)


# Listen for GET requests to yourdomain.com/account/
@app.route("/account/")
def account():
    # Show the account-edit HTML page:
    return render_template('account.html')


# Listen for POST requests to yourdomain.com/submit_form/
@app.route("/submit-form/", methods = ["POST"])
def submit_form():
    # Collect the data posted from the HTML form in account.html:
    username = request.form["username"]
    full_name = request.form["full-name"]
    avatar_url = request.form["avatar-url"]

    # Provide some procedure for storing the new details
    update_account(username, full_name, avatar_url)

    # Redirect to the user's profile page, if appropriate
    return redirect(url_for('profile.html'))


# Listen for GET requests to yourdomain.com/sign_s3/
#
# Please see https://gist.github.com/RyanBalfanz/f07d827a4818fda0db81 for an example using
# Python 3 for this view.
@app.route('/sign-s3/')
def sign_s3():
    # Load necessary information into the application
    s3_bucket = os.environ.get('S3_BUCKET')

    # Load required data from the request
    file_name = request.args.get('file-name')
    file_type = request.args.get('file-type')

    # Initialise the S3 client
    s3 = boto3.client('s3', region_name='eu-west-2', aws_access_key_id=aws_access_key_id,
                      aws_secret_access_key=aws_secret_access_key)

    # Generate and return the presigned URL
    presigned_post = s3.generate_presigned_post(
      Bucket=s3_bucket,
      Key=file_name,
      Fields={"acl": "public-read", "Content-Type": file_type},
      Conditions = [
        {"acl": "public-read"},
        {"Content-Type": file_type}
      ],
      ExpiresIn=3600
    )

    # Return the data to the client
    return json.dumps({
      'data': presigned_post,
      'url': 'https://%s.s3.amazonaws.com/%s' % (s3_bucket, file_name)
    })


# Main code
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port = port)
