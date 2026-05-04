from flask import Flask, render_template, request
import spacy
import random

app = Flask(__name__)
nlp = spacy.load("en_core_web_sm")


# ---------------- QUIZ GENERATION ----------------
def generate_quiz_data(text, num=5):
    doc = nlp(text)
    sentences = list(doc.sents)

    num = min(len(sentences), 10)

    questions = []

    for sent in sentences:
        tokens = [t for t in sent if t.pos_ in ["NOUN", "PROPN"] and t.is_alpha]

        if len(tokens) < 2:
            continue

        answer = random.choice(tokens).text
        question = sent.text.replace(answer, "_____")

        options = list(set([t.text for t in tokens if t.text != answer]))

        while len(options) < 3:
            options.append(answer)

        options = random.sample(options, min(3, len(options)))
        options.append(answer)

        random.shuffle(options)

        questions.append({
            "question": question,
            "options": options,
            "answer": answer
        })

        if len(questions) >= num:
            break

    return questions


# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        text = request.form.get("text")

        if not text or text.strip() == "":
            return render_template("home.html", error="Please enter some text!")

        quiz = generate_quiz_data(text)
        return render_template("quiz.html", quiz=quiz)

    return render_template("home.html")


# ---------------- RESULT ----------------
@app.route("/result", methods=["POST"])
def result():
    total = int(request.form.get("total_q"))
    score = 0
    results = []

    for i in range(total):
        user_ans = request.form.get(f"q{i}")
        correct_ans = request.form.get(f"ans{i}")
        question = request.form.get(f"question{i}")

        is_correct = user_ans == correct_ans
        if is_correct:
            score += 1

        results.append({
            "question": question,
            "user": user_ans,
            "correct": correct_ans,
            "is_correct": is_correct
        })

    return render_template("result.html", score=score, results=results)


if __name__ == "__main__":
    app.run(debug=True)