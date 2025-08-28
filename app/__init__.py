from flask import Flask
from flask_wtf.csrf import CSRFProtect #зашита от цсрф атак 

app = Flask(__name__)

app.config["SECRET_KEY"] = "secret_key" # потом сделаю норм ключ

csrf = CSRFProtect(app) #защита от csrf атак
 
 
 

#импорт всех модулей апп
from .route import (
    auth,
    profile,
    add_products,
    view_products,
    cart
)
    
 