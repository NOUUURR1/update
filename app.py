from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# إعداد قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# تعريف الموديل
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100))
    birthdate = db.Column(db.String(20))
    profile_image_url = db.Column(db.String(200))


# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()


# ✅ مسار تسجيل المستخدم الجديد
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'message': 'Email already exists'}), 400

    new_user = User(
        full_name=data.get('full_name'),
        email=email,
        password=data.get('password'),
        birthdate=data.get('birthdate', ''),
        profile_image_url=data.get('profile_image_url', '')
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully', 'user_id': new_user.id})


# ✅ جلب بيانات المستخدم أو إنشاؤه إن لم يكن موجود
@app.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({
        'id': user.id,
        'full_name': user.full_name,
        'email': user.email,
        'password': user.password,
        'birthdate': user.birthdate,
        'profile_image_url': user.profile_image_url
    })


# ✅ تحديث بيانات المستخدم
@app.route('/profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        # لو مش موجود، ننشئه تلقائيًا
        user = User(id=user_id)
        db.session.add(user)

    data = request.get_json()
    user.full_name = data.get('full_name', user.full_name)
    user.email = data.get('email', user.email)
    user.password = data.get('password', user.password)
    user.birthdate = data.get('birthdate', user.birthdate)
    user.profile_image_url = data.get('profile_image_url', user.profile_image_url)

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})


# ✅ لتشغيل الخادم
if __name__ == '__main__':
    app.run(debug=True)
