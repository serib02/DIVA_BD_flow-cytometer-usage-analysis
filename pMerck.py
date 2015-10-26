from xml.etree.ElementTree import*
import os, codecs, csv, time, datetime
from datetime import datetime, date,timedelta

def readExcelCsv(path):	
	data_initial = open(path, "rU")
	csvFile = csv.reader((line.replace('\0','') for line in data_initial), delimiter=",")
	
	#priming some names
	summed = None
	added = None
	row = None
	neverLoggedOut = 0
	
	rowPos = 0
	for row in csvFile:
		line1 = ';'.join(row)
		line = line1.split(';')
		if rowPos == 0:
			rowPos = rowPos+1
			pass
		elif rowPos == 1:
			updatedSum, added, rowPos, neverLoggedOut = initiateTime(line,rowPos,neverLoggedOut)
		else:
			print 'moving to row',rowPos, ';already added',added, '; didnt log out:',neverLoggedOut, ';total so far',round(abs(updatedSum).total_seconds()/3600.0,2)#updatedSum
			updatedSum, neverLoggedOut, added = sumTime(line, updatedSum, neverLoggedOut,added)
			rowPos = rowPos +1
	
	#expressing time in hour format and then rounding it off
	timeInHours = abs(updatedSum).total_seconds()/3600.0
	timeInHoursRounded = str(round(timeInHours,2))
		
	if neverLoggedOut == 0:
		#Usage time in (y,m,w,d, h:m:s): "+str(updatedSum)+"\n
		return "Time used in hours: "+timeInHoursRounded+" hours" \
			   "\n...... ......"

	elif neverLoggedOut > 0:
		#Usage time in (y,m,w,d, h:m:s): "+str(updatedSum)+"\n
		return "Time used in hours: "+timeInHoursRounded+" hours" \
		   "\nSession(s) when user did not log out: "+str(neverLoggedOut)+"\n...... ......"
	
def initiateTime(values,rowPos,neverLoggedOut):	
	a = values[6]
	aLen = len(values[6])
	b = values[7]
	bLen = len(values[7])
	c = values[8]
	cLen = len(values[8])
	d = values[9]
	dLen = len(values[9])
		
	#file may have a bunch of commas in a row but no entry
	if aLen==0 and bLen==0 and cLen==0: 
		#neverLoggedOut = 0
		rowPos = 1
		return (firstSession, added, rowPos, neverLoggedOut)
		
	#no log out time entry -- user never logged out, skip but keep count 
	if dLen < 5 or cLen < 5:
		neverLoggedOut = neverLoggedOut+1
		firstSession = None
		added = 0
		rowPos = 1
	else:	
		#extracting starting time and date
		startTime = str(a)
		startDate = str(b)
		#extracting ending time and date
		endTime = str(c)
		endDate = str(d)
		#change time to 24hr fmt and concatenate date 
		startDateTime = converTo24hrAndAppendDate(startTime,startDate)
		endDateTime = converTo24hrAndAppendDate(endTime,endDate)
		#time used in a session
		firstSession = (endDateTime-startDateTime)
		#keep track of sessions counted
		added = 1
		rowPos = rowPos+1
		#neverLoggedOut = 0
	
	return (firstSession, added, rowPos, neverLoggedOut)

#finds the name of the machine; checks the 11th column of the first row
def findMachineName(path):

	data_initial = open(path, "rU")
	csvFile = csv.reader((line.replace('\0','') for line in data_initial), delimiter=",")
	
	rowPos = 0
	for row in csvFile:
		line1 = ';'.join(row)
		line = line1.split(';')
		if rowPos == 0:
			rowPos = rowPos + 1
			pass
		else:
			machineName = line[11]
			break
	if len(machineName) == 0:
		return "No machine name"
	else:
		return ""+machineName+""

def sumTime(values, summed, neverLoggedOut, added):
					
	a = values[6]
	aLen = len(values[6])
	b = values[7]
	bLen = len(values[7])
	c = values[8]
	cLen = len(values[8])
	d = values[9]
	dLen = len(values[9])
				
	#file may have a bunch of commas in a row but no entry
	if aLen==0 and bLen==0 and cLen==0: 
		return summed, neverLoggedOut, added
			
	#no log out time entry -- user never logged out, skip but keep count 
	if dLen < 5 or cLen < 5: #5 is arbitrary, picked based the other lengths
		updatedSum = summed
		return updatedSum, neverLoggedOut+1, added
		
	else:
		#extracting starting time and date
		startTime = str(a)
		startDate = str(b)
		#extracting ending time and date
		endTime = str(c)
		endDate = str(d)
		#change time to 24hr fmt and concatenate date 
		startDateTime = converTo24hrAndAppendDate(startTime,startDate)
		endDateTime = converTo24hrAndAppendDate(endTime,endDate)
		#time used in a session
		sessionDuration = (endDateTime-startDateTime)
		#updating the time
		updatedSum = summed + sessionDuration
		#keep track of sessions counted
		added = added+1
	
	return (updatedSum, neverLoggedOut, added)

def combine_t_d_24hr(time1,date1):
	if len(time1) <= 5 or len(date1) <= 5:
		return False
	else:
		timeCheck = time1.split(' ')
		time1 = timeCheck[0]
		
		#add a zero to single hour digits
		hourDigit = time1.split(':')
		if len(hourDigit[0]) == 1:
			pad = '0'
			time1 = pad+hourDigit[0]+':'+hourDigit[1]+':'+hourDigit[2]
		
		FMT = '%B %d %Y %H:%M:%S' #this is the time format used
		
		#convert to 24hr format any time that is PM, ignore 12PM
		if timeCheck[1] =='PM' and hourDigit[0] != '12':
			time1 = date1+' '+time1
			time1 = datetime.strptime(time1, FMT) + timedelta(hours=12) 
			return time1
		else:
			time1 = date1+' '+time1
			time1 = datetime.strptime(time1, FMT) + timedelta(hours=00) 
			return time1


#creates (and returns) and empty db root
def createTimeLogDb():
    root = Element("logtime_database")
    logtime_database = ElementTree(root)
    return logtime_database 

#reads a .csv and transfers lines to xml database
def updateFromCSV(path,databaseFile):
    database1 = parse(databaseFile)
    database = database1.getroot()
    
    data_initial = open(path, "rU")
    csvFile = csv.reader((line.replace('\0','') for line in data_initial), delimiter=",")
    
    rowPos = 0
    for row in csvFile:
        lineInCsv = ';'.join(row)
        line = lineInCsv.split(';')
		        
        if rowPos == 0:
			if len(line) < 14:
				return False
			else:
				#getting column indices
				proper_column, colList = determineCols(line)
				print colList
				if proper_column == False:
					return False
				else:
					cL = colList 
					uName=cL[0]; name=cL[1]; role=cL[3]; dept=cL[5]; logInT=cL[6]; logInD=cL[7]
					logOutT=cL[8]; logOutD=cL[9]; cytometerCol=cL[11]; serialNoCol=cL[12]; custom=cL[13]
            
        elif line[uName]=="Administrator" or line[uName]=="BDService":
            pass
        else:
            #department element under root element, database
            department = line[dept]
            
            #user element under department element
            both_names = getName(line[name])
            userName = line[uName]
            
            #session element under user element
            s_t = startTime = line[logInT]
            s_d = startDate = line[logInD]
            e_t = line[logOutT]
            e_d = line[logOutD]
            cyt = cytometer = line[cytometerCol]
            s_n = serialNo = line[serialNoCol]
            #combining log in and out time and dates
            std,etd = timeAndDate(s_t,s_d,e_t,e_d)

            checkAndAdd(database,department, both_names,userName,std,etd,cyt,s_n)
        rowPos = rowPos+1
    # return database1.write("flow_database.xml")
	database1.write(databaseFile)
    return True

#adds line info to db, avoiding duplicates
def checkAndAdd(database,dept,both_names,userName,std,etd,cyt,ser):
    if len(database.findall("Department")) == 0: #empty db -> add right away
        addElement(database,dept,both_names,userName,std,etd,cyt,ser)
        return
    else:
        sp_dept,dp_c,sp_user,usr_c,session = findElement(database,dept,userName,both_names,std,etd,cyt,ser)
        if session==True:
            return
        elif not sp_dept:
            addElement(database,dept,both_names,userName,std,etd,cyt,ser)
            return
        elif sp_dept and sp_user: #and (session is None):
            addSession(database,sp_dept,sp_user,std,etd,cyt,ser)
            return
        elif sp_dept and (not sp_user):
            addUserAndSession(database,sp_dept,userName,both_names,std,etd,cyt,ser)
            return

#department and user found, add a session
def addSession(database,sp_dept,sp_user,std,etd,cyt,s_n):
    for department in list(database.iter('Department')):
        if department.get("name")== sp_dept:
            for users in list(department.iter("User")):
                bothNs = users.get("name")
                userName = users.get("user_name")
                if bothNs == sp_user[0] and userName == sp_user[1]:
                    attributes = {"logIn":std,"logOut":etd,"cytometer":cyt,"serial_no":s_n}
                    sessionElement = SubElement(users,"session", attrib=attributes)
                    #print "added a session"
                    
#department found, add user and session
def addUserAndSession(database,sp_dept,u_n,b_n,std,etd,cyt,s_n):
    for departments in list(database.iter('Department')):
        if departments.get("name") == sp_dept:
            userElement = SubElement(departments,"User",attrib={"user_name":u_n,"name":b_n})
            attributes = {"logIn":std,"logOut":etd,"cytometer":cyt,"serial_no":s_n}
            sessionElement = SubElement(userElement,"session", attrib=attributes)
            #print "added user and session"
            
#finds any element(department, user, or session)
#returns False if the element isn't there
def findElement(database,department,user_name,name,std,etd,cyt,ser):
    sp_dp = False; dp_count=0 
    user = False; user_count=0 
    sp_session = False

    for departments in list(database.iter('Department')):
        if departments.get("name") == department:
            sp_dp=departments.get("name")
            #print "found a matching department", sp_dp
            for users in list(departments.iter("User")):
                bothNs = users.get("name")
                userName = users.get("user_name")
                if bothNs == name and userName == user_name:
                    user = [bothNs,userName]
                    print "found a matching user", user
                    for session in list(users.iter("session")):
                        w=session.get("logIn"); x=session.get("logOut")
                        y=session.get("cytometer"); z=session.get("serial_no")
                        if w==std and x==etd and y==cyt and z==ser:
                            #print "found a matching session"
                            sp_session = True
                            return (sp_dp,dp_count,user,user_count,sp_session)
                #found a matching user? loop no more
                if user != False:
                    break
                user_count = user_count+1
        #found a matching department name? loop no more
        if sp_dp != False:
            break
        dp_count = dp_count+1
    return (sp_dp,dp_count,user,user_count,sp_session)

#when database is empty, adds the entire tree
def addElement(database,dept, b_n,u_n,std,etd,cyt,s_n):
    deptElement = SubElement(database,"Department", attrib={"name":dept})
    userElement = SubElement(deptElement,"User",attrib={"user_name":u_n,"name":b_n})
    attributes = {"logIn":std,"logOut":etd,"cytometer":cyt,"serial_no":s_n} 
    sessionElement = SubElement(userElement,"session", attrib=attributes)
    #print "element added"
    
#combines log in and out info into a string
#returns a string of login info and a string of logout info.
def timeAndDate(startTime,startDate,endTime,endDate):
    startDateTime = combine_t_d_24hr(startTime,startDate)
    endDateTime = combine_t_d_24hr(endTime,endDate)
    
    #sometime users don't log out and there's no end date or time
    if endDateTime==False: #(startDateTime==False) or (
        endDateTime = "####-##-## ##:##:##"
        return (str(startDateTime),endDateTime)
    
    return (str(startDateTime),str(endDateTime))

#converts time to 24hr format; combines time and date   
def combine_t_d_24hr(time1,date1):
    if len(time1) <= 5 or len(date1) <= 5:
        return False
    else:
        timeCheck = time1.split(' ')
        time1 = timeCheck[0]
        
        #add a zero to single hour digits
        hourDigit = time1.split(':')
        if len(hourDigit[0]) == 1:
            pad = '0'
            time1 = pad+hourDigit[0]+':'+hourDigit[1]+':'+hourDigit[2]
        
        FMT = '%B %d %Y %H:%M:%S' #this is the time format used
        
        #convert to 24hr format any time that is PM, ignore 12PM
        if timeCheck[1] =='PM' and hourDigit[0] != '12':
            time1 = date1+' '+time1
            time1 = datetime.strptime(time1, FMT) + timedelta(hours=12) 
            return time1
        else:
            time1 = date1+' '+time1
            time1 = datetime.strptime(time1, FMT) + timedelta(hours=00) 
            return time1

#resolves entered names to 'firstname lastname' format
def getName(name):
    all_spaces = countNameSpaces(name)
    if all_spaces == True:
        return "N/A"
    else:
        return name

# #resolves comma-separated first and last names to "first last" format
def normalize(name):
    #assumes name is pre-checked and commas have been found
	splitName = name.split(",")
	name_length = len(splitName)
	firstName = (splitName[name_length-1]).strip()
	print "splitName, firstName", splitName, firstName
	lastName = splitName[0]
	# print "Normalizing name"+firstName+" "+lastName+""
	hold = raw_input(".... to continue")

	return firstName+" "+lastName   
    
#counts the number of spaces in a name, returns False
#if the entire name is made of spaces 
def countNameSpaces(name):
    char_count = 1
    for char in name:
        if char == " ":
            char_count =+ 1
    
    if char_count > 1:  
        total_spaces = char_count-1
    else:
        total_spaces = char_count-1 
    
    name_length = len(name)
    if total_spaces == name_length:
        return True
    else:
        return False

#looks at the header, returns the index of each column 
def determineCols(line):
	a=b=c=d=e=f=g=h=i=j=k=l=m=n = None
	column = 0
	for element in line:
		if element == 'User Name':
			a = UserNameCol = column
		if element == 'Full Name':
			b = fullNameCol = column
		if element == 'Application':
			c = applicationCol = column
		if element == 'Role':
			d = roleCol = column
		if element == 'Department':
			e = departmentCol = column
		if element == 'Institution':
			f = InstitutionCol = column
		if element == 'LogIn Time':
			g = logInTimeCol= column
		if element == 'LogIn Date':
			h = logInDateCol= column
		if element == 'LogOut Time':
			i = logOutTimeCol = column
		if element == 'LogOut Date':
			j = logOutDateCol = column
		if element == 'Build Version':
			k = buildVersionCol = column
		if element == 'Cytometer':
			l = cytometerCol= column
		if element == 'Serial No':
			m = serialNoCol= column
		if element == 'Custom':
			n = customCol = column
		column = column+1
	if (a)and(b)and(c)and(d)and(e)and(f)and(g)and(h)and(i)and(j)and(k)and(l)and(m)and(n) is not None:
		return (False, (a,b,c,d,e,f,g,h,i,j,k,l,m,n))
	else:
		return (True, (a,b,c,d,e,f,g,h,i,j,k,l,m,n))


# called when one wants to upload just one .csv to a database		
def upload():
	filePath = raw_input("\nWhat the file path to the '.csv' excel file? Please include extension: \n")
	#filePath = "C:\Users\sebuufu\Desktop\flowCytoProj\2014 January.csv"

	if os.path.exists(filePath):
		while(True):
			os.system("clear")
			print "Would you like to...?"
			print
			print "A. add it to an existing 'xml'"
			print "B. create a new one"
			print "X. Nah.. Exit"
			print
			
			choice = raw_input("Select from menu: ").upper()
			if choice == 'A':
				currentDB = raw_input("\nWhat is the filepath (or name) of the 'xml' you want to add the file to? Please include the extension, '.xml':\n")
				if os.path.exists(currentDB):
					updateFromCSV(filePath,currentDB)
					hold = raw_input("\n Database updated! Press RETURN to continue ")
				else:
					hold = raw_input("The file does not exist. Did you mistype? Press Return to continue ")	
				
			elif choice == 'B':
				currentDB = createTimeLogDb()
				fileName = raw_input("\nWhat would you like to call (save as) this new database? Please add '.xml' extension to filename: \n")
				if fileName.endswith('.xml'):
					currentDB.write(fileName,xml_declaration=True,encoding="utf-8",method="xml")
					updateFromCSV(filePath,fileName)
					hold = raw_input("\n Database created! Press RETURN to continue ")
				else:
					print "The filename, "+fileName+" does not end with an '.xml' extension. Please add extension and try again"
					hold = raw_input("\nPress RETURN to continue ")
				
			elif choice == 'X':
				hold = raw_input("\nYou have chosen to exit! Press RETURN to return to main menu ")
				return False
			else:
				print "\nPlease enter a valid selection"
				hold = raw_input("\nPress RETURN to continue")
	else:
		hold = raw_input("The file does not exist. Did you mistype? Press Return to continue ")

# called when one wants to upload multiple .csv's to a database		
def uploadSeveral():
	fileLoc = raw_input("\nWhat is the folder path? ")
	if os.path.exists(fileLoc):
		if atLeastOne(fileLoc) == False:
			hold = raw_input("No .csv files found. Please ensure that desired files end with a '.csv' extension, as in 'example.csv' ")
		
		else:
			while(True):
				os.system("clear")
				print "Would you like to...?"
				print
				print "A. add files to an existing 'xml' "
				print "B. create a new '.xml' database"
				print "X. Ummm, Nah .. Exit"
				print
				
				choice = raw_input("Select from menu: ").upper()
				
				if choice == 'A':
					currentDB = raw_input("\nWhat is the filepath (or name) of the 'xml' you want to add the file to? Please include the extension, '.xml':\n")
					#currentDB = "tryAgain.xml"
					if os.path.exists(currentDB):
						total_added,not_addedList = addToXml(fileLoc,currentDB)
						not_addedString = ', '.join(not_addedList)
						if len(not_addedList) > 0:
							hold = raw_input("\n\nDatabase updated! "+str(total_added)+""" .csv files were added.
							\n"""+not_addedString+" were not added. Please check their format. \n\nPress RETURN to continue")
						else:
							hold = raw_input("\n\nDatabase updated! "+str(total_added)+""" .csv files were added.\n\nPress RETURN to continue""")
					else:
						hold = raw_input("The file does not exist. Did you mistype? \n\nPress Return to continue")	
					
				elif choice == 'B':
					currentDB = createTimeLogDb()
					fileName = raw_input("\nWhat would you like to call (save as) this new database? Please add '.xml' extension to filename: \n")
					if fileName.endswith('.xml'):
						currentDB.write(fileName)
						total_added,not_addedList = addToXml(fileLoc,fileName)
						not_addedString = ', '.join(not_addedList)
						if len(not_addedList) > 0:
							hold = raw_input("\n\nDatabase updated! "+str(total_added)+""" .csv files were added.
							\n"""+not_addedString+" were not added. Please check their format. \n\nPress RETURN to continue")
						else:
							hold = raw_input("\n\nDatabase updated! "+str(total_added)+""" .csv files were added.\n\nPress RETURN to continue""")
					else:
						print "The filename, "+fileName+" doesn't end with an '.xml' extension. Please add extension and try again"
						hold = raw_input("\nPress RETURN to continue ")
						
				elif choice == 'X':
					hold = raw_input("\nYou have chosen to exit!\n\nPress RETURN to continue to main menu")
					return False
					
				else:
					print "\n Please enter a valid selection"
					hold = raw_input("\nPress RETURN to continue ")
				
	else:
		hold = raw_input("\nNo folder with this name exists. Did you mistype? \n\nPress Return to continue")

#checks if atleast one file in a folder ends with .csv
def atLeastOne(directory):
	for fileName in os.listdir(directory):
		filePath = directory+"/"+fileName
		if filePath.endswith('.csv'):
			return True
	return False
	
#calls updateFromCSV() for all .csv's in a folder; 
def addToXml(directory,database):
	total_added = 0
	print
	not_added = []
	for fileName in os.listdir(directory):
		filePath = directory+"/"+fileName
		if filePath.endswith(".csv"):
			print fileName
			done = updateFromCSV(filePath,database)
			if done == True:
				#print "Total is", done, total_added
				total_added = total_added + 1
			else:
				not_added.append(fileName)
	return (total_added,not_added)

#checks that the root has department elements
def deptNotEmpty(existingDb,dbRoot):
	if existingDb == False or dbRoot is None:
		return "No"
	else:
		if dbEmpty(dbRoot) == True:
			hold = raw_input("This database is empty and has no departments. There are no users. \nDid you mistype? \nPress RETURN to continue")
			return "No"
		else:
			return "Yes"

#prints information about a user	
def printAUser():
	#name of db to check
	dBExists,dbRoot = checkDbFinder()
	forward = deptNotEmpty(dBExists,dbRoot)
			
	if forward != "No":
		#ask for the name of the user and find out if they exist at least once
		userIsThere = checkUserExists(dbRoot)
		if userIsThere == False:
			hold = raw_input("This user is not in the database. Press RETURN to continue")
			return
		else:
			#range of dates to check or just everything
			msgToDisplay = "Would you like to print "+userIsThere+"'s sessions"
			quit,range = datemenu(msgToDisplay)
			
			if range == False:
				return
			elif range is None:
				#-print user with no date
				csvAUser(dbRoot,userIsThere,range)
			elif range is not None and range != False:
				#-print user with date
				csvAUser(dbRoot,userIsThere,range)

#prints information about a group
def printAGroup():
	#name of db to check
	dbExists,dbRoot = checkDbFinder()
	forward = deptNotEmpty(dbExists,dbRoot)
			
	if forward == "Yes":
		groupIsThere = checkGroupExists(dbRoot)
		if groupIsThere == False:
			return
		else:
			#range of dates to check or just everything
			msgToDisplay = "Would you like to print "+groupIsThere+"'s sessions"
			quit,range = datemenu(msgToDisplay)
			
			if range == False:
				return
			elif range is None:
				#-print user with no date
				csvAGroup(dbRoot,groupIsThere,range)
			elif range is not None and range != False:
				#-print user with date
				csvAGroup(dbRoot,groupIsThere,range)
	else:
		return

#prints everything by group and then by last name
def printAll():
	#-name of db to check
	dbExists,dbRoot = checkDbFinder()
	forward = deptNotEmpty(dbExists,dbRoot)
			
	if forward == "Yes":
		fileName = raw_input("\nWhat would you like to call (save as) this new excel .csv file? \nPlease add '.csv' extension to filename, such as 'example.csv'\n")
		if fileName.endswith(".csv"):
			period = None ; sp_dept = False
			doc = open(fileName, "wt")
			doc.write("""Name,User name,Log in,Log out,Cytometer,Duration\n""")
			total_sum = []
			for departments in list(dbRoot.iter("Department")):
				for user in list(departments.iter("User")):
					user_name = user.get("user_name")
					name = user.get("name")
					if (name!="N/A") and (user_name!="") and (countNameSpaces(user_name)==False):
						a,time_used = userToDoc(doc,departments,user_name,period)
						total_sum.append(time_used)
					else:
						pass
				break
			totalUsed = totalled(total_sum)
			if totalUsed > 0:
				doc.write("\n\n\n,,,,Sum of total(s),"+str(totalUsed)+"\n")
			doc.close()

		else:
			holdAndAsk = raw_input("The filename must end with '.csv'.\nPlease also ensure the folder does not contain another file with the same name\n\nPress RETURN to continue: ")
			return	
	else:
		return

#checks the database for a group and prints the group's users
def csvAGroup(dbRoot,group_name,period):
	if period == None:
		doc = open(""+group_name+"_flow sessions"+".csv","wt")
	else:
		st_date = str(period[0]).split(" ")[0] ; ed_date = str(period[1]).split(" ")[0]
		doc = open(""+group_name+"_flow sessions_"+st_date+"__"+ed_date+".csv","wt")
		
	doc.write("""Name,User name,Log in,Log out,Cytometer,Duration (in hours)\n""")
	
	total_sum = []
	for departments in list(dbRoot.iter("Department")):
		if departments.get("name") == group_name:
			for user in (departments.iter("User")):
				user_name = user.get("user_name")
				name = user.get("name")
				if (name!="N/A") and (user_name!="") and (countNameSpaces(user_name)==False):
					a,time_used = userToDoc(doc,departments,user_name,period)
					total_sum.append(time_used)
				else:
					pass
			break
	totalUsed = totalled(total_sum)
	if totalUsed > 0:
		doc.write("\n\n\n,,,,Sum of total(s),"+str(totalUsed)+"\n")
	doc.close()

#checks the database and prints a given user's session in a csv.
def csvAUser(dbRoot,user_name,period):	
	if period == None:
		doc = open(""+user_name+"_flow sessions"+".csv","wt")
	else:
		st_date = str(period[0]).split(" ")[0] ; ed_date = str(period[1]).split(" ")[0]
		doc = open(""+user_name+"_flow sessions_"+st_date+"__"+ed_date+".csv","wt")

	doc.write("""Name,User name,Log in,Log out,Cytometer,Duration (in hours)\n""")
	total_total = []
	for departments in list(dbRoot.iter("Department")):
		a, time_column_total = userToDoc(doc,departments,user_name,period)
		total_total.append(time_column_total)
	
	totalUsed = sum(total_total)
	if totalUsed > 0:
		doc.write("\n\n\n,,,,Sum of total(s),"+str(totalUsed)+"\n")
	doc.close()

#actually writes a user to a file
def userToDoc(doc,departments,user_name,period):
	foundUser = None
	total_column = 0
	for users in list(departments.iter("User")):
		userName = (users.get("user_name")).strip()
		name = users.get("name")
				
		if userName == user_name:
			#making sure the name has no commas in it
			name = name.strip()
			if findComma(name) == True:
				name = normalize(name)

			foundUser = userName
			sessionCount_P = 0
			sessionCount_noP = 0 ; check_noP = 0; check_P = 0
			row_time = []; time_column = []
			sessionCount = 0
			for session in list(users.iter("session")):
				w=session.get("logIn"); x=session.get("logOut")
				y=session.get("cytometer"); z=session.get("serial_no")
				if period is None:
					smallRound,largeRound = sessionDuration(w,x)
					doc.write(""+name+","+userName+","+w+","+x+","+y+","+str(smallRound)+"\n")		
					row_time.append(smallRound)
					time_column.append(largeRound)
					sessionCount_noP =+ 1
				else:
					check_P =+ 1
					FMT = '%Y-%m-%d %H:%M:%S'
					startTime = datetime.strptime(w,FMT)
					if period[1]>startTime>period[0]:
						smallRound,largeRound = sessionDuration(w,x)
												
						doc.write(""+name+","+userName+","+w+","+x+","+y+","+str(smallRound)+"\n")		
						row_time.append(smallRound)
						time_column.append(largeRound)
						sessionCount_P =+ 1
				sessionCount =+ 1
			
			if (sessionCount_P == 0 and check_P>0) or sessionCount==0:
				doc.write("\n\n\n,,,,"+"No session to display"+","+",")
			else:
				totalUsed = sum(row_time)
				doc.write(",,,,Total,"+str(totalUsed)+"\n\n")
			total_column = sum(time_column)
	return (foundUser, total_column)

#returns True if it finds a comma in a name, False otherwise
def findComma(name):
	for char in name:
		if char == ",":
			return True
	return False

#removes character strings (NA's) from used sessions' list and sums the list
def totalled(list):
	total_time = sum(list)
	time_in_hours = total_time 
	return round(time_in_hours,3)
		
#finds the session duration given strings of start and end time
def sessionDuration(startString,endString):
	if endString == "####-##-## ##:##:##":
		endString = startString
		return sessionDuration(startString,endString)
	else:
		FMT = '%Y-%m-%d %H:%M:%S' 
		startTime = datetime.strptime(startString,FMT)
		endTime = datetime.strptime(endString,FMT)
		sessionTime = endTime-startTime
				
		time_hrs = abs(sessionTime).total_seconds()/3600.0
		
		smallRound = round(time_hrs,4)
		largeRound = round(time_hrs,10)

		return(largeRound,smallRound)
					
#asks user to do something either whether to print everything or a given session
def datemenu(message):
	while(True):
		os.system("clear")
		print "Printing..."
		print
		print "A. "+message+" during a specific time period?"
		print "B. Look through the entire database"
		print "X. Exit"
		print
		
		selected = raw_input("Enter a menu selection: ").upper()
		
		if selected == "A":
			start, end = dateRange()
			if start==False or end==False:
				continue
				#hold = raw_input("Press RETURN to go back to date menu")
				#return (False, False)
			else:
				return (False, (start,end))
		
		elif selected == "B":
			catch = None
			return (False,catch)
		
		elif selected == "X":
			return (False,False)
		
		else:
			print "\n  Please enter a valid selection"
			hold = raw_input("\nPress RETURN to continue ")
			
#handles the range in which to do things ... lalala
def dateRange():
	timeRange = raw_input("\nEnter a start and end date in the format 'MM/DD/YYYY', separated by a comma, as in '05/05/2005,07/12/2007'. Please do not leave any spaces\n").strip()
	timeRange = timeRange.split(",")
	#process the given time and then convert it to a time string
	realStart = False
	realEnd = False
	count = 0
	while count < 2:
		date_t = timeRange[count]
		sp_time = date_t.split("/")
		sp_len = len(sp_time)
		
		if (sp_len!=3):
			tryAgain = wrongTimeFMT()
			if tryAgain == True:
				return dateRange()
			if tryAgain == False:
				return (realStart,realEnd)
		
		tP = sp_time 
		mth = tP[0]; dy = tP[1] ; yr = tP[2]
		a = len(mth) ; b = len(dy) ; c = len(yr)
				
		if (a!=2) or (b!=2) or (c!=4):
				tryAgain = wrongTimeFMT()
				if tryAgain == True:
					return dateRange()
				if tryAgain == False:
					return (realStart,realEnd)
		else:
			timeString = " 00:00:00" #in the format %H:%M:%S
			month,day = pad(mth,dy)
			if count == 0:
				realStart = month+" "+day+" "+yr+timeString
			if count == 1:
				realEnd = month+" "+day+" "+yr+timeString
		count = count+1
	
	#converting time strings to time
	FMT = '%m %d %Y %H:%M:%S'
	realTimeStart = datetime.strptime(realStart,FMT)
	realTimeEnd = datetime.strptime(realEnd,FMT)
	return (realTimeStart,realTimeEnd)
		
#adds a zero infront of single digit months/ days
def pad(month,day):
	newMonth = month ; newDay = day
	padd = '0'
	if len(month) == 1:
		newMonth = padd+month
	if len(day) == 1:
		newDay = padd+day
	return (newMonth,newDay)

#checks to see if the format of the given time is correct	
def wrongTimeFMT():
	hold = raw_input("\nYou have entered an incorrect date format. Did you mistype?\nEnter 'y' to try again, or press any key to continue ").upper()
	if hold.startswith("Y"):
		return True
	else:
		return False

#checks to see that the assigned db is not empty
def dbEmpty(dbRoot):
	if len(dbRoot.findall("Department")) == 0:
		return True
	return False

#checks outputs of userExists
def checkGroupExists(dbRoot):
	isThere = groupExists(dbRoot)
	if isThere == False:
		hold = raw_input("This group does not exist. Did you mistype? Please note that the name is not case-sensitive. \n\nEnter 'y' to try a different group name, or press RETURN to continue ").upper()
		if hold.startswith("Y"):
			return checkUserExists(dbRoot)
		else:
			return isThere
	return isThere

#finds a group element, given a group_name
def groupExists(dbRoot):
	groupName = raw_input("What is the name of the group you want to print? ").strip()
	if groupName == "":
		return False
	for departments in list(dbRoot.iter('Department')):
		deptName = departments.get("name")
		if deptName == None:
			pass
		elif deptName== "":
			pass
		elif countNameSpaces(deptName)==True:
			pass
		elif (groupName).upper() == (deptName).upper():
			return deptName
	return False
	
#asks for a user_name, and finds a user element with that attribute value
def userExists(dbRoot):
	username_to_print = raw_input("What is the user name (ISID) of the user you want to print? ").strip()
	for departments in list(dbRoot.iter('Department')):
		for users in list(departments.iter("User")):
			user_name = users.get("user_name")
			if (user_name).upper() == (username_to_print).upper():
				return user_name
	return False

#checks outputs of userExists
def checkUserExists(dbRoot):
	isThere = userExists(dbRoot)
	if isThere == False:
		hold = raw_input("This user is not in the file. Did you mistype? Note that names are not case-sensitive. Enter 'y' to try a different name, or press RETURN to continue ").upper()
		if hold.startswith("Y"):
			return checkUserExists(dbRoot)
		else:
			return isThere
	return isThere

#asks for the name of the db and checks if it exists
def findDatabase():
	database = raw_input("What is the name (or path) of the '.xml' database? Please add '.xml' extension: ")
	exists = False
	dbRoot = None
	if os.path.exists(database):
		exists = True
		db = parse(database)
		dbRoot = db.getroot()
		return (exists,dbRoot)
	return (exists,dbRoot)
	
#checks the outputs of findDatabase()	
def checkDbFinder():
	exists, dbRoot = findDatabase()
	if exists == False:
		hold = raw_input("This '.xml' file does not exist. Did you mistype? Press RETURN to continue ")
		return (exists,dbRoot)
	elif exists == True and dbRoot is None:
		hold = raw_input("Something is wrong with the format of this database. Please take a look at the database. Press RETURN to continue ")
		return (exists, dbRoot)
	return (exists, dbRoot)

#prints how long a machine has been used for
def machineUsage():
	dbExists,dbRoot = checkDbFinder()
	forward = deptNotEmpty(dbExists,dbRoot)
			
	if forward == "Yes":
		machineInfo = raw_input("Please enter the machine name and serial number separated by a comman, as in 'FACSCanto11,1'\nPlease do not leave any spaces. ").strip()
		name_and_sn = machineInfo.split(",")
		if len(name_and_sn) != 2:
			hold = raw_input("The information is not in the right format. Did you mistype? \nEnter RETURN to continue ")
		else:
			name = name_and_sn[0]
			serial = name_and_sn[1]
			machine = machineExists(dbRoot,name,serial)
		
			if machine == False:
				hold = raw_input("A machine with this serial no. (or vice versa) is not in the file. \nPress RETURN to continue ")
				return
			else:
				#range of dates to check or just everything
				msgToDisplay = "Would you like to print "+machine+"'s sessions"
				quit,period = datemenu(msgToDisplay)
			
				if period == False:
					return
				elif period == None:
					doc = open(""+machine+"_flow sessions"+".csv","wt")
				else:
					st_date = str(period[0]).split(" ")[0] ; ed_date = str(period[1]).split(" ")[0]
					doc = open(""+machine+"_flow sessions_"+st_date+"__"+ed_date+".csv","wt")
						
				doc.write("""Name,User name,Log in,Log out,Cytometer,Serial No.,Duration (in hours)\n""")
				machineToCSV(doc,dbRoot,period,name,serial)
					
				if period is not None and period!= False:
					# if period == None:
						# doc = open(""+user_name+"_flow sessions"+".csv","wt")
					# else:
					st_date = str(period[0]).split(" ")[0] ; ed_date = str(period[1]).split(" ")[0]
					doc = open(""+machine+"_flow sessions_"+st_date+"__"+ed_date+".csv","wt")
						
					doc.write("""Name,User name,Log in,Log out,Cytometer,Serial No.,Duration (in hours)\n""")
					machineToCSV(doc,dbRoot,period,name,serial)

#like userToDoc, adds a machine to doc
def machineToCSV(doc,dbRoot,period,name,serial):
	#-print user with no date
	total_total = []
	row_time = []; time_column = []
	for departments in list(dbRoot.iter('Department')):
		for users in list(departments.iter("User")):
			nameN = users.get("name")
			userName = users.get("user_name")
			nameN = nameN.strip()
			if findComma(nameN) == True:
				nameN = normalize(nameN)

			for sessions in list(users.iter("session")):
				machine_name = sessions.get("cytometer")
				machine_sn = sessions.get("serial_no")
				if machine_name.upper()==name.upper() and machine_sn.upper()==serial.upper():
					w=sessions.get("logIn"); x=sessions.get("logOut")
					y=machine_name; z=machine_sn
					if period is None:
						smallRound,largeRound = sessionDuration(w,x)
						if smallRound == 0:
							smallRound = 'N/A'
						doc.write(""+nameN+","+userName+","+w+","+x+","+y+","+z+","+str(smallRound)+"\n")		
						row_time.append(smallRound)
						total_total.append(largeRound)
						sessionCount_noP =+ 1
					else:
						check_P =+ 1
						FMT = '%Y-%m-%d %H:%M:%S'
						startTime = datetime.strptime(w,FMT)
						if period[1]>startTime>period[0]:
							smallRound,largeRound = sessionDuration(w,x)
							if smallRound == 0:
								smallRound = 'N/A'
							doc.write(""+name+","+userName+","+w+","+x+","+y+","+z+","+str(smallRound)+"\n")		
							row_time.append(smallRound)
							total_total.append(largeRound)
							sessionCount_P =+ 1
	# if len(total_total) < 2:
	totalUsed = sum(total_total)
	# else:
		# totalUsed = sum(total_total)
	if totalUsed > 0:
		doc.write("\n\n\n,,,,,Total machine usage,"+str(totalUsed)+"\n")
	doc.close()
		
#checks the database to make sure the machine exists at least once
def machineExists(dbRoot,name,serial):
	for departments in list(dbRoot.iter('Department')):
		for users in list(departments.iter("User")):
			for sessions in list(users.iter("session")):
				machine_name = sessions.get("cytometer")
				machine_sn = sessions.get("serial_no")
				if machine_name.upper()==name.upper() and machine_sn.upper()==serial.upper():
					return machine_name
	return False

#creates (and returns) and empty database root
def createTimeLogDb():
    root = Element("logtime_database")
    logtime_database = ElementTree(root)
    return logtime_database 

#reads a .csv and transfers lines to xml db
def updateFromCSV(path,databaseFile):
    database1 = parse(databaseFile)
    database = database1.getroot()
    
    data_initial = open(path, "rU")
    csvFile = csv.reader((line.replace('\0','') for line in data_initial), delimiter=",")
    
    rowPos = 0
    for row in csvFile:
        lineInCsv = ';'.join(row)
        line = lineInCsv.split(';')
		        
        if rowPos == 0:
			if len(line) < 14:
				return False
			else:
				#getting column indices
				proper_column, colList = determineCols(line)
				print colList
				if proper_column == False:
					return False
				else:
					cL = colList 
					uName=cL[0]; name=cL[1]; role=cL[3]; dept=cL[5]; logInT=cL[6]; logInD=cL[7]
					logOutT=cL[8]; logOutD=cL[9]; cytometerCol=cL[11]; serialNoCol=cL[12]; custom=cL[13]
            
        elif line[uName]=="Administrator" or line[uName]=="BDService":
            pass
        else:
            #department element under root element, database
            department = line[dept]
            
            #user element under department element
            both_names = getName(line[name])
            userName = line[uName]
            
            #session element under user element
            s_t = startTime = line[logInT]
            s_d = startDate = line[logInD]
            e_t = line[logOutT]
            e_d = line[logOutD]
            cyt = cytometer = line[cytometerCol]
            s_n = serialNo = line[serialNoCol]
            #combining log in and out time and dates
            std,etd = timeAndDate(s_t,s_d,e_t,e_d)

            checkAndAdd(database,department, both_names,userName,std,etd,cyt,s_n)
        rowPos = rowPos+1
	database1.write(databaseFile)
    return True

#adds line info to db, avoiding duplicates
def checkAndAdd(database,dept,both_names,userName,std,etd,cyt,ser):
    if len(database.findall("Department")) == 0: #empty db -> add right away
        addElement(database,dept,both_names,userName,std,etd,cyt,ser)
        return
    else:
        sp_dept,dp_c,sp_user,usr_c,session = findElement(database,dept,userName,both_names,std,etd,cyt,ser)
        if session==True:
            return
        elif not sp_dept:
            addElement(database,dept,both_names,userName,std,etd,cyt,ser)
            return
        elif sp_dept and sp_user: #and (session is None):
            addSession(database,sp_dept,sp_user,std,etd,cyt,ser)
            return
        elif sp_dept and (not sp_user):
            addUserAndSession(database,sp_dept,userName,both_names,std,etd,cyt,ser)
            return

#department and user found, add a session
def addSession(database,sp_dept,sp_user,std,etd,cyt,s_n):
    for department in list(database.iter('Department')):
        if department.get("name")== sp_dept:
            for users in list(department.iter("User")):
                bothNs = users.get("name")
                userName = users.get("user_name")
                if bothNs == sp_user[0] and userName == sp_user[1]:
                    attributes = {"logIn":std,"logOut":etd,"cytometer":cyt,"serial_no":s_n}
                    sessionElement = SubElement(users,"session", attrib=attributes)
                    print "added a session"
                    
#department found, add user and session
def addUserAndSession(database,sp_dept,u_n,b_n,std,etd,cyt,s_n):
    for departments in list(database.iter('Department')):
        if departments.get("name") == sp_dept:
            userElement = SubElement(departments,"User",attrib={"user_name":u_n,"name":b_n})
            attributes = {"logIn":std,"logOut":etd,"cytometer":cyt,"serial_no":s_n}
            sessionElement = SubElement(userElement,"session", attrib=attributes)
            print "added a user and a session"
            
#finds any element; returns False if the element isn't there
def findElement(database,department,user_name,name,std,etd,cyt,ser):
    sp_dp = False; dp_count=0 
    user = False; user_count=0 
    sp_session = False

    for departments in list(database.iter('Department')):
        if departments.get("name") == department:
            sp_dp=departments.get("name")
            print "found a matching department", sp_dp
            for users in list(departments.iter("User")):
                bothNs = users.get("name")
                userName = users.get("user_name")
                if bothNs == name and userName == user_name:
                    user = [bothNs,userName]
                    print "found a matching user", user
                    for session in list(users.iter("session")):
                        w=session.get("logIn"); x=session.get("logOut")
                        y=session.get("cytometer"); z=session.get("serial_no")
                        if w==std and x==etd and y==cyt and z==ser:
                            print "found a matching session"
                            sp_session = True
                            return (sp_dp,dp_count,user,user_count,sp_session)
                #found a matching user? loop no more
                if user != False:
                    break
                user_count = user_count+1
        #found a matching department name? loop no more
        if sp_dp != False:
            break
        dp_count = dp_count+1
    return (sp_dp,dp_count,user,user_count,sp_session)

#when database is empty, adds the entire tree
def addElement(database,dept, b_n,u_n,std,etd,cyt,s_n):
    deptElement = SubElement(database,"Department", attrib={"name":dept})
    userElement = SubElement(deptElement,"User",attrib={"user_name":u_n,"name":b_n})
    attributes = {"logIn":std,"logOut":etd,"cytometer":cyt,"serial_no":s_n} 
    sessionElement = SubElement(userElement,"session", attrib=attributes)
    print "element added"
    
#combines log in and out info into a string
def timeAndDate(startTime,startDate,endTime,endDate):
    startDateTime = combine_t_d_24hr(startTime,startDate)
    endDateTime = combine_t_d_24hr(endTime,endDate)
    
    #sometime users don't log out and there's no end date or time
    if endDateTime==False: #(startDateTime==False) or (
        endDateTime = "####-##-## ##:##:##"
        return (str(startDateTime),endDateTime)
    
    return (str(startDateTime),str(endDateTime))

#converts time to 24hr format; combines time and date   
def combine_t_d_24hr(time1,date1):
    if len(time1) <= 5 or len(date1) <= 5:
        return False
    else:
        timeCheck = time1.split(' ')
        time1 = timeCheck[0]
        
        #add a zero to single hour digits
        hourDigit = time1.split(':')
        if len(hourDigit[0]) == 1:
            pad = '0'
            time1 = pad+hourDigit[0]+':'+hourDigit[1]+':'+hourDigit[2]
        
        FMT = '%B %d %Y %H:%M:%S' #this is the time format used
        
        #convert to 24hr format any time that is PM, ignore 12PM
        if timeCheck[1] =='PM' and hourDigit[0] != '12':
            time1 = date1+' '+time1
            time1 = datetime.strptime(time1, FMT) + timedelta(hours=12) 
            return time1
        else:
            time1 = date1+' '+time1
            time1 = datetime.strptime(time1, FMT) + timedelta(hours=00) 
            return time1

#resolves entered names to 'firstname lastname' format
def getName(name):
    all_spaces = countNameSpaces(name)
    if all_spaces == True:
        return "N/A"
    else:
        return name

# #resolves comma-separated first and last names to "first last" format
def normalize(name):
    #assumes name is pre-checked and commas have been found
	splitName = name.split(",")
	nameLen = len(splitName)
	lastIndex = nameLen-1
	firstName = (splitName[lastIndex]).strip()
	lastName = (splitName[0]).strip()
	return firstName+" "+lastName   

#return True if a name is just spaces; False otherwise
def countNameSpaces(name):
    char_count = 1
    for char in name:
        if char == " ":
            char_count =+ 1
    
    if char_count > 1:  
        total_spaces = char_count-1
    else:
        total_spaces = char_count-1 
    
    name_length = len(name)
    if total_spaces == name_length:
        return True
    else:
        return False

#looks at the header, returns the index of each column 
def determineCols(line):
	a=b=c=d=e=f=g=h=i=j=k=l=m=n = None
	column = 0
	for element in line:
		if element == 'User Name':
			a = UserNameCol = column
		if element == 'Full Name':
			b = fullNameCol = column
		if element == 'Application':
			c = applicationCol = column
		if element == 'Role':
			d = roleCol = column
		if element == 'Department':
			e = departmentCol = column
		if element == 'Institution':
			f = InstitutionCol = column
		if element == 'LogIn Time':
			g = logInTimeCol= column
		if element == 'LogIn Date':
			h = logInDateCol= column
		if element == 'LogOut Time':
			i = logOutTimeCol = column
		if element == 'LogOut Date':
			j = logOutDateCol = column
		if element == 'Build Version':
			k = buildVersionCol = column
		if element == 'Cytometer':
			l = cytometerCol= column
		if element == 'Serial No':
			m = serialNoCol= column
		if element == 'Custom':
			n = customCol = column
		column = column+1
	if (a)and(b)and(c)and(d)and(e)and(f)and(g)and(h)and(i)and(j)and(k)and(l)and(m)and(n) is not None:
		return (False, (a,b,c,d,e,f,g,h,i,j,k,l,m,n))
	else:
		return (True, (a,b,c,d,e,f,g,h,i,j,k,l,m,n))

#reads a .csv from an excel file		
def readExcelCsv(path):
		
	data_initial = open(path, "rU")
	csvFile = csv.reader((line.replace('\0','') for line in data_initial), delimiter=",")
	
	#priming some names
	summed = None
	added = None
	row = None
	neverLoggedOut = 0
	
	rowPos = 0
	for row in csvFile:
		line1 = ';'.join(row)
		line = line1.split(';')
		if rowPos == 0:
			rowPos = rowPos+1
			pass
		elif rowPos == 1:
			updatedSum, added, rowPos, neverLoggedOut = initiateTime(line,rowPos,neverLoggedOut)
		else:
			print 'moving to row',rowPos, ';already added',added, '; didnt log out:',neverLoggedOut, ';total so far',round(abs(updatedSum).total_seconds()/3600.0,2)#updatedSum
			updatedSum, neverLoggedOut, added = sumTime(line, updatedSum, neverLoggedOut,added)
			rowPos = rowPos +1
	
	#expressing time in hour format and then rounding it off
	timeInHours = abs(updatedSum).total_seconds()/3600.0
	timeInHoursRounded = str(round(timeInHours,2))
		
	if neverLoggedOut == 0:
		#Usage time in (y,m,w,d, h:m:s): "+str(updatedSum)+"\n
		return "Time used in hours: "+timeInHoursRounded+" hours" \
			   "\n...... ......"
			   #\nNo. of sessions added: "+str(added)+"
	elif neverLoggedOut > 0:
		#Usage time in (y,m,w,d, h:m:s): "+str(updatedSum)+"\n
		return "Time used in hours: "+timeInHoursRounded+" hours" \
		   "\nSession(s) when user did not log out: "+str(neverLoggedOut)+"\n...... ......"

#initiates; sums first sessions. The rest are added to these		   
def initiateTime(values,rowPos,neverLoggedOut):
	a = values[6]
	aLen = len(values[6])
	b = values[7]
	bLen = len(values[7])
	c = values[8]
	cLen = len(values[8])
	d = values[9]
	dLen = len(values[9])
		
	#file may have a bunch of commas in a row but no entry
	if aLen==0 and bLen==0 and cLen==0: 
		#neverLoggedOut = 0
		rowPos = 1
		return (firstSession, added, rowPos, neverLoggedOut)
		
	#no log out time entry -- user never logged out, skip but keep count 
	if dLen < 5 or cLen < 5:
		neverLoggedOut = neverLoggedOut+1
		firstSession = None
		added = 0
		rowPos = 1
		
	else:	
		#extracting starting time and date
		startTime = str(a)
		startDate = str(b)
		#extracting ending time and date
		endTime = str(c)
		endDate = str(d)
		#change time to 24hr fmt and concatenate date 
		startDateTime = converTo24hrAndAppendDate(startTime,startDate)
		endDateTime = converTo24hrAndAppendDate(endTime,endDate)
		#time used in a session
		firstSession = (endDateTime-startDateTime)
		#keep track of sessions counted
		added = 1
		rowPos = rowPos+1
		#neverLoggedOut = 0
	
	return (firstSession, added, rowPos, neverLoggedOut)

#finds the name of the machine; checks the 11th column of the first row
def findMachineName(path):

	data_initial = open(path, "rU")
	csvFile = csv.reader((line.replace('\0','') for line in data_initial), delimiter=",")
	
	rowPos = 0
	for row in csvFile:
		line1 = ';'.join(row)
		line = line1.split(';')
		if rowPos == 0:
			rowPos = rowPos + 1
			pass
		else:
			machineName = line[11]
			break
	if len(machineName) == 0:
		return "No machine name"
	else:
		return ""+machineName+""

#add another time session to the existing sum
def sumTime(values, summed, neverLoggedOut, added):
	a = values[6]
	aLen = len(values[6])
	b = values[7]
	bLen = len(values[7])
	c = values[8]
	cLen = len(values[8])
	d = values[9]
	dLen = len(values[9])
				
	#file may have a bunch of commas in a row but no entry
	if aLen==0 and bLen==0 and cLen==0: 
		return summed, neverLoggedOut, added
			
	#no log out time entry -- user never logged out, skip but keep count 
	if dLen < 5 or cLen < 5: #5 is arbitrary, picked based the other lengths
		updatedSum = summed
		return updatedSum, neverLoggedOut+1, added
		
	else:
		#extracting starting time and date
		startTime = str(a)
		startDate = str(b)
		#extracting ending time and date
		endTime = str(c)
		endDate = str(d)
		#change time to 24hr fmt and concatenate date 
		startDateTime = converTo24hrAndAppendDate(startTime,startDate)
		endDateTime = converTo24hrAndAppendDate(endTime,endDate)
		#time used in a session
		sessionDuration = (endDateTime-startDateTime)
		#updating the time
		updatedSum = summed + sessionDuration
		#keep track of sessions counted
		added = added+1
	
	return (updatedSum, neverLoggedOut, added)

#combines a string of time and date
def combine_t_d_24hr(time1,date1):
	if len(time1) <= 5 or len(date1) <= 5:
		return False
	else:
		timeCheck = time1.split(' ')
		time1 = timeCheck[0]
		
		#add a zero to single hour digits
		hourDigit = time1.split(':')
		if len(hourDigit[0]) == 1:
			pad = '0'
			time1 = pad+hourDigit[0]+':'+hourDigit[1]+':'+hourDigit[2]
		
		FMT = '%B %d %Y %H:%M:%S' #this is the time format used
		
		#convert to 24hr format any time that is PM, ignore 12PM
		if timeCheck[1] =='PM' and hourDigit[0] != '12':
			time1 = date1+' '+time1
			time1 = datetime.strptime(time1, FMT) + timedelta(hours=12) 
			return time1
		else:
			time1 = date1+' '+time1
			time1 = datetime.strptime(time1, FMT) + timedelta(hours=00) 
			return time1

#menu program displaying options => what the program can do.
def menu(): 
	while(True):
		os.system("clear")
		print "WHAT WOULD YOU LIKE TO DO?"
		print           
		print "A. Upload a .csv excel file (just one) to a database"
		print "B. Upload several .csv excel files to an '.xml' database" 
		print "C. Print a specific user's sessions"  
		print "D. Print a specific group's sessions"  
		print "E. Print all usage"
		print "F. Print sessions and total time used on a given machine"
		print "X. Exit Program"
		print
			

		#user chooses an option from above
		selected = raw_input("Enter menu selection: ").upper()

		if selected == "A":
			upload()
		
		elif selected == "B":
			uploadSeveral()
			
		elif selected == "C":
			printAUser()
		
		elif selected == "D":
			printAGroup()
		
		elif selected == "E":
			printAll()
						
		elif selected == "F":
			machineUsage()
			
		elif selected == 'X':
			hold = raw_input("You have chosen to exit. \n\nPress RETURN to continue with Terminal ")
			return False
		
		else:
			print "\n  Please enter a valid selection"
			hold = raw_input("\nPress RETURN to continue ")
menu()