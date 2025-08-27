from .. import app
from .auth import redirect, render_template, current_user, login_required, request

from ..database import select, Session, Subcategory, Category, joinedload, selectinload, func, Product, desc, Cart

from math import ceil

@app.get("/view_category")
@login_required
def all_category():
    with Session() as session:

        category = session.scalars(select(Category)).all()
    
    return render_template("view_category.html", category = category)
    


@app.get("/view_sub_category_product/<int:category_id>")
@login_required
def view_sub_category(category_id):

    with Session() as session:

        #выводим под категории этой категории
        sub_category = session.scalars(
            select(Subcategory)
            .where(Subcategory.category_id == category_id)
            .options(joinedload(Subcategory.parent_categories))
        ).all()

    return render_template("sub_category_product.html", sub_category = sub_category)



@app.get("/view_products/<int:page>/<int:sub_category_id>")
@login_required
def wath_all_products(page , sub_category_id):
    #количество товаров на странице
    PER_PAGE = 10

    with Session() as session:

        #выводим определенное количество товаров
        products = session.scalars(
            select(Product)
            .where(Product.sub_category_id == sub_category_id)
            .offset((page - 1) * PER_PAGE)
            .order_by(desc(Product.date_add))
            .limit(PER_PAGE)
        ).all()

        #Корзина юзера
        user_cart = session.scalars(
            select(Cart)
            .where(Cart.user_id == current_user.id)
            
        ).all()

        #передаем обьект подкатегории для явного указания всех товаров
        sub_category_obj = session.scalar(
            select(Subcategory)
            .where(Subcategory.id == sub_category_id)
            .options(joinedload(Subcategory.parent_categories))
        )


        #количество товаров общее
        total_product = session.scalar(
            select(func.count(Product.id))
            .where(Product.sub_category_id == sub_category_id)
        )

        #количество товаров страниц
        count_page = max(1, ceil(total_product / PER_PAGE))

    return render_template(
        "products.html",
        products = products,
        page = page,
        count_page = count_page,
        sub_category_id = sub_category_id,
        user_cart = user_cart,
        sub_category_obj = sub_category_obj

    )
