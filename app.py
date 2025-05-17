from flask import Flask, request, redirect, send_from_directory, jsonify, render_template, session, redirect, url_for
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "CHANGE_ME_SECRET_KEY"

UPLOAD_FOLDER = "static/photos_factures"
CSV_FILE = "depenses.csv"
MARKDOWN_FILE = "depenses.md"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Authentification simple
USERNAME = "admin"
PASSWORD = "motdepasse"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == USERNAME and request.form["password"] == PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home"))
        return "Identifiants invalides", 403
    return '''
    <form method="post">
        <input type="text" name="username" placeholder="Utilisateur" required>
        <input type="password" name="password" placeholder="Mot de passe" required>
        <button type="submit">Se connecter</button>
    </form>'''

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/submit-expense", methods=["POST"])
def submit_expense():
    if not session.get("logged_in"):
        return "Non autorisé", 403
    try:
        date = request.form.get("date")
        item = request.form.get("item")
        marc = request.form.get("marc") or ""
        etienne = request.form.get("etienne") or ""
        sci = request.form.get("sci") or ""
        type_paiement = request.form.get("type") or ""

        photo_file = request.files.get("photo")
        photo_filename = ""

        if photo_file and photo_file.filename:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            photo_filename = f"{timestamp}_{photo_file.filename}"
            photo_path = os.path.join(UPLOAD_FOLDER, photo_filename)
            photo_file.save(photo_path)

        with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([date, item, marc, etienne, sci, type_paiement, photo_filename])

        update_markdown()
        return "OK", 200

    except Exception as e:
        return str(e), 500

def update_markdown():
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    with open(MARKDOWN_FILE, 'w', encoding='utf-8') as md:
        md.write("| Date | Item | Marc | Etienne | SCI | Type | Facture |")
        md.write("\n|------|------|------|---------|-----|------|---------|")
        for row in rows:
            photo_link = f"![facture](static/photos_factures/{row['Photo']})" if row['Photo'] else ""
            md.write(f"\n| {row['Date']} | {row['Item']} | {row['Marc']} | {row['Etienne']} | {row['SCI']} | {row['Type']} | {photo_link} |")

@app.route("/static/photos_factures/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/md")
def get_markdown():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return send_from_directory(".", MARKDOWN_FILE)

if __name__ == "__main__":
    app.run(debug=True)
