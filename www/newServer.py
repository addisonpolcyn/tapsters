#Echo server program
import socket
import os

# opens connection postgreSQL Database
import psycopg2

# import thread module
from thread import *
import threading

HOST = '127.0.0.1'        # LocalHost IP address
PORT = 50007              # Arbitrary non-privileged port

thread_lock = threading.Lock()

####################### HELPER FUNCTIONS #####################################

def parseRequestMethod(data):
	dataLines = data.split("\r")
	requestMethod = dataLines[0].split(" ")
	return requestMethod

def loadFile(fileName):
	try: 
		file = open(fileName, "r")
		str = file.read(100000)
		file.close()
		return str
	except:
		print "BAD REQUEST: " + fileName + " failed to be found on our server side"
		return ""

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

#################################################   THREAD FUNCTION #########################################################
#This function is the main function which handles all the client requests
def threaded(conn):
		#while True:
	 
	        # data received from client
			data = conn.recv(1024)

			if not data: 
				print('Bye')

				# lock released on exit
				##########################################################################################
				thread_lock.release()
				#break

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
						password = 'XXXXXXXX'
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
					query = query.lstrip('/')

					if ".css" in query:
						query = query.lstrip('templates/')
						conn.send('HTTP/1.0 200 OK\n')
						conn.send('Content-Type: text/css\n')
						file = loadFile(query)
						conn.send(file)
						print "serving: " + query + " to client: ", addr

					elif ".js" in query:
						conn.send('HTTP/1.0 200 OK\n')
						conn.send('Content-Type: application/javascript\n')
						file = loadFile(query)
						conn.send(file)
						print "serving: " + query + " to client: ", addr 

					elif ".ico" in query:
						conn.send('HTTP/1.0 200 OK\n')
						print "favicon.ico handled for now..."
						# favicon.ico is the small icon in the left side of the url; currently we are sending nothing

					elif ".html" in query:
						conn.send('HTTP/1.0 200 OK\n')
						conn.send('Content-Type: text/html\n')
						conn.send('\n')
						str = loadFile(query)
						conn.send(str)
						print "serving: " + query + " to client: ", addr 

					else:	
						#SEND 404 Page Not Found
						conn.send('HTTP/1.0 404\n')
						print "QUERY NOT RECOGNIZED\n"
						print "query: " + query
						print "Printing invalid request:\n" + data

					print('\n')
			
			else: 
				print "METHOD NOT RECOGNIZED\n"
				print "Printing invalid request:\n" + data

			#client has been served, unlock thread for next clients and close connection
			thread_lock.release()
			conn.close() 
			
			
########################	MAIN	###################################

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a socket
s.bind((HOST, PORT)) #binds the server to a static host and port name of which the server socket will open

while 1:
	#socket.accept(): accept accepts a connection; socket must be bound to an address and listening for a connection for this to be taking place.function returns conn and addr, where conn is a new socket object which can send and recieve data, address is the address bound to the socket on the client side
	s.listen(5) #socket listens for a connection: 5 denotes that it will queue up to 5 connections
	conn, addr = s.accept()

	# lock acquired by client
	thread_lock.acquire()#####################################################################
	print 'Connected by', addr

	start_new_thread(threaded, (conn,))
	#threaded(conn)

s.close()

############# END OF MAIN #################################################

