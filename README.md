> This is only in alpha and can have some errors. [If you find any Please create an issue](https://github.com/DerSchinken/FontServer/issues/new)

# Why
Well, because of GDPR you can't use Google Fonts without using a consent banner. Which can get quite expensive.     
So I wrote this just change the Google url to this servers url/ip, and you have access to all Google Fonts again,    
but you don't need a consent management tool this time because there is no traffic to Google servers from the Client

# How to use
You need to configure the `server.env` with the given template (`server.template.env`) and then just run run.py    
If debug flag is set to false the server will automatically start in production mode with [waitress](https://docs.pylonsproject.org/projects/waitress/en/latest/)

# Extras:
There is a protected web interface where you can search for fonts and view them.   
It will also give you the code to load the font form the server.   
At the first start of the server you will be asked to create a new user which credentials are the credentials for the web interface    
But don't worry you don't need them to access the fonts
