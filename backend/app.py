## develop your flask app here ##
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(
    __name__,
    template_folder="../frontend/templates", 
)

app.secret_key = "VerySupersecretKey"  # Secret key for session management


# Shows the consent form at the beginning of the application, if the user had already given consent (tracked by session) then redirects to the auth page.
@app.route('/')
def show_consent():
    if not session.get('consent_given'):
        return render_template('consentform.html')
    return redirect(url_for("auth"))

# Checks if the user has given consent to redirect to auth page.
@app.route('/consentform', methods=['POST'])
def handle_consent():
    accepted = request.form.get("accept", "false")

    if accepted.lower() == "true":
        session['consent_given'] = True
        return redirect(url_for("auth"))
    else:
        session['consent_given'] = False

# Shows the authentication page if consent is given, here users can log in or create a new profile.
@app.route("/auth")
def auth():
    if not session.get('consent_given'):
        return "Access denied. Please accept the consent form first.", 403
    return "login or create profile"

if __name__ == "__main__":
    app.run(debug=True)