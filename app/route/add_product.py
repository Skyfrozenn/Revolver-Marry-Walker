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
from ..database import Cart, joinedload, selectinload


@app.get("/adding_cards_page")
@login_required
def watch_cards_page():
    return render_template("add_cards_page.html")




@app.post("/add_cards")
@login_required
def adding_card():
    file = request.files.get("photo") #фото товара может быть null
    title = request.form.get("title")
    descriprion = request.form.get("descriprion")
    price = request.form.get("price")
    count = request.form.get("count")

    # переводим в инт от сервера 
    price = int(price)
    count = int(count)

    new_cards = None

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
                descriprion = descriprion,
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





         



