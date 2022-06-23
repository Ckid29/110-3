import json
from flask import Flask, abort,  Response, request
from about_me import me
from mock_data import catalog
from config import db
from bson import ObjectId
from dns import resolver
from flask_cors import CORS

app = Flask('class2python')
CORS(app)


@app.route("/", methods=['GET'])  # root
def home():
    return "This is the home page"

# Create an about endpoint and show your name


@app.route("/about")
def about():
    return me["first"] + " " + me["last"]


@app.route("/myaddress")
def address():
    return f'{me["address"]["street"]} {me["address"]["number"]}'

 ########################################################### API ENDPOINTS################################################################################################################################

 # Postman -> Test endpoints of REST APIs


@app.route("/api/catalog", methods=["GET"])
def get_catalog():
    results = []
    cursor = db.products.find({})  # get all data from the collection

    for prod in cursor:
        prod["_id"] = str(prod["_id"])
        results.append(prod)

    return json.dumps(results)

# POST Method to create new products


@app.route("/api/catalog", methods=["POST"])
def save_product():
    try:
        product = request.get_json()
        errors = ""
        # title exist
        if not "title" in product or len(product["title"]) < 5:
            errors = "Title is required and should have atleast 5 chars"

        #must have an image
        if not "image" in product:
            errors+= ", Image is required"

        #must have a price, the price should be greater/equal to 1
        if not "price" in product or product["price"] < 1:
            errors += ", Price is requires and should be >= 1"


        if errors:
            return abort(400, errors)

        db.slapme.insert_one(product)
        product["_id"] = str(product["_id"])

        return json.dumps(product)
    
    except Exception as ex:
        return abort(500, F"Unexpected error {ex}")


@app.route("/api/catalog/count", methods=["GET"])
def get_count():
    cursor = db.products.find({})
    # Here... count how many products are in the list catalog
    num_items = 0 
    for prod in cursor:
        num_items += 1
    return json.dumps(num_items)
# Request 127.0.0.1:5000/api/product/


@app.route("/api/product/<id>", methods=["GET"])
def get_product(id):
    try:
        if not ObjectId.is_valid(id):
            return abort(400, "Invalid id")

        product = db.products.find_one({"_id": ObjectId(id)})
    # find the product whose _id is equal to id
    # catalog

        if not product:
            abort(404, "Product not found")

        product["_id"] = str(product["_id"])
        return json.dumps(product)

    except:
        return abort (500,"Unexpected error")

    # travel catalog with for loop
    # Get the product inside the list
    # if the _id of the product is equal to th id variable
    # found it, return that product as json


# Create an endpoint that returns the sum of all the products' price
# GET /api/catalog/total
# @app.route('/api/catalog/total', methods=['GET'])
@app.get("/api/catalog/total")
def get_total():
    total = 0
    cursor = db.products.find({})
    for prod in cursor:
        # total = total + prod["price"]
        total += prod["price"]

    return json.dumps(total)

# get product by category
# get /api/products/<category>


@app.get("/api/products/<category>")
def products_by_category(category):
    results = []
    cursor = db.products.find({"category": category})
    for prod in cursor:
        prod["_id"] = str(prod["_id"])
        results.append(prod)

    return json.dumps(results)

# get the list of categories
# get /api/categories


@app.get("/api/categories")
def get_unique_categories():
    cursor = db.products.find({})
    results = []
    for prod in catalog:
        cat = prod["category"]
        # if cat does not exist in results, then
        if not cat in results:
            results.append(cat)

    return json.dumps(results)

    # get the cheapest product


@app.get("/api/product/cheapest")
def get_cheapest_product():
    cursor = db.products.find({})
    solution = cursor[0]
    for prod in cursor:
        if prod["price"] < solution["price"]:
            solution = prod

    solution["_id"] = str(solution["_id"])
    return json.dumps(solution)




@app.route("/api/coupons", methods=["GET"])
def get_all_coupons():
    cursor = db.coupons.find({})
    results = []
    for cc in cursor:
        cc["_id"] = str(cc["_id"])
        results.append(cc)

    return json.dumps(results)

@app.route("/api/coupons", methods=["POST"])
def save_coupon():
    try:
        coupon = request.get_json()

        # validations
        # discount must be 1 < discount < 50
        # code should have atleast 5 chars

        #do not duplicate code
        errors = ""
        if not "code" in coupon or len(coupon["code"]) < 5:
            errors += "Coupon should have at least 5 chars, "

        if not "discount" in coupon or coupon["discount"] < 1 or coupon["discount"] > 50:
            error += "Discount is required and should be between 1 and 50, "

        if errors:
            return Response(errors, status=400)

        exist = db.coupons.find_one({"code": coupon["code"]})
        if exist:
            return Response( "A coupon already exist for that code", status=400)            
        
        db.coupons.insert_one(coupon)

        coupon["_id"] = str(coupon["_id"])
        return json.dumps(coupon)
    
    except Exception as ex:
        print(ex)
        return Response(500, "Unexpected error", status=500)

@app.route("/api/coupons/<code>", methods=["GET"])
def get_coupon_by_code(code):

    #code, code > 4
    coupon = db.coupons.find_one({"code": code})
    if not coupon:
        return abort(404, "Coupon not found")

    coupon["_id"] = str(coupon["_id"])
    return json.dumps(coupon)




app.run(debug=True)
