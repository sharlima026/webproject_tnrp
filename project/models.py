from project import db
from flask_login import UserMixin
from datetime import datetime



from project import login_manager
 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


import datetime


class Tweet(db.Model):
    __tablename__ = 'filteredtweets'

    tweet_id = db.Column(db.Integer, primary_key=True)
    user_name= db.Column(db.String,nullable=False)
    pro_pic=db.Column(db.String)
    media= db.Column(db.String, default="noMedia")#uploaded media 
    inTextAUrl=db.Column(db.String, default="noUrl")
    tweetText = db.Column(db.String, nullable=False) 
    date_posted = db.Column(db.DateTime)

  
    def __init__(self,tweetId,userName,proPic, text, uploadMedia,url):
        self.tweet_id = tweetId
        self.user_name = userName
        self.pro_pic = proPic
        self.tweetText=text
        self.media=uploadMedia
        self.inTextAUrl = url
        
  

    @classmethod
    def delta_time(cls, tweet_posted):
        now = datetime.datetime.now()
        td = now - tweet_posted
        days = td.days
        hours = td.seconds//3600
        minutes = (td.seconds//60)%60
        if days > 0:
            return tweet_posted.strftime("%d %B, %Y")
        elif hours > 0:
            return str(hours) + 'h'
        elif minutes > 0:
            return str(minutes) + 'm'
        else:
            return 'few seconds ago'



class User(db.Model,UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
 
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default='user')
    image_file = db.Column(db.String(20), nullable=False, default='user.png')
    date_joined = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)


    def __init__(self, name, email, password, role):
        self.username = name
        self.email = email
        self.password = password
        self.role = role

    def __repr__(self):
        return '<User {0}>'.format(self.name)
 
 
    def toDict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'role': self.role
        }

 