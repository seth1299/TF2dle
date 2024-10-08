Prerequisites:
Install Python:

If Python isn't already installed, download and install it from the official Python website.
During installation, make sure to check the option "Add Python to PATH".
Install pip:

Pip should come installed with Python. To check if it’s installed, open a terminal/command prompt and type:
bash
pip --version

If pip isn't installed, follow these instructions: https://pip.pypa.io/en/stable/installation/

Instructions for Setting Up:
Clone the Project or Download the Files.

Get a copy of the project, either by cloning it with Git or downloading it as a ZIP file from the Releases page and then extracting it.

Install Flask and Other Dependencies:
Navigate to the project directory in the terminal/command prompt and install the necessary dependencies by running:
bash
pip install -r requirements.txt

If requirements.txt is not available, manually install Flask with:
bash
pip install Flask

Running the Flask Server:
Navigate to the folder where app.py is located using the terminal or command prompt.
If you're using an IDE like Visual Studio Code, you can simply click "Run in dedicated Terminal"; or you can manually start the Flask server by typing:
bash
python app.py

Flask will start running on localhost at a port, typically 5000. You should see output similar to this:
* Running on http://127.0.0.1:5000/
  
Opening the Game in a Browser:
Open a web browser and go to http://127.0.0.1:5000/ or instead, if you're using an IDE, just control+click on the "running on [X]" message and it will automatically open your default web browser and automatically open your webpage to the correct localhost. Now you're ready to play!
