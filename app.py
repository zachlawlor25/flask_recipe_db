# Import all modules
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect, url_for
from flask import render_template
from random import choice, random
import json
from flask import jsonify
from marshmallow import Schema, fields, ValidationError, pre_load, pprint
import random


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
    # Renders html template for posting new recipe
    return render_template('post_recipe.html')

# api route to post new recipe to database. Page will be redirected to "/post" that has HTML template
@app.route('/post_recipe', methods=['POST', 'GET'])
def post_recipe():
    # Requests values from html form with the ID "recipe_name"
    recipeValue = request.form['recipe_name']
    #Converts the value of recipe name to uppercase. This is the desired format within the database.
    upperRecipe = recipeValue.upper()
    # Formats the values to be appended to the DB
    new_recipe = recipe_list(upperRecipe, request.form['cuisine'], request.form['cooking_time'], request.form['ingredients'] ,request.form['hyperlink'])
    print(new_recipe)
    # Adds new recipe to DB
    db.session.add(new_recipe)
    # Commits new addition to DB
    db.session.commit()
    # Redirects the page to render an HTML template
    return redirect(url_for('post'))

# Defines API route and page for viewing all recipes currently in the DB
@app.route('/view_all')
def all_recipes():
    # Queries the database, returns all values ordered by recipe name field
    recipeQuery = recipe_list.query.order_by(recipe_list.name).all()
    # Renders template for tabular view of all recipes
    return render_template('all_recipes.html', recipeQuery=recipeQuery)

# Defines api route to delete row in table
@app.route('/delete/<name>', methods=['POST', 'GET'])
def deleteRow(name):
    recipe_list.query.filter_by(name=name).delete()
    db.session.commit()
    #Redirect to all recipe page
    return redirect(url_for('all_recipes'))

# Defines API dynamic route and page for viewing specific type of cuisine. Fed by dropdown on landing page.
@app.route('/view/<cuisineType>')
def query(cuisineType):
    # Takes the input cuisine and capitalizes first letter. This follows format in DB.
    newUpper = cuisineType.capitalize()
    # Queries database for specified cuisine type and returns ordered list.
    cuisineQuery = recipe_list.query.order_by(recipe_list.name).filter_by(cuisine=newUpper)
    # Renders template for tabular view, similar to all_recipes.
    return render_template('cuisines.html', cuisineQuery=cuisineQuery)

# Create dynamic API route for main ingredient type
@app.route('/view/main/<ingredient>')
def ingredientSearch(ingredient):
    # Query database for all recipes that share a similar main ingredient.
    ingredientQuery = recipe_list.query.order_by(recipe_list.name).filter_by(ingredients=ingredient)
    # Render html template for for tabular view of recipes.
    return render_template('main_ingredient.html', ingredientQuery=ingredientQuery)

# Create API route for viewing a random recipe
@app.route('/random')
def random_recipe():
    # Query the database for all recipes and then select a random one from the query.
    randomRecipe = choice(recipe_list.query.all())
    # Render template for random recipe view
    return render_template('random_recipe.html', randomRecipe=randomRecipe)

#Define API route for recipe sources. This references a different table within the database called "sources"
@app.route('/sources', methods=['POST', 'GET'])
def add_sources():
    # Query the databse for all sources and order by website name
    sourceQuery = sources.query.order_by(sources.website).all()
    # Render template for source tabular view
    return render_template('source_page.html', sourceQuery=sourceQuery)

# Create API route to post a new source
@app.route('/post_source')
def post_source():
    # Render template for posting new source. Redirected from '/post_recipe_source'
    return render_template('post_source.html')

# Create API route to post a new source
@app.route('/post_recipe_source', methods=['POST'])
def post_recipe_source():
    # Pull data from HTML form
    recipeSource = request.form['source_name']
    # Convert recipe source to uppercase. Database standard
    upperSource = recipeSource.upper()
    # Format inputted data for database commit
    new_source = sources(upperSource, request.form['hyperlink'])
    # Add data to DB
    db.session.add(new_source)
    # Commit changes to DB
    db.session.commit()
    # Redirect to html page
    return redirect(url_for('post_source'))



@app.route('/data', methods=["GET"])
def data():
    # Query for distinct cuisines
    cuisineDistinctQuery = recipe_list.query.with_entities(recipe_list.cuisine).distinct()
    # Create List from distinct query
    cuisinesList = sorted([row.cuisine for row in cuisineDistinctQuery])
    # Blank list to contain counts of cuisine types
    counts = []
    # Blank list to contain random colors generates
    colors = []
    for value in cuisinesList:
        count = recipe_list.query.filter_by(cuisine=value).count()
        counts.append(count)
        colors.append("#{:06x}".format(random.randint(0, 0xFFFFFF)))
    return render_template('chart_test.html', counts=counts, cuisinesList=cuisinesList, colors=colors)
   
    




if __name__ == "__main__":
    app.run()