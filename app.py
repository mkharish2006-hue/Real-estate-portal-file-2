from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "mkharish2006@gmail.com"
SENDER_PASSWORD = "chec iale qilt albh"

# Uploads folder
uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(uploads_dir, exist_ok=True)
app.config['UPLOAD_FOLDER'] = uploads_dir

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# =====================
# FAVORITES TABLE (FIX)
# =====================
favorites = db.Table(
    'favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('property_id', db.Integer, db.ForeignKey('property.id'))
)

# =====================
# MODELS
# =====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

    properties = db.relationship('Property', backref='owner', lazy=True)

    favorites = db.relationship(
        'Property',
        secondary=favorites,
        backref='favorited_by'
    )

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    price = db.Column(db.Integer)
    location = db.Column(db.String(200))
    address = db.Column(db.String(200))
    amenities = db.Column(db.Text)
    property_type = db.Column(db.String(50))
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    area = db.Column(db.Integer)
    map_url = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    images = db.relationship('PropertyImage', backref='property', lazy=True)
    reviews = db.relationship('Review', backref='property', lazy=True)
    inquiries = db.relationship('Inquiry', backref='property', lazy=True)

class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    
    reviewer = db.relationship('User', backref='reviews_written', lazy=True)
    
class Inquiry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'))
    message = db.Column(db.Text)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_inquiries')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_inquiries')

# =====================
# LOGIN
# =====================

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# =====================
# ROUTES
# =====================

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for("login"))
            
        # Generate OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Store in verification session
        session['temp_user'] = {
            'name': name,
            'email': email,
            'password_hash': generate_password_hash(password),
            'otp': otp
        }
        
        # Send Email
        try:
            send_otp_email(email, name, otp)
            flash("OTP sent to your email. Please verify.", "info")
            return redirect(url_for("verify_otp"))
        except Exception as e:
            flash(f"Error sending email: {str(e)}", "danger")
            return redirect(url_for("register"))
            
    return render_template("register.html")

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    if 'temp_user' not in session:
        return redirect(url_for("register"))
        
    if request.method == "POST":
        user_otp = request.form["otp"]
        stored_otp = session['temp_user']['otp']
        
        if user_otp == stored_otp:
            # Create User
            temp = session['temp_user']
            user = User(
                name=temp['name'],
                email=temp['email'],
                password=temp['password_hash'] # Already hashed
            )
            db.session.add(user)
            db.session.commit()
            
            # Login
            login_user(user)
            session.pop('temp_user', None)
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid OTP. Please try again.", "danger")
            
    return render_template("verify_otp.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Email not found!", "danger")
            return redirect(url_for("forgot_password"))
            
        # Generate OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Store in session for reset
        session['reset_user'] = {
            'email': email,
            'otp': otp
        }
        
        # Send Email
        try:
            send_otp_email(email, user.name, otp, subject="Reset Your Password")
            flash("OTP sent to your email.", "info")
            return redirect(url_for("reset_perform"))
        except Exception as e:
            flash(f"Error sending email: {str(e)}", "danger")
    
    return render_template("forgot_password.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_perform():
    if 'reset_user' not in session:
        return redirect(url_for("forgot_password"))
        
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "verify_otp":
            user_otp = request.form.get("otp")
            if user_otp == session['reset_user']['otp']:
                session['reset_verified'] = True
                flash("OTP Verified. Set new password.", "success")
                return render_template("reset_password.html", step="new_password")
            else:
                flash("Invalid OTP", "danger")
                
        elif action == "set_password":
            if not session.get('reset_verified'):
                return redirect(url_for("reset_perform"))
                
            new_pass = request.form.get("password")
            user = User.query.filter_by(email=session['reset_user']['email']).first()
            user.password = generate_password_hash(new_pass)
            db.session.commit()
            
            session.pop('reset_user', None)
            session.pop('reset_verified', None)
            flash("Password reset successfully! Please login.", "success")
            return redirect(url_for("login"))
            
    return render_template("reset_password.html", step="verify_otp")

def send_otp_email(receiver_email, name, otp, subject="Your Verification Code"):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg['Subject'] = f"{subject} - Real Estate Portal"
    
    # Generic HTML body for both Reg and Reset
    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; color: #333; border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
        <div style="background-color: #000; padding: 20px; text-align: center;">
            <h1 style="color: #fff; margin: 0;">Real Estate Portal</h1>
        </div>
        <div style="padding: 30px; background-color: #fff;">
            <h2 style="color: #000;">Hello {name},</h2>
            <p>Here is your verification code:</p>
            <div style="text-align: center; margin: 30px 0;">
                <span style="font-size: 32px; font-weight: bold; color: #dc3545; letter-spacing: 5px;">{otp}</span>
            </div>
            <p>If you didn't request this, please ignore this email.</p>
        </div>
        <div style="background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #666;">
            &copy; {datetime.now().year} Real Estate Portal
        </div>
    </div>
    """
    
    msg.attach(MIMEText(html_body, 'html'))
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form["email"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("dashboard"))
    return render_template("login.html")



@app.route("/dashboard")
@login_required
def dashboard():
    inquiries = Inquiry.query.filter_by(receiver_id=current_user.id).order_by(Inquiry.date_sent.desc()).all()
    return render_template("dashboard.html", inquiries=inquiries)

@app.route("/properties")
# @login_required  <-- REMOVED FOR GUEST ACCESS
def view_properties():
    properties = Property.query.all()
    # If user is logged in, pass favorites info, else empty list
    # current_user is available in template automatically via context processor 
    # but we might need explicit handling if logic depends on it
    return render_template("view_properties.html", properties=properties)

@app.route("/property/<int:property_id>")
@login_required
def property_detail(property_id):
    property = Property.query.get_or_404(property_id)
    reviews = Review.query.filter_by(property_id=property_id).all()
    return render_template("property_detail.html", property=property, reviews=reviews)

@app.route("/add-review/<int:property_id>", methods=["POST"])
@login_required
def add_review(property_id):
    rating = request.form.get("rating")
    comment = request.form.get("comment")
    review = Review(property_id=property_id, reviewer_id=current_user.id, rating=rating, comment=comment)
    db.session.add(review)
    db.session.commit()
    return redirect(url_for("property_detail", property_id=property_id))

@app.route("/edit-property/<int:property_id>", methods=["GET", "POST"])
@login_required
def edit_property(property_id):
    property = Property.query.get_or_404(property_id)
    if property.user_id != current_user.id:
        flash("You cannot edit this property.", "danger")
        return redirect(url_for("view_properties"))
        
    if request.method == "POST":
        property.title = request.form["title"]
        property.price = request.form["price"]
        property.location = request.form["location"]
        property.address = request.form["address"]
        property.property_type = request.form["property_type"]
        property.bedrooms = request.form.get("bedrooms")
        property.bathrooms = request.form.get("bathrooms")
        property.area = request.form.get("area")
        property.amenities = request.form["amenities"]
        property.map_url = request.form.get("map_url")
        
        # Handle details update
        db.session.commit()
        
        # Handle Images
        if 'images' in request.files:
            files = request.files.getlist('images')
            for file in files:
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(uploads_dir, filename))
                    img = PropertyImage(filename=filename, property_id=property.id)
                    db.session.add(img)
            db.session.commit()
            
        return redirect(url_for("property_detail", property_id=property.id))
    return render_template("edit_property.html", property=property)

@app.route("/search")
@login_required
def search_properties():
    properties = Property.query.all()
    locations = sorted(list(set([p.location for p in properties])))
    return render_template("search_properties.html", properties=properties, locations=locations)

@app.route("/search-results")
@login_required
def search_results():
    location = request.args.get('location')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    property_type = request.args.get('property_type')
    bedrooms = request.args.get('bedrooms')
    
    query = Property.query
    
    if location:
        query = query.filter(Property.location == location)
    if min_price:
        query = query.filter(Property.price >= int(min_price))
    if max_price:
        query = query.filter(Property.price <= int(max_price))
    if property_type:
        query = query.filter(Property.property_type == property_type)
    if bedrooms:
        query = query.filter(Property.bedrooms >= int(bedrooms))
        
    properties = query.all()
    return render_template("search_results.html", properties=properties)

@app.route("/contact/<int:property_id>", methods=["GET", "POST"])
@login_required
def contact_seller(property_id):
    property = Property.query.get_or_404(property_id)
    if request.method == "POST":
        message = request.form["message"]
        inquiry = Inquiry(
            sender_id=current_user.id,
            receiver_id=property.user_id,
            property_id=property.id,
            message=message
        )
        db.session.add(inquiry)
        db.session.commit()
        flash("Message sent successfully!", "success")
        return redirect(url_for("property_detail", property_id=property_id))
    return render_template("contact_seller.html", property=property)

@app.route("/add-property", methods=["GET", "POST"])
@login_required
def add_property():
    if request.method == "POST":
        prop = Property(
            title=request.form["title"],
            price=request.form["price"],
            location=request.form["location"],
            address=request.form.get("address"),
            amenities=request.form.get("amenities"),
            property_type=request.form.get("property_type"),
            bedrooms=request.form.get("bedrooms"),
            bathrooms=request.form.get("bathrooms"),
            area=request.form.get("area"),
            map_url=request.form.get("map_url"),
            user_id=current_user.id
        )
        db.session.add(prop)
        db.session.commit()
        
        # Handle images
        images = request.files.getlist("images")
        for image in images:
            if image and image.filename:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_image = PropertyImage(filename=filename, property_id=prop.id)
                db.session.add(new_image)
        db.session.commit()

        return redirect(url_for("dashboard"))
    return render_template("add_property.html")

@app.route("/delete-property/<int:property_id>", methods=["POST"])
@login_required
def delete_property(property_id):
    prop = Property.query.get_or_404(property_id)
    if prop.user_id != current_user.id:
        flash("You can only delete your own properties!", "danger")
        return redirect(url_for("view_properties"))
    
    db.session.delete(prop)
    db.session.commit()
    flash("Property deleted successfully!", "success")
    return redirect(url_for("view_properties"))

@app.route("/toggle-favorite/<int:property_id>", methods=["POST"])
@login_required
def toggle_favorite(property_id):
    prop = Property.query.get_or_404(property_id)
    if prop in current_user.favorites:
        current_user.favorites.remove(prop)
    else:
        current_user.favorites.append(prop)
    db.session.commit()
    return redirect(url_for("view_properties"))

@app.route("/favorites")
@login_required
def favorites():
    return render_template("favorites.html", properties=current_user.favorites)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# =====================
# MAIN
# =====================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)  