from flask import Flask , request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

#Para usar fronted
from flask_cors import CORS
#------------------------------

#Para autentificar
from flask_bcrypt import check_password_hash, generate_password_hash
import jwt
import datetime
#------------------------------

app = Flask(__name__)

#Para usar fronted
CORS(app)
#---------

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mypassword@localhost:3306/flaskmysql'
#app.config['SQLALCHEMY_DATABASE_URI'] =  'postgresql://postgres:mypassword@localhost:5432/flaskpostgresql'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db=SQLAlchemy(app)


ma= Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    user= db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))

    def __init__(self, email, user, password):
        self.email = email
        self.user = user
        self.password = password


# Define la función para crear el esquema dinámicamente
def create_table_schema(id):
    class TableSchema(ma.Schema):
        class Meta:
            fields = ('id','id_contact','user')

    table_schema = TableSchema()
    tables_schema = TableSchema(many=True)

    globals()[f'table_{id}_schema'] = table_schema
    globals()[f'tables_{id}_schema'] = tables_schema


#----------------------------
# Define la función para crear el esquema dinámicamente CHATS
def create_table_schema_chats(id,id_contact):
    class TableSchemaChats(ma.Schema):
        class Meta:
            fields = ('id', 'content', 'sender_id', 'receiver_id', 'created_at','created_at')

    table_schema_chats = TableSchemaChats()
    tables_schema_chats= TableSchemaChats(many=True)

    globals()[f'table_{id}_{id_contact}schema'] = table_schema_chats
    globals()[f'tables_{id}_{id_contact}schema'] = tables_schema_chats



with app.app_context():
    db.create_all()


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'user', 'password')


user_schema = UserSchema()
users_schema = UserSchema(many=True)



@app.route('/loginup', methods=['POST'])
def create_user():
    email=request.json['email']
    user=request.json['user']
    password = generate_password_hash(request.json['password'])
    existing_user = User.query.filter_by(user=user).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 409
    new_user = User(email, user, password)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

@app.route('/loginup', methods=['GET'])
def get_users():
    all_users=User.query.all()
    result=users_schema.dump(all_users)
    return jsonify(result)                    

@app.route('/loginup/<id>', methods=['GET'])
def get_user(id):
    user=User.query.get(id)
    return user_schema.jsonify(user) 

@app.route('/loginup/<id>', methods=['PUT'])
def update_user(id):
    user_to_update = User.query.get(id)  # Renombrar la variable aquí
    
    email = request.json['email']
    new_user = request.json['user']
    password = generate_password_hash(request.json['password'])

    user_to_update.email = email
    user_to_update.user = new_user  # Renombrar la variable aquí
    user_to_update.password = password
    
    db.session.commit()
    return user_schema.jsonify(user_to_update)



@app.route('/loginup/<id>', methods=['DELETE'])
def delete_user(id):
    user=User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)


#Login IN (Iniciar sesion)
@app.route('/', methods=['POST'])
def login():
    data = request.get_json()
    username = data['user']
    password = data['password']

    user = User.query.filter_by(user=username).first()
    if user and check_password_hash(user.password, password):
        # Las credenciales son válidas, puedes generar un token de autenticación aquí
        token = generate_token(user)  # Ejemplo: función para generar el token

        return jsonify({'token': token ,"user_id": user.id}), 200

    # Las credenciales son incorrectas
    return jsonify({'error': 'Credenciales inválidas'}), 401


def generate_token(user):
    # Definir las opciones y configuraciones del token
    token_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expira en 1 hora
    }
    secret_key = 'tuclavesecretadeltoken'  # Cambia esto a tu clave secreta real

    # Generar el token JWT utilizando PyJWT
    token = jwt.encode(token_payload, secret_key, algorithm='HS256')
    return token

#-------------------------------------

#Table ID
@app.route('/tableid', methods=['POST'])
def create_tableid():
    try:
        id = request.json.get('id')
        if not id:
            return 'id not provided', 400

        table_name = f'table_{id}'
        user_table = type(table_name, (db.Model,), {
            'id': db.Column(db.Integer, primary_key=True),
            'id_contact': db.Column(db.Integer),
            'user': db.Column(db.String(100))
        })

        create_table_schema(id)  # Llama a la función para crear el esquema dinámicamente

        db.create_all()
        return 'id table created successfully', 201

    except Exception as e:
        return str(e), 500


from sqlalchemy import inspect

@app.route('/tableid/<id>', methods=['POST'])
def post_tableid(id):
    try:
        # Obtener los datos de temperatura y humedad de la solicitud JSON
        id_contact = request.json.get('id_contact')
        username = request.json.get('user')

        # Verificar si la tabla existe en la base de datos
        table_name = f'table_{id}'
        inspector = inspect(db.engine)
        if table_name not in inspector.get_table_names():
            return 'Table not found', 404

        # Crear una instancia de la clase de la tabla dinámica
        TableClass = type(table_name, (db.Model,), {})
        table_entry = TableClass(id_contact=id_contact, user=username)

        # Agregar la nueva entrada a la base de datos
        db.session.add(table_entry)
        db.session.commit()

        return 'Data added successfully', 201

    except Exception as e:
        return str(e), 500  # Devuelve el mensaje de error en caso de que ocurra una excepción

#-----------------------------------------------------------------------------------------
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

@app.route('/tableid/<id>', methods=['DELETE'])
def delete_tableid(id):
    try:
        # Verificar si la tabla existe en la base de datos
        table_name = f'table_{id}'
        inspector = inspect(db.engine)
        if not inspector.has_table(table_name):
            return 'Table not found', 404

        # Crear una conexión y una sesión
        engine = create_engine(db.engine.url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Ejecutar una consulta SQL para eliminar la tabla
        query = text(f'DROP TABLE {table_name}')
        session.execute(query)
        session.commit()

        return 'Table deleted successfully', 200

    except Exception as e:
        return str(e), 500  # Devuelve el mensaje de error en caso de que ocurra una excepción




#-----------------------------------------------------------------------------------------

from sqlalchemy import inspect
from sqlalchemy import Table

@app.route('/tableid/<id>', methods=['GET'])
def get_tableid(id):
    try:
        table_name = f'table_{id}'  # Genera el nombre de la tabla a buscar
        inspector = inspect(db.engine)
        if not inspector.has_table(table_name):  # Verifica si la tabla existe en la base de datos
            return 'Table not found', 404

        # Reflect the tables from the database
        db.reflect()

        # Obtén la tabla dinámica a partir del nombre
        table = db.Model.metadata.tables[table_name]

        # Realiza la consulta a la tabla
        table_data = db.session.query(table).all()

        # Procesa los datos obtenidos y devuélvelos como respuesta
        data = []
        for row in table_data:
            data.append({
                'id': row.id,
                'id_contact': row.id_contact,
                'user': row.user
            })

        return jsonify(data), 200

    except Exception as e:
        return str(e), 500  # Devuelve el mensaje de error en caso de que ocurra una excepción


#Table Id _ IDcontact  chat

@app.route('/tablechat', methods=['POST'])
def create_tablechat():
    try:
        id = request.json.get('id')
        id_contact = request.json.get('id_contact')
        if not id or not id_contact:
            return 'id or id_contact not provided', 400

        # Comprueba si la tabla ya existe en la base de datos
        table_name = f'table_{id_contact}_{id}'
        inspector = inspect(db.engine)
        if table_name in inspector.get_table_names():
            return 'Table already exists', 200 

        # Si la tabla no existe, crea la nueva tabla dinámicamente
        table_name = f'table_{id}_{id_contact}'
        user_table = type(table_name, (db.Model,), {
            'id': db.Column(db.Integer, primary_key=True),
            'content' : db.Column(db.String(250)),
            'sender_id' : db.Column(db.Integer), 
            'receiver_id': db.Column(db.Integer), 
            'created_at' : db.Column(db.DateTime, default=datetime.datetime.utcnow)
        })

        create_table_schema_chats(id, id_contact)  # Llama a la función para crear el esquema dinámicamente

        db.create_all()
        return 'Chat table created successfully', 201

    except Exception as e:
        return str(e), 500




@app.route('/tablechat/<id>/<id_contact>', methods=['POST'])
def post_tablechat(id, id_contact):
    try:
        content = request.json['content']
        sender_id = request.json['sender_id']
        receiver_id = request.json['receiver_id']

        # Verificar si la tabla existe en la base de datos
        table_name = f'table_{id}_{id_contact}'
        inspector = inspect(db.engine)
        if table_name not in inspector.get_table_names():
           table_name = f'table_{id_contact}_{id}'

        # Crear una instancia de la clase de la tabla dinámica
        TableClass = type(table_name, (db.Model,), {})
        table_entry = TableClass(content=content, sender_id=sender_id, receiver_id=receiver_id,created_at=datetime.datetime.utcnow())

        # Agregar la nueva entrada a la base de datos
        db.session.add(table_entry)
        db.session.commit()

        return 'Data added successfully', 201

    except Exception as e:
        return str(e), 500  # Devuelve el mensaje de error en caso de que ocurra una excepción




""" @app.route('/tablechat/<id>/<id_contact>', methods=['DELETE'])
def delete_tablechat(id, id_contact):
    try:
        # Verificar si la tabla existe en la base de datos
        table_name = f'table_{id}_{id_contact}'
        inspector = inspect(db.engine)
        if not inspector.has_table(table_name):
            return 'Table not found', 404

        # Crear una conexión y una sesión
        engine = create_engine(db.engine.url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Ejecutar una consulta SQL para eliminar la tabla
        query = text(f'DROP TABLE {table_name}')
        session.execute(query)
        session.commit()

        return 'Table deleted successfully', 200

    except Exception as e:
        return str(e), 500  # Devuelve el mensaje de error en caso de que ocurra una excepción   """




#-----------------------------------------------------------------------------------------


@app.route('/tablechat/<id>/<id_contact>', methods=['GET'])
def get_tablechat(id, id_contact):
    try:
        table_name = f'table_{id}_{id_contact}'  # Genera el nombre de la tabla a buscar
        inspector = inspect(db.engine)
        if not inspector.has_table(table_name):  # Verifica si la tabla existe en la base de datos
            table_name = f'table_{id_contact}_{id}' 

        # Reflect the tables from the database
        db.reflect()

        # Obtén la tabla dinámica a partir del nombre
        table = db.Model.metadata.tables[table_name]

        # Realiza la consulta a la tabla
        table_data = db.session.query(table).all()

        # Procesa los datos obtenidos y devuélvelos como respuesta
        data = []
        for row in table_data:
            data.append({
                'id': row.id,
                'content': row.content,
                'sender_id': row.sender_id,
                'receiver_id': row.receiver_id,
                'created_at': row.created_at
            })

        return jsonify(data), 200

    except Exception as e:
        return str(e), 500  # Devuelve el mensaje de error en caso de que ocurra una excepción



if __name__ == '__main__':
    app.run(debug=True)

#Comands for use docker container mysql
#docker run --name mymysql -e MYSQL_ROOT_PASSWORD=mypassword -p 3306:3306 -d mysql:latest
#docker exec -it mymysql bash
#mysql -u root -p
#create database flaskmysql;