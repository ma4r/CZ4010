import openmined_psi
import requests
import base64
import json
import utils
class CLIClient:

    #Simple CLI client for interface with webbackend
    baseURL = "http://localhost:8000/"
    def __init__(self):
        self._loginToken = None
        self._sessionHeader = {}
        self._id = None
        self._loggedin = False

    def option_loop(self,options,funcs,go_back):
        i = 1
        for opt in options:
            print(str(i)+". "+opt)
            i+=1

        n = input("Enter Choice:(0 to go back)")

        try:
            n = int(n)
            if n<0 or n>len(options):
                raise Exception
        except:
            print("Invalid input")
            return False
        if n==0:
            return go_back()
        return funcs[n-1]()

    # Main application loop
    def start(self):
        while True:
            opts = ['Login', 'Register']
            funcs = [self.login, self.register]
            go_back = quit
            while self._loggedin == False:
                res = self.option_loop(opts,funcs,go_back)
                if res == True:
                    break
            opts = ['View my data set',
                    'Upload data',
                    'New Sharing session',
                    'Join Sharing session',
                    'My hosted sessions',
                    'View PSI results']
            funcs = [self.get_data_all,
                     self.post_data,
                     self.new_session,
                     self.join_session,
                     self.hosted_sessions,
                     self.my_sessions]
            go_back = self.logout

            self.option_loop(opts,funcs,go_back)

    # Login with credentials on backend, authenticate with self._loginToken
    def login(self,user = None, pwd = None,check=False):
        if user is None:
            user = input("\nUsername: ")
        if pwd is None:
            pwd = input("\nPassword: ")
        url = self.baseURL+"login/"

        body = {'username':user,
                'password':pwd}
        res = requests.post(url,data=body)
        if res.status_code == 400:
            print("Wrong Username/Password")
            return False

        if res.status_code == 200:


            print("Login success")
            if check:
                token = "Token "+res.json()["token"]
                if token == self._loginToken:
                    return (user,pwd)
                else:
                    print("Wrong username/password")
                    return False
            print("Session Start")

            self._loginToken = "Token "+res.json()["token"]
            self._sessionHeader={"Authorization":self._loginToken}
            self._id = requests.get(self.baseURL+"me/",headers=self._sessionHeader).json()['id']
            self._loggedin = True
            return True

    # Register with credentials, also logs in
    def register(self):
        url = self.baseURL+"user/"
        user = input("\nUsername: ")
        email = input("\nEmail: ")
        pwd = input("\nPassword: ")

        body = {'username': user,
                'email':email,
                'password': pwd}

        resp = requests.post(url,data=body)
        if resp.status_code != 200:
            print("Registration Failed: ",resp.json())
            return False
        else:
            return self.login(user,pwd)

    # Revoke token, logout
    def logout(self):

        res = requests.post(self.baseURL+'logout/',headers=self._sessionHeader)

        if res.status_code == 200:
            self._loggedin = False
            self._loginToken = None
            self._sessionHeader = False
            self._id = False
            return True
        print("Failed to Log out")
        print(res.status_code,res.json())
        return False


    def input_data(self,method):
        if method == "1":
            n = input("Number of entries: ")
            data = []
            for i in range(int(n)):
                data.append(input("Entry "+str(i)+" :"))
            return data

        if method == "2":
            path = input("Enter path: ")
            try:
                with open(path,'r') as f:
                    data = f.read()
                    data = data.split("\n")
                    if data[-1] == "":
                        data.pop()
                    return data
            except:
                print("Failed to Open file")
                raise Exception

    # Send data to be hosted on server
    def post_data(self):
        title = input("Dataset Title: ")
        description = input("Dataset Description: ")
        while True:
            method = input("(1)Manual input/(2)File: (1/2) ")
            if method =="1" or method =="2":
                break
            else:
                print("Invalid Input")
        try:
            data = self.input_data(method)
        except:
            return False

        url = self.baseURL+"data/"
        header = self._sessionHeader

        jsonData = json.dumps({"data": data})
        body = {"title":title,
                "description":description,
                "data":jsonData }

        resp = requests.post(url,data=body,headers=header)
        if resp.status_code != 201:
            print("Failed to post data:")
            print(resp.status_code,resp.json())
            return False

        else:
            print("Data posted sucessfully")
            res= resp.json()
            print("Title: ",res["title"])
            print("Description: ", res["description"])
            return True

    def get_data_all(self,select = False):
        url = self.baseURL+"data/"
        header = self._sessionHeader

        res = requests.get(url,headers=header).json()
        base = "{:<5}{:<20}{}"

        while True:
            print(base.format("No.", "Title", "Description"))

            for i in range(len(res)):
                print(base.format(i + 1, res[i]["title"], res[i]["description"]))

            if select:
                quer = "Select entry number to post:(0 to go back)"
            else:
                quer = "Enter number for details:(0 to go back)"
            n = input(quer)
            try:
                n = int(n)
                if n<0 or n>len(res):
                    raise Exception
            except:
                print("Invalid Input")
                continue
            if n ==0:
                return False
            print("Title: ",res[n-1]["title"])
            print("Description: ",res[n-1]["description"])
            print("Data: ")
            for data in res[n-1]["data"]["data"]:
                print(data)
            if select:
                return res[n-1]
            continue

    def new_session(self):
        dataSet = self.get_data_all(select=True)
        if dataSet == False:
            return False
        url = self.baseURL+"session/"
        header = self._sessionHeader

        title = input("Session Title: ")
        desc = input("Session Description:")
        id = dataSet["id"]
        body  ={"title":title,
                "description":desc,
                "data":id
        }
        res =requests.post(url,data=body,headers=header)

        if res.status_code!= 201:
            print("Failed to create sharing session")
            print(res.status_code,res.json())
            return False
        else:
            print("Session started sucessfully, share ID to other party to begin PSI")
            print("Session ID: ",res.json()["session_id"])
            return True

    def get_data(self,method):
        if method == '1':
            while True:
                method = input("(1)Manual input/(2)File: (1/2) ")
                if method == "1" or method == "2":
                    break
                else:
                    print("Invalid Input")
            return self.input_data(method)

        elif method == '2':
            dataSet = self.get_data_all(True)
            return dataSet["data"]["data"]

    # Store psi client key, encrypted with password
    def save_key(self,k,session,data):
        while True:
            print("Login to store session key")
            res = self.login(check=True)
            if res != False:
                break
        user,pwd = res

        encrypted = utils.password_encrypt(k,pwd,5)

        with open(res[0]+".txt",'a') as f:
            f.write(session+","+encrypted.decode()+","+str(data)+"\n")
        return True

    # Load psi client key
    def load_key(self,session,user,pwd):
        with open(user+ ".txt", 'r') as f:
            file = f.read()
            sessions = file.split("\n")
            if sessions[-1] == '':
                sessions.pop()
        flag = False
        for one_sess in sessions:
            sess = one_sess.split(",")
            if sess[0] == session:
                flag = True
                token = sess[1].encode()
                data = sess[2:len(sess)]
        if not flag:
            print("Session key not found")
            return False
        data = utils.clean_arr(data)
        decrypted = utils.password_decrypt(token,pwd)
        return decrypted,data

    # PSI Protocol
    def begin_psi(self,data,session,save_key=True):
        client = openmined_psi.client.CreateWithNewKey(reveal_intersection=True)
        key = client.GetPrivateKeyBytes()
        req = client.CreateRequest(data)
        encoded = base64.b64encode(req).decode("ascii")

        url = self.baseURL + "session/"+session+"/"
        header = {"Authorization":self._loginToken,
                  "Content-Type":'application/json'}

        body = {'n': len(data),
                'data': encoded}

        res = requests.patch(url=url, headers=header, data=json.dumps(body))
        print(res)
        if res.status_code == 200:
            print("Request Success")
            self.save_key(key,session,data)
            return True
        else:
            print("Request Failed")
            print(res.status_code,res.json())
            return False

    # Join existing private sharing sessions, needs session id
    def join_session(self):
        sess = input("Enter the given session ID to join an existing session: ")
        while True:
            get_data = input("(1) Use local data or (2)existing one on database :(1/2)")
            if get_data == '1' or get_data == '2':
                break
            else:
                print("Invalid Input")
        try:
            data = self.get_data(get_data)
            if data == False:
                raise Exception
        except:
            print("Failed to get data")
            return False

        try:
            res = self.begin_psi(data,sess)
            if res == False:
                raise Exception
            return res
        except:
            print("Failed to begin PSI session")
            return False

    def calculate_intersection(self,key,sess,data):

        res = sess['res']
        setup = base64.b64decode(res['setup'])
        response = base64.b64decode(res['response'])

        client = openmined_psi.client.CreateFromKey(key,reveal_intersection=True)
        intersect = client.GetIntersection(setup,response)
        print("Intersection: ")
        for i in intersect:
            print(data[i])

    # Retrieve all joined sessions, and calculate psi intersection
    def my_sessions(self):
        url = self.baseURL+"session/"
        header = self._sessionHeader
        res = requests.get(url,headers=header)
        if res.status_code != 200:
            print("Failed to retrieve sessions")
            return False
        else:
            sessions = res.json()
            filtered = []
            for session in sessions:
                if session['client2'] == self._id:
                    filtered.append(session)

            base = "{:<5}{:<45}{}"
            print(base.format("No.", "Session ID","Status"))
            for i in range(len(filtered)):
                print(base.format(i+1,filtered[i]["id"],filtered[i]["status"]))
            while True:
                n = input("Enter entry number to retrieve dataset result: (0 to go back)")
                try:
                    n = int(n)
                    if n<0 or n>len(filtered):
                        raise Exception
                except:
                    print("Invalid Input")
                    continue
                if n ==0:
                    return False
                break


            user = input("Reenter user name to get session key: ")
            pwd = input("Reenter password to get session key: ")

            try:
                key,data = self.load_key(filtered[n-1]['id'],user,pwd)
            except:
                print("Invalid User/password")
                return False

            print("My Data: ")
            for d in data:
                print(d)

            self.calculate_intersection(key,filtered[n-1],data)
            return True

    # Retreive all data that are hosted on server
    def hosted_sessions(self):
        url = self.baseURL + "session/"
        header = self._sessionHeader
        res = requests.get(url, headers=header)
        if res.status_code != 200:
            print("Failed to retrieve sessions")
            return False
        else:
            sessions = res.json()
            filtered = []
            for session in sessions:
                if session['client1'] == self._id:
                    filtered.append(session)
            base = "{:<5}{:<45}{}"
            while True:
                print(base.format("No.", "Session ID", "Status"))
                for i in range(len(filtered)):
                    print(base.format(i + 1, filtered[i]["id"], filtered[i]["status"]))
                n = input("Enter entry number to retrieve sent dataset: (0 to go back)")
                try:
                    n = int(n)
                    if n < 0 or n > len(filtered):
                        raise Exception
                except:
                    print("Invalid Input")
                    continue
                if n == 0:
                    return False

                dataId = filtered[n-1]["data"]

                res = requests.get(self.baseURL+'data/'+str(dataId)+'/',headers=self._sessionHeader)
                if res.status_code!= 200:
                    print("Failed to retreive data")
                    continue

                print("Session: ",filtered[n-1]["id"])
                d = res.json()
                print("Title: ",d['title'])
                print('Description: ',d['description'])
                print('Data: ')
                for e in d['data']['data']:
                    print(e)

                return True

if __name__ == "__main__":
    ui = CLIClient()
    ui.start()
