import os

from dotenv import load_dotenv
from flask import Flask, render_template, request
from openai import OpenAI

load_dotenv()

app = Flask(__name__)

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

MODEL = os.getenv("MODELNAME")


cuisines = [
    "",
    "Italian",
    "Mexican",
    "Chinese",
    "Indian",
    "Japanese",
    "Thai",
    "French",
    "Mediterranean",
    "American",
    "Greek",
    "Korean",
]


dietary_restrictions = [
    "Gluten-Free",
    "Dairy-Free",
    "Vegan",
    "Pescatarian",
    "Nut-Free",
    "Kosher",
    "Halal",
    "Low-Carb",
    "Organic",
    "Locally Sourced",
]


languages = [
    "English",
    "Korean",
    "Japanese",
    "Chinese",
    "Spanish",
    "French",
    "German",
    "Italian",
]


@app.route("/")
def index():
    return render_template(
        "index.html",
        cuisines=cuisines,
        dietary_restrictions=dietary_restrictions,
        languages=languages,
    )


@app.route("/generate_recipe", methods=["POST"])
def generate_recipe():
    ingredients = request.form.getlist("ingredient")
    selected_cuisine = request.form.get("cuisine")
    selected_restrictions = request.form.getlist("restrictions")
    selected_language = request.form.get("language", "English")

    if len(ingredients) != 3:
        return "Kindly provide exactly 3 ingredients."

    if not os.getenv("OPENROUTER_API_KEY"):
        return "OPENROUTER_API_KEY is not set."

    cuisine_instruction = ""
    if selected_cuisine:
        cuisine_instruction = f"The cuisine should be {selected_cuisine}."

    restriction_instruction = ""
    if selected_restrictions:
        restriction_instruction = (
            "The recipe should follow these dietary restrictions: "
            + ", ".join(selected_restrictions)
            + "."
        )

    language_instruction = f"Write the entire recipe in {selected_language}."

    prompt = f"""
Create a recipe using these three ingredients:
{", ".join(ingredients)}

{cuisine_instruction}
{restriction_instruction}
{language_instruction}

Requirements:
- Write the response in HTML format.
- Put the recipe title at the top.
- Include an ingredients section.
- Include step-by-step cooking instructions.
- Make the recipe practical and easy to follow.
- The recipe can use basic seasonings such as salt, pepper, oil, and water if needed.
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a creative cooking assistant who writes clear and practical recipes.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        recipe = response.choices[0].message.content

    except Exception as e:
        recipe = f"<p>API Error: {str(e)}</p>"

    return render_template("recipe.html", recipe=recipe)


if __name__ == "__main__":
    app.run(debug=True)