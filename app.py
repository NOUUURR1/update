from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# إعداد قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# موديل المستخدم
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    birthdate = db.Column(db.String(20))
    profile_image_url = db.Column(db.String(250))

# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()

# ✅ مسار تحديث البروفايل (بدون توكن)
@app.route('/profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json()
    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    user.password = data.get('password', user.password)
    user.birthdate = data.get('birthdate', user.birthdate)
    user.profile_image_url = data.get('profile_image_url', user.profile_image_url)

    db.session.commit()

    return jsonify({'message': 'Profile updated successfully'}), 200
















