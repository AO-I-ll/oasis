from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.String(500))
    limit = db.Column(db.String(50))
    category = db.Column(db.String(50))


### タスクを表示する ###
@app.route("/", methods=["GET", "POST"])
def home():
    category_filter = request.args.get("category")
    if category_filter:
        todo_list = Todo.query.filter_by(category=category_filter).all()
    else:
    # データベースから全てのTodoレコードを取得
        todo_list = Todo.query.all()
    # 取得したTodoリストを"index.html"テンプレートに渡し、ウェブページとして表示
    return render_template("index.html", todo_list=todo_list)

### タスク追加 ###
@app.route("/add", methods=["POST"])
def add():
    category = None
    title = request.form.get("title")
    content = request.form.get("content") or None
    limit = request.form.get("limit") or None
    category = request.form.get("category") or None

    new_todo = Todo(title=title, content=content, limit=limit, category=category)
    db.session.add(new_todo)
    db.session.commit()

    return redirect(url_for("home"))


### タスク削除 ###
@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    # URLから渡されたIDに基づいて、該当するTodoをデータベースから取得
    todo = Todo.query.filter_by(id=todo_id).first()
    # 取得したTodoをデータベースセッションから削除
    db.session.delete(todo)
    # 変更をデータベースにコミット
    db.session.commit()
    # タスク削除後、ホームページにリダイレクト
    return redirect(url_for("home"))




# 追加したところ #
# カレンダー用のToDoデータを取得
@app.route("/get_todos", methods=["GET"])
def get_todos():
    with sqlite3.connect("todo.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content, limit, category FROM todos")
        todos = [{"id": row[0], "title": row[1], "content": row[2], "limit": row[3], "category": row[4]} for row in cursor.fetchall()]
   
        return jsonify(todos)


@app.route("/update_todo", methods=["POST"])
def update_todo():
    todo_id = request.form.get("id")
    title = request.form.get("title") or None
    content = request.form.get("content") or None
    limit = request.form.get("limit") or None

    # categoryがフォームから取得できない場合、デフォルトでNoneを設定
    category = request.form.get("category") or None # categoryの取得

    if category is None:
        category = ''  # categoryがNoneだった場合、空文字や適切なデフォルト値を設定する

    todo = Todo.query.get(todo_id)
    if not todo:
        return "タスクが見つかりません", 404

    todo.title = title
    todo.content = content
    todo.limit = limit
    todo.category = category  # categoryの設定

    db.session.commit()

    return redirect(url_for("home"))



@app.route("/add_todo", methods=["POST"])
def add_todo():
    data = request.json
    title = data.get("title")
    content = data.get("content")
    date = data.get("limit")
    category = data.get("category")

    if not title or not date:
        return jsonify({"error": "タイトルと詳細、日付を入力してください"}), 400

    conn = sqlite3.connect("todo.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO todos (title, content, limit, category) VALUES (?, ?, ?, ?)", (title, content, date, category))
    conn.commit()
    conn.close()

    return jsonify(), 201


@app.route("/edit/<int:todo_id>")
def edit_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return "タスクが見つかりません", 404
    return render_template("edit.html", todo=todo)


@app.route('/calendar')
def calendar():
    return render_template('calendar.html')

@app.route('/edit')
def edit():
    return render_template('edit.html')



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=80, debug=True)

