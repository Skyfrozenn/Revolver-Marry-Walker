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
    price = request.form.get("price")
    count = request.form.get("count")

    # переводим в инт от сервера 
    price = int(price)
    count = int(count)

     

    #1) провека майм типа
     
    with Session.begin() as db_session:
        
        #1) провека майм типа
        if file and file.filename:
            kind = filetype.guess(file.stream.read(261)) #читаем первые 261 байтов, то есть расширения фото
            file.stream.seek(0) #возвращаем поток в начало

            if kind  is None or kind.mime not in ALLOWED_MIME_TYPES:
                flash("Неверный формат файла!")

            #2 убираем опасные символы из содержания имени
            secure_filename(file.filename)

            #3 кодируем данные
            avatar = b64encode(file.read()).decode("utf-8") #размешаем биты в бд в формате читаемой строки
         
            new_cards = Product(
                title = title,
                description = description,
                avatar = avatar,
                price = price,
                count = count

            )

        else:
            flash("Фото обязательно для карточек!")
             
        #комитим
        db_session.add(new_cards)
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

    #в капиталайз
    sub_category_name = sub_category_name.capitalize().strip()
    category_name = category_name.capitalize().strip()

 
    

    if file and file.filename:

        #1 прояерм майм тип
        kind = filetype.guess(file.stream.read(261)) #читаем первые 261 байт
        file.stream.seek(0) #вернули данные обратно

        if kind is None or kind.mime not in ALLOWED_MIME_TYPES:
             flash("Загрузите только фото!")

        #2 убираем опасные символы на всякий случай 
        secure_filename(file.filename)


        #3 кодируем фото
        avatar = b64encode(file.read()).decode("utf-8")

        #СЕСИИ БД
        with Session.begin() as session:
            
            # 3 вывод категорий и их проверка с созданием если их нет
            category = session.scalar(
                select(Category)
                .where(Category.title == category_name)
            )

            sub_category = session.scalar(
                select(Subcategory)
                .where(Subcategory.title == sub_category_name)
            )

            #если категории нет , нахуй создаем
            if not category:
                category = Category(title = category_name)
                session.add(category)
                session.flush()

            if not sub_category:
                sub_category = Subcategory(title = sub_category_name, category_id = category.id)
                session.add(sub_category)
                session.flush()

            product = Product(
                title = title,
                description = description,
                avatar = avatar,
                price = price,
                count = count,
                sub_category_id = sub_category.id

  
            )
            #4 cохраняем в память
            session.add(product)

            #5 получаем айди до закрытия сессии
            sub_category_id = sub_category.id

        return redirect(url_for("wath_all_products", page = 1, sub_category_id = sub_category_id))

    else:
        flash("Фото обязательно!")





    



         



