##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2020/2021 ===============
## =============================================
## ================= Leiloes ===================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================


from typing import final
from flask import Flask, jsonify, request
from datetime import datetime
import logging, psycopg2, time, math, random
import os

app = Flask(__name__) 


@app.route('/') 
def hello(): 
	return """

	Hello World!  <br/>
	<br/>
	Check the sources for instructions on how to use the endpoints!<br/>
	<br/>
	BD 2021 Team<br/>
	<br/>
	"""


##############################################################
##		Funcoes para listar a varias tabelas
##############################################################


# Listar todos os utilizadores
@app.route("/dbproj/users", methods=["GET"])
def list_users():
	logger.info("###			PROJECT: GET /dbproj/users				###");

	conn = db_connection()
	cur = conn.cursor()

	cur.execute("SELECT user_id, username, password, email, auth_token FROM auction_user")
	rows = cur.fetchall()

	payload = []
	logger.debug("---- users ----")
	for row in rows:
		logger.debug(row)
		content = {'UserId': int(row[0]), 'Username': row[1], 'Password': row[2], 'Email': row[3], 'AuthToken': row[4]}
		payload.append(content) # appending to the payload to be returned

	conn.close()
	return jsonify(payload)


# listar todos os leiloes existentes
@app.route("/dbproj/leilao", methods=['GET'])
def list_auctions():
	logger.info("###              PROJECT: GET /dbproj/leilao              ###");   

	conn = db_connection()
	cur = conn.cursor()

	# seleciona todos os dados da tabela de leiloes
	cur.execute("""SELECT auction_id, title, description, price_min, date_start, date_end, user_id, is_finished, winner_id 
					FROM auction""")
	rows = cur.fetchall()

	payload = []
	logger.debug("---- auctions  ----")

	# adiciona ao payload todos os dados das varias eleicoes
	for row in rows:
		logger.debug(row)
		
		# seleciona o username do vendedor
		cur.execute("SELECT username FROM auction_user WHERE user_id = %s", (row[6],))
		user = cur.fetchall()

		content = {'LeilaoId': int(row[0]), 'Titulo': row[1], 'Descricao': row[2], 'Preço minimo': row[3], 'Data de comeco': row[4], 'Data de fim': row[5], 'Vendedor': user[0][0], 'Terminada': row[7], 'Vencedor': row[8]}
		payload.append(content) # appending to the payload to be returned

	conn.close()
	return jsonify(payload)


# listar todos os leiloes
@app.route("/dbproj/licitar/", methods=['GET'])
def list_bids():
	logger.info("###			PROJECT: GET /dbproj/licitar/				###");

	conn = db_connection()
	cur = conn.cursor()

	cur.execute("SELECT date, value, user_id, auction_id FROM bid")
	rows = cur.fetchall()

	payload = []
	logger.debug("---- users ----")
	for row in rows:
		logger.debug(row)
		content = {'Data': row[0], 'Valor': row[1], 'User ID': row[2], 'LeilaoID': row[3]}
		payload.append(content) # appending to the payload to be returned

	return jsonify(payload)


# listar todas as mensagens
@app.route("/dbproj/msgs", methods=['GET'])
def list_msgs():
	logger.info("###              PROJECT: GET /dbproj/leilao              ###");   

	conn = db_connection()
	cur = conn.cursor()

	# seleciona todos os dados da tabela de leiloes
	cur.execute("""SELECT auction_id, message, date, user_id 
					FROM auction_msg""")
	rows = cur.fetchall()

	payload = []
	logger.debug("---- messages  ----")

	# adiciona ao payload todos os dados das varias eleicoes
	for row in rows:
		logger.debug(row)
		
		# seleciona o username de quem enviou a mensagem
		cur.execute("SELECT username FROM auction_user WHERE user_id = %s", (row[3],))
		user = cur.fetchall()

		content = {'LeilaoId': int(row[0]), 'Mensagem': row[1], 'Data': row[2], 'Utilizador': user[0][0]}
		payload.append(content) # appending to the payload to be returned

	conn.close()
	return jsonify(payload)


# listar todas as notificacoes de licitacoes
@app.route("/dbproj/notifs", methods=['GET'])
def list_notifs():
	logger.info("###              PROJECT: GET /dbproj/notifs              ###");   

	conn = db_connection()
	cur = conn.cursor()

	# seleciona todos os dados da tabela de leiloes
	cur.execute("""SELECT date, message, auction_id, user_id 
					FROM bid_notification""")
	rows = cur.fetchall()

	payload = []
	logger.debug("---- notifications  ----")

	# adiciona ao payload todos os dados das varias eleicoes
	for row in rows:
		logger.debug(row)
		
		# seleciona o username de quem enviou a mensagem
		cur.execute("SELECT username FROM auction_user WHERE user_id = %s", (row[3],))
		user = cur.fetchall()

		content = {'LeilaoId': int(row[2]), 'Mensagem': row[1], 'Data': row[0], 'Utilizador': user[0][0]}
		payload.append(content) # appending to the payload to be returned

	conn.close()
	return jsonify(payload)


# listar todas as notificacoes de mensagens
@app.route("/dbproj/msg_notifs", methods=['GET'])
def list_msg_notifs():
	logger.info("###              PROJECT: GET /dbproj/msg_notifs              ###");   

	conn = db_connection()
	cur = conn.cursor()

	# seleciona todos os dados da tabela de leiloes
	cur.execute("""SELECT date, message, auction_id, user_id 
					FROM message_notification""")
	rows = cur.fetchall()

	payload = []
	logger.debug("---- notifications  ----")

	# adiciona ao payload todos os dados das varias eleicoes
	for row in rows:
		logger.debug(row)
		
		# seleciona o username de quem enviou a mensagem
		cur.execute("SELECT username FROM auction_user WHERE user_id = %s", (row[3],))
		user = cur.fetchall()

		content = {'LeilaoId': int(row[2]), 'Mensagem': row[1], 'Data': row[0], 'Utilizador': user[0][0]}
		payload.append(content) # appending to the payload to be returned

	conn.close()
	return jsonify(payload)


##############################################################
##				Funcionalidades gerais
##############################################################


## 	Adiciona um novo utilizador por payload em JSON
@app.route("/dbproj/user", methods=['POST'])
def register_user():
	logger.info("###			PROJECT: POST /dbproj/user				###");
	payload = request.get_json()

	conn = db_connection()
	cur = conn.cursor()

	logger.info("---- new user ----")
	logger.debug(f'payload: {payload}')

	statement = """INSERT INTO auction_user (username, password, email)
					VALUES (%s, %s, %s)"""

	values = (payload["username"], payload["password"], payload["email"])

	## Protecao contra null
	values = (payload["username"], payload["password"], payload["email"])
	if(len(payload["username"])<1 or (" "in payload["username"])):
		result={'error':'username null'}
		return jsonify(result)
	if(len(payload["password"])<1 or (" "in payload["password"])):
		result={'error':'password null'}
		return jsonify(result)

	if(len(payload["email"])<1 or (" "in payload["email"])):
		result={'error':'email null'}
		return jsonify(result)
	if(("@" not in payload["email"])):
		result={'error':'email must have @'}
		return jsonify(result)
	try:
		## Protecao contra username ou password j existente
		cur.execute("SELECT user_id, username, password, email, auth_token FROM auction_user")
		rows = cur.fetchall()
		for row in rows:
			logger.debug(row)
			if(row[1]==payload["username"]):
				result={'error':'username already exist'}
				return jsonify(result)
			if(row[3]==payload["email"]):
				result={'error':'email already exist'}
				return jsonify(result)
		##------------

		cur.execute(statement, values)
		cur.execute("commit")

		# seleciona o utilizador inserido, para depois retornar o id gerado
		cur.execute("SELECT user_id FROM auction_user WHERE username = %s", (payload["username"],) )
		
		rows = cur.fetchall()
		row = rows[0]
		result = {"userId": int(row[0]) }
	
	except (Exception, psycopg2.DatabaseError) as error:
		logger.error(error)
		result = {'error': 'errorCode'}
	
	finally:
		if conn is not None:
			conn.close()

	return jsonify(result)


## 	Verifica o login de um utilizador atraves uma payload em JSON
@app.route("/dbproj/user", methods=['PUT'])
def verify_user():
	logger.info("###			PROJECT: PUT /dbproj/user				###");
	payload = request.get_json()

	conn = db_connection()
	cur = conn.cursor()

	if "username" not in payload or "password" not in payload:
		return 'username and password are required to login'

	logger.info("---- new login ----")
	logger.debug(f'payload: {payload}')

	## Protecao para pedir o token só se o user existir e pass corresponder
	cur.execute("SELECT user_id, username, password, email, auth_token FROM auction_user")
	rows = cur.fetchall()
	aux_username=0
	aux_pass=0
	for row in rows:
		logger.debug(row)
		if(row[1]==payload["username"]): ##entao o username existe
			aux_username=1
			if(row[2]==payload["password"]):##entao a password corresponde
				aux_pass=2
	if(aux_username!=1):
		result={'error':'username not exist'}
		return jsonify(result)
	if(aux_pass!=2):
		result={'error':'password error'}
		return jsonify(result)
	##------------
	## proteger contra token ja existente
	cur.execute("SELECT auth_token FROM auction_user WHERE username= %s",(payload["username"],))
	row=cur.fetchall()
	logger.debug(row[0][0])
	if(row[0][0]!=None): ##existe ja um token
		result={'error':'o user ja foi verificado'}
		return jsonify(result)

	##fim proteger
	statement = """UPDATE auction_user 
					SET auth_token = %s
					WHERE user_id = (SELECT user_id FROM auction_user WHERE username = %s)"""
				
	rand = random.randint(0, 100000000)
	values = (rand, payload["username"])

	try:
		res = cur.execute(statement, values)
		result = f'authToken: {rand}'
		cur.execute("commit")
	except(Exception, psycopg2.DatabaseError) as error:
		logger.error(error)
		result = {'error': 'errorCode'}
	
	finally:
		if conn is not None:
			conn.close()

	return jsonify(result)


## 	Adiciona um novo leilao por payload de JSON
@app.route("/dbproj/leilao", methods=['POST'])
def create_auction():
	logger.info("###			PROJECT: POST /dbproj/leilao				###");
	payload = request.get_json()

	conn = db_connection()
	cur = conn.cursor()

	# recebe o token do utilizador
	headers = request.headers
	token = headers['token']

	#obter o id do utilizador
	cur.execute("SELECT user_id, auth_token FROM auction_user WHERE auth_token = %s", (token,))
	rows = cur.fetchall()

	if len(rows) < 1:
		conn.close()
		return jsonify({"error": "invalid auth_token"})

	user_id = rows[0][0]

	logger.info("---- user id -----")
	logger.debug(user_id)

	logger.info("---- new auction ----")
	logger.debug(f'payload: {payload}')

	statement = """INSERT INTO auction (auction_id, title, description, date_start, date_end, price_min, user_id, is_finished, version)
					VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

	## Protecao contra null
	ean_code = str(random.randint(1000000000000, 9999999999999))
	values = (ean_code, payload["title"], payload["description"], payload["date_start"], payload["date_end"], payload["price_min"], user_id, 0, 1)
	if(len(payload["title"])<1 or (" "== payload["title"][0])):
		result={'error':'title null'}
		return jsonify(result)
	if(len(payload["description"])<1 or (" "==payload["description"][0])):
		result={'error':'description null'}
		return jsonify(result)
	if(len(payload["date_start"])<1 ):
		result={'error':'date_start null'}
		return jsonify(result)
	if(payload["price_min"]<=0):
		result={'error':'price_min null'}
		return jsonify(result)
	
	##protecao para data_start
	aux1=0
	aux2=0
	if(("-" or " " or ":") not in payload["date_start"] or len(payload["date_start"])!=19):
		result={'error':'format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
		return jsonify(result)
	for i in range(len(payload["date_start"])):
		if(payload["date_start"][i]=="-"):
			aux2+=1
			if(aux2==1):
				if(aux1!=4):
					result={'error':'type: ano, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			elif(aux2==2):
				if(aux1!=2):
					result={'error':'type: mes, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			else:
				result={'error':'here format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
				return jsonify(result)
			aux1=0
		elif(payload["date_start"][i]==" "):
			aux2+=1
			if(aux2==3):
				if(aux1!=2):
					result={'error':'type: dia, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			else:
				result={'error':'aqui format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
				return jsonify(result)
			aux1=0
		elif(payload["date_start"][i]==":"):
			aux2+=1
			if(aux2==4):
				if(aux1!=2):
					result={'error':'type: hora, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			elif(aux2==5):
				if(aux1!=2):
					result={'error':'type: min, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			else:
				result={'error':'vamos format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
				return jsonify(result)
			aux1=0
		else:
			aux1+=1

	##fim protecao start
	##protecao para data_end
	aux1=0
	aux2=0
	if(("-" or " " or ":") not in payload["date_end"] or len(payload["date_end"])!=19):
		result={'error':'format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
		return jsonify(result)
	for i in range(len(payload["date_end"])):
		if(payload["date_start"][i]=="-"):
			aux2+=1
			if(aux2==1):
				if(aux1!=4):
					result={'error':'type: ano, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			elif(aux2==2):
				if(aux1!=2):
					result={'error':'type: mes, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			else:
				result={'error':'here format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
				return jsonify(result)
			aux1=0
		elif(payload["date_end"][i]==" "):
			aux2+=1
			if(aux2==3):
				if(aux1!=2):
					result={'error':'type: dia, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			else:
				result={'error':'aqui format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
				return jsonify(result)
			aux1=0
		elif(payload["date_end"][i]==":"):
			aux2+=1
			if(aux2==4):
				if(aux1!=2):
					result={'error':'type: hora, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			elif(aux2==5):
				if(aux1!=2):
					result={'error':'type: min, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			else:
				result={'error':'vamos format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
				return jsonify(result)
			aux1=0
		else:
			aux1+=1
	##fim protecao end

	##protege contra data_end inferior a data atual
	row=payload["date_end"]
	logger.info("---- data end ----")
	logger.debug(str(datetime.now()))
	aux=str(datetime.now())
	aux2=""
	logger.debug(aux)
	for i in range(len(aux)):
		if(aux[i-2]==" " and aux[i+1]==":"):	
			aux2+=str(int(aux[i])+1)
		else:
			aux2+=aux[i]
	logger.debug(aux2)
	if(payload["date_end"]<=str(aux2)):
		result={'error':'date_end tem de ser superior a data atual'}
		return jsonify(result)

	##protege contra data de incio > data fim
	logger.info("---- data incio>date end----")
	logger.debug(payload["date_start"])
	if(payload["date_start"]>=payload["date_end"]):
		result={'error':'date_start tem de ser inferior a data_end'}
		return jsonify(result)

	
	try:
		cur.execute(statement, values)
		cur.execute("commit")

		cur.execute("SELECT auction_id FROM auction WHERE title = %s", (payload["title"],) )

		rows = cur.fetchall()
		row = rows[0]
		result = {"leilaoId": int(row[0])}

	except (Exception, psycopg2.DatabaseError) as error:
		logger.error(error)
		result = {'error': 'errorCode'}
	
	finally:
		if conn is not None:
			conn.close()

	return jsonify(result)


# pesquisar por leilao existente
@app.route("/dbproj/leiloes/<keyword>", methods=['GET'])
def get_auction(keyword):
	logger.info("###              PROJECT: GET /dbproj/leiloes/<keyword>              ###");   

	logger.debug(f'keyword: {keyword}')

	conn = db_connection()
	cur = conn.cursor()

	# seleciona os leiloes que contem keyword
	cur.execute("""SELECT auction_id, title, description, price_min, date_start, date_end, user_id, is_finished, winner_id
					FROM auction 
					WHERE title LIKE %(name)s OR description LIKE %(name)s""",  { 'name': '%{}%'.format(keyword), 'name': '%{}%'.format(keyword)} )
	rows = cur.fetchall()

	payload = []
	logger.debug("---- selected auctions  ----")

	# adiciona ao payload os dados das varias eleicoes
	for row in rows:
		logger.debug(row)
		
		# seleciona o username do vendedor
		cur.execute("SELECT username FROM auction_user WHERE user_id = %s", (row[6],))
		user = cur.fetchall()

		content = {'LeilaoId': int(row[0]), 'Titulo': row[1], 'Descricao': row[2], 'Preço minimo': row[3], 'Data de comeco': row[4], 'Data de fim': row[5], 'Vendedor': user[0][0], 'Terminada': row[7], 'Vencedor': row[8]}
		payload.append(content)

	conn.close ()
	return jsonify(payload)


# listar leiloes em que um utilizador tenha atividade
@app.route("/dbproj/user/leiloes", methods=['GET'])
def get_user_auctions():
	# alterar para receber token atraves dos headers
	logger.info("###              PROJECT: GET /dbproj/user/leiloes              ###");   

	conn = db_connection()
	cur = conn.cursor()

	# recebe o token do utilizador
	headers = request.headers
	token = headers['token']

	if(len(token)<1):
		result={'error':'token vazio'}
		return jsonify(result)

	# seleciona o user, baseado no token de login recebido
	cur.execute("SELECT user_id, username FROM auction_user WHERE auth_token = %s", (token,) )
	rows = cur.fetchall()
	logger.debug(len(rows))
	if(len(rows)<1): 
		result={'error':'invalid token'}
		return jsonify(result)
	username = rows[0][1]
	user_id = rows[0][0]
	

	logger.debug("---- selected user  ----")
	logger.debug(username)

	# seleciona todos os leiloes criados pelo utilizador
	cur.execute("""SELECT auction_id, title, description, auction_id, price_min, date_start, date_end, user_id 
					FROM auction 
					WHERE user_id = %s""", (user_id,))
	rows = cur.fetchall()

	# adiciona os leiloes ao payload
	payload = []
	logger.debug("---- auctions created by user  ----")
	for row in rows:
		logger.debug(row)
		content = {'LeilaoId': int(row[0]), 'Titulo': row[1], 'Descricao': row[2], 'Codigo EAN': row[3], 'Preço minimo': row[4], 'Data de comeco': row[5], 'Data de fim': row[6], 'Vendedor': username}
		payload.append(content) # appending to the payload to be returned

	# seleciona todos os leiloes em que o utilizador fez licitacoes
	cur.execute("""SELECT auction_id, title, description, auction_id,price_min, date_start, date_end, user_id 
					FROM auction 
					WHERE auction_id = (SELECT auction_id FROM bid WHERE user_id = %s)""", (user_id,))
	rows = cur.fetchall()

	#adiciona os leiloes ao payload
	logger.debug("---- auctions bidded by user ----")
	for row in rows:
		logger.debug(row)

		# seleciona o username do vendedor
		cur.execute("SELECT username FROM auction_user WHERE user_id = %s", (row[7],))
		user = cur.fetchall()[0][0]

		content = {'LeilaoId': int(row[0]), 'Titulo': row[1], 'Descricao': row[2], 'Codigo EAN': row[3], 'Preço minimo': row[4], 'Data de comeco': row[5], 'Data de fim': row[6], 'Vendedor': user}
		payload.append(content) # appending to the payload to be returned

	conn.close ()
	return jsonify(content)


# licitar num leilao 
@app.route("/dbproj/licitar/<leilaoId>/<licitacao>", methods=['GET'])
def bid_auction(leilaoId, licitacao):
	logger.info("###			PROJECT: GET /dbproj/leiloes				###");

	logger.debug(f'leilaoId: {leilaoId}')
	logger.debug(f'licitacao: {licitacao}')

	conn = db_connection()
	cur = conn.cursor()

	# recebe o token do utilizador
	headers = request.headers
	token = headers['token']
	if(len(token)<1):
		result={'error':'token vazio'}
		return jsonify(result)

	# seleciona o user, baseado no token de login dado
	cur.execute("SELECT user_id FROM auction_user WHERE auth_token = %s", (token,) )
	rows = cur.fetchall()
	if(len(rows)<1):
		result={'error':'invalid token'}
		return jsonify(result)
	user = rows[0][0]

	logger.debug("---- selected user id ----")
	logger.debug(user)

	#seleciona o leilao, baseado no id recebido no url
	cur.execute("SELECT auction_id, price_min FROM auction WHERE auction_id = %s", (leilaoId,))
	rows = cur.fetchall()

	auction = rows[0][0]
	min_value = rows[0][1]

	if float(licitacao) < float(min_value):
		return jsonify("Erro: Valor licitado menor que o minimo aceite.")

	logger.debug("---- selected auction id ----")
	logger.debug(auction)

	# seleciona a licitacao maxima neste leilao
	cur.execute("""SELECT MAX(value)
					FROM bid
					WHERE auction_id = %s""", (auction,))
	rows = cur.fetchall()

	value = rows[0][0]

	if value != None:
		if float(licitacao) <= float(value):
			return jsonify("Erro: Licitacao menor ou igual a atual.")

	# cria uma nova licitacao
	logger.info("---- new bid ----")
	logger.debug(licitacao)

	statement = """INSERT INTO bid (date, value, user_id, auction_id)
					VALUES (%s, %s, %s, %s)"""

	# para guardar a data atual
	timestamp = datetime.now()

	values = (timestamp, licitacao, user, auction)

	## protege contra o vendedor ser licitador
	
	cur.execute("SELECT user_id FROM auction WHERE auction_id = %s", (leilaoId,) )
	rows = cur.fetchall()
	if(user==rows[0][0]):
		result={'error':'o vendedor nao pode ser licitador'}
		return jsonify(result)
	
	##protege contra data_end inferior a data atual
	cur.execute("SELECT date_end FROM auction WHERE auction_id = %s", (leilaoId,))
	row=cur.fetchall()
	logger.info("---- data end ----")
	logger.debug(str(row[0][0]))
	logger.debug(str(datetime.now()))
	aux=str(datetime.now())
	aux2=""
	logger.debug(aux)

	for i in range(len(aux)):
		if(aux[i-2]==" " and aux[i+1]==":"):	
			aux2+=str(int(aux[i])+1)
		else:
			aux2+=aux[i]
	logger.debug(aux2)
	if(str(row[0][0])<=str(aux2)):
		result={'error':'o leilão já acabou'}
		return jsonify(result)

	try:
		cur.execute(statement, values)
		cur.execute("commit")

		result = {"Success": licitacao}
	
	except (Exception, psycopg2.DatabaseError) as error:
		logger.error(error)
		result = {'error': 'database Error'}
	
	finally:
		if conn is not None:
			conn.close()

	return jsonify(result)


# editar propriedades de um leilao
@app.route("/dbproj/leilao/<leilaoId>", methods=['PUT'])
def edit_auction(leilaoId):
	logger.info("###			PROJECT: PUT /dbproj/leilao/{leilaoId}				###");
	logger.debug(f'leilaoId: {leilaoId}')
	
	payload = request.get_json()

	conn = db_connection()
	cur = conn.cursor()

	# recebe o token do utilizador
	headers = request.headers
	token = headers['token']
	if(len(token)<1):
		result={'error':'token vazio'}
		return jsonify(result)
	
	logger.debug(token)
	# obter o id do utilizador
	cur.execute("SELECT user_id FROM auction_user WHERE auth_token = %s", (token,))
	rows = cur.fetchall()

	if len(rows) < 1:
		conn.close()
		return jsonify({"error": "invalid auth_token"})

	user = rows[0][0]

	# obter id do dono do leilao
	cur.execute("SELECT user_id FROM auction WHERE auction_id = %s", (leilaoId,))
	rows = cur.fetchall()

	auction_user = rows[0][0]

	if user != auction_user:
		return jsonify({"Error":"Utilizador nao e dono deste leilao"})

	logger.info("---- new info  ----")
	logger.debug(f'payload: {payload}')

	# seleciona a versao do leilao atual
	cur.execute("""SELECT version
					FROM auction
					WHERE auction_id = %s""", (leilaoId,))
	version = cur.fetchall()

	# edita o leilao
	statement = """UPDATE auction
					SET title = %s, description = %s, date_start = %s, date_end = %s, price_min = %s, version = %s
					WHERE auction_id = %s"""

	values = (payload["title"], payload["description"], payload["date_start"], payload["date_end"], payload["price_min"], int(version[0][0]) + 1, leilaoId)
	
	if(len(payload["title"])<1 or (" "== payload["title"][0])):
		result={'error':'title null'}
		return jsonify(result)
	if(len(payload["description"])<1 or (" "==payload["description"][0])):
		result={'error':'description null'}
		return jsonify(result)
	if(len(payload["date_start"])<1 ):
		result={'error':'date_start null'}
		return jsonify(result)
	if(payload["price_min"]<=0):
		result={'error':'price_min null'}
		return jsonify(result)
	
	##protecao para data_start
	aux1=0
	aux2=0
	if(("-" or " " or ":") not in payload["date_start"] or len(payload["date_start"])!=19):
		result={'error':'format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
		return jsonify(result)
	for i in range(len(payload["date_start"])):
		if(payload["date_start"][i]=="-"):
			aux2+=1
			if(aux2==1):
				if(aux1!=4):
					result={'error':'type: ano, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			elif(aux2==2):
				if(aux1!=2):
					result={'error':'type: mes, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			else:
				result={'error':'here format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
				return jsonify(result)
			aux1=0
		elif(payload["date_start"][i]==" "):
			aux2+=1
			if(aux2==3):
				if(aux1!=2):
					result={'error':'type: dia, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			else:
				result={'error':'aqui format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
				return jsonify(result)
			aux1=0
		elif(payload["date_start"][i]==":"):
			aux2+=1
			if(aux2==4):
				if(aux1!=2):
					result={'error':'type: hora, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			elif(aux2==5):
				if(aux1!=2):
					result={'error':'type: min, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			else:
				result={'error':'vamos format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
				return jsonify(result)
			aux1=0
		else:
			aux1+=1

	##fim protecao start
	##protecao para data_end
	aux1=0
	aux2=0
	if(("-" or " " or ":") not in payload["date_end"] or len(payload["date_end"])!=19):
		result={'error':'format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
		return jsonify(result)
	for i in range(len(payload["date_end"])):
		if(payload["date_start"][i]=="-"):
			aux2+=1
			if(aux2==1):
				if(aux1!=4):
					result={'error':'type: ano, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			elif(aux2==2):
				if(aux1!=2):
					result={'error':'type: mes, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			else:
				result={'error':'here format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
				return jsonify(result)
			aux1=0
		elif(payload["date_end"][i]==" "):
			aux2+=1
			if(aux2==3):
				if(aux1!=2):
					result={'error':'type: dia, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			else:
				result={'error':'aqui format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
				return jsonify(result)
			aux1=0
		elif(payload["date_end"][i]==":"):
			aux2+=1
			if(aux2==4):
				if(aux1!=2):
					result={'error':'type: hora, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			elif(aux2==5):
				if(aux1!=2):
					result={'error':'type: min, format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
					return jsonify(result)
			else:
				result={'error':'vamos format date(ano-mes-dia hora:min:s): XXXX-XX-XX XX:XX:XX'}
				return jsonify(result)
			aux1=0
		else:
			aux1+=1
	##fim protecao end

	##protege contra data_end inferior a data atual
	row=payload["date_end"]
	logger.info("---- data end ----")
	logger.debug(str(datetime.now()))
	aux=str(datetime.now())
	aux2=""
	logger.debug(aux)
	for i in range(len(aux)):
		if(aux[i-2]==" " and aux[i+1]==":"):	
			aux2+=str(int(aux[i])+1)
		else:
			aux2+=aux[i]
	logger.debug(aux2)
	if(payload["date_end"]<=str(aux2)):
		result={'error':'date_end tem de ser superior a data atual'}
		return jsonify(result)

	##protege contra data de incio > data fim
	logger.info("---- data incio>date end----")
	logger.debug(payload["date_start"])
	if(payload["date_start"]>=payload["date_end"]):
		result={'error':'date_start tem de ser inferior a data_end'}
		return jsonify(result)


	try:
		cur.execute(statement, values)
		cur.execute("commit")
		result = {"LeilaoId": leilaoId}
	
	except (Exception, psycopg2.DatabaseError) as error:
		logger.error(error)
		result = {'error': 'data base error'}
	
	finally:
		if conn is not None:
			conn.close()

	return jsonify(result)


# escrever mensagem no mural de um leilao
@app.route("/dbproj/leilao/<leilaoId>", methods=['POST'])
def post_msg(leilaoId):
	logger.info("###			PROJECT: POST /dbproj/leilao/<leilaoId>				###");
	logger.debug(f'leilaoId: {leilaoId}')
	payload = request.get_json()

	conn = db_connection()
	cur = conn.cursor()

	# recebe o token do utilizador
	headers = request.headers
	token = headers['token']
	if(len(token)<1):
		result={'error':'token vazio'}
		return jsonify(result)
	# obter o id do utilizador
	cur.execute("SELECT user_id FROM auction_user WHERE auth_token = %s", (token,))
	rows = cur.fetchall()

	if len(rows) < 1:
		conn.close()
		return jsonify({"error": "invalid auth_token"})

	user_id = rows[0][0]

	logger.info("---- user id -----")
	logger.debug(user_id)

	# verificar se leilao existe
	cur.execute("""SELECT auction_id 
					FROM auction 
					WHERE auction_id = %s""", (leilaoId,))
	rows = cur.fetchall()

	if len(rows) < 1:
		conn.close()
		return jsonify({"error": "invalid auction_id"})

	logger.info("---- new message ----")
	logger.debug(f'payload: {payload}')

	statement = """INSERT INTO auction_msg (date, message, user_id, auction_id)
					VALUES (%s, %s, %s, %s)"""
	timestamp = datetime.now()
	logger.debug(payload["message"])
	values = (timestamp, payload["message"], user_id, leilaoId)
	
	## protege contra message null
	if(len(payload["message"])<1 or (" "== payload["message"][0])):
		result={'error':'message null'}
		return jsonify(result)
	
	try:
		cur.execute(statement, values)
		cur.execute("commit")

		result = {"leilaoId": leilaoId}

	except (Exception, psycopg2.DatabaseError) as error:
		logger.error(error)
		result = {'error': 'errorCode'}
	
	finally:
		if conn is not None:
			conn.close()


	return jsonify(result)


# consultar mural de um leilao
@app.route("/dbproj/leilao/<leilaoId>/mural", methods=["GET"])
def get_mural(leilaoId):
	logger.info("###              PROJECT: GET /dbproj/user              ###");   

	conn = db_connection()
	cur = conn.cursor()

	# recebe o token do utilizador
	headers = request.headers
	token = headers['token']
	if(len(token)<1):
		result={'error':'token vazio'}
		return jsonify(result)
	# obter o id do utilizador
	cur.execute("SELECT user_id FROM auction_user WHERE auth_token = %s", (token,))
	rows = cur.fetchall()

	if len(rows) < 1:
		conn.close()
		return jsonify({"error": "invalid auth_token"})

	payload = []

	cur.execute("""SELECT message, date, auction_id, user_id
					FROM auction_msg
					WHERE auction_id = %s""", (leilaoId,))
	rows = cur.fetchall()

	logger.debug("---- Messages ----")
	for row in rows:
		logger.debug(row)

		content = {"Messagem": row[0], "Data": row[1], "Leilao": row[2], "Utilizador": row[3]}

		payload.append(content)

	return jsonify(payload)


# consultar mensagens recebidas
@app.route("/dbproj/user", methods=['GET'])
def get_messages():
	logger.info("###              PROJECT: GET /dbproj/user              ###");   

	conn = db_connection()
	cur = conn.cursor()

	# recebe o token do utilizador
	headers = request.headers
	token = headers['token']
	if(len(token)<1):
		result={'error':'token vazio'}
		return jsonify(result)

	# obter o id do utilizador
	cur.execute("SELECT user_id FROM auction_user WHERE auth_token = %s", (token,))
	rows = cur.fetchall()

	if len(rows) < 1:
		conn.close()
		return jsonify({"error": "invalid auth_token"})

	user_id = rows[0][0]

	payload = []

	# selecionar todas as mensagens recebidas pelo utilizador
	cur.execute("""SELECT message, date, auction_id, user_id
					FROM message_notification
					WHERE user_id = %s""", (user_id,))
	rows = cur.fetchall()

	logger.debug("---- messages ----")

	# adiciona ao payload JSON todas as mensagens
	for row in rows:
		logger.debug(row)

		content = {'Mensagem': row[0], 'Data': row[1], 'Leilao': row[2], 'Utilizador': row[3]}
		payload.append(content)

	conn.close ()
	return jsonify(payload)


# terminar leiloes
@app.route("/dbproj/leilao/terminar", methods=['POST'])
def finish_auctions():
	logger.info("###			PROJECT: POST /dbproj/leilao/terminar			###");

	conn = db_connection()
	cur = conn.cursor()

	# seleciona leiloes que data de fim inferior a data atual, ou seja, leiloes que ja terminaram
	cur.execute("SET TIMEZONE='Europe/Lisbon'")
	cur.execute("""SELECT auction_id, date_end
					FROM auction
					WHERE is_finished = 0 AND date_end < current_timestamp""")
	rows = cur.fetchall()

	result = []

	for row in rows:
		logger.debug(row)

		auction = row[0]

		statement = """UPDATE auction
						SET is_finished = %s, winner_id = %s, price_final = %s
						WHERE auction_id = %s"""
		
		# seleciona todas as licitacoes neste leilao, escolhe o user_id com maior valor licitado
		cur.execute("""SELECT MAX(value), user_id
						FROM bid
						WHERE auction_id = %s
						GROUP BY user_id
						ORDER BY MAX(value) DESC""", (auction,))
			
		tmp = cur.fetchall()

		# se len for 0, significa que nao houveram licitacoes neste leilao
		if len(tmp) != 0:
			price_final = tmp[0][0]
			winner = tmp[0][1]
		
		else:
			price_final = 0
			winner = 0

		values = (1, winner, price_final, auction)

		# atualiza o leilao para terminado
		try:
			cur.execute(statement, values)
			cur.execute("commit")

			result = {"leilaoId": auction, "Terminado": "true", "Vencedor": winner, "Preco final": price_final}

		except (Exception, psycopg2.DatabaseError) as error:
			logger.error(error)
			result = {'error': 'errorCode'}
		
		finally:
			if conn is not None:
				conn.close()

	return jsonify(result)


# ver detalhes de leiloes
@app.route("/dbproj/leilao/<leilaoId>", methods=["GET"])
def view_auction_details(leilaoId):
	logger.info("###              PROJECT: GET /dbproj/leilao/<leilaoId>              ###");   

	conn = db_connection()
	cur = conn.cursor()

	# recebe o token do utilizador
	headers = request.headers
	token = headers['token']
	if(len(token)<1):
		result={'error':'token vazio'}
		return jsonify(result)

	# obter o id do utilizador
	cur.execute("SELECT user_id FROM auction_user WHERE auth_token = %s", (token,))
	rows = cur.fetchall()

	if len(rows) < 1:
		conn.close()
		return jsonify({"error": "invalid auth_token"})

	payload = []

	# selecionar os detalhes deste leilao
	cur.execute("""SELECT title, description, date_start, date_end, price_min, price_final, is_finished, winner_id, version
					FROM auction
					WHERE auction_id = %s""", (leilaoId,))
	rows = cur.fetchall()

	logger.debug("---- auction ----")

	# adiciona ao payload JSON todos os dados
	for row in rows:
		logger.debug(row)

		content = {'Titulo': row[0], 'Descricao': row[1], 'Data de comeco': row[2], 'Data de fim': row[3], 'Preco minimo': row[4], 'Preco final': row[5], 'Terminado': row[6], 'Vencedor': row[7], 'Versao': row[8]}
		payload.append(content)

	# selecionar todas as licitacoes feitas neste leilao
	cur.execute("""SELECT date, value, user_id
					FROM bid
					WHERE auction_id = %s""", (leilaoId,))
	rows = cur.fetchall()

	logger.debug("---- bids in auction ----")

	# adiciona ao payload JSON todas as notificacoes
	for row in rows:
		logger.debug(row)

		content = {'Data': row[0], 'Valor': row[1], 'Utilizador': row[2]}
		payload.append(content)

	# selecionar todas as mensagens no mural neste leilao
	cur.execute("""SELECT date, message, user_id
					FROM auction_msg
					WHERE auction_id = %s""", (leilaoId,))
	rows = cur.fetchall()

	logger.debug("---- messages in auction ----")

	# adiciona ao payload JSON todas as notificacoes
	for row in rows:
		logger.debug(row)

		content = {'Data': row[0], 'Message': row[1], 'Utilizador': row[2]}
		payload.append(content)

	conn.close ()
	return jsonify(payload)


# listar todas as versoes dos leiloes
@app.route("/dbproj/leilao_bak/<leilaoId>", methods=['GET'])
def list_baks(leilaoId):
	logger.info("###              PROJECT: GET /dbproj/leilao              ###");   

	conn = db_connection()
	cur = conn.cursor()

	# seleciona todos os dados da tabela de leiloes
	cur.execute("""SELECT auction_id, title, description, price_min, date_start, date_end, user_id, version
					FROM auction_backup
					WHERE auction_id = %s""", (leilaoId,))
	rows = cur.fetchall()

	payload = []
	logger.debug("---- auctions  ----")

	# adiciona ao payload todos os dados das varias eleicoes
	for row in rows:
		logger.debug(row)
		
		# seleciona o username do vendedor
		cur.execute("SELECT username FROM auction_user WHERE user_id = %s", (row[6],))
		user = cur.fetchall()

		content = {'LeilaoId': int(row[0]), 'Titulo': row[1], 'Descricao': row[2], 'Preço minimo': row[3], 'Data de comeco': row[4], 'Data de fim': row[5], 'Vendedor': user[0][0], 'Versao': row[7]}
		payload.append(content) # appending to the payload to be returned

	conn.close()
	return jsonify(payload)


# logout
@app.route("/dbproj/user/logout", methods=['POST'])
def logout():
	logger.info("###			PROJECT: POST /dbproj/leilao/terminar			###");

	conn = db_connection()
	cur = conn.cursor()

	# recebe o token do utilizador
	headers = request.headers
	token = headers['token']
	if(len(token)<1):
		result={'error':'token vazio'}
		return jsonify(result)
	# obter o id do utilizador
	cur.execute("SELECT user_id FROM auction_user WHERE auth_token = %s", (token,))
	rows = cur.fetchall()

	user_id = rows[0][0]

	if len(rows) < 1:
		conn.close()
		return jsonify({"error": "invalid auth_token"})

	statement = ("""UPDATE auction_user
					SET auth_token = %s
					WHERE user_id = %s""")
	
	values = (None, user_id)

	try:
		cur.execute(statement, values)
		cur.execute("commit")
		result = {"User logged out": user_id }
	
	except (Exception, psycopg2.DatabaseError) as error:
		logger.error(error)
		result = {'error': 'database error'}
	
	finally:
		if conn is not None:
			conn.close()

	return jsonify(result)


##########################################################
## 					DATABASE ACCESS
##########################################################


def db_connection():
	db = psycopg2.connect(user = os.getenv('db_username'),
							password = os.getenv('db_password'),
							host = "db",
							port = "5432",
							database = "dbfichas")
	return db


##########################################################
## 						MAIN
##########################################################


if __name__ == "__main__":
	# Set up the logging
	logging.basicConfig(filename="logs/log_file.log")
	logger = logging.getLogger('logger')
	logger.setLevel(logging.DEBUG)
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)

	# create formatter
	formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s',
							  '%H:%M:%S')
							  # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
	ch.setFormatter(formatter)
	logger.addHandler(ch)


	time.sleep(1) # just to let the DB start before this print :-)


	logger.info("\n---------------------------------------------------------------\n" + 
				  "API v1.0 online: http://localhost:8080/departments/\n\n")


	

	app.run(host="0.0.0.0", debug=True, threaded=True)