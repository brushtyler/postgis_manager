# -*- coding: utf-8 -*-

from ui.DlgGeomProcessing_ui import Ui_DlgGeomProcessing
from DlgDbError import DlgDbError

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import postgis_utils


class DlgGeomProcessing(QDialog, Ui_DlgGeomProcessing):
	def __init__(self, parent=None, db=None):
		QDialog.__init__(self, parent)
		
		self.setupUi(self)
		
		self.db = db

		self.connect(self.buttonBox, SIGNAL("accepted()"), self.onOK)
		
		self.populateSchemas()
		self.populateTables()
		self.populateColumns()

		self.connect(self.cboSchema, SIGNAL("currentIndexChanged(int)"), self.populateTables)
		self.connect(self.cboTable, SIGNAL("currentIndexChanged(int)"), self.populateColumns)


	def populateSchemas(self):
		
		if not self.db:
			return
		
		schemas = self.db.list_schemas()
		self.cboSchema.clear()
		for schema in schemas:
			self.cboSchema.addItem(schema[1])


	def populateTables(self):
		
		if not self.db:
			return
		
		schema = unicode(self.cboSchema.currentText())
		tables = self.db.list_geotables(schema)
		self.cboTable.clear()
		for table in tables:
			if table[6]: # contains geometry column?
				self.cboTable.addItem(table[0])
			

	def populateColumns(self):
		
		if not self.db:
			return
		
		schema = unicode(self.cboSchema.currentText())
		table = unicode(self.cboTable.currentText())
		fields = self.db.get_table_fields(table, schema)
		
		self.cboGeomColumn.clear()
		self.cboResColumn.clear()
		
		for fld in fields:
			if fld.data_type == 'geometry':
				self.cboGeomColumn.addItem(fld.name)
			else:
				self.cboResColumn.addItem(fld.name)
		

	def onOK(self):

		if self.radLength.isChecked():
			fct = "length"
		elif self.radArea.isChecked():
			fct = "area"
		else:
			QMessageBox.information(self, "error", "No function selected!")
			return
			
		addTrigger = self.chkUpdateTrigger.isChecked()

		QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
		
		try:
			schema, table = unicode(self.cboSchema.currentText()), unicode(self.cboTable.currentText())
			resColumn, geomColumn = unicode(self.cboResColumn.currentText()),unicode(self.cboGeomColumn.currentText())
			self.db.table_apply_function( schema, table, resColumn, fct, geomColumn )
																		
			if addTrigger:
				self.db.table_add_function_trigger( schema, table, resColumn, fct, geomColumn )
		
			QApplication.restoreOverrideCursor()
		
		except postgis_utils.DbError, e:
			QApplication.restoreOverrideCursor()
			
			DlgDbError.showError(e, self)
			return

		QMessageBox.information(self, "good", "Everything went fine.")
		self.accept()
