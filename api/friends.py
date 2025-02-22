#!/usr/bin/python3

from flask import Blueprint, Response, request
import json
import MySQLdb
import jwt

appFriends = Blueprint('api_friends',__name__)


@appFriends.route("/api/friends", methods = ['GET'])
def friends():

	response = {}

	db = MySQLdb.connect(host = "localhost",user ="root", passwd = "QAZxsw1234", db="linksdb")

	#get authorization token for user, used to prevent spamming or unwanted access
	user1Token = request.headers.get("Authorization")

	if user1Token == None:
		response["error"] = "Request does not contain an access token"
		response["description"] = "Authorization required"
		response["status_code"] = 401
		return Response(json.dumps(response,sort_keys=True),mimetype="application/json"),401

	#get key to code/decode the token
	f = open('server.conf','r')
	key = f.readline()

	#what is coding dictionary user1Acc
	try:
		user1Acc = jwt.decode(user1Token,key)
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

	query = "SELECT id FROM users WHERE auth_token ='%s' " % (user1Token)
	cursor = db.cursor()
	cursor.execute(query)

	#get current user from db
	user1Data = cursor.fetchone()
	#user1Data[0] -- id

	if user1Data == None :
		response["status"] = 'Invalid token'
		response["description"] = 'Token is not registered to any user'
		response["status_code"] = 401
		return Response(json.dumps(response,sort_keys=True),mimetype="application/json"),401
	user1Id = user1Data[0]

	queryFriends = "SELECT id, user_1, user_2 FROM friendships WHERE (user_1 = '%s' OR user_2 = '%s') AND status = 1 " % (user1Id,user1Id) 
	cursor.execute(queryFriends)
	friendData = cursor.fetchall()


	#check if user has friends
	if cursor.rowcount == 0:
		response["status"] = 'ok'
		response["total"] = 0
		response["friends"] = []
		return Response(json.dumps(response,sort_keys=True),mimetype="application/json")

	#store friend ids in array as we find them in db data
	#array of tuples (fid, id)
	friendsId = {}

	#need to check in friendData which of user 1 and 2 is the friend
	#row[0] -friendshipid, row[1] -u1, row[2] - u2
	for row in friendData:
		if row[1] != user1Id:
			friendsId[str(row[0])] = row[1]
		else:
			friendsId[str(row[0])] = row[2]



	#get name and email for each friend, with friendship_id and auth_token ( to check if friend is online or not)
	query = """SELECT f.id, u.name, u.email, u.auth_token
		 FROM  users u JOIN friendships f
		 ON ( (u.id = f.user_1 AND f.user_2 = '%s') OR (u.id = f.user_2 AND f.user_1 = '%s') AND status = 1)
 	WHERE """ % (user1Id,user1Id)
	i = 1
	for fid in friendsId:
		if i == 1:
			i = 0
			query += "u.id = '%s' " % (friendsId[fid])
		else:
			query += "or u.id = '%s' " % (friendsId[fid])


	cursor.execute(query)
	friendsDb = cursor.fetchall()

	#debugging purposes
	#return Response(json.dumps(friendsDb,sort_keys=True),mimetype="application/json")

	friends = []
	#get friends using friend ids

	#data[0] - fid, data[1] - name, data[2] - email
	for data in friendsDb:
		friend = {}
		friend["friendship_id"] = str(data[0])
		friend["name"] = data[1]
		friend["email"] = data[2]
		if data[3] != None:
			friend["online"] = 1
		else:
			friend["online"] = 0
		friends.append(friend)

	response["status"] = 'ok'
	response["friends"] = friends
	response["total"] = len(friends)

	return Response(json.dumps(response,sort_keys=True),mimetype="application/json")

