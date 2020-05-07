# Import all modules
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for
from flask import render_template
from random import choice, random
import json
from flask import jsonify
from marshmallow import Schema, fields, ValidationError, pre_load, pprint



# define the app
app = Flask(__name__)

#Define database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/recipes'

#Turn on Flask de-bugging feature
app.debug = True
db = SQLAlchemy(app)

# Define database structure for recipe_list table
class recipe_list(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    cuisine = db.Column(db.String())
    cooking_time = db.Column(db.Integer)
    hyperlink = db.Column(db.String())
    ingredients = db.Column(db.String())

    def __init__(self, name, cuisine, cooking_time, ingredients, hyperlink):
        self.name = name
        self.cuisine = cuisine
        self.cooking_time = cooking_time
        self.ingredients = ingredients
        self.hyperlink = hyperlink
        

    def __repr__(self):
        return '<Recipe %r>' % self.name

# Define database structure for sources table
class sources(db.Model):
    website = db.Column(db.String(), primary_key=True)
    link = db.Column(db.String())

    def __init__(self, website, link):
        self.website = website
        self.link = link
        

    def __repr__(self):
        return '<Recipe %r>' % self.name


class recipeSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    cuisine = fields.Str()
    cooking_time = fields.Int()
    hyperlink = fields.Str()
    ingredients = fields.Str()

recipe_schema = recipeSchema(many=True)

# Create landing or "Home" page
@app.route('/')
def index():
    # Query the recipe_list database for distinct cuisine types
    cuisineQuery = recipe_list.query.with_entities(recipe_list.cuisine).distinct()
    # Create list containing all distinct cuisine types in database to be used by dropdown list
    cuisines = sorted([row.cuisine for row in cuisineQuery])
    # Query the database for distinct main ingredient types
    ingredientListQuery = recipe_list.query.with_entities(recipe_list.ingredients).distinct()
    # Create list containing all distinct main ingredient types to be used by dropdown list
    ingredientList = sorted([row.ingredients for row in ingredientListQuery])
    # Clost the database session
    db.session.close()
    # Return the html teplate to be used by this page. Carry over cuisine and main ingredient lists
    return render_template('index.html', cuisines=cuisines, ingredientList=ingredientList)


@app.route('/post')
def post():
    return render_template('post_recipe.html')

# api route to post new recipe to database. Page will be redirected to "/post" that has HTML template
@app.route('/post_recipe', methods=['POST', 'GET'])
def post_recipe():
    recipeValue = request.form['recipe_name']
    upperRecipe = recipeValue.upper()
    new_recipe = recipe_list(upperRecipe, request.form['cuisine'], request.form['cooking_time'], request.form['ingredients'] ,request.form['hyperlink'])
    print(new_recipe)
    db.session.add(new_recipe)
    db.session.commit()
    return redirect(url_for('post'))

@app.route('/view_all')
def all_recipes():
    recipeQuery = recipe_list.query.order_by(recipe_list.name).all()
    return render_template('all_recipes.html', recipeQuery=recipeQuery)

@app.route('/view/<cuisineType>')
def query(cuisineType):
    newUpper = cuisineType.capitalize()
    cuisineQuery = recipe_list.query.order_by(recipe_list.name).filter_by(cuisine=newUpper)
    return render_template('cuisines.html', cuisineQuery=cuisineQuery)

@app.route('/view/main/<ingredient>')
def ingredientSearch(ingredient):
    ingredientQuery = recipe_list.query.order_by(recipe_list.name).filter_by(ingredients=ingredient)
    return render_template('main_ingredient.html', ingredientQuery=ingredientQuery)

@app.route('/random')
def random_recipe():
    randomRecipe = choice(recipe_list.query.all())
    return render_template('random_recipe.html', randomRecipe=randomRecipe)

@app.route('/sources', methods=['POST', 'GET'])
def add_sources():
    sourceQuery = sources.query.order_by(sources.website).all()
    return render_template('source_page.html', sourceQuery=sourceQuery)

@app.route('/post_source')
def post_source():
    return render_template('post_source.html')

@app.route('/post_recipe_source', methods=['POST'])
def post_recipe_source():
    recipeSource = request.form['source_name']
    upperSource = recipeSource.upper()
    new_source = sources(upperSource, request.form['hyperlink'])
    db.session.add(new_source)
    db.session.commit()
    return redirect(url_for('post_source'))



@app.route('/data', methods=["GET"])
def data():
    authors = recipe_list.query.all()
    # Serialize the queryset
    result = recipe_schema.dump(authors)
    testDict = {"recipes": result}
    dict2 = testDict.values()
    dict3 = dict()
    return testDict
   
    




if __name__ == "__main__":
    app.run()