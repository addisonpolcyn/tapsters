#Echo server program
import socket
import os
import psycopg2

HOST = '127.0.0.1'        # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port

####################### FUNCTIONS #####################################

def parseRequestMethod(data):
	dataLines = data.split("\r")
	requestMethod = dataLines[0].split(" ")
	return requestMethod

def loadFile(fileName):
	file = open(fileName, "r")
		
	str = file.read(100000)
	file.close()
	return str

########################	MAIN	###################################

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a socket
s.bind((HOST, PORT)) #binds the server to a static host and port name of which the server socket will open

#this is for the login package we will not use this for now
def getLoginPackage():
	loginPackage = open("login.html", "r")
	string = loginPackage.read(100000)
	loginPackage.close()
	newstr=""
	gate=0
	door=False
	for i in range(0,len(string)):
		if(gate==1 and string[i]=='<'):
			door=True
		elif(gate==2 and string[i]=='>'):
			newstr+='>'
			door=False
			break

		if(string[i] == '~'):
			if(gate):
				gate=2
			else:	
				gate=1
		elif(door):
			newstr+=string[i]
			
	return newstr


while 1:
	#socket.accept(): accept accepts a connection; socket must be bound to an address and listening for a connection for this to be taking place.function returns conn and addr, where conn is a new socket object which can send and recieve data, address is the address bound to the socket on the client side
	s.listen(1) #socket listens for a connection
	conn, addr = s.accept()

	print 'Connected by', addr

	data = conn.recv(1024)

	if not data: break

	#parse connection
	requestMethod = parseRequestMethod(data)
	method = requestMethod[0]
	query = requestMethod[1]


	#Handle Request Method
	if method == "GET":
		if '?' in query:
   	   	   	print "query is an action"
			#split the query
			query = query.split('?')
			action=query[1]
			query=query[0]

			print "action: " + action
			print "query: " + query

			if query == "/login":
				#Send Header
				conn.send('HTTP/1.0 200 OK\n')
				print "somebody wants to login bruh\n"

				action = action.split('&')
				print action[0]
				print action[1]
				print action[2]

				uname = action[0].split('=')
				uname = uname[1]
				
				uname = "'" + uname  +"'"
				print "uname: " + uname
				

				#make a sql query send to database to check if account is there if is then allow auth
				hostname = 'localhost'
				username = 'postgres'
				password = 'P15mac^new'
				database = 'localTaps'

				# Simple routine to run a query on a database and print the results:
				def doQuery( conn ) :
					cur = conn.cursor()
					sqlQuery = "SELECT username FROM users WHERE username=" + uname 
					cur.execute( sqlQuery )

				# 	for name, country, province, population, latitude, longitude, elevation in cur.fetchall() :
				#		print name, country, province, population, latitude, longitude, elevation 
					stringstr = cur.fetchall() 

					print stringstr
				#	uname = uname in cur.fetchall()
					return stringstr

				print "Using psycopg2..."
				myConnection = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )
				dbResponse = len(doQuery(myConnection))
				myConnection.close()
				
				if dbResponse:
					print "Login Success!\n"
					
					#redirect to page but now with authorization

					conn.send('Content-Type: text/html\n')
					conn.send('\n')
					
					#Send File
					loginPack=getLoginPackage()
					
					str = loadFile("home.html")
					str=str.split('<head>')
					packedFile=str[0] + "\n<head>\n" + "<script> console.log('username: kook'); </script>" + loginPack + str[1]

					conn.send(packedFile)
	
					#Log Request
					print data

				else:
					print "Login Failure!\n"

					conn.send('Content-Type: text/html\n')
					conn.send('\n')
					
					#Send File
					loginPack=getLoginPackage()
					
					str = loadFile("home.html")
					str=str.split('<head>')
					packedFile=str[0] + "\n<head>\n" + "<script> window.onload = function(){console.log('error version pinged');modal.style.display = 'block';document.getElementById('uname').style.background = 'lightyellow';document.getElementById('loginError').innerHTML = 'username or password is incorrect';document.getElementById('pass').style.background = 'lightyellow';} </script>" + loginPack + str[1]

					conn.send(packedFile)
	
					#Log Request
					print data

			elif query == "/signup":
				#Send Header
				conn.send('HTTP/1.0 200 OK\n')
				print "someone wants to make an account\n"
				#sql query to check if account remains, if it does not, insert account into db 

			else:	
				#SEND 400 Bad Request
				conn.send('HTTP/1.0 400\n')
				print "QUERY NOT RECOGNIZED\n"
				print "query: " + query
				print "SEND BAD REQUEST --->>> Printing invalid request:\n" + data

		else:
			print "query is not an action"
			if query == "/favicon.ico":
				#Allow Icon
				conn.send('HTTP/1.0 200 OK\n')
				print "/favicon.ico handled\n"

			elif query == "/home":
				#Send Header
				conn.send('HTTP/1.0 200 OK\n')
				conn.send('Content-Type: text/html\n')
				conn.send('\n')
					
				#Send File
			#	loginPack=getLoginPackage()
					
				'''str = loadFile("home.html")
				str=str.split('<head>')
				packedFile=str[0] + "\n<head>\n" + loginPack + str[1]

				conn.send(packedFile)'''
				str = loadFile("index.html")
				conn.send(str)

				#Log Request
				print data

			elif query == "/body.html":
				#Send Header
				conn.send('HTTP/1.0 200 OK\n')
				conn.send('Content-Type: text/html\n')
				conn.send('\n')
					
				#Send File
				loginPack=getLoginPackage()
					
				'''str = loadFile("home.html")
				str=str.split('<head>')
				packedFile=str[0] + "\n<head>\n" + loginPack + str[1]

				conn.send(packedFile)'''
				str = loadFile("body.html")
				conn.send(str)

				#Log Request
				print data

			elif query == "/css/index.css":
				#Send Header
				conn.send('HTTP/1.0 200 OK\n')
				conn.send('Content-Type: text/css\n')
				conn.send('\n')
					
				#Send File
				#loginPack=getLoginPackage()
					
				'''str = loadFile("home.html")
				str=str.split('<head>')
				packedFile=str[0] + "\n<head>\n" + loginPack + str[1]

				conn.send(packedFile)'''
				str = loadFile("css/index.css")
				conn.send(str)

				#Log Request
				print data

			elif query == "/controls.html":
				#Send Header
				conn.send('HTTP/1.0 200 OK\n')
				conn.send('Content-Type: text/html\n')
				conn.send('\n')
					
				#Send File
				loginPack=getLoginPackage()
					
				'''str = loadFile("home.html")
				str=str.split('<head>')
				packedFile=str[0] + "\n<head>\n" + loginPack + str[1]

				conn.send(packedFile)'''
				str = loadFile("controls.html")
				conn.send(str)

				#Log Request
				print data

			elif query == "/home/taps":
				#Send Header
				conn.send('HTTP/1.0 200 OK\n')
				conn.send('Content-Type: text/html\n')
				conn.send('\n')
					
				#Send File
				str = loadFile("taps.html");
				loginPack=getLoginPackage()
							
				str=str.split('<head>')
				packedFile=str[0] + "\n<head>\n" + loginPack + str[1]

				conn.send(packedFile)
					
				#Log Request
				print data

			elif query == "/home/brewers":
				#Send Header
				conn.send('HTTP/1.0 200 OK\n')
				conn.send('Content-Type: text/html\n')
				conn.send('\n')
					
				#Send File
				str = loadFile("brewers.html");
				loginPack=getLoginPackage()
					
				str=str.split('<head>')
				packedFile=str[0] + "\n<head>\n" + loginPack + str[1]

				conn.send(packedFile)
					
				#Log Request
				print data

			else:	
				#SEND 404 Page Not Found
				conn.send('HTTP/1.0 404\n')
				print "QUERY NOT RECOGNIZED\n"
				print "query: " + query
				print "Printing invalid request:\n" + data
	
	else: 
		print "METHOD NOT RECOGNIZED\n"
		print "Printing invalid request:\n" + data
	
	conn.close()

s.close()

############# END OF MAIN #################################################


