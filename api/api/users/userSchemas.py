from config.db import db
from bson import ObjectId

def userEntity(user) -> dict:

    if user is None:
        return {
            'id': 'unknown',
            'username': 'unknown',
            'email': 'unknown',
            'role': 'user'
        }
    
    out = {
        'id': str(user['_id']),
        'type': user['type'],
        'username': user['username'] ,
        'email': user['email'] ,
        'role': user['role']
    }

    if 'expires' in user:
        out['expires'] = user['expires']

    return out


def usersEntity(users) -> list:
    return [userEntity(user) for user in users]

def resolveUser(user) -> dict:

    if isinstance(user, str):
        
        userRecord = db.users.find_one({"_id": ObjectId(user)})
        if userRecord is None:
            return {
                'id': 'unknown',
                'username': 'unknown',
                'email': 'unknown'
            }
        else: 
            return {
                'id': str(userRecord['_id']),
                'username': userRecord['username'],
                'email': userRecord['email']
            }
    elif isinstance(user, dict):

        if 'id' in user:
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email']
            }
    else: 

        return user.model_dump(exclude_none=True, exclude=['password','role'])
