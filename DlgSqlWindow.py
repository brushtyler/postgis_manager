
from DlgSqlWindow_ui import Ui_DlgSqlWindow

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import postgis_utils


class DlgSqlWindow(QDialog, Ui_DlgSqlWindow):

	def __init__(self, parent=None, db=None):
		QDialog.__init__(self, parent)
		
		self.db = db
		
		self.setupUi(self)

		settings = QSettings()
		self.restoreGeometry(settings.value("/PostGIS_Manager/sql_geometry").toByteArray())
		
		self.connect(self.btnExecute, SIGNAL("clicked()"), self.executeSql)
		self.connect(self.buttonBox.button(QDialogButtonBox.Close), SIGNAL("clicked()"), self.close)
		
		m = QStandardItemModel(self)
		self.viewResult.setModel(m)
		
		
	def closeEvent(self, e):
		""" save window state """
		settings = QSettings()
		settings.setValue("/PostGIS_Manager/sql_geometry", QVariant(self.saveGeometry()))
		
		QDialog.closeEvent(self, e)
		

	def executeSql(self):
		
		txt = str(self.editSql.toPlainText())
		
		m = self.viewResult.model()
		m.clear()
		
		QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

		try:
			c = self.db.con.cursor()
			self.db._exec_sql(c, txt)
			for row in c.fetchall():
				m.appendRow( [ QStandardItem(str(i)) for i in row ] )
			c.close()
			QApplication.restoreOverrideCursor()
		except postgis_utils.DbError, e:
			self.db.con.rollback()
			QApplication.restoreOverrideCursor()
			QMessageBox.critical(self, "sorry", "you have a problem:\n%s\nQUERY:\n%s" % (e.message, e.query))
		