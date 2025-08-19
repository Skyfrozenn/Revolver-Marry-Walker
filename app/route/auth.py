from flask import redirect, render_template, url_for, request, flash #фласк

from flask_login import(  #фласк логин сессии

    LoginManager,
    current_user,
    login_user,
    login_required,
    UserMixin,
    logout_user

)

from flask_wtf import FlaskForm #базовый класс форм

from wtforms import StringField, PasswordField, SubmitField #поля формы

from wtforms.validators import DataRequired, Length, ValidationError #валидаторы проверки




from .. import app

from ..database import User, Session, select

from argon2 import PasswordHasher
from argon2.exceptions import  InvalidHashError


ph = PasswordHasher(time_cost=3, memory_cost=66536, parallelism=4)



#ФЛАСК ЛОГИН

login_manager = LoginManager() #наш обьект логина главный
login_manager.init_app(app)
login_manager.login_view = "auth"

class Login(UserMixin): #паспорт 
    def __init__(self,id,name,role):
        self.id = id
        self.name = name
        self.role = role
        
        

@login_manager.user_loader #загрузка при login_required
def load_user(id):
    with Session() as db_session:
        user = db_session.scalar(select(User).where(User.id == id))
        if user:
            return Login(
                id = user.id,
                name = user.name,
                role = user.role
            )
    return None



#ФЛАСК ФОРМЫ

class RegistrForm(FlaskForm):

    username =  StringField("Регистрация", validators=[
        DataRequired(message = "Обязательное поле"),
        Length(min=1 , max=20, message = "Длинна от 1 до 20 символов!")
    ])

    password = PasswordField(validators=[
        Length(min=6, message = "Длинна пароля должна быть от 6 символов и выще!")
    ])

    submit = SubmitField("Зарегистрироваться")

    #кастомный валидатор
    def validate_password(self, field):
        password = field.data 
        errors = []

        if not any(c.isupper() for c in password): 
            errors.append("Добавьте заглавную букву в пароле!")

        if not any(c in "!@#$%^&*()_+" for c in password):
            errors.append("Добавьте спецсимвол в пароль!")

        if errors:
            raise ValidationError(errors)


@app.get("/")
def home_page():
    form = RegistrForm()
    return render_template("auth.html", form = form)



@app.post("/register")
def reg():
    form = RegistrForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        hash_password = ph.hash(password) #шифруем

        with Session.begin() as db_session:
            #ПРОВЕРКА
            check_user = db_session.scalar(select(User).where(User.name == username))

            if check_user:
                flash("Имя занято!")
                return redirect(url_for('home_page'))


            #черновое сохранение в бд
            new_user = User(name = username, password = hash_password, role = "Creator")

             # добавляем в бд
            db_session.add(new_user)

            db_session.flush()

            # добавили в сессию и паспорт юзермиксина
            login_obj = Login(id = new_user.id, name = new_user.name, role = new_user.role)
            login_user(login_obj)

             
 
            return render_template("cards.html")
    else:
        return render_template("auth.html", form = form)
    
@app.post("/exit")
def end():
    logout_user()
    return redirect(url_for('home_page'))



@app.post("/entrance")
def identif():
    username = request.form.get("username")
    password = request.form.get("password")
    with Session() as session:
        user = session.scalar(select(User).where(User.name == username))
        if user:

            try:
                ph.verify(user.password, password)
                return render_template("cards.html")
            
            except InvalidHashError:
                flash("Неверный пароль!")
                return redirect(url_for("home_page"))
            
        else:
            flash("Пользователь не найден")
            return redirect(url_for("home_page"))
