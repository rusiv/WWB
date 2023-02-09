import sublime
import sublime_plugin
import os
import base64
from .wwb.pymysql import *
from datetime import datetime

DEFAULT_SETTINGS = {
	'folder': 'WWB',
	'db': {
		'host': 'localhost',
		'user': 'mysql',
		'password': 'mysql',
		'database': 'wbase'
	}
}
ALLOW_EXTS = ['txt', 'xml', 'js', 'css']

def _getSettings():
	activeWindow = sublime.active_window()
	variables = activeWindow.extract_variables()
	projectPath = variables.get('project_path')
	wwbSettings = activeWindow.project_data().get('wwb')
	if (not wwbSettings):
		wwbSettings = DEFAULT_SETTINGS
	wwbPath = os.path.join(projectPath, wwbSettings.get('folder'))	
	dictTmp = {
		'wwbPath': wwbPath,
		'projectPath': projectPath
	}
	wwbSettings.update(dictTmp)	
	return wwbSettings

def _isPathFromWWB(fullFilePath):
	result = False		
	filePath = ''
	fileExt = ''
	pathParts = os.path.split(fullFilePath)
	fileNameParts =  pathParts[1].split('.')	
	if (len(fileNameParts) == 2):
		filePath = pathParts[0]
		fileExt = fileNameParts[1].lower()		
	else:
		filePath = fullFilePath		
	
	wwbSettings = _getSettings()
	if (wwbSettings.get('wwbPath') in filePath):
		if (fileExt):			
			result = fileExt in ALLOW_EXTS
		else:
			result = True		
	return result

def _isCurrentFileForWWB():
	result = False
	activeWindow = sublime.active_window()
	filePath = activeWindow.extract_variables()['file_path']	
	fileExt = activeWindow.extract_variables()['file_extension'].lower()
	
	wwbSettings = _getSettings()
	if ((wwbSettings.get('wwbPath') in filePath) and (fileExt in ALLOW_EXTS)):
		result = True
	return result

def _getConnection():
	dbSettings = _getSettings()['db']	
	connection = connect(
		host = dbSettings['host'],
		user = dbSettings['user'],
		password = dbSettings['password'],
		database = dbSettings['database'],
		cursorclass = cursors.DictCursor
	)
	return connection

def _makeLocalPartPath(pathList):
	result = ''
	l = len(pathList)
	if (l > 2):
		i = 0
		for item in pathList:
			if ((i > 0) and (i < l - 1)):
				result = result + item + '.'
			i = i + 1	
	return result			

def _makeLocalName(relPath):
	aList = relPath.split('\\')	
	l = len(aList)
	if (l <= 1):
		return None
	project = aList[0]
	fileParts = aList[l - 1].split('.')	
	if (len(fileParts) != 2):
		return None	
	fileName = fileParts[0]
	fileExt = fileParts[1].lower()
	if (not (fileExt in ALLOW_EXTS)):
		return None
	if ((fileExt == 'txt') or (fileExt == 'xml')):
		fileExt = 'var'
	partPath = _makeLocalPartPath(aList)
	return 'ab' + '.' + fileExt + '.' + project + '.' + partPath + fileName

def _makeLocalNameMainParts(relPath):
	result = [];
	aList = relPath.split('\\')	
	l = len(aList)
	if (l <= 1):
		return None
	project = aList[0]
	partPath = _makeLocalPartPath(aList)
	for ext in ['var', 'css', 'js']:
		result.append('ab' + '.' + ext + '.' + project + '.' + partPath + aList[l - 1])
	return result

def _saveLocal(name, value):	
	result = False
	try:
		connection = _getConnection()
		now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')			
		with connection.cursor() as cursor:		
			# INSERT INTO table (id, name, age) VALUES(1, "A", 19) ON DUPLICATE KEY UPDATE name="A", age=19		
			sql = 'INSERT INTO `a_local` (`a_tim`, `a_user`, `a_mtim`, `a_muser`, `a_type`, `a_key`, `a_v`, `a_info`, `a_sea`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
				ON DUPLICATE KEY UPDATE `a_tim` = %s, `a_mtim` = %s, `a_v` = %s, `a_sea` = %s'
			value64 = base64.b64encode(value).decode('utf8', 'ignore')
			valueTxt = value.decode('utf8', 'ignore')
			sea = valueTxt.upper() + name.upper()
			cursor.execute(sql, (now, '16', now, '16', '', name, value64, '', sea,     now, now, value64, sea))			
			connection.commit()			
			result = True
	finally:
		connection.close()
		return result

def _delLocal(name):
	result = False
	try:
		connection = _getConnection()
		with connection.cursor() as cursor:		
			sql = 'DELETE FROM `a_local` WHERE `a_key` = %s'
			cursor.execute(sql, (name))			
			connection.commit()			
			result = True
	finally:
		connection.close()
		return result

def _delLocalsByNameMainPart(name):
	result = False	
	try:
		connection = _getConnection()
		with connection.cursor() as cursor:					
			sql = 'DELETE FROM `a_local` WHERE `a_key` LIKE CONCAT(%s, ".", "%%")'			
			cursor.execute(sql, (name,))						
			connection.commit()			
			result = True
	finally:
		connection.close()
		return result

class wwbCompileEventListeners(sublime_plugin.EventListener):
	def on_post_save(self, view):		
		wwbSettings = _getSettings()
		if (not wwbSettings.get('projectPath')):
			print('No project, create a project.')
			return None
		if (not _isCurrentFileForWWB()):
			return None	
		activeWindow = sublime.active_window()
		variables = activeWindow.extract_variables()
		filePath = variables.get('file')		
		localName = _makeLocalName(os.path.relpath(filePath, wwbSettings.get('wwbPath')))
		if (not localName):
			print('File name ' + filePath + ' is not correct.')
			return None		
		file = open(filePath, 'rb')		
		localValue = file.read()		
		file.close()		
		if (not _saveLocal(localName, localValue)):
			print('Local ' + localName + ' not saved.')
			return None

	def on_post_window_command(self, window_id, name, args):				
		wwbSettings = _getSettings()
		if (name == 'delete_file'):
			files = args['files']
			for file in files:
				if (not _isPathFromWWB(file)):
					continue
				localName = _makeLocalName(os.path.relpath(file, wwbSettings.get('wwbPath')))				
				if (not _delLocal(localName)):
					print('Local ' + localName + ' not deleted.')
		if (name == 'delete_folder'):			
			dirs = args['dirs']
			for folder in dirs:
				if (not _isPathFromWWB(folder)):
					continue
				localNameMainParts = _makeLocalNameMainParts(os.path.relpath(folder, wwbSettings.get('wwbPath')))
				for nameMainPart in localNameMainParts:					
					if (not _delLocalsByNameMainPart(nameMainPart)):
						print('Locals by ' + nameMainPart + ' not deleted.')
				

			