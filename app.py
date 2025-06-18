from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

SECRET_KEY = "heart_guardian_super_key"

# 🧠 موديل المستخدم
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    birthdate = db.Column(db.String(20))
    profile_image_url = db.Column(db.String(200))

# 🛡️ دالة التحقق من التوكين
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'Missing Authorization header'}), 401
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

# 🔐 مسار تسجيل الدخول (للحصول على توكين)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.checkpw(data['password'].encode(), user.password):
        token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(days=1)},
            SECRET_KEY, algorithm='HS256'
        )
        return jsonify({'token': token, 'user_id': user.id})
    return jsonify({'message': 'Invalid credentials'}), 401

# 📝 عرض وتحديث البروفايل
@app.route('/profile/<int:user_id>', methods=['GET', 'PUT'])
@token_required
def profile(current_user_id, user_id):
    if current_user_id != user_id:
        return jsonify({'message': 'Unauthorized'}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if request.method == 'GET':
        return jsonify({
            'full_name': user.full_name,
            'email': user.email,
            'password': user.password,
            'birthdate': user.birthdate,
            'profile_image_url': user.profile_image_url
        })

    if request.method == 'PUT':
        data = request.get_json()
        user.full_name = data['full_name']
        user.email = data['email']
        user.password = data['password']
        user.birthdate = data['birthdate']
        user.profile_image_url = data.get('profile_image_url', '')
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)








