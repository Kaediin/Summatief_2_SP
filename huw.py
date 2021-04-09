import os
import urllib.parse

from dotenv import load_dotenv
from flask import Flask, request, session, render_template
from pymongo import MongoClient

from controller import database_controller as database
from controller import db_auth
from model import convert_to_model, product
from page_logic import page_home, page_cart, page_details

# The secret key used for session encryption is randomly generated every time
# the server is started up. This means all session data (including the 
# shopping cart) is erased between server instances.
app = Flask(__name__)
app.secret_key = os.urandom(16)

client = MongoClient(port=27017)
db = db_auth.getMongoDatabase(client)

products = db.products.find({})
sessions = db.sessions.find({'has_sale': True})
visitors = db.visitors.find({})

database.instantiate(products, sessions, visitors)


class HUWebshop(object):
    """ This class combines all logic behind the HU Example Webshop project. 
    Note that all rendering is performed within the templates themselves."""

    app = None
    client = None
    database = None

    envvals = ["MONGODBUSER", "MONGODBPASSWORD", "MONGODBSERVER", "RECOMADDRESS"]
    dbstring = 'mongodb+srv://{0}:{1}@{2}/test?retryWrites=true&w=majority'
    recseraddress = "http://127.0.0.1:5001"

    categoryindex = None
    catlevels = ["category", "sub_category", "sub_sub_category", "sub_sub_sub_category"]
    catencode = {}
    catdecode = {}
    mainmenucount = 8
    mainmenuitems = None

    paginationcounts = [8, 16, 32, 0]

    productfields = ["name", "price.selling_price", "properties.discount", "images"]

    recommendationtypes = {'popular': "Anderen kochten ook", 'similar': "Soortgelijke producten",
                           'combination': 'Combineert goed met', 'behaviour': 'Passend bij uw gedrag',
                           'personal': 'Persoonlijk aanbevolen'}

    """ ..:: Initialization and Category Index Functions ::.. """

    def __init__(self, app):
        """ Within this constructor, we establish a connection with the database
        and perform necessary setup of the database (if applicable) and menu."""
        self.app = app

        # Depending on whether environment variables have been set, we connect
        # to a local or remote instance of MongoDB, and a default or non-default
        # external recommendation service.
        load_dotenv()
        envdict = {}
        if os.getenv(self.envvals[0]) is not None:
            for val in self.envvals:
                envdict[val] = str(os.getenv(val))
            if envdict["MONGODBUSER"] and envdict["MONGODBPASSWORD"] and envdict["MONGODBSERVER"]:
                self.client = MongoClient(
                    self.dbstring.format(envdict["MONGODBUSER"], envdict["MONGODBPASSWORD"], envdict["MONGODBSERVER"]))
            else:
                self.client = MongoClient()
            if envdict["RECOMADDRESS"]:
                self.recseraddress = envdict["RECOMADDRESS"]
        else:
            self.client = MongoClient()
        self.database = db_auth.getMongoDatabase(self.client)

        # Once we have a connection to the database, we check to see whether it
        # has a category index prepared; if not, we have a function to make it.
        if "categoryindex" not in self.database.list_collection_names() or self.database.categoryindex.count_documents(
                {}) == 0:
            self.createcategoryindex()

        # We retrieve the categoryindex from the database when it is set.
        self.categoryindex = self.database.categoryindex.find_one({}, {'_id': 0})

        # In order to save time in future, we flatten the category index once,
        # and translate all values to and from an encoded, URL-friendly, legible
        # format.
        catlist = self.flattendict(self.categoryindex)
        for cat in catlist:
            enc_cat = self.encodecategory(cat)
            self.catencode[cat] = enc_cat
            self.catdecode[enc_cat] = cat

        # Since the main menu can't show all the category options at once in a
        # legible manner, we choose to display a set number with the greatest 
        # number of associated products.
        countlist = list(map(lambda x, y: (y['_count'], x), self.categoryindex.keys(), self.categoryindex.values()))
        countlist.sort(reverse=True)
        self.mainmenuitems = [x[1] for x in countlist[0:self.mainmenucount]]

        # Finally, we here attach URL rules to all pages we wish to render, to
        # make the code self-contained; although the more common decorators do
        # the same thing, we wish to have this class contain as much logic as
        # possible.
        self.app.before_request(self.checksession)
        self.app.add_url_rule('/', 'index', self.renderpackettemplate)
        self.app.add_url_rule('/producten/', 'producten-0', self.productpage)
        self.app.add_url_rule('/producten/<cat1>/', 'producten-1', self.productpage)
        self.app.add_url_rule('/producten/<cat1>/<cat2>/', 'producten-2', self.productpage)
        self.app.add_url_rule('/producten/<cat1>/<cat2>/<cat3>/', 'producten-3', self.productpage)
        self.app.add_url_rule('/producten/<int:page>/', 'producten-4', self.productpage)
        self.app.add_url_rule('/producten/<cat1>/<int:page>/', 'producten-5', self.productpage)
        self.app.add_url_rule('/producten/<cat1>/<cat2>/<int:page>/', 'producten-6', self.productpage)
        self.app.add_url_rule('/producten/<cat1>/<cat2>/<cat3>/<int:page>/', 'producten-7', self.productpage)
        self.app.add_url_rule('/producten/<cat1>/<cat2>/<cat3>/<cat4>/<int:page>/', 'producten-8', self.productpage)
        self.app.add_url_rule('/productdetail/<productid>/', 'productdetail', self.productdetail)
        self.app.add_url_rule('/winkelmand/', 'winkelmand', self.shoppingcart)
        self.app.add_url_rule('/categorieoverzicht/', 'categorieoverzicht', self.categoryoverview)
        self.app.add_url_rule('/change-profile-id', 'profielid', self.changeprofileid, methods=['POST'])
        self.app.add_url_rule('/add-to-shopping-cart', 'toevoegenaanwinkelmand', self.addtoshoppingcart,
                              methods=['POST'])
        self.app.add_url_rule('/producten/pagination-change', 'aantalperpaginaaanpassen', self.changepaginationcount,
                              methods=['POST'])

    def createcategoryindex(self):
        """ Within this function, we compose a nested dictionary of all 
        categories that occur within the database's products collection, and 
        save it to the categoryindex collection. """
        pcatentries = self.database.products.find({}, self.catlevels)
        index = {}
        for entry in pcatentries:
            self.reccatindex(index, entry, 0, len(self.catlevels) - 1)
        for k, v in index.items():
            self.reccatcount(k, v, 0, len(self.catlevels) - 1)
        self.database.categoryindex.insert_one(index)

    def reccatindex(self, d, e, l, m):
        """ This subfunction of createcategoryindex() sets up the base structure
        (tree) of the categories and subcategories, leaving leaves as empty 
        dicts."""
        if l > m:
            return
        t = self.catlevels[l]
        if t in e and e[t] is not None and type(e[t]) != list and e[t] not in d:
            d[e[t]] = {}
        if t in e and e[t] is not None and type(e[t]) != list and e[t] in d:
            self.reccatindex(d[e[t]], e, l + 1, m)

    def reccatcount(self, k, v, l, m):
        """ This subfunction of createcategoryindex() adds the number of 
        documents associated with any (sub)category to its dictionary as the
        _count property. """
        if l > m:
            return
        if isinstance(v, dict):
            for k2, v2 in v.items():
                self.reccatcount(k2, v2, l + 1, m)
        if k[:1] != "_":
            v['_count'] = self.database.products.count_documents({self.catlevels[l]: k})

    """ ..:: Helper Functions ::.. """

    def flattendict(self, d, s=[]):
        """ This helper function provides a list of all keys that exist within a
        nested dictionary. """
        for k, v in d.items():
            # Note that the condition below prevents the _count property from
            # being added to the list over and over again.
            if k[:1] != "_":
                s.append(k)
                if isinstance(v, dict) and v:
                    s = self.flattendict(v, s)
        return s

    def encodecategory(self, c):
        """ This helper function encodes any category name into a URL-friendly
        string, making sensible and human-readable substitutions. """
        c = c.lower()
        c = c.replace(" ", "-")
        c = c.replace(",", "")
        c = c.replace("'", "")
        c = c.replace("&", "en")
        c = c.replace("ë", "e")
        c = c.replace("=", "-is-")
        c = c.replace("%", "-procent-")
        c = c.replace("--", "-")
        c = urllib.parse.quote(c)
        return c

    def prepproduct(self, p):
        """ This helper function flattens and rationalizes the values retrieved
        for a product block element. """
        # print(p)
        r = {}
        r['name'] = p.name
        r['price'] = p.price / 100
        # r['price'] = str(r['price'])[0:-2] + ",-" if r['price'] % 100 == 0 else str(r['price'])[0:-2] + "," + str(
        #     r['price'])[-2:]
        # if r['price'][0:1] == ",":
        #     r['price'] = "0" + r['price']
        if p.discount is not None:
            r['discount'] = p.discount
        r['smallimage'] = ""  # TODO: replace this with actual images!
        r['bigimage'] = ""  # TODO: replace this with actual images!
        r['id'] = p.product_id
        return r

    def shoppingcartcount(self):
        """ This function returns the number of items in the shopping cart. """
        return sum(list(map(lambda x: x[1], session['shopping_cart'])))

    """ ..:: Session and Templating Functions ::.. """

    def checksession(self):
        """ This function sets certain generally used session variables when
        those have not yet been set. This executes before every request, but
        will most likely only make changes once. """
        if ('session_valid' not in session) or (session['session_valid'] != 1):
            session['shopping_cart'] = []
            session['items_per_page'] = self.paginationcounts[0]
            try:
                session['session_id'] = self.database.sessions.find_one({})['buid'][0]
            except TypeError:
                session['session_id'] = None
                pass
            try:
                session['profile_id'] = str(self.database.profiles.find_one({})['_id'])
            except TypeError:
                session['profile_id'] = None
                pass
            session['session_valid'] = 1

    def renderpackettemplate(self, template="homepage.html", packet={}):
        """ This helper function adds all generally important variables to the
        packet sent to the templating engine, then calss upon Flask to forward
        the rendering to Jinja. """
        packet['categoryindex'] = self.categoryindex
        packet['mainmenulist'] = self.mainmenuitems
        packet['categories_encode'] = self.catencode
        packet['categories_decode'] = self.catdecode
        packet['paginationcounts'] = self.paginationcounts
        packet['items_per_page'] = session['items_per_page']
        packet['session_id'] = session['session_id']
        packet['profile_id'] = session['profile_id']
        packet['shopping_cart'] = session['shopping_cart']
        packet['shopping_cart_count'] = self.shoppingcartcount()
        return render_template(template, packet=packet)

    """ ..:: Full Page Endpoints ::.. """

    def productpage(self, cat1=None, cat2=None, cat3=None, cat4=None, page=1):
        """ This function renders the product page template with the products it
        can retrieve from the database, based on the URL path provided (which
        corresponds to product categories). """
        limit = session['items_per_page'] if session['items_per_page'] != 0 else database.execute_query("select count(product_id) from products", '')[0][0]

        rec_limit = 4
        catlist = [cat1, cat2, cat3, cat4]
        nononescats = [e for e in catlist if e is not None]
        skipindex = session['items_per_page'] * (page - 1)

        """ Get all products (this need to be based on profile if has profile id) """
        profile_id = session['profile_id'] if session['profile_id'] is not None else '5a393d68ed295900010384ca'
        retrieved_ids = page_home.get_recommendations(profile_id, nononescats, limit)

        id_batch = retrieved_ids[skipindex:(skipindex + limit)]

        """ Convert the recommended ids to product objects """
        prodList = [convert_to_model.toProduct(e) for e in id_batch]

        """ Get 'anderen kochten ook' recommendations """
        recs = page_home.get_anderen_kochten_ook(id_batch, rec_limit, profile_id)
        recs = [convert_to_model.toProduct(e) if type(e) != product.Product else e for e in recs]

        """ Set the url path to match the categries and page we are in """
        if len(nononescats) > 0:
            pagepath = "/producten/" + ("/".join(nononescats)) + "/"
        else:
            pagepath = "/producten/"

        return self.renderpackettemplate('products.html', {'products': prodList,
                                                           'productcount': len(retrieved_ids),
                                                           'pstart': skipindex + 1,
                                                           'pend': skipindex + session['items_per_page'] if session[
                                                                                                                'items_per_page'] > 0 else len(
                                                               retrieved_ids),
                                                           'prevpage': pagepath + str(page - 1) if (
                                                                   page > 1) else False,
                                                           'nextpage': pagepath + str(page + 1) if (session[
                                                                                                        'items_per_page'] * page < len(
                                                               retrieved_ids)) else False,
                                                           'r_products': recs[:rec_limit],
                                                           'r_type': list(self.recommendationtypes.keys())[0],
                                                           'r_string': list(self.recommendationtypes.values())[0],
                                                           'header_text': 'Voor u aanbevolen' if len(
                                                               nononescats) == 0 else ''
                                                           })

    def productdetail(self, productid):
        """ This function renders the product detail page based on the product
        id provided. """

        try:
            product = convert_to_model.toProduct(
                database.retrieve_properties("products", {"product_id": str(productid)})[0])

            r_products = page_details.product_detail_alg_selection(product)

        except IndexError:
            print('No product found, returning back to productpage')
            return self.productpage()

        return self.renderpackettemplate('productdetail.html', {'product': product, \
                                                                'prepproduct': self.prepproduct(product), \
                                                                'r_products': r_products, \
                                                                'r_type': list(self.recommendationtypes.keys())[1], \
                                                                'r_string': list(self.recommendationtypes.values())[1]})

    def shoppingcart(self):
        """ This function renders the shopping cart for the user."""

        # Set vars, get profile_id and het shopping cart items
        i = []
        limit = 4
        profile_id = session['profile_id'] if session['profile_id'] is not None else '5a393d68ed295900010384ca'
        shopping_cart = session['shopping_cart']

        # Convert de items naar onze Product objecten en tel de kwantiteit
        for tup in shopping_cart:
            prod_obj = convert_to_model.toProduct(
                database.retrieve_properties("products", {"product_id": f"{tup[0]}"})[0])
            product = self.prepproduct(prod_obj)
            product["itemcount"] = tup[1]
            i.append(product)

        # Haal de recommended producten op
        r_prods = [convert_to_model.toProduct(e) if type(e) == tuple else e for e in
                   page_cart.cart_alg_selection(limit, shopping_cart, profile_id)]

        return self.renderpackettemplate('shoppingcart.html', {'itemsincart': i, \
                                                               'r_products': r_prods, \
                                                               'r_type': list(self.recommendationtypes.keys())[2], \
                                                               'r_string': list(self.recommendationtypes.values())[2]})

    def categoryoverview(self):
        """ This subpage shows all top-level categories in its main menu. """
        return self.renderpackettemplate('categoryoverview.html')

    """ ..:: Dynamic AJAX Endpoints ::.. """
    """ ..:: Dynamic AJAX Endpoints ::.. """

    def changeprofileid(self):
        """ This function checks whether the provided session ID actually exists
        and stores it in the session if it does. """
        try:
            newprofileid = request.form.get('profile_id')
            available_profiles = database.execute_query("select visitor_id from visitor_recs where visitor_id = %s",
                                                        (newprofileid,))
            profidexists = available_profiles[0][0] == newprofileid
            if profidexists:
                session['profile_id'] = newprofileid
                return '{"success":true}'
            return '{"success":false}'
        except:
            return '{"success":false}'

    def addtoshoppingcart(self):
        """ This function adds one object to the shopping cart. """
        productid = request.form.get('product_id')
        cartids = list(map(lambda x: x[0], session['shopping_cart']))
        if productid in cartids:
            ind = cartids.index(productid)
            session['shopping_cart'][ind] = (session['shopping_cart'][ind][0], session['shopping_cart'][ind][1] + 1)
        else:
            session['shopping_cart'].append((productid, 1))
        session['shopping_cart'] = session['shopping_cart']
        return '{"success":true, "itemcount":' + str(self.shoppingcartcount()) + '}'

    def changepaginationcount(self):
        """ This function changes the number of items displayed on the product
        listing pages. """
        session['items_per_page'] = int(request.form.get('items_per_page'))
        # TODO: add method that returns the exact URL the user should be
        # returned to, including offset
        return '{"success":true, "refurl":"' + request.form.get('refurl') + '"}'


# TODO: add @app.errorhandler(404) and @app.errorhandler(405)


huw = HUWebshop(app)
