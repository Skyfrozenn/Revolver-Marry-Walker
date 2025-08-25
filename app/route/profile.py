import filetype

from .auth import login_required, current_user, render_template, request, flash, redirect, url_for

from .. import app
from ..database import Session, func,  select, User, Product, Purchase_history

from base64 import b64encode
from werkzeug.utils import secure_filename


ALLOWED_MIME_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']







@app.get("/profile")
@login_required
def profile():
    with Session() as db_session:
        # наш юзер
        user = db_session.scalar(select(User).where(User.id == current_user.id))

        count = db_session.scalar(
            select(func.sum(Purchase_history.count))
            .where(Purchase_history.user_id == user.id)
        )
    return render_template("profile.html", user = user, count = count)




@app.post("/uploads_photo")
def update_photo():
    file = request.files.get("photo")

  
     # 1 проверка майм типа
    kind = filetype.guess(file.stream.read(261)) # Читаем первые байты файла для определения типа
    file.stream.seek(0)  # Возвращаем указатель файла в начало

    if kind is None or kind.mime not in ALLOWED_MIME_TYPES:
        flash("Неверный формат файла! Только 'image/jpeg', 'image/png', 'image/gif', 'image/webp'", "error")
        return redirect(url_for('profile'))

    
    #защита от хакерства
    secure_filename(file.filename)

    with Session.begin() as session:
        user = session.scalar(select(User).where(User.id == current_user.id))
        user.photo_uploads = b64encode(file.read()).decode("utf-8")

    return redirect(url_for('profile'))








