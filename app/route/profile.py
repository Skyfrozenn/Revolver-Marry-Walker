import filetype

from .auth import login_required, current_user, render_template, request, flash, redirect, url_for

from .. import app
from ..database import Session, func,  select, User, Product, Purchase_history, selectinload , desc, Subcategory, Category

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


@app.get("/statistics")
def state():
    with Session() as session:
        # 1. Самый прибыльный товар
        max_product = session.execute(
            select(Product, func.sum(Purchase_history.spent).label("total_revenue"))
            .join(Product.order_item)
            .group_by(Product.id)
            .order_by(desc("total_revenue"))
            .limit(1)
        ).first()

        # 2. Самый частый покупатель
        max_user = session.execute(
            select(User, func.count(Purchase_history.id).label("purchase_count"))
            .join(User.order_item)
            .group_by(User.id)
            .order_by(desc("purchase_count"))
            .limit(1)
        ).first()

        # 3. Общая статистика
        total_count = session.scalar(select(func.sum(Purchase_history.count))) or 0
        total_revenue = session.scalar(select(func.sum(Purchase_history.spent))) or 0

        # 4. Самая популярная категория
        pop_category = session.execute(
            select(
                Subcategory.title.label("sub_category"),
                Category.title.label("category_name"), 
                func.count(Purchase_history.id).label("total_purchases")
            )
            .join(Subcategory.parent_categories)
            .join(Subcategory.sub_category_products)
            .join(Product.order_item)
            .group_by(Subcategory.title, Category.title)
            .order_by(desc(func.count(Purchase_history.id)))
            .limit(1)
        ).first()

    return render_template(
        "static.html",
        max_product=max_product,
        max_user=max_user,
        total_count=total_count,
        total_revenue=total_revenue,
        pop_category=pop_category
    )





