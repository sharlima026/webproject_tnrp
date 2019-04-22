import tweepy
from flask import Flask,request, render_template, flash, url_for, redirect
import json
from project.models import Tweet,User
from project import app,host,api,db
from project.forms import RegForm,LoginForm, UpdateAccountForm
from project import twitter_cred
from project import bcrypt
from flask_login import login_user, current_user,logout_user,login_required
from datetime import date
from sqlalchemy import extract  
import pygal                                                        
from pygal.style import Style
 
from datetime import datetime
from email.utils import parsedate_tz, mktime_tz


 

custom_style = Style(
  background='transparent',
  plot_background='transparent',
  foreground='#ffff',
  foreground_strong='#fff',
  foreground_subtle='#fffa',
  opacity='.6',
  opacity_hover='.9',
  transition='400ms ease-in',
  value_colors = '#fff'
#   colors=('#E853A0', '#E8537A', '#E95355', '#E87653', '#E89B53'))
)



@app.before_first_request
def setup():

   db.create_all()
   db.session.commit()

   User.query.filter(User.username == "Admin").delete()
   Admin_pw = bcrypt.generate_password_hash("password").decode('utf-8')
   admin = User( "Admin","admin@tnrp.com",Admin_pw, "Admin")
   admin.id=1
   db.session.add(admin)
 
   db.session.commit()

   logout_user()


def tweetLoader(terms):
   for status in tweepy.Cursor(api.search,q=terms,count=1000,lang="en",include_entities="True").items():
               tweet = Tweet.query.filter_by(tweet_id = status.id).first()
               if tweet:
                  username = str(status.user.screen_name)
                  statid = str(status.id)
                  
                  print("tweet exists already")
               else:

                  Urls = status.entities.get('urls',[])
                  media = status.entities.get('media', [])  
                  newTweet=Tweet(status.id,status.user.screen_name,status.user.profile_image_url_https,status.text,"NoMedia","NoUrl")

                  if(len(Urls) > 0):
                     newTweet.inTextAUrl=str(Urls[0]['expanded_url'])
                  if(len(media) > 0):
                     newTweet.media= str(media[0]['media_url_https'])

                  
                  datestring = status.created_at
                  newTweet.date_posted=datestring
                  db.session.add(newTweet)
                  db.session.commit()


                  



@app.route("/")
@app.route("/home")
def home():

   if current_user.is_authenticated:
      tweetLoader("trinidad is not a real place -filter:retweets")
      tweetLoader("#TrinidadIsNotARealPlace -filter:retweets")
      TweetCharts()
      page = request.args.get('page',1,type=int)
      records = Tweet.query.order_by(Tweet.date_posted.desc()).paginate(page=page,per_page=6)
      return render_template("feed.html",Tweets=records)
   else:
      return render_template("app.html",host=host)




@app.route("/login", methods=['GET', 'POST'])
def login():
   if current_user.is_authenticated:
         return redirect(url_for('home'))
   else:
      form = LoginForm()
      if form.validate_on_submit():
         user = User.query.filter_by(email = form.email.data).first()
         if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect (next_page) if next_page else redirect(url_for('home'))
         else:     
            flash('Login Unsuccessful. Please check username and password', 'danger')
      return render_template('login.html', title='Login', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
   if current_user.is_authenticated:
      return redirect(url_for('home'))
   else:
      form = RegForm()
      if form.validate_on_submit():
         hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
         u = User( form.username.data, form.email.data,hashed_pw, "user")
        
         db.session.add(u)
         db.session.commit()
 
         msgstr = 'Account created for '+form.username.data+'!'
        #print(u.username)
         flash(msgstr, 'success')
         return redirect(url_for('login'))
   return render_template('reg.html', title='Register', form=form)


@app.route("/logout")
def logout():
   logout_user()
   return redirect(url_for('home'))


@app.route("/analytics")
@login_required
def analytics():

   if current_user.role =="Admin":
      records = User.query.all()
      image_file = url_for('static', filename='propics/' + current_user.image_file)
      chartData= UserCharts()
      tweetchart=TweetCharts()
      return render_template('analytics.html', tweetData=tweetchart, chartdata=chartData, Users=records,title='analytics',image_file=image_file)
   else:
      return redirect(url_for('home'))

   
def UserCharts():
 
   users = [None,None,None,None,None,None,None,None,None,None,None,None]
   for x in range(12):
      num=User.query.filter(extract('month', User.date_joined)==x+1).count()
      users[x]=num   
   line_chart = pygal.Bar(show_minor_y_labels=False,show_legend=False,  style=custom_style)
   line_chart.x_labels = 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug','Sep', 'Oct', 'Nov', 'Dec'

   line_chart.title = 'New Users 2019'
   line_chart.add('users joined',users)
   graphdata = line_chart.render_data_uri()
   return graphdata

def TweetCharts():
 
   tweets = [None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None]
   for x in range(24):
      num=Tweet.query.filter(extract('hour', Tweet.date_posted)==x).count()
      tweets[x]=num
   radar_chart = pygal.Radar(show_legend=False, show_minor_y_labels=False, fill=True,  style=custom_style)
   radar_chart.title = 'Post Time'
   radar_chart.x_labels = range(0,24)
   radar_chart.render_data_uri()


   radar_chart.add('Tweet By Hour',tweets)
   graphdata = radar_chart.render_data_uri()
   return graphdata

 
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.firstname=form.fname.data
        current_user.lastname = form.lname.data

        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.fname.data = current_user.firstname
        form.lname.data = current_user.lastname

        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='propics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)
 