from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    posts: Mapped[list["Post"]] = relationship(back_populates="user")
    likes: Mapped[list["Like"]] = relationship(back_populates="user")
    comentarios: Mapped[list["Comentario"]
                        ] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    contenido: Mapped[str] = mapped_column(String(600), nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False)
    fecha_publicacion: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.utcnow, nullable=False)
    user: Mapped["User"] = relationship(back_populates="posts")
    multimedias: Mapped[list["Multimedia"]
                        ] = relationship(back_populates="post")
    likes: Mapped[list["Like"]] = relationship(back_populates="post")
    comentarios: Mapped[list["Comentario"]
                        ] = relationship(back_populates="post")

    def serialize(self):
        return {
            "id": self.id,
            "contenido": self.contenido,
            "user_id": self.user_id,
            "fecha_publicacion": self.fecha_publicacion,
        }


class Multimedia(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(600), nullable=False)
    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("post.id"), nullable=False)
    fecha_publicacion: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.utcnow, nullable=False)
    post: Mapped["Post"] = relationship(back_populates="multimedias")

    def serialize(self):
        return {
            "id": self.id,
            "url": self.url,
            "post_id": self.post_id,
            "fecha_publicacion": self.fecha_publicacion,
        }


class Like(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("post.id"), nullable=False)
    fecha_publicacion: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.utcnow, nullable=False)
    user: Mapped["User"] = relationship(back_populates="likes")
    post: Mapped["Post"] = relationship(back_populates="likes")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "fecha_publicacion": self.fecha_publicacion
        }


class Comentario(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    contenido: Mapped[str] = mapped_column(String(800), nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("post.id"), nullable=False)
    fecha_publicacion: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.utcnow, nullable=False)
    user: Mapped["User"] = relationship(back_populates="comentarios")
    post: Mapped["Post"] = relationship(back_populates="comentarios")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "contenido": self.contenido,
            "post_id": self.post_id,
            "fecha_publicacion": self.fecha_publicacion
        }
