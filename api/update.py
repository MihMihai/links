#!/usr/bin/python3

from flask import Response,request,Blueprint
import jwt
import json
import MySQLdb

appUpdate = Blueprint("api_update",__name__)

@appUpdate.route("/api/update")
def update():
	response = {}
	
	userToken = request.headers.get("Authorization")
	
	if userToken == None:
		response["error"] = "Request does not contain an acces token"
		response["description"] = "Authorization required"
		response["status_code"] = 401
		return Response(json.dumps(response,sort_keys=True),mimetype="application/json"),401
		
	f = open('server.conf','r')
	key = f.readline()
	
	try:
		userAcc = jwt.decode(userToken,key)
	except jwt.ExpiredSignatureError:
		response["error"] = "Invalid token"
		response["description"] = "Token has expired"
		response["status_code"] = 401
		return Response(json.dumps(response,sort_keys=True),mimetype="application/json"),401
	except jwt.InvalidTokenError:
		response["error"] = "Invalid token"
		response["description"] = "Invalid token"
		response["status_code"] = 401
		return Response(json.dumps(response,sort_keys=True),mimetype="application/json"),401

	
	name = request.form.get("name")
	birthDay = request.form.get("birth_day")
	birthMonth = request.form.get("birth_month")
	birthYear = request.form.get("birth_year")
	
	if birthDay != None and birthMonth != None and birthYear != None:
		birthday = birthDay + "-" + birthMonth + "-" + birthYear
		try:
			birthdayDate = date.strptime(birthday,'%d-%B-%Y')
		except:
			response["error"] = "Invalid date"
			response["description"] = "Bad format for date. It should be %d for Day, %B for Month, %Y for Year"
			response["status_code"] = 400
			return Response(json.dumps(response,sort_keys=True),mimetype="application/json"),400 
		birthday_date = birth_date.strftime('%Y-%m-%d')
		cursor = db.cursor()
		
		query = "UPDATE users SET name = '%s', birthday_date = str_to_date('%s','%%Y-%%m-%%d') WHERE access_token = '%s'" % (name,birthday_date,userToken)
		cursor.execute(query)
		db.commit()
		db.close()
	response["status"] = 'ok'
	return Response(json.dumps(response,sort_keys=True),mimetype="application/json")


