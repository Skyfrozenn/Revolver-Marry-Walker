from .. import app
from .view_products import render_template, redirect, request, login_required, current_user, flash, url_for

from ..database import Cart, User,Subcategory,Category, Session, select, Product, func, joinedload, desc


@app.post("/add_product_cart")
@login_required
def add_product_cart():
    product_id = request.form.get("product_id")
    action = request.form.get("action")

    product_id = int(product_id)

    with Session.begin() as session:
        #находим товар
        product = session.scalar(
                    select(Cart)
                    .where(Cart.product_id == product_id)
                    .where(Cart.user_id == current_user.id)

                )
        
        #если это карточка
        if request.form.get("_method") == "cards":

            #если товар уже есть просто + 1
            if action == "increase":
                product.count +=1
                return redirect(url_for('watch_cards'))


            elif action == "decrease":
                product.count -=1

                if product.count == 0:
                    session.delete(product)
                     
                return redirect(url_for('watch_cards'))

            
            elif action == "add":

                product = Cart(user_id = current_user.id, product_id = product_id)
                session.add(product)
                return redirect(url_for('watch_cards'))
        
        #ТОВАРЫ 
        elif request.form.get("_method") == "products":

            sub_category_id = request.form.get("sub_category_id", type = int)
            page = request.form.get("page", type = int)

            #если товар уже есть просто + 1
            if action == "increase":

                product.count +=1
                return redirect(url_for("wath_all_products", page = page, sub_category_id = sub_category_id))

            elif action == "decrease":

                product.count -=1
      
                if product.count == 0:
                    session.delete(product)
                     
                return redirect(url_for("wath_all_products", page = page, sub_category_id = sub_category_id))

            elif action == "add":

                product = Cart(user_id = current_user.id, product_id = product_id)
                session.add(product)
                return redirect(url_for('wath_all_products', page = page, sub_category_id = sub_category_id))



             
@app.get("/cart_user_card")
@login_required
def cart_user_card():

    with Session() as session:
   
        user_products = session.execute(
            select(Product, Cart.count )
            .where(Product.sub_category_id == None)
            .join(Product.cart)
            .where(Cart.user_id == current_user.id)
            .options(
                joinedload(Product.sub_category)
                .joinedload(Subcategory.parent_categories)
            )
            
            
        ).all()
    return render_template("cart_cards.html", user_products = user_products)
        

@app.post("/decrease_products_cart")
def delete_products_cart():
    product_id = request.form.get("product_id", type=int)
    method = request.form.get("method")

    with Session.begin() as session:

        product_cart = session.scalar(
                    select(Cart)
                    .where(Cart.product_id == product_id)
                )
        
        if method == "decrease":
            product_cart.count -=1
            if product_cart.count == 0:
                session.delete(product_cart)

        elif method == "all_del":
            session.delete(product_cart)

    return redirect(url_for("cart_user_card"))


         
            



        
        

            


