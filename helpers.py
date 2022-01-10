from flask import redirect, session
from functools import wraps
from os.path import exists
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from pytz import timezone

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

engine = create_engine('sqlite:///dating.db')


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/registration")
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
  return '.' in filename and \
         filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def getAvailableName(name, path):
  if exists(path):
    path = path[:-len(name)]
    filename = name.split(".")
    fmt = filename[1]
    filename = filename[0]
    i = 0
    while True:
      npa = path + filename + f"{i}" + "." + fmt
      # print(npa)
      if exists(npa):
        i+=1
        continue
      else:
        res = filename + f"{i}" + "." + fmt
        return res
  else:
      return name


def limitsearch(settings, limit=10):
    with engine.connect() as con:
      rs=con.execute("SELECT * FROM users WHERE age >= ? AND age <= ?", settings["lowerage"], settings["upperage"])

      rs = rs.fetchall()
      stepids = []
      if rs:
        for i in range(len(rs)):
          stepids.append(rs[i].id)


      if settings["query"] and not settings["query"].strip() == "":
        if stepids:
          if len(stepids) > 1:
            query = "SELECT * FROM users WHERE username LIKE ? AND id IN {};".format(tuple(stepids))
          else:
            query = "SELECT * FROM users WHERE username LIKE ? AND id = {};".format(stepids[0])

          rs = con.execute(query, "%" + settings["query"] + "%")
          rs = rs.fetchall()
          stepids = []
          if rs:
            for i in range(len(rs)):
              stepids.append(rs[i].id)


      if settings["gender"] and not int(settings["gender"]) == 0:
        if stepids:
          if len(stepids) > 1:
            query = "SELECT * FROM users WHERE gender_id = ? AND id IN {};".format(tuple(stepids))
          else:
            query = "SELECT * FROM users WHERE gender_id = ? AND id = {};".format(stepids[0])

          rs = con.execute(query, int(settings["gender"]))
          rs = rs.fetchall()
          stepids = []
          if rs:
            for i in range(len(rs)):
              stepids.append(rs[i].id)


      if settings["country"]:
        if stepids:
          if len(stepids) > 1:
            query = "SELECT * FROM location WHERE user_id IN {} AND country LIKE ?;".format(tuple(stepids))
          else:
            query = "SELECT * FROM location WHERE user_id = {} AND country LIKE ?;".format(stepids[0])
          rs = con.execute(query, "%" + settings["country"] + "%")
          rs = rs.fetchall()
          stepids = []
          if rs:
            for i in range(len(rs)):
              stepids.append(rs[i].user_id)


      if settings["city"]:
        if stepids:
          if len(stepids) > 1:
            query = "SELECT * FROM location WHERE user_id IN {} AND city LIKE ?;".format(tuple(stepids))
          else:
            query = "SELECT * FROM location WHERE user_id = {} AND city LIKE ?;".format(stepids[0])

          rs=con.execute(query, "%" + settings["city"] + "%")
          rs = rs.fetchall()
          stepids = []
          if rs:
            for i in range(len(rs)):
              stepids.append(rs[i].user_id)


      if settings["hasphoto"]:
        if stepids:
          if len(stepids) > 1:
            query = "SELECT * FROM photos WHERE user_id IN {} AND active = 1;".format(tuple(stepids))
          else:
            query = "SELECT * FROM photos WHERE user_id = {} AND active = 1;".format(stepids[0])

          rs=con.execute(query)
          rs = rs.fetchall()
          stepids = []
          if rs:
            for i in range(len(rs)):
              stepids.append(rs[i].user_id)

      images = []
      locations = []

      if stepids:
        if len(stepids) > 1:
          if limit == -1:
            query = "SELECT * FROM users WHERE id IN {} ORDER BY id DESC;".format(tuple(stepids))
          else:
            if settings['lastusername']:
              # // get id from username
              lastuserid = con.execute("SELECT id FROM users WHERE username = ?;", settings['lastusername']).fetchone()

              query = "SELECT * FROM users WHERE id IN {} AND id < {} ORDER BY id DESC LIMIT {};".format(tuple(stepids), lastuserid.id, limit)
            else:
              query = "SELECT * FROM users WHERE id IN {} ORDER BY id DESC LIMIT {};".format(tuple(stepids), limit)
        else:
          query = "SELECT * FROM users WHERE id = {};".format(stepids[0])

        rs=con.execute(query)
        rs=rs.fetchall()

        for i in range(len(rs)):
          image = con.execute("SELECT * FROM photos WHERE user_id = ? AND active = 1;", rs[i].id)
          location = con.execute("SELECT * FROM location WHERE user_id = ?", rs[i].id)

          image = image.fetchone()
          location = location.fetchone()

          if image:
            images.append(image.url)
          else:
            images.append("static/img/pictures/defaultavatar.png")

          if location:
            locations.append(location.country)
          else:
            locations.append("Unset")

        # Get favorite ids
        resfavs = con.execute("SELECT fav_id FROM favorites WHERE user_id = ?;", session.get("user_id")).fetchall()

        favs = []
        for res in resfavs:
          favs.append(res.fav_id)

        if rs:
          length=len(rs)
        else:
          length=0

        result = {}
        result["locations"] = locations
        result["images"] = images
        result["length"] = length

        if settings['lastusername']:
          result["rs"] = asdict(rs)
        else:
          result["rs"] = rs
        result["favorites"] = favs

        return result


def time(value):
    return f"{value:02}"


def asdict(self):
  new = []
  for i in range(len(self)):
    new.append({'username': self[i].username, 'age': self[i].age, 'gender_id': self[i].gender_id, 'id': self[i].id})
  return new;


def isonline(userid):
  with engine.connect() as con:
    lastonline = con.execute("SELECT * FROM online WHERE user_id = ?;", userid).fetchone()

    if not lastonline:
      return 0;

    previousTime = datetime.strptime(lastonline.time[0:26], "%Y-%m-%d %H:%M:%S.%f")
    willBeOffline = previousTime + timedelta(seconds=10)

    timenow = datetime.now(timezone("Asia/Istanbul"))
    nowTime = datetime(second=timenow.second, minute=timenow.minute, hour=timenow.hour, day=timenow.day, month=timenow.month, year=timenow.year)

    if willBeOffline > nowTime:
      return 1
    else:
      return previousTime
