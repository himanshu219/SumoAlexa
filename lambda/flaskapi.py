import sys
sys.path.insert(0, '/opt')
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

from jenkins_api import JenkinsAPI
from jiraapi import JiraAPI

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'secret'
# app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)
# from werkzeug import url_decode
# class MethodRewriteMiddleware(object):
#     """Middleware for HTTP method rewriting.
#
#     Snippet: http://flask.pocoo.org/snippets/38/
#     """
#
#     def __init__(self, app):
#         self.app = app
#
#     def __call__(self, environ, start_response):
#         if 'METHOD_OVERRIDE' in environ.get('QUERY_STRING', ''):
#             args = url_decode(environ['QUERY_STRING'])
#             method = args.get('__METHOD_OVERRIDE__')
#             if method:
#                 method = method.encode('ascii', 'replace')
#                 environ['REQUEST_METHOD'] = method
#         return self.app(environ, start_response)

username = ""
password = ""

jira_api = JiraAPI(username, password)
jenkins_api = JenkinsAPI(username, password)

@app.route('/issue/<jira_id>')
def get_jira(jira_id):
    return jsonify(jira_api.get_issue_by_id(jira_id))

@app.route('/release_blocker_issues/<branch>')
def get_blocker_issues(branch):
    return jsonify(jira_api.get_blocker_issues(branch))

@app.route('/component_blocker_issues/<name>')
def get_blocker_issues_by_project(name):
    return jsonify(jira_api.get_blocker_issues_by_project(name))

@app.route('/assigned_blocker_issues/<user>')
def get_blocker_issues_by_user(user):
    return jsonify(jira_api.get_blocker_issues_by_user(user))

@app.route('/myissues')
def get_latest_reported_issues():
    return jsonify(jira_api.get_latest_reported_issues())

@app.route('/failing_jobs')
def get_failing_jobs():
    return jsonify(jenkins_api.find_all_failed_jobs())

# @app.route('/books/<id>')
# def show_book(id):
#     """GET /books/<id>
#
#     Get a book by its id"""
#     book = Book(id=id, name=u'My great book') # Your query here ;)
#     return render_template('show_book.html', book=book)
#
# @app.route('/books/new')
# def new_book():
#     """GET /books/new
#
#     The form for a new book"""
#     return render_template('new_book.html')
#
# @app.route('/books', methods=['POST',])
# def create_book():
#     """POST /books
#
#     Receives a book data and saves it"""
#     name = request.form['name']
#     book = Book(id=2, name=name) # Save it
#     flash('Book %s sucessful saved!' % book.name)
#     return redirect(url_for('show_book', id=2))
#
# @app.route('/books/<id>/edit')
# def edit_book(id):
#     """GET /books/<id>/edit
#
#     Form for editing a book"""
#     book = Book(id=id, name=u'Something crazy') # Your query
#     return render_template('edit_book.html', book=book)
#
# @app.route('/books/<id>', methods=['PUT'])
# def update_book(id):
#     """PUT /books/<id>
#
#     Updates a book"""
#     book = Book(id=id, name=u"I don't know") # Your query
#     book.name = request.form['name'] # Save it
#     flash('Book %s updated!' % book.name)
#     return redirect(url_for('show_book', id=book.id))
#
# @app.route('/books/<id>', methods=['DELETE'])
# def delete_book(id):
#     """DELETE /books/<id>
#
#     Deletes a books"""
#     book = Book(id=id, name=u"My book to be deleted") # Your query
#     flash('Book %s deleted!' % book.name)
#     return redirect(url_for('list_books'))

if __name__ == '__main__':
    app.run()


