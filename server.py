import json

from flask import Flask, redirect, render_template, url_for
from flask_wtf import FlaskForm
from wtforms import FieldList, StringField
from wtforms.validators import DataRequired, ValidationError

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret_string"

next_id = 5


def validate_steps(form, field):
    if not any(field.data):
        raise ValidationError("At least one step is required.")


def validate_ingredients(form, field):
    if not any(field.data):
        raise ValidationError("At least one ingredient is required.")


def validate_imageurl(form, field):
    if field.data:
        if not field.data.startswith("http"):
            raise ValidationError("Image URL is invalid.")


class RecipeForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    imageurl = StringField("Image URL", validators=[validate_imageurl])
    steps = FieldList(StringField("Step"), min_entries=10, validators=[validate_steps])
    ingredients = FieldList(
        StringField("Ingredient"), min_entries=5, validators=[validate_ingredients]
    )


def save_recipe(name, imageurl, steps, ingredients):
    global next_id
    with open("data.json", "r") as f:
        recipes = json.load(f)
    with open("data.json", "w") as f:
        id = next_id
        new_recipe = {
            "id": id,
            "name": name,
            "image": imageurl,
            "ingredients": ingredients,
            "steps": steps,
        }
        print(new_recipe)
        next_id += 1
        recipes.append(new_recipe)
        f.write(json.dumps(recipes, indent=4))

    return id





@app.route("/recipe/new", methods=["GET", "POST"])
def recipes():
    form = RecipeForm()
    print(form.steps.errors)
    if form.validate_on_submit():
        name = form.name.data
        imageurl = form.imageurl.data
        steps = [field.data for field in form.steps if field.data != ""]
        ingredients = [field.data for field in form.ingredients if field.data != ""]
        id = save_recipe(name, imageurl, steps, ingredients)
        return redirect(url_for("get_recipes", id=id))
    return render_template("new.html", form=form)


@app.route("/recipe/<id>", methods=["GET"])
def get_recipes(id):
    try:
        int(id)
    except ValueError:
        return "Invalid ID supplied", 400

    with open("data.json", "r") as f:
        recipes = json.load(f)
        for recipe in recipes:
            if recipe["id"] == int(id):
                return render_template("recipe.html", recipe=recipe)

    return render_template("notFound.html")


if __name__ == "__main__":
    app.run(debug=True)
