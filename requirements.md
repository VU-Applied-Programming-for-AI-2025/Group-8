# NutriSpoon Application Requirements

---

## 1. Consent Form
- When a user visits the site for the first time, they are shown a consent form.
- If the user gives consent, they are redirected to the authentication/registration page.

---

## 2. User Profile Management 
- Users can register a profile with all required fields: age, gender, allergies, etc.
- Users can log in and log out.
- Users can view and update their profile information.

---

## 3. Symptom Selection & Nutrient Analysis
- Users can input their symptoms to get an analysis on possible inadequate nutrient intakes.
- Submitting symptoms triggers a call to the LLM (Groq API).
- The LLM response is parsed into structured data containing:
  - 3 Nutrient likelihoods
  - Explanations for each nutrient possible inadequacy.
  - 3 Food suggestions for each nutrient. 
  - Tips
- The UI is accessible (e.g., screen readers, tab-navigable).

---

## 4. Inadequacy Save Feature
- Users nutrient analysis results is saved to their profile and can be accessed through the homepage.

---

## 5. Food and Recipe Recommendations 
- For each nutrient inadequacy, the user sees multiple personalized recipe suggestions.
- Each recipe includes:
  - Nutrient info (calories, protein, fiber)
  - Option to save the recipe to favorites

---

## 6. Favorites Management 
- Users can save a recipe to favorites.
- Saved recipes appear in the favorites section.
- Users can unsave a recipe.

---

## 7. Meal Planning

- Generate a custom meal plan from recommended recipes.
- Create a custom Spoonacular meal plan based on the BMR which will be calculated with the users data.
- Find mealplans back on homepage where you can go to your mealplan.

---

## 8. Nutrient Information Page 
- Users can search for nutrients in a search bar for quick access.
- Users can quickly go to nutrient information pages in a navigation menu.
- Each nutrient page displays:
  - It's function
  - Why it's important
  - Deficiency symptoms
  - Top food sources. 

---

## 9. General & Security
- The UI is accessible (e.g., screen readers, tab-navigable).
- The site loads and responds within 10 seconds after symptom submission.
- **error handling**: Show clear error messages for
  - Missing required fields (e.g., password, username)
  - Duplicate usernames during registration
  - Invalid login credentials
  - Invalid or incomplete profile updates
---

## Additional Notes

- **API Integrations**:
  - Groq API for AI-driven symptom analysis.
  - Spoonacular API for recipes and nutrition data.
- **All API keys** must be set in the `.env` file and never committed to version control.
- **All dependencies** are listed in `requirements.txt`.

---
