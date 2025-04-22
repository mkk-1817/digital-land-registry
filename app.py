from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime
from functools import wraps
from algorithms.greedy import find_optimal_properties
from algorithms.dynamic_programming import predict_optimal_bid
from algorithms.divide_conquer import search_properties
from algorithms.hashing import verify_document_hash, generate_document_hash, hash_property_data

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')

app.config["MONGO_URI"] = "mongodb+srv://karthikmakkam:mkk_1817@project.e5qxv.mongodb.net/digital_land_registry?retryWrites=true&w=majority&appName=Project"
mongo = PyMongo(app)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('login'))
        
        user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
        if not user or user['role'] != 'admin':
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate form data
        if not name or not email or not password:
            flash('Please fill in all fields', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = mongo.db.users.find_one({'email': email})
        if existing_user:
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Hash the password
        hashed_password = generate_password_hash(password)
        
        # Create new user
        new_user = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'role': 'user',  # Default role
            'created_at': datetime.datetime.utcnow()
        }
        
        user_id = mongo.db.users.insert_one(new_user).inserted_id
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find user by email
        user = mongo.db.users.find_one({'email': email})
        
        if not user or not check_password_hash(user['password'], password):
            flash('Invalid email or password', 'danger')
            return render_template('login.html')
        
        # Set session variables
        session['user_id'] = str(user['_id'])
        session['name'] = user['name']
        session['email'] = user['email']
        session['role'] = user['role']
        
        flash(f'Welcome back, {user["name"]}!', 'success')
        
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user properties
    user_properties = list(mongo.db.properties.find({
        'ownerId': session['user_id'],
        'status': 'approved'
    }))
    
    # Get available properties for sale
    available_properties = list(mongo.db.properties.find({
        'status': 'approved',
        'forSale': True,
        'ownerId': {'$ne': session['user_id']}  # Exclude user's own properties
    }))
    
    # Get active auctions
    current_time = datetime.datetime.utcnow()
    active_auctions = list(mongo.db.auctions.find({
        'endDate': {'$gt': current_time},
        'status': 'active'
    }))
    
    # Get property details for each auction
    for auction in active_auctions:
        property_obj = mongo.db.properties.find_one({'_id': ObjectId(auction['propertyId'])})
        auction['property'] = property_obj
    
    return render_template('dashboard.html', 
                          user_properties=user_properties,
                          available_properties=available_properties,
                          active_auctions=active_auctions)

@app.route('/add_property', methods=['GET', 'POST'])
@login_required
def add_property():
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        location = request.form.get('location')
        area = float(request.form.get('area'))
        value = float(request.form.get('value'))
        description = request.form.get('description')
        image_url = request.form.get('image_url')
        registration_number = request.form.get('registration_number')
        
        # Create new property
        new_property = {
            'title': title,
            'location': location,
            'area': area,
            'value': value,
            'description': description,
            'imageUrl': image_url,
            'registrationNumber': registration_number,
            'ownerId': session['user_id'],
            'ownerName': session['name'],
            'status': 'pending',  # Initial status is pending for admin approval
            'forSale': False,
            'submissionDate': datetime.datetime.utcnow()
        }
        
        # Generate hash for property data
        new_property['dataHash'] = hash_property_data(new_property)
        
        property_id = mongo.db.properties.insert_one(new_property).inserted_id
        
        flash('Property submitted for approval!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_property.html')

@app.route('/sell_property/<property_id>', methods=['GET', 'POST'])
@login_required
def sell_property(property_id):
    property_obj = mongo.db.properties.find_one({'_id': ObjectId(property_id)})
    
    if not property_obj:
        flash('Property not found', 'danger')
        return redirect(url_for('dashboard'))
    
    if property_obj['ownerId'] != session['user_id']:
        flash('You do not own this property', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        asking_price = float(request.form.get('asking_price'))
        
        mongo.db.properties.update_one(
            {'_id': ObjectId(property_id)},
            {'$set': {'forSale': True, 'askingPrice': asking_price}}
        )
        
        flash('Property listed for sale!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('sell_property.html', property=property_obj)

@app.route('/buy_property/<property_id>', methods=['GET', 'POST'])
@login_required
def buy_property(property_id):
    property_obj = mongo.db.properties.find_one({'_id': ObjectId(property_id)})
    
    if not property_obj:
        flash('Property not found', 'danger')
        return redirect(url_for('dashboard'))
    
    if not property_obj['forSale']:
        flash('Property is not for sale', 'danger')
        return redirect(url_for('dashboard'))
    
    if property_obj['ownerId'] == session['user_id']:
        flash('You already own this property', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Create transaction record
        transaction = {
            'propertyId': property_id,
            'sellerId': property_obj['ownerId'],
            'buyerId': session['user_id'],
            'amount': property_obj['askingPrice'],
            'date': datetime.datetime.utcnow(),
            'type': 'sale'
        }
        
        mongo.db.transactions.insert_one(transaction)
        
        # Update property ownership
        mongo.db.properties.update_one(
            {'_id': ObjectId(property_id)},
            {
                '$set': {
                    'ownerId': session['user_id'],
                    'ownerName': session['name'],
                    'forSale': False,
                    'lastTransferDate': datetime.datetime.utcnow()
                }
            }
        )
        
        flash('Property purchased successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('buy_property.html', property=property_obj)

@app.route('/create_auction/<property_id>', methods=['GET', 'POST'])
@login_required
def create_auction(property_id):
    property_obj = mongo.db.properties.find_one({'_id': ObjectId(property_id)})
    
    if not property_obj:
        flash('Property not found', 'danger')
        return redirect(url_for('dashboard'))
    
    if property_obj['ownerId'] != session['user_id']:
        flash('You do not own this property', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        starting_bid = float(request.form.get('starting_bid'))
        end_date_str = request.form.get('end_date')
        end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
        
        # Create new auction
        new_auction = {
            'propertyId': property_id,
            'startingBid': starting_bid,
            'currentHighestBid': starting_bid,
            'currentHighestBidder': None,
            'startDate': datetime.datetime.utcnow(),
            'endDate': end_date,
            'status': 'active',
            'bids': []
        }
        
        auction_id = mongo.db.auctions.insert_one(new_auction).inserted_id
        
        # Update property status
        mongo.db.properties.update_one(
            {'_id': ObjectId(property_id)},
            {'$set': {'inAuction': True, 'auctionId': str(auction_id)}}
        )
        
        flash('Auction created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_auction.html', property=property_obj)

@app.route('/place_bid/<auction_id>', methods=['GET', 'POST'])
@login_required
def place_bid(auction_id):
    auction = mongo.db.auctions.find_one({'_id': ObjectId(auction_id)})
    
    if not auction:
        flash('Auction not found', 'danger')
        return redirect(url_for('dashboard'))
    
    if auction['status'] != 'active':
        flash('Auction is not active', 'danger')
        return redirect(url_for('dashboard'))
    
    if datetime.datetime.utcnow() > auction['endDate']:
        flash('Auction has ended', 'danger')
        return redirect(url_for('dashboard'))
    
    property_obj = mongo.db.properties.find_one({'_id': ObjectId(auction['propertyId'])})
    
    if request.method == 'POST':
        bid_amount = float(request.form.get('bid_amount'))
        
        if bid_amount <= auction['currentHighestBid']:
            flash('Bid amount must be higher than current highest bid', 'danger')
            return render_template('place_bid.html', auction=auction, property=property_obj)
        
        # Create new bid
        new_bid = {
            'userId': session['user_id'],
            'userName': session['name'],
            'amount': bid_amount,
            'timestamp': datetime.datetime.utcnow()
        }
        
        # Update auction with new bid
        mongo.db.auctions.update_one(
            {'_id': ObjectId(auction_id)},
            {
                '$push': {'bids': new_bid},
                '$set': {
                    'currentHighestBid': bid_amount,
                    'currentHighestBidder': session['user_id']
                }
            }
        )
        
        flash('Bid placed successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    # Get optimal bid suggestion using dynamic programming
    user_bids = list(mongo.db.auctions.aggregate([
        {'$match': {'status': 'completed'}},
        {'$unwind': '$bids'},
        {'$match': {'bids.userId': session['user_id']}},
        {'$project': {'bids': 1, 'propertyId': 1}}
    ]))
    
    optimal_bid = predict_optimal_bid(auction, property_obj, user_bids)
    
    return render_template('place_bid.html', 
                          auction=auction, 
                          property=property_obj,
                          optimal_bid=optimal_bid)

@app.route('/find_optimal_properties', methods=['GET', 'POST'])
@login_required
def find_optimal_properties_route():
    if request.method == 'POST':
        # Get user preferences
        location = request.form.get('location')
        price = float(request.form.get('price') or 0)
        area = float(request.form.get('area') or 0)
        location_weight = int(request.form.get('location_weight') or 1)
        price_weight = int(request.form.get('price_weight') or 1)
        area_weight = int(request.form.get('area_weight') or 1)
        
        preferences = {
            'location': location,
            'price': price,
            'area': area,
            'locationWeight': location_weight,
            'priceWeight': price_weight,
            'areaWeight': area_weight
        }
        
        # Get all available properties
        available_properties = list(mongo.db.properties.find({
            'status': 'approved',
            'forSale': True,
            'ownerId': {'$ne': session['user_id']}  
        }))
        print(available_properties)
        
        # Use greedy algorithm to find optimal properties
        optimal_properties = find_optimal_properties(available_properties, preferences)
        
        return render_template('optimal_properties.html', 
                              properties=optimal_properties,
                              preferences=preferences)
    
    return render_template('find_optimal_properties.html')

@app.route('/search_properties', methods=['GET', 'POST'])
@login_required
def search_properties_route():
    if request.method == 'POST':
        # Get search criteria
        location = request.form.get('location')
        min_price = float(request.form.get('min_price') or 0)
        max_price = float(request.form.get('max_price') or float('inf'))
        min_area = float(request.form.get('min_area') or 0)
        max_area = float(request.form.get('max_area') or float('inf'))
        
        criteria = {
            'location': location,
            'minPrice': min_price,
            'maxPrice': max_price,
            'minArea': min_area,
            'maxArea': max_area,
            'ownerId': {'$ne': session['user_id']}
        }
        
        results = search_properties(mongo.db.properties, criteria)
        
        return render_template('search_results.html', properties=results, criteria=criteria)
    
    return render_template('search_properties.html')

# Admin routes
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Get pending properties
    pending_properties = list(mongo.db.properties.find({'status': 'pending'}))
    
    return render_template('admin/dashboard.html', pending_properties=pending_properties)

@app.route('/admin/approve_property/<property_id>')
@admin_required
def approve_property(property_id):
    mongo.db.properties.update_one(
        {'_id': ObjectId(property_id)},
        {
            '$set': {
                'status': 'approved',
                'approvedBy': session['user_id'],
                'approvedDate': datetime.datetime.utcnow()
            }
        }
    )
    
    flash('Property approved successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/reject_property/<property_id>', methods=['GET', 'POST'])
@admin_required
def reject_property(property_id):
    if request.method == 'POST':
        reason = request.form.get('reason') or 'No reason provided'
        
        mongo.db.properties.update_one(
            {'_id': ObjectId(property_id)},
            {
                '$set': {
                    'status': 'rejected',
                    'rejectedBy': session['user_id'],
                    'rejectionReason': reason,
                    'rejectedDate': datetime.datetime.utcnow()
                }
            }
        )
        
        flash('Property rejected successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    property_obj = mongo.db.properties.find_one({'_id': ObjectId(property_id)})
    return render_template('admin/reject_property.html', property=property_obj)

@app.route('/admin/verify_documents/<property_id>')
@admin_required
def verify_property_documents(property_id):
    property_obj = mongo.db.properties.find_one({'_id': ObjectId(property_id)})
    
    if not property_obj:
        flash('Property not found', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    # Get documents for the property
    documents = list(mongo.db.documents.find({'propertyId': property_id}))
    
    verification_results = []
    for doc in documents:
        # Use hashing technique to verify document authenticity
        is_authentic = verify_document_hash(doc['hash'], doc['content'])
        verification_results.append({
            'documentId': str(doc['_id']),
            'name': doc['name'],
            'isAuthentic': is_authentic
        })
    
    # Verify property data hash
    property_data_authentic = hash_property_data(property_obj) == property_obj.get('dataHash')
    
    return render_template('admin/verify_documents.html', 
                          property=property_obj,
                          documents=verification_results,
                          property_data_authentic=property_data_authentic)

# API routes for AJAX calls
@app.route('/api/optimal_bid/<auction_id>')
@login_required
def get_optimal_bid(auction_id):
    auction = mongo.db.auctions.find_one({'_id': ObjectId(auction_id)})
    
    if not auction:
        return jsonify({'error': 'Auction not found'}), 404
    
    # Get property details
    property_obj = mongo.db.properties.find_one({'_id': ObjectId(auction['propertyId'])})
    
    # Get user's bidding history
    user_bids = list(mongo.db.auctions.aggregate([
        {'$match': {'status': 'completed'}},
        {'$unwind': '$bids'},
        {'$match': {'bids.userId': session['user_id']}},
        {'$project': {'bids': 1, 'propertyId': 1}}
    ]))
    
    # Use dynamic programming to predict optimal bid
    optimal_bid = predict_optimal_bid(auction, property_obj, user_bids)
    
    return jsonify({'optimalBid': optimal_bid})

if __name__ == '__main__':
    app.run(debug=True)
