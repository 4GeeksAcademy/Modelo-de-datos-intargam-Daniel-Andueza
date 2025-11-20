"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Post, User, Multimedia, Like, Comentario
# from models import Person   # <- comentario original dejado

app = Flask(__name__)
app.url_map.strict_slashes = False

# DATABASE CONFIG
db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    # Replace deprecated postgres:// with postgresql://
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    # Local fallback using SQLite (default for 4Geeks testing)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# MIGRATIONS AND CORS
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)

# ADMIN PANEL (from boilerplate)
setup_admin(app)

# Handle/serialize errors like a JSON object (boilerplate)


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints (boilerplate)


@app.route('/')
def sitemap():
    return generate_sitemap(app)

# endpoints Usuario


@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    serialized = [user.serialize() for user in users]
    return jsonify(serialized), 200


@app.route('/users/<int:user_id>', methods=['GET'])
def get_single_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify(user.serialize()), 200


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    is_active = data.get("is_active", True)

    if not email or not password:
        return jsonify({"error": "Email y contraseña son obligatorios"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Ya existe un usuario con ese email"}), 409

    nuevo_user = User(
        email=email,
        password=password,
        is_active=is_active
    )

    db.session.add(nuevo_user)
    db.session.commit()

    return jsonify(nuevo_user.serialize()), 201


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    data = request.get_json()

    if "email" in data:
        user.email = data["email"]
    if "password" in data:
        user.password = data["password"]
    if "is_active" in data:
        user.is_active = data["is_active"]

    db.session.commit()

    return jsonify(user.serialize()), 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"msg": "Usuario eliminado correctamente"}), 200


# endpoints para los post

@app.route('/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    serialized = [post.serialize() for post in posts]
    return jsonify(serialized), 200


@app.route('/posts/<int:post_id>', methods=['GET'])
def get_single_post(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return jsonify({"error": "Post no encontrado"}), 404
    return jsonify(post.serialize()), 200


@app.route('/posts', methods=['POST'])
def create_post():
    data = request.get_json()

    contenido = data.get("contenido")
    user_id = data.get("user_id")

    if not contenido or not user_id:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    # Validar usuario existente
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "Usuario no existe"}), 404

    nuevo_post = Post(
        contenido=contenido,
        user_id=user_id
    )

    db.session.add(nuevo_post)
    db.session.commit()

    return jsonify(nuevo_post.serialize()), 201


@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return jsonify({"error": "Post no encontrado"}), 404

    db.session.delete(post)
    db.session.commit()

    return jsonify({"msg": "Post eliminado correctamente"}), 200


# endpoints para likes

@app.route('/posts/<int:post_id>/likes', methods=['GET'])
def get_likes_of_post(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return jsonify({"error": "Post no encontrado"}), 404

    likes = [like.serialize() for like in post.likes]

    return jsonify(likes), 200


@app.route('/likes', methods=['POST'])
def create_like():
    data = request.get_json()

    user_id = data.get("user_id")
    post_id = data.get("post_id")

    if not user_id or not post_id:
        return jsonify({"error": "user_id y post_id son obligatorios"}), 400

    # Validar usuario
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Validar post
    post = Post.query.get(post_id)
    if post is None:
        return jsonify({"error": "Post no encontrado"}), 404

    # Validar que no existe ya el like
    existing_like = Like.query.filter_by(
        user_id=user_id, post_id=post_id).first()
    if existing_like:
        return jsonify({"error": "El usuario ya dio like a este post"}), 409

    new_like = Like(user_id=user_id, post_id=post_id)

    db.session.add(new_like)
    db.session.commit()

    return jsonify(new_like.serialize()), 201


@app.route('/likes', methods=['DELETE'])
def delete_like():
    data = request.get_json()

    user_id = data.get("user_id")
    post_id = data.get("post_id")

    if not user_id or not post_id:
        return jsonify({"error": "user_id y post_id son obligatorios"}), 400

    like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()

    if like is None:
        return jsonify({"error": "Like no encontrado"}), 404

    db.session.delete(like)
    db.session.commit()

    return jsonify({"msg": "Like eliminado correctamente"}), 200


# endpoints para los comentarios

@app.route('/posts/<int:post_id>/comentarios', methods=['GET'])
def get_post_comments(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return jsonify({"error": "Post no encontrado"}), 404

    data = [c.serialize() for c in post.comentarios]
    return jsonify(data), 200


@app.route('/comentarios', methods=['POST'])
def create_comment():
    data = request.get_json()

    contenido = data.get("contenido")
    user_id = data.get("user_id")
    post_id = data.get("post_id")

    if not contenido or not user_id or not post_id:
        return jsonify({"error": "contenido, user_id y post_id son obligatorios"}), 400

    # Validar usuario
    user = User.query.get(user_id)
    if user is None:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Validar post
    post = Post.query.get(post_id)
    if post is None:
        return jsonify({"error": "Post no encontrado"}), 404

    nuevo = Comentario(
        contenido=contenido,
        user_id=user_id,
        post_id=post_id
    )

    db.session.add(nuevo)
    db.session.commit()

    return jsonify(nuevo.serialize()), 201


@app.route('/comentarios/<int:comentario_id>', methods=['DELETE'])
def delete_comment(comentario_id):
    comentario = Comentario.query.get(comentario_id)

    if comentario is None:
        return jsonify({"error": "Comentario no encontrado"}), 404

    db.session.delete(comentario)
    db.session.commit()

    return jsonify({"msg": "Comentario eliminado correctamente"}), 200


# multimedia

@app.route('/posts/<int:post_id>/multimedia', methods=['GET'])
def get_post_multimedia(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return jsonify({"error": "Post no encontrado"}), 404

    multimedia = [m.serialize() for m in post.multimedias]
    return jsonify(multimedia), 200


@app.route('/posts/<int:post_id>/multimedia', methods=['POST'])
def add_multimedia_to_post(post_id):
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "La URL es obligatoria"}), 400

    # Validar que el post existe
    post = Post.query.get(post_id)
    if post is None:
        return jsonify({"error": "Post no encontrado"}), 404

    nueva_multimedia = Multimedia(
        url=url,
        post_id=post_id
    )

    db.session.add(nueva_multimedia)
    db.session.commit()

    return jsonify(nueva_multimedia.serialize()), 201


@app.route('/posts/<int:post_id>/multimedia/<int:multimedia_id>', methods=['DELETE'])
def delete_multimedia_from_post(post_id, multimedia_id):
    post = Post.query.get(post_id)
    if post is None:
        return jsonify({"error": "Post no encontrado"}), 404

    multimedia = Multimedia.query.get(multimedia_id)
    if multimedia is None or multimedia.post_id != post_id:
        return jsonify({"error": "Multimedia no encontrada para este post"}), 404

    db.session.delete(multimedia)
    db.session.commit()

    return jsonify({"msg": "Multimedia eliminada correctamente"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
