import os
from functools import wraps

from flask import Flask, jsonify, render_template, request, session, redirect, url_for

from database.database import get_db, init_db
from chatbot.retrieval import RetrievalEngine
from chatbot.response import AIResponseGenerator


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")
    app.config["DATABASE"] = os.path.join(app.instance_path, "chatbot.db")
    os.makedirs(app.instance_path, exist_ok=True)
    init_db(app.config["DATABASE"])
    engine = RetrievalEngine(app.config["DATABASE"])
    ai_responder = AIResponseGenerator()

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/chat")
    def chat():
        payload = request.get_json(silent=True) or {}
        message = str(payload.get("message", "")).strip()
        if not message:
            return jsonify({"error": "Please enter a message."}), 400
        answer, score = engine.respond(message)
        source = "knowledge-base" if score >= engine.threshold else "fallback"
        if score < engine.threshold:
            ai_answer = ai_responder.answer(message)
            if ai_answer:
                answer = ai_answer
                source = "ai"
        db = get_db(app.config["DATABASE"])
        db.execute("INSERT INTO chats (user_message, bot_response, score) VALUES (?, ?, ?)", (message, answer, score))
        db.commit()
        db.close()
        return jsonify({"answer": answer, "score": round(score, 3), "source": source})

    @app.get("/admin/login")
    def admin_login():
        return render_template("login.html")

    @app.post("/admin/login")
    def admin_login_post():
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        expected_user = os.environ.get("ADMIN_USERNAME", "admin")
        expected_password = os.environ.get("ADMIN_PASSWORD", "admin123")
        if username == expected_user and password == expected_password:
            session["admin"] = True
            return redirect(url_for("admin"))
        return render_template("login.html", error="Invalid credentials."), 401

    @app.get("/admin/logout")
    def admin_logout():
        session.pop("admin", None)
        return redirect(url_for("admin_login"))

    def admin_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("admin"):
                return redirect(url_for("admin_login"))
            return view(*args, **kwargs)
        return wrapped

    @app.get("/admin")
    @admin_required
    def admin():
        db = get_db(app.config["DATABASE"])
        questions = db.execute("SELECT * FROM knowledge_base ORDER BY id DESC").fetchall()
        stats = {
            "questions": db.execute("SELECT COUNT(*) AS count FROM knowledge_base").fetchone()["count"],
            "chats": db.execute("SELECT COUNT(*) AS count FROM chats").fetchone()["count"],
        }
        db.close()
        return render_template("admin.html", questions=questions, stats=stats)

    @app.post("/admin/questions")
    @admin_required
    def add_question():
        question = request.form.get("question", "").strip()
        answer = request.form.get("answer", "").strip()
        if question and answer:
            db = get_db(app.config["DATABASE"])
            db.execute("INSERT INTO knowledge_base (question, answer) VALUES (?, ?)", (question, answer))
            db.commit()
            db.close()
            engine.reload()
        return redirect(url_for("admin"))

    @app.post("/admin/questions/<int:question_id>/delete")
    @admin_required
    def delete_question(question_id):
        db = get_db(app.config["DATABASE"])
        db.execute("DELETE FROM knowledge_base WHERE id = ?", (question_id,))
        db.commit()
        db.close()
        engine.reload()
        return redirect(url_for("admin"))

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
