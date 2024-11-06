import pyrebase
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime

# provide the correct path to your Firebase Admin SDK JSON file
cred = credentials.Certificate(
    "./authfirebasepython-firebase-adminsdk-15h6t-48fc1310eb.json")
# initialize the Firebase Admin SDK
firebase_admin.initialize_app(cred)

firebaseConfig = {
    'apiKey': "AIzaSyAPJ0D5DbIVNSvupSP6FmgqRyrLDKlsxqQ",
    'authDomain': "authfirebasepython.firebaseapp.com",
    'projectId': "authfirebasepython",
    'storageBucket': "authfirebasepython.appspot.com",
    'messagingSenderId': "961061327444",
    'appId': "1:961061327444:web:5359043f66682bbdb213c1",
    'measurementId': "G-DRNXNY4MLR",
    'databaseURL': ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

firestore_db = firestore.client()


def sign_up():
    email = input('Enter email: ')
    password = input('Enter password: ')
    full_name = input('Enter full name: ')
    mobile_number = input('Enter mobile number: ')
    try:
        user = auth.create_user_with_email_and_password(
            email=email, password=password)
        print(f'Sucessfully created user')
        user_data = {
            'email': email,
            'password': password,
            'full_name': full_name,
            'mobile_number': mobile_number,
            'uid': user['localId']
        }

        firestore_db = firestore.client()
        firestore_db.collection('users').document(
            user['localId']).set(user_data)
        print('successfully added user to firestore')
        return user
    except Exception as e:
        print(f'Error creating user {e}')
        return None


def login():
    email = input('Enter email: ')
    password = input('Enter password: ')
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        print(f'Sucessfully logged in user')
        return user
    except Exception as e:
        print(f'Error logging in user {e}')
        return None


def chat():
    chat_name = input('Enter chat name: ')
    current_time = datetime.now()
    chat_data = {
        'chat_name': chat_name,
        'created_at': current_time
    }
    firestore_db = firestore.client()
    firestore_db.collection('chats').add(chat_data)
    print('chats data saved to firestore')


def message():
    chat_room_id = input('Enter chat room id: ')
    message = input('Enter message: ')
    user_email = input('Enter Your Email :')
    current_time = datetime.now()

    message_data = {
        'chat_room_id': chat_room_id,
        'message': message,
        'created_at': current_time,
        'send_by': user_email
    }
    chat_message = firestore_db.collection('chats').document(
        chat_room_id).collection('messages').add(message_data)
    print('message saved to firestore')

def get_messages():
    # send_by_user = auth.current_user

    user = auth.current_user
    if user is None:
        print("No user is currently logged in.")
        return

    user_email = user["email"]
    chat_room_id = input('Enter a Chat Room ID: ').strip()

    if not chat_room_id:
        print('Invalid Chat Room ID')
        return

    try:
        # Retrieve messages from the chat room
        messages = firestore_db.collection('chats').document(
            chat_room_id).collection('messages').get()

        if messages:
            print(
                f"Messages sent by {user_email} in chat room {chat_room_id}:")
            for msg in messages:
                data = msg.to_dict()
                # Print the message only if it was sent by the current user
                print(f"Message: {data['message']}")
                print(f"Send By: {data['send_by']}")
                print(f"Created At: {data['created_at']}")
                print('------------------------')
        else:
            print("No messages found.")

    except Exception as e:
        print(f"Error retrieving messages: {e}")


print('Welcome to Firebase Login System')
print('1. Sign Up')
print('2. Login')
print('3. Start Chat')
print('4. Coming Soon')
print('5. Get Messages')
print('q. Quit')
while True:
    choice = input('Enter Your Choice in 1,2,3,4,5,q: ')
    if choice == '1':
        sign_up()
    elif choice == '2':
        login()
    elif choice == '3':
        print('Create ChatRoom or Message 1: Create ChatRoom 2: Message')
        choice = input('Enter your choice: ')
        if choice == '1':
            chat()
            while (True):
                msg_choice = input(
                    'Enter your choice 1 : Message in ChatRoom 2 : Quit :')
                if msg_choice == '1':
                    message()
                    break
                elif msg_choice == '2':
                    break
                else:
                    print('Invalid Choice')
        elif choice == '2':
            message()
            break
    elif choice == '4':
        print('Coming Soon')
        break
    elif choice == '5':
        get_messages()
        break
    elif choice.lower() == 'q':
        break
    else:
        print('Invalid Choice')

"""
Security Rules

rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {

   // Rules for the 'users' collection
    match /users/{userId} {
      // Only allow users to read/write their own data
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    match /chats/{chatId} {
      // Anyone authenticated can create a chat room
      allow create: if request.auth != null;
      
      // For reading/writing a specific message within a chat room
      match /chats/{chatId}/messages/{messageId} {
        // Only allow users to write their own messages
        allow read : if request.auth != null;
        allow write: if request.auth != null && request.auth.token.email == resource.data.send_by;
    }
    }
  }
}

"""
