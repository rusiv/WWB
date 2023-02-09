# WWB for Sublime
This project contains utils for save local file to WWBPlatform.

# Installation
**With the Package Control plugin**: bring up the Command Palette (Command+Shift+P on OS X, Control+Shift+P on Linux/Windows), select "Package Control: Install Package", wait while Package Control fetches the latest package list, then select WWB when the list appears. 
The advantage of using this method is that Package Control will automatically keep WWB up to date with the latest version.

**Without Git**: Download the latest source from GitHub and copy the WWB folder to your Sublime Text "Packages" directory.

**With Git**: Clone repository git://github.com/rusiv/WWB.git in your Sublime Text"Packages" directory.

# Configuration
For correct operation it is desirable to create a project. 
Add WWB setting to project seetings. Example:
`
	"wwb": {
		"folder": "WWB",
		"db": {
			"host": "localhost",
			"user": "mysql",
			"password": "mysql",
			"database": "wbase"
		}
	}
`
Description of the used settings:
* folder - path to WWB project
* host - wwb database server address
* user - wwb database user
* password - wwb database password
* database - wwb database name

# Use
For insert or update record in database save file. Allowed file extensions: txt, xml, js, css

For delete record in database delete file or folder using sublime.
