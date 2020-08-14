import json
import os
from cryptography.fernet import Fernet


def does_file_exist(which_file, verbose=True):
    if which_file == "database": file_to_check = "database.json"
    if which_file == "key": file_to_check = "key.key"

    if verbose==True: print ("Checking if", which_file, "exists")
    # Check if file exists
    if os.path.exists(file_to_check):
        if verbose==True: print(which_file, "exists")
        return True
    else:
        if verbose==True: print(which_file, "does not exist")
        return False


def create_key():
    # Creates master password, or key
    key = Fernet.generate_key()
    with open ("key.key", "wb") as key_file:
        key_file.write(key)
        # Instructions
    print('Key, has been created. Check "key.key".\nInstructions:\n* Before you open the program, paste the valid key in this directory.\n* The program will attempt to validate the key\n* If failed, the program will be terminated\n* Once the key is validated, the database will be unlocked, or decrypted\n* When you exit the program, the database will be automatically locked, or encrypted\n* Remove key from this directory and hide it somewhere only you know (this is to prevent unauthorized access, the valid key is very difficult to crack, if possible anyway)\n!! DISCLAIMER: IF KEY IS LOST, YOU WILL NOT BE ABLE TO ACCESS THE DATABASE. You make open the key.key file in a text editor and save the key somewhere to re-create the key.key file.\nDO NOT SHARE THIS KEY WITH ANYONE TO AVOID UNAUTHORIZED ACCESS!')


def get_key():
    # Accesses key
    with open("key.key", "rb") as key_file:
        key = key_file.read()
    fernet = Fernet(key)
    return fernet


def test_key():
    if does_key_exist == False:
        print ("Key does not exist...")
        create_new_key = input ("Key does not exist. Do you want to create it? (Y)es or (N)o?").lower()
        if create_new_key == "y":
            create_key()
        else:
            return

    # If the key does exist in the directory (or if we have just created it), the program will attempt validate the key
    try:
        fernet = get_key()
        testing_string = 'testing string'.encode()
        testing_string = fernet.encrypt(testing_string)
        print('Valid token provided, proceeding.')
        return

    # If the key is not valid, the program will return
    except:
        print('Error: Invalid key provided.')
        return


def load_database_from_file():
    if does_file_exist("database", verbose=False):
        with open("database.json", 'rb') as database_file:
            encrypted_data = database_file.read()

        fernet = get_key()
        plaintext_data = fernet.decrypt(encrypted_data)

        # I really hate that we have to do this, but fernet seems to require it be read from a file, so ok
        with open("database_plaintext.json", 'wb') as database_file:
            database_file.write(plaintext_data)

        with open("database_plaintext.json", "rb") as database_file:
            decrypted_data = json.load(database_file)

        os.remove("database_plaintext.json")

        if type(decrypted_data) is dict:
            decrypted_data = [decrypted_data]

    else:
        decrypted_data = []

    return decrypted_data


def write_database_to_file(plaintext_data):
    # write the data in plaintext
    with open('database.json', 'w') as database_file:
        json.dump(plaintext_data, database_file, indent=4)

    # reload it and load into memory
    with open("database.json", 'rb') as database_file:
        data = database_file.read()

    # get the key
    fernet = get_key()

    # Encrypts database
    encrypted_database = fernet.encrypt(data)

    # Writes encrypted database
    with open("database.json", 'wb') as f:
        f.write(encrypted_database)

    return


def view_accounts():
    # Loads database
    data = load_database_from_file()

    number_of_accounts_loaded = len(data)
    print(str(number_of_accounts_loaded), "accounts found!")
    print('###########\n')


    if number_of_accounts_loaded == 0:
        return

    # Attempts to print all accounts and their information
    for account in data:
        print("Website: ", account.get("website"))
        print("Username: ", account.get("username"))
        print("Password: ", account.get("password"))
        print("Username: ", account.get("notes"))

        print('###########\n')

    return


def add_account():
    # Asking for information
    website = input('Enter website name: ').lower()
    username = input('Enter username: ')
    password = input('Enter password: ')
    notes = input('Enter notes (If none, type "None"): ')

    # You probably want to add some validation here to check that something has actually been entered...

    # Loads previous data from json file
    data = load_database_from_file()

    # Append the new data
    data.append({
        "website": website,
        "username": username,
        "password": password,
        "notes": password
    })

    # Then write it back to the file
    write_database_to_file(data)

    print('###########\n')
    print('Account has been successfully added to file!')
    return


def specific_account(website, action="view"):
    data = load_database_from_file()

    # Looping through the accounts to find the account that the user is looking for
    for account in data:
        if account["website"] == website:

            print('###########')
            print('Website: ', account["website"])
            print('Username: ', account["username"])
            print('Password: ', account["password"])
            print('Notes: ', account["notes"])
            print('###########')

            if action == "delete":
                # Confirmation
                prompt = input('Are you sure you want to delete? This action cannot be undone(Y/N): ').lower()
                if prompt == 'y':
                    data.remove(account)
                    write_database_to_file(data)
                    print('Account deleted.')
                    print('###########\n')

                else:
                    print('Operation cancelled.')
                    print('###########\n')

            return

    print('Account not found!')
    print('###########\n')
    return


def select_operation():
    print('\nOperations:\nA: View Accounts\nB: Add Account\nC: Delete Account\nD: Search For Account\nE: Exit\n')
    answer = 'e'
    answer = input('Input operation letter: ').lower()

    print('\n###########')
    if answer == 'a':
        view_accounts()
    if answer == 'b':
        add_account()
    if answer == 'c':
        website = input('Enter website name to delete: ').lower()
        specific_account (website, "delete")
    if answer == 'd':
        website = input('Enter website name to view: ').lower()
        specific_account (website)

    return answer


# Main loop

print('Loading Assets...')

if does_file_exist("key") == False:
    print ("Creating key...")
    create_key()

function_to_run = None
while function_to_run != "e":
    function_to_run = select_operation()
    # doing it this way means the script will loop until we get the exit key

print ("Exiting...")