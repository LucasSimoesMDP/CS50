# WordleCup
OLD VERSION - SQL MANAGED WITH SQLite3 

#### Description:

When i started this final proyect required by cs50, my idea was to adapt the Wordle Game combined into the football world.

Football arouses great passions all over the world, and for those of us who love this sport, the FIFA World Cup is one of the most exciting and expecting events of the year. The whole planet comes together to enjoy a competition full of emotions. WordleCup is a tribute to remember this ephemeral moment of joy that crosses the feeling of fooball fans every four years and lasts only for a month.

WordleCup is a a web-based game using JavaScript, Python, SQL, AJAX and JINJA2, created under the knowledge taught by the cs50 teachers in each lecture since the beginning of the course, and added to autonomous learining, with internet forums and YouTube videos.

The main idea of the game is similar to the Wordle one, the user has ten chances to guess the footballer hiding behind the silhouette. In each attempt, the user can see if the player they chose shares any characteristics with the mysterious player. After completing the 10 opportunities or correctly guessing the player, the user will have to wait until 3pm UTC to play again.

In these following paragraphs, all the folders/files that are inside the project will be explained in detail.

To begin with, inside the 'static' folder you can find:

    -players_faces_ALL folder: Inside this folder you can find all the players images, along with their silhouettes. The number of the images matches their ID value within the database. You can see that the name of each image differs, in addition to its number, in two parameters: -n and -f. This is because -n is the silhouette and -f is the image of the player.

    -logo.svg: Website's logo created in Photoshop with the Qatar 2022 World Cup's font.

    -noshow.png: Image that can be found inside the 'how to play' button.

    -styles.css: Stylesheet where i edited some of the Bootstrap features like the navbar. I've also added my own heading tags.

    -whoami.png: 'Who am i?' text showed when 'Use Silhouette' button is pressed.

Inside the 'templates' folder you will find all those .html files that are rendered when the website's server is active. In the following paragraphs i will explain every file with details.

    -layout.html: The main template, all the other templates extend this particular file. At the top of the code, inside the head tag there are links/scripts required by Bootstrap and AJAX for its internal functionalities.
    After that, we can find the body with the navbar and all the buttons. There are some buttons that will always be there for the user to interact with (like the HOW TO PLAY button) and other buttons that will appear only if the user has/hasn't logged in(Using JINJA2). I've also implemented a plugin from Bootstrap called 'modal' inside the 'HOW TO PLAY' and 'STATS' buttons to show the user a clean interactive popup with its corresponding information. 'REGISTER' and 'LOGIN' button will send user to their respectives .html files. At the bottom of the code, the script tag has a function called show_image_example() with a simple code that shows an image when user press a button inside the modal.

    -register.html: Basically this template works as a form with three empty fields and a confirmation button. I've also added get_flashed_messages(), a function that extracts flash messages from the session (Flask feature)

    -login.html: The template is almost identical as the register.html one, with the get_flashed_messages() function that gives feedback to the user when entering empty fields or incorrect password/username.

    -index.html: Game's first template. It contains an input field where user types the name of a player and a list with 7 names that will appear below(the way it works will be explained in the end of the paragraph). After the input tag, there is the table that will be completed by the user choice's information, and the 'Show Silhouette' button which activates a modal with the mistery player's shadow/silhouette. Now, onto the script part: First, i receive a variable called answer, with the misterious player and his information. In line 64, i create an image inside the 'Show silhouette' modal, fetching inside the folder with all the images in order to look for the one that matches the mistery player's id.
    The userChoice() function receives the 'guess' variable (the user choice's id), and sends an AJAX request to the server with the information in a json format.
    Debounce() is a function which implements a technique to send requests only after the user has stopped typing, it receives 'callback' variable (that will be the playersInput() function in this case) and a 'limit' variable with the delay time in milliseconds. The function playersInput() is similar to the one explained by David in Week 9.

    -guess.html: Similar to index.html, but this template will update the game's table with all the information from the user's guesses, like the player's nation, continent,etc(using JINJA2).

    -gameover.html: This template will appear only if user fail to guess the player. In the Javascript part of the template, i created a countdown timer that will reset every second and when it hits 15:00 UTC Time, it will send an AJAX request to the server, to restart user guesses and change the mistery player.

    -winner.html: This template will appear only if user guess the player. It works almost identical as gameover.html.

Now, app.py: At the top of the code. First all the imports and the flask's session configurations. I created two global variables that i will use in most of the internal functions. 'correct_option' is the data of the mistery player (SQL will choose a random player inside the players table from the game.db database). 'activate_block' is a global variable that acts as an on/off switch, so user can't pass those 10 tries. In line 54 i recycled a function used in cs50's Finance that creates a decorated function for the login path.
Index() function will render the index.html template so the user can make his first choice.
Redirect() function will receive an AJAX request from the index template and convert it into a json object to later send it to the table() function.
Table() function will receive the user pick's id and will save it into the user_guess table inside the database. Then, i've added an if conditional in line 115 in case user wants to keep guessing after 10 tries, to start deleting the guesses in order to prevent it to collapse the database. In the end of the function, inside the for loop there are four if statements:

    -line 128: User got the right answer before the 10th try. Code will update user's stats database and code  will render template winner.html with updated points.

    -line 143: user wasted all 10 tries and did not get the right answer. code will render template gameover.html with updated stats.

    -line 153: User is using f5 after 10 tries, code will keep rendering the gameover template.

    -line 159: User still has some tries to use. Codeline will render template guess.html

login(),logout() and register() are pretty standard functions, recycled from cs50's Finance pset. I've added flash messages that will popup in certain templates with JINJA2, if user fails to login or register.
In the end, cooldown() function will receive an AJAX request in a 24hrs period starting every day 15:00pm UTC time, to reactivate the 'block' global variable and to pick a new mistery player.

game.db is the database file executed in SQL, which contains all the tables with information from the user and the football players. I had to search for every single piece of data from the footballers.
There are three tables inside the database:
    -players: Table filled with all the information from the real football players, like their age or shirt number. Every one of them with an unique ID.

    -user: Table filled with all the user's information, like the username, password hash and user stats.

    -user_guess: Table that saves all the user guesses.

I have a lot of ideas to implement to this code, like adding an EASY/MEDIUM/HARD level with less tries but only with nations that qualified for the round of 16/quarterfinals, or adding a weekly leaderboard (using the points saved in the user database). I also did not put ALL of the players that participated in the World Cup (There were a lot of them)

I have to admit that my intention was to finish this project by the end of 2022 (October/November), because it was the perfect timing before the start of the World Cup. WordleCup now will remain as a tribute to the BEST World Cup i've ever seen. I don't think any other will ever surpass it 🇦🇷❤

Thank you very much for your time reading all this, i hope you enjoyed this proyect as much as i enjoyed creating it!
