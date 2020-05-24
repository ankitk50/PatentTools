from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtWidgets, QtWebEngineWidgets
import pandas as pd 
import urllib.request as urllib
import sys,time

app = QtWidgets.QApplication(sys.argv)
window = QWidget()

#loader = QtWebEngineWidgets.QWebEngineView()
#loader.setZoomFactor(1)
#loader.page().pdfPrintingFinished.connect(lambda *args: print('finished:', args))

def download_pdfurl_file(download_url,filename):
    response = urllib.urlopen(download_url)
    file = open(filename, 'wb')
    file.write(response.read())
    file.close()

def emit_pdf(filename,loader,loop):
    #print("I'm here")
    #loader.show()
    loader.page().printToPdf(filename)
    loader.page().pdfPrintingFinished.connect(lambda: loop.exit())
    a= lambda filename: print(filename, "downloaded")
    a(filename)

def main(filename='mastersheet.xlsx'):
    excel_file=filename
    df=pd.read_excel(excel_file)
    df=df.dropna()
    
    for i in range(df.shape[0]):
        details=[]
        for j in range(df.shape[1]):
            #print(df.iloc(0)[i][j])
            details.append(df.iloc(0)[i][j])
        print("Downloading files for: ",details[0])
        if details[3].lower()=='video':
            print("Videos cannot be downloaded, please download manually!!")
        elif details[3].upper()=='PDF':
            download_pdfurl_file(details[1],details[2])
        else:
            #print("here")
            loader = QtWebEngineWidgets.QWebEngineView()
            loader.setZoomFactor(1)
            loader.load(QtCore.QUrl(details[1]))
            loop = QtCore.QEventLoop()         
            loader.loadFinished.connect(lambda: emit_pdf(details[2],loader,loop))
            loop.exec_()

def getUserInput():
	text, okPressed = QInputDialog.getText(window, "Enter excel filename","for e.g- mastersheet.xlsx", QLineEdit.Normal,"mastersheet.xlsx")


	if okPressed:
		print("filename: ",text)
		try:
			if text !='':
				main(str(text))
				return True
			else:
				main()
				return True

		except FileNotFoundError:
			alert1 = QMessageBox()
			alert1.setText('File specified not found. Keep [.exe file] and [excel file] in same folder and try again.')
			alert1.exec_()
			return False

getUserInput()	
sys.exit()
app.exec_()