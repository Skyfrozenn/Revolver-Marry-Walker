from .profile import (
    filetype,
    app,
    redirect,
    render_template,
    request,
    ALLOWED_MIME_TYPES,
    secure_filename,
    flash,
    Session,
    Product,
    b64encode,
    login_required,
    select,
    current_user,
    func,
    url_for
  
 
)

from ..database import Cart, joinedload, selectinload, Category, Subcategory



@app.get("/adding_cards_page")
@login_required
def watch_cards_page():
    return render_template("add_cards_page.html")




@app.post("/add_cards")
@login_required
def adding_card():
    file = request.files.get("photo")  
    title = request.form.get("title")
    description = request.form.get("description")
    price = request.form.get("price", type=int)
    count = request.form.get("count", type=int)

    title = title.capitalize().strip()

    with Session.begin() as db_session:
        if file and file.filename:
            kind = filetype.guess(file.stream.read(261))
            file.stream.seek(0)

            if kind is None or kind.mime not in ALLOWED_MIME_TYPES:
                flash("Неверный формат файла!")
                return redirect(url_for("watch_cards"))

            secure_filename(file.filename)
            avatar = b64encode(file.read()).decode("utf-8")

            # Проверяем есть ли товар
            product_check = db_session.scalar(
                select(Product)
                .where(Product.title == title)
            )

            if product_check:  # ← ТОВАР СУЩЕСТВУЕТ
                product_check.count += count
                product_check.price = price
                product_check.description = description
                product_check.avatar = avatar

                if product_check.status == "Нет в наличии":
                    product_check.status = "В наличии"
                    flash("Товар снова в наличии!")
                else:
                    flash("Данные обновлены!")
                    
            else:  # ← ТОВАРА НЕТ
                new_cards = Product(
                    title=title,
                    description=description,
                    avatar=avatar,
                    price=price,
                    count=count
                )
                db_session.add(new_cards)
                flash("Новая карточка добавлена!")
                
        else:
            flash("Фото обязательно для карточек!")

    return redirect(url_for("watch_cards"))

 
    


@app.get("/cards")
@login_required
def watch_cards():

    with Session() as session:

        all_products = session.scalars(
            select(Product)
            .where(Product.sub_category_id == None)
        ).all()

        cart = session.scalars(
            select(Cart)
            .where(Cart.user_id == current_user.id)
            
        ).all()

     
    return render_template("cards.html", all_products = all_products, cart = cart)


@app.get("/add_products_page")
def add_page_products():
    return render_template("add_product_page.html")



@app.post("/add_new_product")
def add_product():
    file = request.files.get("photo")
    category_name = request.form.get("category")
    sub_category_name = request.form.get("sub_category")
    title = request.form.get("title")
    description = request.form.get("description")
    price = request.form.get("price", type=int)
    count = request.form.get("count", type=int)

    # в капиталайз
    sub_category_name = sub_category_name.capitalize().strip()
    category_name = category_name.capitalize().strip()
    title = title.capitalize().strip()

    if file and file.filename:
        # 1 проверяем майм тип
        kind = filetype.guess(file.stream.read(261))
        file.stream.seek(0)

        if kind is None or kind.mime not in ALLOWED_MIME_TYPES:
            flash("Загрузите только фото!")
            return redirect(url_for("add_product_page"))  # Редирект при ошибке

        # 2 убираем опасные символы
        secure_filename(file.filename)

        # 3 кодируем фото
        avatar = b64encode(file.read()).decode("utf-8")

        # СЕССИИ БД
        with Session.begin() as session:
            # Проверяем есть ли товар
            product_check = session.scalar(
                select(Product)
                .where(Product.title == title)
            )

            if product_check:
                # ОБНОВЛЯЕМ существующий товар
                product_check.count += count
                product_check.price = price
                product_check.description = description
                product_check.avatar = avatar

                if product_check.status == "Нет в наличии":
                    product_check.status = "В наличии"
                    flash("Товар снова в наличии!")
                else:
                    flash("Данные товара обновлены!")

                # Категория и подкатегория остаются прежними!
                sub_category_id = product_check.sub_category_id

            else:
                # СОЗДАЕМ новый товар
                # Находим или создаем категорию и подкатегорию
                category = session.scalar(
                    select(Category)
                    .where(Category.title == category_name)
                )

                sub_category = session.scalar(
                    select(Subcategory)
                    .where(Subcategory.title == sub_category_name)
                )

                # Если категории нет - создаем
                if not category:
                    category = Category(title=category_name)
                    session.add(category)
                    session.flush()

                if not sub_category:
                    sub_category = Subcategory(title=sub_category_name, category_id=category.id)
                    session.add(sub_category)
                    session.flush()

                product = Product(
                    title=title,
                    description=description,
                    avatar=avatar,
                    price=price,
                    count=count,
                    sub_category_id=sub_category.id
                )
                session.add(product)
                flash("Новый товар добавлен!")
                sub_category_id = sub_category.id

        return redirect(url_for("wath_all_products", page=1, sub_category_id=sub_category_id))

    else:
        flash("Фото обязательно!")
        return redirect(url_for("add_product_page"))





    



         



