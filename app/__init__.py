from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret_key" # потом сделаю норм ключ


#здесь будут импорты из роут папки других апп конфигураций 