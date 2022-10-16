import psycopg2, hashlib
from tkinter import *
from tkinter import simpledialog
from functools import partial
######################
# Initialize DB 
# Connection Variables
DB_HOST = "localhost"
DB_NAME = "sdesai"
DB_USER = "sdesai"
DB_PASS = ""

# Connection to DB
conn = psycopg2.connect(dbname = DB_NAME, user = DB_USER, password = DB_PASS, host = DB_HOST)

# Initiates Cursor - To Perform DB Operations
cur  = conn.cursor()

# Creates Password Table
cur.execute("""
CREATE TABLE IF NOT EXISTS masterpasswords(
id serial PRIMARY KEY,
password TEXT NOT NULL
)
""")

# Creates Vault Table
cur.execute("""
CREATE TABLE IF NOT EXISTS vault(
id serial PRIMARY KEY,
website TEXT NOT NULL,
username TEXT NOT NULL,
password TEXT NOT NULL
)
""")
######################
# Create Pop Up for adding different logins/passwords
def popUp(text):
    answer = simpledialog.askstring("input string", text)
    return answer

# # Close the connection
# conn.close()

# Initiates TK Interface (GUI)
window = Tk()
window.title("KEY VAULT")

# Function to Hash Passwords
def hashPasswords(input):
    # Will Take The Input And Create A md5 Hash
    hash = hashlib.md5(input)
    # This WIll Return the Hash as text So We Can Read It
    hash = hash.hexdigest()

    return hash

def firstScreen():
    window.geometry("350x155") 
    #Creates Label For New Pass
    lbl = Label(window, text = "Create Master Key")
    lbl.config(anchor=CENTER)
    lbl.pack()   
    # Creates Input Box For New Key
    text = Entry(window, width = 20, show = "*")
    text.pack()
    text.focus()
    # Creates Label For Re Enter Key
    lbl1 = Label(window, text = "Re-Enter Master Key")
    lbl1.pack()
    # Creates Input Box For Re Enter Key
    text1 = Entry(window, width = 20, show = "*")
    text1.pack()
    # Creates Lable For No Match
    lbl2 = Label(window)
    lbl2.pack()

    # Function To Save And Authenticate New Key
    def savePassword():
        # Checks Both Inputs To See If They Match
        if text.get() == text1.get():
            # Stores New Pass into Hashed Variable and encodes it
            hashedPass = hashPasswords(text.get().encode('utf-8'))
            # Inserts Variable Into Created DB Table
            insert_password = """INSERT INTO masterpasswords(password)
            VALUES(%s) """
            cur.execute(insert_password, [(hashedPass)])
            conn.commit()
            # If Succesfully Saved, Immediatly Jumps To The Vault
            passWordVault()
        else:
            # Label Appears If Both Inputs Dont Match
            lbl2.config(text = "Keys Do Not Match")

    # Creates Save Button
    btn = Button(window, text="Save", command=savePassword)
    btn.pack()
  
def loginScreen():    
    window.geometry("260x105")
    # Creates Label For Masterkey
    lbl = Label(window, text = "Enter Master Key")
    lbl.config(anchor=CENTER)
    lbl.pack()
    # Creates Input Box For Masterkey
    text = Entry(window, width=20, show="*")
    text.pack()
    text.focus()
    # Creates Label For Incorrect Key
    lbl1 = Label(window)
    lbl1.pack()

    def getMasterPassword():
        # Checks for match on password the user entered and returns
        checkHashedPassword = hashPasswords(text.get().encode('utf-8'))
        cur.execute("SELECT * FROM masterpasswords WHERE id = 1 AND password = %s", [(checkHashedPassword)])
        print(checkHashedPassword)
        return cur.fetchall()
    # Function To Check If The Password Matches The One Created
    def checkPassword():
        # Test Key
        match = getMasterPassword()
        print(match)
        # Conditional to Authenticate Key
        if match:
            passWordVault()
        else: 
            text.delete(0, "end")
            lbl1.config(text="Wrong Key")

    # Creates Submit Button
    btn = Button(window, text="Submit", command=checkPassword)
    btn.pack()

def passWordVault():
    # Upon Success, This Command will clear Login Screen and Bring up All Stored Keys
    for widget in window.winfo_children():
        widget.destroy()
    # Function to Add Entries to vault    
    def addEntry(): 
        webPrompt = "Website"
        userPrompt = "Username"
        passPrompt = "Password"

        website = popUp(webPrompt)
        username  = popUp(userPrompt)
        password = popUp(passPrompt)
        
        # Inserts variables into DB
        insert_fields = """INSERT INTO vault(website,username,password)
        VALUES(%s, %s, %s)"""

        cur.execute(insert_fields, (website, username, password))
        conn.commit()

        passWordVault()
    # Function to Remove Entries From vault
    def removeEntry(input):
        cur.execute("DELETE FROM vault WHERE id = %s", (input,))
        conn.commit()

        passWordVault()

    window.geometry("750x400")
    # Creates Label For Key Vault
    lbl = Label(window, text = "Key Vault")
    lbl.grid(row = 1, column = 1)
    
    btn = Button(window, text = '+', command = addEntry)
    btn.grid(row = 1, column = 3, pady = 10)
    # Grid for the vault layout
    lbl = Label(window, text = "Website")
    lbl.grid(row = 2, column = 0, padx = 80)
    lbl = Label(window, text = "Username")
    lbl.grid(row = 2, column = 1, padx = 80)
    lbl = Label(window, text = "Password")
    lbl.grid(row = 2, column = 2, padx = 80)

    # Show entries in vault
    cur.execute("SELECT * FROM vault")
    if (cur.fetchall() != None):
        i = 0 
        while True:
           cur.execute("SELECT * FROM vault") 
           array  = cur.fetchall()

           lbl1 = Label(window, text  = (array[i][1]))
           lbl1.grid(column  = 0, row = i+3)
           lbl1 = Label(window, text  = (array[i][2]))
           lbl1.grid(column  = 1, row = i+3)
           lbl1 = Label(window, text  = (array[i][3]))
           lbl1.grid(column  = 2, row = i+3)
           # Delete Button 
           btn = Button(window, text  = "-", command  = partial(removeEntry, array[i][0]))
           btn.grid(column = 3, row = i+3)
           # Increases i
           i = i+1
           # Stops while loop 
           cur.execute("SELECT * FROM vault")
           if (len(cur.fetchall()) <= i):
            break
# Checks To See If There Is a MasterPass in the DB
cur.execute("SELECT * FROM masterpasswords")

if cur.fetchall():
    loginScreen()
else:
    firstScreen()
window.mainloop()