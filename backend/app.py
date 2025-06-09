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
    return render_template("homepage.html")

#analyze symptoms
@app.route("/results")
def analyze_symptoms():
    symptoms = request.args.get("symptoms")

    ai_prompt = f"analyze the possible vitamins/nutrients the user might be lacking for hair loss and acne. give the results in a structured way like this:\n- vitamin/nutrient that might be lacking\n- why this vitamin/nutrient matters\n- foods to eat to fix this issue\n"
    
    ## llm should incorporate the pesonal details of the user like allergies, pregnancy, etc 
    
    analysis_results = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": ai_prompt,
            }
        ],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None
    )
    analysis = analysis_results.choices[0].message.content
    
    return render_template("results.html", symptoms = symptoms, analysis = analysis)

if __name__ == "__main__":
    app.run(debug=True)