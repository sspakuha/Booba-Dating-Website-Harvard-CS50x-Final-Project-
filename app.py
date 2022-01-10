from sqlalchemy import create_engine
from flask import Flask, render_template, redirect, request, flash, session, jsonify, make_response
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.utils import secure_filename
import random
import re
from os.path import join, exists
from os import remove
from tempfile import mkdtemp
from datetime import datetime, timedelta
from pytz import timezone
from helpers import login_required, allowed_file, getAvailableName, limitsearch, time, isonline


# Configure application
app = Flask(__name__)

# secret key generated via python -c 'import os; print(os.urandom(16))' :)
# Needed to keep users logged in after website is switched off.
app.secret_key = b"\xb2\xbe7=vyt\x98>\xdcW\x1c:\xab`\xf1|'8"


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = 'static/img/pictures'

# Custom filter
app.jinja_env.filters["time"] = time


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

engine = create_engine('sqlite:///dating.db')

# Auto updating templates
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route("/")
@login_required
def index():
  with engine.connect() as con:
    rs = con.execute("SELECT * FROM users WHERE id = ?;", session["user_id"])
    result=rs.fetchone()
    return redirect("/" +result["username"])


# Rendering user page (both current user and other people's pages)
@app.route("/<name>")
@login_required
def page(name=None):
  if name:
    with engine.connect() as con:
      rs = con.execute("SELECT * FROM users WHERE username = ?;", name).fetchone()

      auth = con.execute("SELECT * FROM users WHERE id = ?;", session["user_id"]).fetchone()

      # If <name> page is found:
      if rs:
        # Add current user as a visitor
        tabs = {}
        tabs["favorites"] = []
        tabs["visitors"] = []
        tabs["likes"] = []

        # If the page is not of current user:
        if not rs.id == auth.id:

          # Add/Update visitor
          live = datetime.now(timezone("Asia/Istanbul"))
          entry = con.execute("SELECT * FROM visitors WHERE user_id = ? AND visitor_id = ?;", rs.id, auth.id).fetchone()
          if entry:
            con.execute("UPDATE visitors SET time = ? WHERE user_id = ? AND visitor_id = ?;", live, rs.id, auth.id)
          else:
            con.execute("INSERT INTO visitors (user_id, visitor_id, time) VALUES (?, ?, ?);", rs.id, auth.id, live)

          tabs["visitors"] = None

        images = con.execute("SELECT * FROM photos WHERE user_id = ? ORDER BY id DESC;", rs.id)
        images = images.fetchall()

        avatar = con.execute("SELECT * FROM photos WHERE user_id = ? AND active = 1;", rs.id)
        avatar = avatar.fetchone()

        if not avatar:
          avatar = "static/img/pictures/defaultavatar.png"
        else:
          avatar = avatar.url

        location = con.execute("SELECT * FROM location WHERE user_id = ?;", rs.id)

        lookingfor = con.execute("SELECT * FROM lookin WHERE user_id = ?;", rs.id)
        lookingfor = lookingfor.fetchone()
        location = location.fetchone()

        if rs.id == auth.id:

          # Get current user visitors/likes/favorites/online/gift to render on the page
          visitors = con.execute("SELECT * FROM visitors WHERE user_id = ? ORDER BY time DESC LIMIT 10;", rs.id).fetchall()
          if visitors:
            for i in range(len(visitors)):
              temp = {}
              visids = con.execute("SELECT id, username FROM users WHERE id = ?;", visitors[i].visitor_id).fetchone()

              temp["username"] = visids.username;
              visimg = con.execute("SELECT url FROM photos WHERE user_id = ? AND active = 1;", visids.id).fetchone()
              if visimg:
                temp["url"] = visimg.url;
              else:
                temp["url"] = 'static/img/pictures/defaultavatar.png';
              temp["time"] = datetime.strptime(visitors[i].time[:26], "%Y-%m-%d %H:%M:%S.%f")
              tabs["visitors"].append(temp)
          else:
            tabs["visitors"] = None

          favorites = con.execute("SELECT * FROM favorites WHERE user_id = ?;", rs.id).fetchall()

          likes = con.execute("SELECT * FROM likes WHERE user_id = ? ORDER BY time DESC", rs.id).fetchall()

          if likes:
            for i in range(len(likes)):
              temp = {}

              likesids = con.execute("SELECT id, username FROM users WHERE id = ?;", likes[i].who_liked).fetchone()

              temp["username"] = likesids.username;

              likesimg = con.execute("SELECT url FROM photos WHERE user_id = ? AND active = 1;", likesids.id).fetchone()

              if likesimg:
                temp["url"] = likesimg.url;
              else:
                temp["url"] = 'static/img/pictures/defaultavatar.png';

              tabs["likes"].append(temp)

          if favorites:
            for i in range(len(favorites)):
              temp = {}

              favids = con.execute("SELECT id, username FROM users WHERE id = ?;", favorites[i].fav_id).fetchone()

              temp["username"] = favids.username;

              favimg = con.execute("SELECT url FROM photos WHERE user_id = ? AND active = 1;", favids.id).fetchone()

              if favimg:
                temp["url"] = favimg.url;
              else:
                temp["url"] = 'static/img/pictures/defaultavatar.png';

              tabs["favorites"].append(temp)
        else:
          tabs["favorites"] = con.execute("SELECT * FROM favorites WHERE user_id = ? AND fav_id = ?;", auth.id, rs.id).fetchone()

          tabs["likes"] = con.execute("SELECT * FROM likes WHERE user_id = ? AND who_liked = ?;", rs.id, auth.id).fetchone()

        # Check if user is allowed to open a gift
        gift = con.execute("SELECT * FROM gift WHERE user_id = ?;", session["user_id"])
        gift = gift.fetchone()

        if gift:
          lastgift = datetime(minute=gift.minutes, hour=gift.hours, day=gift.day, month=gift.month, year=gift.year)
          timenow = datetime.now(timezone("Asia/Istanbul"))
          finish = lastgift + timedelta(days=1)

          cmpnew = datetime(minute=timenow.minute, hour=timenow.hour, day=timenow.day, month=timenow.month, year=timenow.year)

          if finish >= cmpnew:
            gift = False
          else:
            gift = True
        else:
          gift = True

        online = isonline(rs.id)

        return render_template("profile.html", user=auth, page=rs, images=images, avatar=avatar, picamount=len(images), location=location, lookingfor=lookingfor, gift=gift, tabs=tabs, online=online)
      else:
        return render_template("404user.html", user=auth)


@app.route('/settings')
@login_required
def settings():
  with engine.connect() as con:
    auth = con.execute("SELECT * FROM users WHERE id = ?;", session["user_id"]).fetchone()
    location = con.execute("SELECT * FROM location WHERE user_id = ?;", auth.id).fetchone()
    lookingfor = con.execute("SELECT * FROM lookin WHERE user_id = ?;", auth.id).fetchone()

    return render_template('settings.html', user=auth, location=location, lookingfor=lookingfor)


@app.route("/updatepassword", methods=["POST"])
@login_required
def updatepassword():
  with engine.connect() as con:
    password = request.form.get("password")
    npassword = request.form.get("npassword")
    npasswordr = request.form.get("npasswordr")

    if not password or len(password) < 6 or len(password) > 25:
      flash("Wrong password", "rgba(115, 95, 95, 0.5)")
      return redirect("/settings")

    if not npassword or len(npassword) < 6 or len(npassword) > 25:
      flash("Password gotta be from 6 to 25 chars.", "rgba(115, 95, 95, 0.5)")
      return redirect("/settings")

    if npassword != npasswordr:
      flash("New passwords do not match.", "rgba(115, 95, 95, 0.5)")
      return redirect("/settings")

    auth = con.execute("SELECT * FROM users WHERE id = ?;", session["user_id"]).fetchone()

    if not check_password_hash(auth["hash"], password):
      flash("You've entered wrong account password.", "rgba(115, 95, 95, 0.5)")
      return redirect("/settings")

    con.execute("UPDATE users SET hash = ? WHERE id = ?;", generate_password_hash(npassword), session["user_id"])

    flash("You've changed your password.", "rgba(95, 115, 100, 0.5)")
    return redirect("/settings")


@app.route("/logout")
@login_required
def logout():
  session.clear()
  return redirect("/")


@app.route("/login", methods=['GET', 'POST'])
def login():
  if "user_id" in session:
    return redirect("/")

  if request.method == 'POST':

    if not request.form.get("username") or not request.form.get("password"):
      flash("INCORRECT INPUT")
      return render_template("login.html")

    with engine.connect() as con:
      result = con.execute("SELECT * FROM users WHERE username = ?;",
                       request.form.get("username")).fetchone()

      if not result or not check_password_hash(result["hash"], request.form.get("password")):
        flash("Wrong username/password.")
        return render_template("login.html")

      session["user_id"] = result["id"]
      session.permanent = True
      flash("You have successfully logged in.", "rgba(95, 115, 100, 0.5)")
      return redirect("/")
  return render_template("login.html")


@app.route("/registration", methods=['GET', 'POST'])
def reg():
    if "user_id" in session:
      return redirect("/")

    if request.method == 'POST':
      username = request.form.get("username")
      if not username or " " in username or len(username) < 6 or len(username) >= 24:
        flash("Try using username withous spaces, longer than 5 chars and shorter than 25 chars.")
        return redirect("/registration")

      email = request.form.get("email")
      if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$',
                         email) or not email or " " in email:
        flash("Not a valid email.")
        return redirect("/registration")

      sex = request.form.get("sex")
      if not sex or sex not in ["Female", "Male"]:
        flash("Wrong sex")
        return redirect("/registration")
      if sex == "Female":
        sex = 2
      else:
        sex = 1

      lookingfor = request.form.get("lookingfor")
      if not lookingfor or lookingfor not in ["Female", "Male"]:
        flash("Wrong looking for")
        return redirect("/registration")

      lookingfor = 1 if lookingfor == "Male" else 2
      password = request.form.get("password")
      if not password or len(password) < 6 or len(password) > 25:
        flash("Password gotta be from 6 to 25 chars long.")
        return redirect("/registration")

      password_repeat = request.form.get("password-repeat")
      if not password_repeat or len(password_repeat) < 6:
        flash("Password gotta be at least 6 chars.")
        return redirect("/registration")

      if password != password_repeat:
        flash("Password gotta be at least 6 chars.")
        redirect("/registration")

      age = request.form.get("age")
      if int(age) < 18:
        flash("Sorry, you gotta be at least 18 to proceed to website.")
        redirect("/registration")

      with engine.connect() as con:
        rs = con.execute("SELECT * FROM users WHERE username = ?;",
                         username).fetchone()
        if rs:
          flash("User with the same username already exists.")
          return redirect("/registration")

        rs = con.execute("SELECT * FROM users WHERE email = ?;",
                         email).fetchone()
        if rs:
          flash("Email was already registrated.")
          return redirect("/registration")

        rs = con.execute("INSERT INTO users (username, gender_id, age, email, hash) VALUES(?, ?, ?, ?, ?);", username, sex, age, email, generate_password_hash(password))
        con.execute("INSERT INTO lookin(user_id, gender_id) VALUES (?, ?);", rs.lastrowid, lookingfor)
        session["user_id"] = rs.lastrowid
        session.permanent = True

        flash("Welcome aboard! Registration was successfull.", "rgba(95, 115, 100, 0.5)")
        return redirect("/")
    return render_template("registration.html")


# Avatar uploading
@app.route("/avatar", methods=["POST"])
@login_required
def avatar():
  if 'avatar' not in request.files:
    flash("No file part.", "rgba(115, 95, 95, 0.5)")
    return redirect("/")

  file = request.files['avatar']

  if file.filename == '':
    flash("No selected file.", "rgba(115, 95, 95, 0.5)")
    return redirect("/")

  if file and allowed_file(file.filename):
    filename = secure_filename(file.filename)
    name = getAvailableName(filename, join(app.config['UPLOAD_FOLDER'], filename))
    path = join(app.config['UPLOAD_FOLDER'], name)
    file.save(path)
    with engine.connect() as con:
      con.execute("UPDATE photos SET active = 0 WHERE active = 1 AND user_id = ?;", session["user_id"])
      con.execute("INSERT INTO photos(url, user_id, active) VALUES (?,?,1);", path, session["user_id"])
    flash("Avatar uploaded successfully.", "rgba(95, 115, 100, 0.5)")
  else:
    flash("Wrong file format.", "rgba(115, 95, 95, 0.5)")

  return redirect("/")


# Picture uploading
@app.route("/addpicture", methods=["POST"])
@login_required
def addpicture():
  if 'picture' not in request.files:
    flash("No file part.", "rgba(115, 95, 95, 0.5)")
    return redirect("/")

  file = request.files['picture']

  if file.filename == '':
    flash("No selected file.", "rgba(115, 95, 95, 0.5)")
    return redirect("/")

  if file and allowed_file(file.filename):
    filename = secure_filename(file.filename)

    name = getAvailableName(filename, join(app.config['UPLOAD_FOLDER'], filename))

    path = join(app.config['UPLOAD_FOLDER'], name)
    file.save(path)
    with engine.connect() as con:
      con.execute("INSERT INTO photos(url, user_id) VALUES (?,?);", path, session["user_id"])
    flash("Picture uploaded successfully.", "rgba(95, 115, 100, 0.5)")
  else:
    flash("Wrong file format.", "rgba(115, 95, 95, 0.5)")

  return redirect("/")


# Rendering user images page
@app.route("/<name>/images")
@login_required
def images(name=None):
  with engine.connect() as con:
    rs = con.execute("SELECT * FROM users WHERE username = ?;", name).fetchone()
    auth = con.execute("SELECT * FROM users WHERE id = ?;", session["user_id"]).fetchone()

    if rs:
      images = con.execute("SELECT * FROM photos WHERE user_id = ? ORDER BY id DESC;", rs.id).fetchall()

      return render_template("images.html", user=auth, page=rs, images=images)
    else:
      return render_template("404user.html", user=auth)


# Deleting user image
@app.route("/deletepicture", methods=["POST"])
@login_required
def deletepicture():
  delete = request.form.get("picid")
  pagelogin = request.form.get("pagelogin")
  if not delete or not pagelogin:
    flash("Error deleting the file.", "rgba(115, 95, 95, 0.5)")
    return redirect("/"+pagelogin+"/images")

  with engine.connect() as con:
    rs = con.execute("SELECT * FROM photos WHERE id = ? AND user_id = ?;", delete, session["user_id"]).fetchone()
    if rs:
      if exists(rs.url):
        remove(rs.url)
      con.execute("DELETE FROM photos WHERE id = ? AND user_id = ?;", delete, session["user_id"])
      flash("Picture deleted successfully.", "rgba(95, 115, 100, 0.5)")
    else:
      flash("Error deleting the file.", "rgba(115, 95, 95, 0.5)")
  return redirect("/"+pagelogin+"/images")


# Setting user image as avatar
@app.route("/setavatar", methods=["POST"])
@login_required
def setavatar():
  avatar = request.form.get("picidavatar")
  pagelogin = request.form.get("pagelogin")

  if not avatar or not pagelogin:
    flash("Error chanhing the avatar.", "rgba(115, 95, 95, 0.5)")
    return redirect("/"+pagelogin+"/images")

  with engine.connect() as con:
      con.execute("UPDATE photos SET active = 0 WHERE active = 1 AND user_id = ?;", session["user_id"])

      con.execute("UPDATE photos SET active = 1 WHERE id = ? AND user_id = ?;", avatar, session["user_id"])

      flash("Avatar set successfully.", "rgba(95, 115, 100, 0.5)")
  return redirect("/"+pagelogin)


@app.route("/profiledata", methods=["POST"])
@login_required
def profiledata():
  desc = request.form.get("description")
  if not desc or desc.strip() == "":
    flash("Please use a valid text.", "rgba(115, 95, 95, 0.5)")
    return redirect("/")
  with engine.connect() as con:
    con.execute("UPDATE users SET about = ? WHERE id = ?;", desc, session["user_id"])
    flash("You've changed your profile data.", "rgba(95, 115, 100, 0.5)")
  return redirect("/")


@app.route("/updatedataleft", methods=["POST"])
@login_required
def updatedataleft():
  country = request.form.get("country")
  city = request.form.get("city")
  sex = request.form.get("sex")
  lookingfor = request.form.get("lookingfor")
  age = request.form.get("age")

  if not country or country.strip() == "" or len(country) > 25:
    flash("Please use a valid country name.", "rgba(115, 95, 95, 0.5)")
    return redirect("/")

  if not city or city.strip() == "" or len(city) > 25:
    flash("Please use a valid city name.", "rgba(115, 95, 95, 0.5)")
    return redirect("/")

  if not age or int(age) < 18 or int(age) > 123:
    flash("Only users older than 18 y.o. can proceed.", "rgba(115, 95, 95, 0.5)")
    return redirect("/")

  if not int(sex) in [1,2] or not int(lookingfor) in [1,2]:
    flash("Error.", "rgba(115, 95, 95, 0.5)")
    return redirect("/")

  with engine.connect() as con:
    con.execute("UPDATE users SET gender_id = ?, age = ? WHERE id = ?;", sex, age, session["user_id"])
    con.execute("UPDATE lookin SET gender_id = ? WHERE user_id = ?;", lookingfor, session["user_id"])

    rs = con.execute("SELECT * FROM location WHERE user_id = ?;", session["user_id"]).fetchone()
    if rs:
      con.execute("UPDATE location SET country = ?, city = ? WHERE user_id = ?;", country, city, session["user_id"])
    else:
      con.execute("INSERT INTO location (country, city, user_id) VALUES (?, ?, ?);", country, city, session["user_id"])

    flash("You've changed your profile data.", "rgba(95, 115, 100, 0.5)")
  return redirect("/")


@app.route("/getgift", methods=["POST", "GET"])
@login_required
def getgift():
  with engine.connect() as con:
    rs = con.execute("SELECT * FROM gift WHERE user_id = ?;", session["user_id"]).fetchone()
    if rs:
      lastgift = datetime(minute=rs.minutes, hour=rs.hours, day=rs.day, month=rs.month, year=rs.year)

      timenow = datetime.now(timezone("Asia/Istanbul"))
      finish = lastgift + timedelta(days=1)

      cmpnew = datetime(minute=timenow.minute, hour=timenow.hour, day=timenow.day, month=timenow.month, year=timenow.year)

      if finish >= cmpnew:
        res = finish - timedelta(hours=timenow.hour,  minutes=timenow.minute)
        response = make_response(
        jsonify(
          {
            "amount": -1,
            "minute": res.minute,
            "hour": res.hour,
            # "day": date.day,
            }
        ),
        # 401,
        )
        response.headers["Content-Type"] = "application/json"
        return response

  gift = int(random.random()*100)
  if gift > 97:
    gift = 1000
  elif gift >= 85:
    gift = 300
  elif gift >= 65:
    gift = 150
  elif gift >= 40:
    gift = 100
  else:
    gift = 50

  date = datetime.now(timezone("Asia/Istanbul"))
  with engine.connect() as con:
    con.execute("UPDATE users SET balance = (balance + ?) WHERE id = ?;", gift, session["user_id"])
    rs = con.execute("SELECT * FROM gift WHERE user_id = ?;", session["user_id"]).fetchone()
    if rs:
      con.execute("UPDATE gift SET minutes = ?, hours = ?, day = ?, month = ?, year = ?, amount = ? WHERE user_id = ?;", date.minute, date.hour, date.day, date.month, date.year, gift, session["user_id"])
    else:
      con.execute("INSERT INTO gift (user_id, minutes, hours, day, month, year, amount) VALUES (?, ?, ?, ?, ?, ?, ?);", session["user_id"], date.minute, date.hour, date.day, date.month, date.year, gift)

    response = make_response(
      jsonify(
        {
          "amount": gift,
          }
      ),
    )

  response.headers["Content-Type"] = "application/json"
  return response


@app.route("/checkgift")
@login_required
def checkgift():
  with engine.connect() as con:
    rs = con.execute("SELECT * FROM gift WHERE user_id = ?;", session["user_id"]).fetchone()
    if rs:
      lastgift = datetime(minute=rs.minutes, hour=rs.hours, day=rs.day, month=rs.month, year=rs.year)

      timenow = datetime.now(timezone("Asia/Istanbul"))
      finish = lastgift + timedelta(days=1)

      cmpnew = datetime(minute=timenow.minute, hour=timenow.hour, day=timenow.day, month=timenow.month, year=timenow.year)

      if finish >= cmpnew:
        res = finish - timedelta(hours=timenow.hour,  minutes=timenow.minute)
        response = make_response(
        jsonify(
          {
            "amount": -1,
            "minute": res.minute,
            "hour": res.hour,
            }
        ),
        )
        response.headers["Content-Type"] = "application/json"
        return response

  response = make_response(
    jsonify(
      {
        "amount": 0,
        "minute": 0,
        "hour": 0,
        }
    ),
  )
  response.headers["Content-Type"] = "application/json"
  return response

@app.route("/getsearch", methods=["POST"])
@login_required
def getsearch():
  settings = {}
  settings["lowerage"] = int(request.form.get("lowerage")) if request.form.get("lowerage") else None
  settings["upperage"] = int(request.form.get("upperage")) if request.form.get("upperage") else None
  settings["hasphoto"] = int(request.form.get("hasphoto")) if request.form.get("hasphoto") else None
  settings["country"] = request.form.get("country").strip() if request.form.get("country") else None
  settings["city"] = request.form.get("city").strip() if request.form.get("city") else None
  settings["gender"] = int(request.form.get("gender")) if request.form.get("gender") else None
  settings["query"] = request.form.get("query").strip() if request.form.get("query") else None
  settings['lastusername'] = request.form.get("lastusername").strip()
  result = limitsearch(settings, 10)



  for i in range(len(result)):
    result

  return jsonify(result)



@app.route("/search", methods=["GET"])
@login_required
def search():
  # Saving search settings
  settings = {}
  settings["lowerage"] = int(request.args.get("lowerage")) if request.args.get("lowerage") else None
  settings["upperage"] = int(request.args.get("upperage")) if request.args.get("upperage") else None
  settings["hasphoto"] = int(request.args.get("hasphoto")) if request.args.get("hasphoto") else None
  settings["country"] = request.args.get("country").strip() if request.args.get("country") else None
  settings["city"] = request.args.get("city").strip() if request.args.get("city") else None
  settings["gender"] = int(request.args.get("gender")) if request.args.get("gender") else None
  settings["query"] = request.args.get("query").strip() if request.args.get("query") else None
  settings['lastusername'] = False

  with engine.connect() as con:
    # Getting current user
    auth = con.execute("SELECT * FROM users WHERE id = ?;", session["user_id"])
    auth = auth.fetchone()
    # Starting to proccess settings
    # If not lowerage or upperage - user hasn't been searching for anything yet.
    if not settings["lowerage"] or not settings["upperage"]:
      return render_template("search.html", user=auth, searching=False, setting=settings)
    else:
      result = limitsearch(settings, 10)
      if result:
        return render_template("search.html", searching=True, result=result["rs"], user=auth, images=result["images"], length=result["length"], locations=result["locations"], setting=settings, favorites = result["favorites"])
      else:
        return render_template("search.html", searching=True, result=None, user=auth, images=None, length=0, locations=None, setting=settings)


@app.route("/messages", methods=["GET", "POST"])
@login_required
def messages():
  with engine.connect() as con:
    auth = con.execute("SELECT * FROM users WHERE id = ?;", session["user_id"])
    auth = auth.fetchone()

    if request.method == 'POST':
      username = request.form.get("username")
      if not username or username.strip == "":
        flash("Error sending message. Wrong username.", "rgba(115, 95, 95, 0.5)")

      recipient = con.execute("SELECT * FROM users WHERE username = ?;", username).fetchone()

      if not recipient:
        flash("There is no account with username {}.".format(username), "rgba(115, 95, 95, 0.5)")
        return redirect("/")

      newmessage = {}
      newconv = con.execute("SELECT * FROM conversations WHERE to_uid = ? AND from_uid = ? OR to_uid = ? AND from_uid = ?;", session["user_id"], recipient.id, recipient.id, session["user_id"]).fetchone()
      if newconv:
        con.execute("UPDATE messages SET status = 1 WHERE conversation_id = ? AND from_uid = ?;", newconv.id, recipient.id)

        newmessage["messages"] = con.execute("SELECT * FROM messages WHERE id IN (SELECT id FROM messages WHERE conversation_id = ? ORDER BY id DESC LIMIT 40) ORDER BY id;", newconv.id).fetchall()

        lastmessage = con.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY (time) DESC LIMIT 1;", newconv.id).fetchone()
      else:
        lastmessage = None

      newmessage["username"] = recipient.username

      authpic = con.execute("SELECT * FROM photos WHERE user_id = ? AND active = 1;", auth.id).fetchone()

      if not authpic:
        authpic = 'static/img/pictures/defaultavatar.png'
      else:
        authpic = authpic.url

      userpic = con.execute("SELECT * FROM photos WHERE user_id = ? AND active = 1;", recipient.id).fetchone()

      if not userpic:
        userpic = 'static/img/pictures/defaultavatar.png'
      else:
        userpic = userpic.url

      newmessage["id"] = recipient.id
      newmessage["authpic"] = authpic
      newmessage["userpic"] = userpic
      newmessage["userlogin"] = recipient.username
      newmessage["lastmsg"] = lastmessage
    else:
      newmessage = False

    # GET RECEPIENTS GROUP BY
    conversations = con.execute("SELECT * FROM conversations WHERE from_uid = ? OR to_uid = ? ORDER BY time DESC;", session["user_id"], session["user_id"]).fetchall()
    if conversations:
      dialogs = []
      # for dialog in conversations:
      for i in range(len(conversations)):
        messages = con.execute("SELECT * FROM messages WHERE conversation_id = ?;", conversations[i].id).fetchall()

        partnerid = conversations[i].from_uid if not conversations[i].from_uid == session["user_id"] else conversations[i].to_uid

        username = con.execute("SELECT username FROM users WHERE id = ?", partnerid).fetchone()

        lastmessage = con.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY (time) DESC LIMIT 1;", conversations[i].id).fetchone()

        photo = con.execute("SELECT url FROM photos WHERE user_id = ? AND active = 1;", partnerid).fetchone()

        if not photo:
          photo = 'static/img/pictures/defaultavatar.png'

        temp = {}

        if "url" in photo:
          temp["photo"] = photo.url
        else:
          temp["photo"] = photo

        temp["username"] = username.username
        temp["messages"] = messages
        temp["lastmsg"] = lastmessage
        dialogs.append(temp)
    else:
      dialogs=False
  return render_template("messages.html", user=auth, conversations=dialogs, recipient=newmessage)


@app.route("/getconversations", methods=["POST"])
@login_required
def getconversations():
  with engine.connect() as con:
    conversations = con.execute("SELECT * FROM conversations WHERE from_uid = ? OR to_uid = ? ORDER BY (time) DESC;", session["user_id"], session["user_id"]).fetchall()
    if conversations:
      dialogs = []
      for i in range(len(conversations)):
        partnerid = conversations[i].from_uid if not conversations[i].from_uid == session["user_id"] else conversations[i].to_uid

        username = con.execute("SELECT username FROM users WHERE id = ?", partnerid).fetchone()

        lastmessage = con.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY (time) DESC LIMIT 1;", conversations[i].id).fetchone()

        photo = con.execute("SELECT url FROM photos WHERE user_id = ? AND active = 1;", partnerid).fetchone()

        if not photo:
          photo = 'static/img/pictures/defaultavatar.png'

        temp = {}

        if "url" in photo:
          temp["photo"] = photo.url
        else:
          temp["photo"] = photo

        temp["username"] = username.username
        temp["userid"] = partnerid
        temp["status"] = lastmessage.status
        temp["lastmsg"] = lastmessage.content[:22]
        temp["sentby"] = lastmessage.from_uid
        dialogs.append(temp)
      return jsonify(dialogs)
    else:
      return jsonify([0])


@app.route("/getmessages", methods=["POST"])
@login_required
def getmessages():
  username = request.form.get("username")
  lastmsgid = request.form.get("lastmsgid")

  if not username or username.strip() == "":
    return jsonify([-1])

  with engine.connect() as con:
    user = con.execute("SELECT * FROM users WHERE username = ?;", username).fetchone()
    auth = con.execute("SELECT * FROM users WHERE id = ?;", session["user_id"]).fetchone()

    convid = con.execute("SELECT * FROM conversations WHERE to_uid = ? AND from_uid = ? OR to_uid = ? AND from_uid = ?;", session["user_id"], user.id, user.id, session["user_id"]).fetchone()

    if convid:
      con.execute("UPDATE messages SET status = 1 WHERE conversation_id = ? AND from_uid = ?;", convid.id, user.id)
    else:
      return jsonify([0])

    if lastmsgid and not lastmsgid.strip() == "":
      rs = con.execute("SELECT * FROM messages WHERE id IN (SELECT id FROM messages WHERE conversation_id = ? AND id < ? ORDER BY id DESC LIMIT 40) ORDER BY id;", convid.id, lastmsgid).fetchall()
    else:
      rs = con.execute("SELECT * FROM messages WHERE id IN (SELECT id FROM messages WHERE conversation_id = ? ORDER BY id DESC LIMIT 40) ORDER BY id;", convid.id).fetchall()

    fres = []
    for res in rs:
      temp = {}
      temp["content"] = res.content
      temp["status"] = res.status
      temp["time"] = res.time[:16]
      temp["author"] = user.username if res.from_uid == user.id else auth.username
      temp["id"] = res.id

      photo = con.execute("SELECT url FROM photos WHERE user_id = ? AND active = 1;", res.from_uid).fetchone()

      if not photo:
        photo = 'static/img/pictures/defaultavatar.png'

      if "url" in photo:
        temp["authorimg"] = photo.url
      else:
        temp["authorimg"] = photo
      fres.append(temp)

    if rs:
      return jsonify(fres)
    else:
      return jsonify([0])


@app.route("/sendmessage", methods=["POST"])
@login_required
def sendmessage():
  username = request.form.get("username")
  content = request.form.get("content")
  if not username or username.strip() == "":
    return "Bad"
  if not content or content.strip() == "":
    return "Bad"

  with engine.connect() as con:
    # Get conversant id
    user = con.execute("SELECT * FROM users WHERE username = ?;", username).fetchone()
    # Check if dialog already exists
    dialog = con.execute("SELECT * FROM conversations WHERE from_uid = ? AND to_uid = ? OR from_uid = ? AND to_uid = ?;", user.id, session["user_id"], session["user_id"], user.id).fetchone()

    id = 0;
    # If not, create one.
    if not dialog:
      rs = con.execute("INSERT INTO conversations (from_uid, to_uid, time) VALUES (?,?,?)",session["user_id"], user.id, datetime.now(timezone("Asia/Istanbul")))
      id = rs.lastrowid
    else:
      # Insert sent time
      con.execute("UPDATE conversations SET time = ? WHERE from_uid = ? AND to_uid = ? OR from_uid = ? AND to_uid = ?;", datetime.now(timezone("Asia/Istanbul")), user.id, session["user_id"], session["user_id"], user.id )
      id = dialog.id

    # Insert message
    con.execute("INSERT INTO messages (from_uid, to_uid, content, time, conversation_id) VALUES (?, ?, ?, ?, ?);", session["user_id"], user.id, content, datetime.now(timezone("Asia/Istanbul")), id)
    return "Good"


@app.route("/favorite", methods=["POST"])
@login_required
def favorite():
  username = request.form.get("username")
  with engine.connect() as con:
    rs = con.execute("SELECT * FROM users WHERE username = ?;", username).fetchone()
    if rs:
      isfav = con.execute("SELECT * FROM favorites WHERE user_id = ? AND fav_id = ?;", session["user_id"], rs.id).fetchone()
      if isfav:
        con.execute("DELETE FROM favorites WHERE user_id = ? AND fav_id = ?;", session["user_id"], rs.id)
        text = '<i class="fas fa-star"></i> Favorite'
      else:
        con.execute("INSERT INTO favorites (user_id, fav_id) VALUES (?, ?);", session["user_id"], rs.id)
        text = '<i class="far fa-star"></i> Unfavorite'

    else:
      text = -1

    response = make_response(
      jsonify(
        {
          "text": text,
          }
      ),
      )
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/like", methods=["POST"])
@login_required
def like():
  username = request.form.get("username")

  with engine.connect() as con:
    rs = con.execute("SELECT * FROM users WHERE username = ?;", username).fetchone()
    if rs:
      islike = con.execute("SELECT * FROM likes WHERE user_id = ? AND who_liked = ?;", rs.id, session["user_id"]).fetchone()
      if islike:
        con.execute("DELETE FROM likes WHERE user_id = ? AND who_liked = ?;", rs.id, session["user_id"])
        text = '<i class="fas fa-heart"></i> Like'
      else:
        # Payment
        userbalance = con.execute("SELECT balance FROM users WHERE id = ?", session["user_id"]).fetchone()

        if userbalance.balance >= 75:
          con.execute("UPDATE users SET balance = (balance - 75) WHERE id = ?;", session["user_id"])
          # Updating db
          con.execute("INSERT INTO likes (time, user_id, who_liked) VALUES (?, ?, ?);", datetime.now(timezone("Asia/Istanbul")), rs.id, session["user_id"])
          text = '<i class="far fa-heart"></i> Unlike'
        else:
          text = -1

    response = make_response(
      jsonify(
        {
          "text": text,
          }
      ),
      )
    response.headers["Content-Type"] = "application/json"
    return response


@app.route("/connection", methods=["POST"])
@login_required
def connection():
  with engine.connect() as con:
    lastonline = con.execute("SELECT * FROM online WHERE user_id = ?;", session["user_id"]).fetchone()
    if lastonline:
      con.execute("UPDATE online SET time = ? WHERE user_id = ?;", datetime.now(timezone("Asia/Istanbul")), session["user_id"])
    else:
      con.execute("INSERT INTO online (time, user_id) VALUES (?, ?);", datetime.now(timezone("Asia/Istanbul")), session["user_id"])

  return "Good"


@app.route("/checkonline", methods=["POST"])
@login_required
def checkonline():
  username = request.form.get("username")
  with engine.connect() as con:
    userid = con.execute("SELECT * FROM users WHERE username = ?;", username).fetchone()
    if not userid:
      online = 0
    else:
      online = isonline(userid.id)
    if not online == 0 and not online == 1 :
      temp = {
        'hour': online.hour,
        'minute': online.minute,
        'month': online.month,
        'day': online.day,
      }
      return jsonify(temp)
    return jsonify(online)


@app.route("/checkallonlines", methods=["POST"])
@login_required
def checkallonlines():
  with engine.connect() as con:
    # Get all conversations
    conversations = con.execute("SELECT * FROM conversations WHERE from_uid = ? OR to_uid = ? ORDER BY (time) DESC;", session["user_id"], session["user_id"]).fetchall()
    # For each coversation get online
    if conversations:
      temp = {}
      for i in range(len(conversations)):
        partnerid = conversations[i].from_uid if not conversations[i].from_uid == session["user_id"] else conversations[i].to_uid
        username = con.execute("SELECT username FROM users WHERE id = ?;", partnerid).fetchone()
        online = isonline(partnerid)
        if not online == 0 and not online == 1 :
          dictt = {
            'hour': online.hour,
            'minute': online.minute,
            'month': online.month,
            'day': online.day,
          }
          temp[username.username] = dictt
        else:
          temp[username.username] = online
    else:
      return jsonify([-1]);

    return jsonify(temp)


def errorhandler(e):
  """Handle error"""
  if not isinstance(e, HTTPException):
    e = InternalServerError()
  with engine.connect() as con:
    if "user_id" in session:
      auth = con.execute("SELECT * FROM users WHERE id = ?;", session["user_id"]).fetchone()
      return render_template("apology.html", message=e.name, code=e.code, user=auth)
    else:
      return redirect('/')


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

app.run(host='0.0.0.0', port=8080)
