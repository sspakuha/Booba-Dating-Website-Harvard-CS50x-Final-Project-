# Booba Dating Social Network
#### Video Demo:  https://youtu.be/WQcsW8mnZSQ
#### Description:
Booba is a fully-adaptive social dating website where you can meet people, upload images, chat, track your page visitors and send likes.
Every 24 hours user can receive a gift on his page in the form of a random number of coins (from 50 to 1000), which can later be used to send likes (like cost is 75 coins). The user's starting balance is 100 coins.

There are 5 possible gift amounts:
- 1000 coins - 3%
- 300 coins - 12%
- 150 coins - 20%
- 100 coins - 25%
- 50  coins - 40%

Additional features: adding users to bookmarks, search for users by criteria, displaying user activity (whether the user is online or when was the last time he was online).

Messages on the site are automatically loaded on receiving by AJAX.
Searchbar up in the title of message window sorts the dialogs via JS (only on the user side)
When user opens dialog AJAX gets 40 messages, and each time user gets the top of the dialog window (scrolls all the messages) it's loading 40 messages more.


Every search result returns up to 10 users. If you want to load more simply click on "load more" button which is located below the last user in result.
Note: ***12 fake users are pre-registered on the website for testing.***

**Stack**:
Python, SQLite, HTML, CSS(written with SCSS Preprocessor), JavaScript(including jQuery and Vue libraries).

#### Description of the project content
1. `app.py` - generic application entry point which is responsible for displaying webpages to user
2. `helpers.py` - some addictional functions to app.py (user login requiruing decorator function, getting available names for image files uploaded by users, getting users online/last online, function that searches for users by given criterias)
3. `dating.db` - main website sqlite3 database
4. `static/css/` - folder which contains all the CSS files (both normal and minified)
5. `static/js/` - folder which contains all the JavaScript files
6. `static/img/` - folder which contains all the images from the website
   - `static/img/pictures/` - folder which is used to save in users upload images
7. `static/webfonts/` - folder with iconic fonts
8. `templates/` - folder with html templates


#### Possible improvements
- Email notifications on registration/news.
- Create an ability for users to delete page and messages.
- Notification popup on receiving message.

#### How to use
To run the web application use these commands:

```
$ export FLASK_APP=app.py
$ flask run
```

#### Requirements
- python 3
- sqlalchemy
- flask
- werkzeug.security
- werkzeug.exceptions
- werkzeug.utils
- random
- re
- tempfile
- datetime
- pytz
- functools
