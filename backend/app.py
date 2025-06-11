## develop your flask app here ##
from flask import Flask, render_template, url_for, request, redirect
from dotenv import load_dotenv
import os
from groq import Groq
import json

load_dotenv()

app = Flask(__name__, template_folder = "../frontend/templates",)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

#homepage
@app.route("/", methods = ["GET", "POST"])
def home_page():
    """
    This function displays the homepage and handles the submission from the user for their symptoms. After symptoms are provided, redirects to /results
    with the symptoms being the url parameter. 
    """
    if request.method == "POST":
        symptoms = request.form.get("symptoms").strip()
        if symptoms:
            return redirect(url_for("display_results", symptoms = symptoms))
        return redirect(url_for("home_page"))
    return render_template("homepage.html")

#function to analyze symptoms 
def analyze_symptoms():
    """
    This function sends the inputted symptoms to the groq api to analyze(, then returns it as text on the /results page.)
    """
    symptoms = request.args.get("symptoms")
    
    ai_prompt = f"""
        user symptoms: {symptoms}

        required analysis:
        1. top 3 likely vitamin/mineral deficiencies for each symptom
        2. for each deficiency:
        - biological explanation (short but detailed, easy to grasp. don't use the word "deficiency", in stead use something like "lack of")
        - foods to eat to fix the issue (comma-seperated list, no extra information, list each food on its own)
        - 1 lifestyle tip
        3. flag any urgent medical concerns

        return the analysis only in this format:
        [deficiency name]:
        - Why: [explanation]
        - Foods: [comma-separated list]
        - Tip: [actionable advice]

        [Urgency Note]: (if applicable)
        """
    
    ## llm should incorporate the pesonal details of the user like allergies, pregnancy, etc 
    
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": ai_prompt,
            }
        ],
        temperature=0.7,
        max_completion_tokens=1024,
        top_p=1,
        stop=None
    )
    analysis_results = response.choices[0].message.content 
    return analysis_results

#results page to display analysis results
@app.route("/results")
def display_results():
    """
    This function displays the groq llm analysis on the webpage.
    """
    analysis = analyze_symptoms()
    symptoms = request.args.get("symptoms")

    return render_template("results.html", symptoms = symptoms, analysis = analysis)

#helper to function extract foods from the groq response
def extract_food_recs():
    """
    This function extracts the food recommendations from the llm response and stores it in a list for backend use.

    Call this function to extract a list with foods to eat from the groq llm response.
    """
    groq_response = analyze_symptoms()
    list_foods = []

    for line in groq_response.split("\n"):
        line = line.strip()
        if line.startswith('- Foods:'):
            all_foods = line[8:].split(',')
            foods = [food.strip() for food in all_foods]
            list_foods.extend(foods)

    seen_foods = set() #to check duplicates
    food_recs = [] #new list w/o duplicates
    for food in list_foods:
        if not (food in seen_foods or seen_foods.add(food)):
            food_recs.append(food)
    
    return food_recs

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)  