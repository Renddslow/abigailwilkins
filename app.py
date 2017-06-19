import os
import json
from datetime import datetime
import uuid

from flask import Flask, render_template, g, request, jsonify
import redis
from twilio.twiml.messaging_response import MessagingResponse
import requests

application = Flask(__name__)
application.secret_key = os.environ.get('ABIGAIL_KEY')


@application.before_request
def before_request():
	g.r = redis.StrictRedis(host='localhost', port=6379, db=0)


@application.route("/")
def home():
	title = "Abigail Wilkins :: " + g.r.get("ab:title")
	description = g.r.get("ab:description")
	media = g.r.get("ab:main_img")
	url = request.base_url
	return render_template("home.html", 
							ip=request.remote_addr,
							title=title,
							description=description,
							media=media,
							url=url)


@application.route("/posts/<id>")
def post(id):
	post = json.loads(g.r.get("ab:post:" + id))
	title = 'Abigail Wilkins :: ' + post['content'][:45] + '...'
	if post['media']:
		media = post['media']
	else:
		media = g.r.get('ab:main_img')
	url = request.base_url
	description = post['content']
	return render_template('post.html',
							title=title,
							description=description,
							url=url,
							media=media,
							post=post,
							ip=request.remote_addr)


@application.route("/feed", methods=['GET'])
def feed():
	response = []

	page = request.args.get("page") if request.args.get("page") else 1
	posts = g.r.lrange('ab:posts', int(page) - 1, 12)

	for post in posts:
		response.append(json.loads(post))

	return jsonify(response)


@application.route("/update", methods=['POST'])
def update():
	form = request.form
	body = form['Body']
	_from = form['From']
	media = None
	image_uri = None

	if 'MediaUrl0' in form:
		media = form['MediaUrl0']
		print(media)

	if media:
		try:
			headers = {
				"Authorization": "Client-ID cbd22022907d26a"
			}
			form_data = {
				"image": media
			}
			image_uri = requests.post("https://api.imgur.com/3/upload", 
									headers=headers,
									data=form_data).json()['data']['link']
		except Exception as e:
			return str(MessagingResponse().message("Whoops, something went wrong uploading your picture. " + str(e)))
	
	data = {
		"id": str(uuid.uuid4())[-6:],
		"content": body,
		"media": image_uri,
		"author": g.r.get('ab:author'),
		"datePublished": datetime.now().strftime("%-d %B %Y")
	}
	data_as_string = json.dumps(data)
	g.r.lpush('ab:posts', data_as_string)
	g.r.set('ab:post:' + data['id'], data_as_string)

	return str(MessagingResponse().message("Post has been posted! Check it out! http://abigailwilkins.net/posts/" + data["id"]))


if __name__ == "__main__":
	application.run(host='0.0.0.0')
