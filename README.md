# dots-and-boxes
A REST API, Python Client, and JavaScript frontend for playing the children's game Dots and Boxes. https://en.wikipedia.org/wiki/Dots_and_Boxes. The purpose of this project it to write NN models that players can play against.


## Repository Layout
 - static/ - Contains JavaScript and CSS for the UI.
 - templates/ - Jinja 2 HTML templates running in Flask.
 - client.py - This file is a python client that can be used to play the game using the REST API.
 - game.py - This file contains the core game logic and state tracking.
 - server.py - This is the Flask app that contains all of the routes for the API and UI.

 ## Requirements
 These are the versions this has been tested on, other version may work as well (also listed in requirements.txt)
  - Python 3.8
  - Flask 1.1
  - Requests 2.23
  - Bootstrap 4.5
  - jQuery 3.5.1

## Running the server in development mode
    python server.py

## Running the client
    python client.py

  ## TODO
   - Finish writting the JS frontend