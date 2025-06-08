## develop your flask app here ##
from flask import Flask, render_template, url_for, request, redirect
import os
from groq import Groq

app = Flask(__name__)
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

#homepage
@app.route("/home", methods = ["GET", "POST"])
def home_page():
    """
    This function displays the homepage and handles the submission from the user for their symptoms. After symptoms are provided, redirects to /results
    with the symptoms being the url parameter. 
    """
    if request.method == "POST":
        symptoms = request.form.get("symptoms")
        return redirect(url_for("analyze_symptoms", symptoms = symptoms))
    return render_template("index.html")

#analyze symptoms

    

# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "Explain the importance of fast language models",
#         }
#     ],
#     model="llama-3.3-70b-versatile",
# )

# print(chat_completion.choices[0].message.content)