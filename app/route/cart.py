from .. import app
from .view_products import render_template, redirect, request, login_required, current_user, flash, url_for

from ..database import Cart, User,Subcategory,Category, Session, select


@app.post("/add_product_cart")
@login_required
def add_product_cart():
    product_id = request.form.get("product_id")
    action = request.form.get("action")

    product_id = int(product_id)

    with Session.begin() as session:
        
        #если это карточка
        if request.form.get("_method") == "cards":

            #если товар уже есть просто + 1
            if action == "increase":

                product = session.scalar(
                    select(Cart)
                    .where(Cart.product_id == product_id)
                    .where(Cart.user_id == current_user.id)

                )
                product.count +=1
                return redirect(url_for('watch_cards'))


            elif action == "decrease":

                product = session.scalar(
                    select(Cart)
                    .where(Cart.product_id == product_id)
                    .where(Cart.user_id == current_user.id)

                )
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

            sub_category_id = request.form.get("sub_category_id")
            page = request.form.get("page")

            # в итнеджер для передачи на юрл функцию
            sub_category_id = int(sub_category_id)
            page = int(page)

            
            #если товар уже есть просто + 1
            if action == "increase":

                product = session.scalar(
                    select(Cart)
                    .where(Cart.product_id == product_id)
                    .where(Cart.user_id == current_user.id)

                )
                product.count +=1
                return redirect(url_for("wath_all_products", page = page, sub_category_id = sub_category_id))


            elif action == "decrease":

                product = session.scalar(
                    select(Cart)
                    .where(Cart.product_id == product_id)
                    .where(Cart.user_id == current_user.id)

                )
                product.count -=1
                
                 

                if product.count == 0:
                    session.delete(product)
                     

                return redirect(url_for("wath_all_products", page = page, sub_category_id = sub_category_id))

            
            elif action == "add":

                product = Cart(user_id = current_user.id, product_id = product_id)
                session.add(product)
                return redirect(url_for('wath_all_products', page = page, sub_category_id = sub_category_id))



             
        
             
            


