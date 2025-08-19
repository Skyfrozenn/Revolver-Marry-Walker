from sqlalchemy import ForeignKey, create_engine, func, BINARY, select, LargeBinary
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column, relationship

from datetime import datetime

from typing import Optional



engine = create_engine("sqlite:///datebase.db", echo=True) #движок

Session = sessionmaker(engine) #фабрика сессий

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key = True)
    name : Mapped[str]
    password : Mapped[str]
    role : Mapped[str] = mapped_column(default = "user")
    photo_uploads : Mapped[Optional[bytes]] = mapped_column(LargeBinary,  nullable = True)
    join : Mapped[datetime] = mapped_column(server_default = func.now())

    #ебучие связи 
    cart : Mapped[list["Cart"]] = relationship(back_populates = "user_cart", cascade = "all, delete-orphan", lazy = "joined")
    order_item : Mapped[list["Purchase_history"]] = relationship(back_populates = "user_purchases", cascade = "all, delete-orphan", lazy = "joined")

    


 


class Category(Base):
    __tablename__ = "categories"
    id:Mapped[int] = mapped_column(primary_key = True)
    title : Mapped[str]

    sub_category : Mapped[list["Subcategory"]] = relationship(back_populates = "parent_categories", cascade = "all, delete-orphan", lazy = "joined")




class Subcategory(Base):
    __tablename__ = "subcategories"
    id:Mapped[int] = mapped_column(primary_key = True)
    title:Mapped[str]
    
    #внешний ключ
    category_id:Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete = "CASCADE"))

    #связь
    parent_categories : Mapped["Category"] = relationship(back_populates = "sub_category")
    sub_category_products : Mapped["Product"] = relationship(back_populates = "sub_category")



class Cart(Base):
    __tablename__ = "cart"
    id : Mapped[int] = mapped_column(primary_key = True)
    count : Mapped[int] = mapped_column(default = 1)

    #внешние ключи
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id", ondelete = "CASCADE"))
    product_id : Mapped[int] = mapped_column(ForeignKey("products.id"))

    

    #связь с юзером и товарами
    user_cart : Mapped[list["User"]] = relationship(back_populates = "cart")
    product_cart : Mapped[list["Product"]] = relationship(back_populates = "cart")
    
    



class Purchase_history(Base):
    __tablename__ = "purchases"
    id : Mapped[int] = mapped_column(primary_key = True)
    count : Mapped[int] = mapped_column(default = 1)

    #внешние ключи
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id", ondelete = "CASCADE"))
    product_id : Mapped[int] = mapped_column(ForeignKey("products.id"))

    

    #связь с юзером и товарами
    user_purchases : Mapped[list["User"]] = relationship(back_populates = "order_item")
    purchased_products : Mapped[list["Product"]] = relationship(back_populates = "order_item")
    


class Product(Base):
    __tablename__ = "products"

    id : Mapped[int] = mapped_column(primary_key = True)
    title : Mapped[str]
    descriprion : Mapped[str]
    avatar : Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable = True)
    date_add : Mapped[datetime] = mapped_column(server_default = func.now())
    price : Mapped[int]
    count : Mapped[int] = mapped_column(default = 1)

    #внещний ключ подкатегории 
    sub_category_id : Mapped[int] = mapped_column(ForeignKey("subcategories.id"), nullable = True) #для карточек они будут без подкатегорий

    #связи корзина, история покупок, подкатегория
    cart : Mapped[list["Cart"]] = relationship(back_populates = "product_cart")
    order_item : Mapped[list["Purchase_history"]] = relationship(back_populates = "purchased_products")
    sub_category : Mapped[list["Subcategory"]] = relationship(back_populates = "sub_category_products")



#def creat_table():
    #Base.metadata.create_all(engine)

def migrate():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
 