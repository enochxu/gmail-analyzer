from __future__ import print_function
import pickle
import os.path
from googleapiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def list_messages(service, user_id):
    try:
        results = service.users().messages().list(userId=user_id, 
        includeSpamTrash='true', maxResults=10).execute()
        messages = results.get('messages', [])
        return messages

    except errors.HttpError as error:
        print('An error occurred: %s' % error)


def get_sender(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

    else:
        header = message['payload']['headers']
        for values in header:
            if values['name'] == 'From':
                return values['value']

def main():
    service = get_service()
    user_id = 'me'    
    message_list = list_messages(service, user_id)
    senders = []
    for message in message_list:
        senders.append(get_sender(service, user_id, message['id']))

    print(senders)

if __name__ == "__main__":
    main()