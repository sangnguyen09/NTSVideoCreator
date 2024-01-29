import sys

from PySide2.QtCore import QUrl
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PySide2.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    web = QWebEngineView()
    # web.settings().LocalStorageEnabled
    web.settings().setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture,True)
    web.settings().setAttribute(QWebEngineSettings.AllowRunningInsecureContent,True)
    web.settings().setAttribute(QWebEngineSettings.JavascriptEnabled,True)
    web.settings().setAttribute(QWebEngineSettings.WebGLEnabled,True)
    web.settings().setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard,True)
    web.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls,True)
    web.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls,True)
    web.settings().setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled,True)
    web.settings().setAttribute(QWebEngineSettings.PluginsEnabled,True)
    web.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled,True)


    web.load(QUrl("http://localhost:3000/studio/editor?codePc=dsdsd&toolCode=TKVR"))

    web.setMinimumWidth(1270)
    web.setMinimumHeight(720)
    web.setMaximumWidth(1270)
    web.setMaximumHeight(720)

    web.show()

    sys.exit(app.exec())
