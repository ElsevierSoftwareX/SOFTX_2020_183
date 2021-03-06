import numpy as np
from PyQt5 import Qt, QtCore, QtGui, QtWidgets

from anduryl import io
from anduryl.ui import widgets
from anduryl.ui.dialogs import NotificationDialog
from anduryl.ui.models import ItemDelegate, ItemsListsModel


class ItemsWidget(QtWidgets.QFrame):
    """
    Widget with the items table
    """
    def __init__(self, mainwindow):

        super(ItemsWidget, self).__init__()

        self.mainwindow = mainwindow
        self.project = mainwindow.project
        self.construct_widget()

    def construct_widget(self):
        """
        Construct the UI widget
        """
        # Create the table view
        self.table = QtWidgets.QTableView()
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("QTableView{border: 1px solid "+self.mainwindow.bordercolor+"}")
        self.table.installEventFilter(self)

        # Create and add model
        self.model = ItemsListsModel(parentwidget=self)
        self.model.leftalign.append(3)

        self.table.setModel(self.model)
        self.table.setItemDelegate(ItemDelegate(self.model))
        
        for i in range(3):
            self.table.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)

        mainbox = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel('Items')
        label.setContentsMargins(5, 2.5, 5, 2.5)
        label.setStyleSheet("QLabel {border: 1px solid "+self.mainwindow.bordercolor+"}")
        mainbox.addWidget(label)
        mainbox.addWidget(self.table)
        
        self.setLayout(mainbox)

    def eventFilter(self, source, event):
        """
        Eventfilter for copying table content.
        """
        if (event.type() == QtCore.QEvent.KeyPress and
            event.matches(QtGui.QKeySequence.Copy)):
            selection = self.table.selectedIndexes()
            if selection:
                text = io.selection_to_text(selection)
                QtWidgets.qApp.clipboard().setText(text)
                return True
        return self.mainwindow.eventFilter(source, event)

    def to_csv(self):
        """
        Calls the anduryl.io.table_to_csv function for the table model
        """
        io.table_to_csv(self.model, self.mainwindow)
        
    def add_item(self):
        """
        Add item button clicked. Adds an item to the project and updates the UI accordingly
        """
        
        # Add expert
        self.project.items.add_item(item_id=f'item{len(self.project.items.ids):02d}')       

        # Update GUI
        self.mainwindow.signals.update_gui()
        self.mainwindow.signals.update_color_range()
        self.mainwindow.setWindowModified(True)

    def remove_item_clicked(self):
        """
        Function that checks whether an item is selected
        when the option "remove item" is clicked.
        """
        rownum = self.table.currentIndex().row()
        if rownum == -1:
            NotificationDialog('Select a row to remove an expert')
            return None
        # Get item id    
        itemid = self.project.items.ids[rownum]

        # Remove expert from table widget
        self.remove_item(itemid)

    def remove_item(self, itemid):
        """
        Removes an item form the project and updates the UI accordingly.
        
        Parameters
        ----------
        itemid : str
            Item id
        """
        # Remove from project
        self.project.items.remove_item(item_id=itemid)
        self.mainwindow.assessmentswidget.table.setCurrentIndex(QtCore.QModelIndex())
        self.mainwindow.signals.update_gui()
        self.mainwindow.signals.update_color_range()
        self.table.setCurrentIndex(QtCore.QModelIndex())
        self.mainwindow.setWindowModified(True)

    def toggle_item(self, item):
        """
        Executed when the checkbox before an item is clicked. The item is
        added or removed to the excluded list of the items class.
        
        Parameters
        ----------
        item : str
            Item id
        """
        if item in self.project.items.excluded:
            self.project.items.excluded.remove(item)
        else:
            self.project.items.excluded.append(item)

    def exclude_item_clicked(self):
        """
        Function that checks whether an item is selected
        when the option "exclude item" is clicked.
        """
        rownum = self.table.currentIndex().row()
        if rownum == -1:
            NotificationDialog('Select a row to exclude an item')
            return None

        # Remove expert from table widget
        self.toggle_item(self.project.items.ids[rownum])

    def contextMenuEvent(self, event):
        """
        Describes the context menu for the items widget, and
        handles the clicked action
        """
    
        menu = QtWidgets.QMenu(self)
        rownum = self.table.currentIndex().row()
        
        # Add actions
        add_item_action = menu.addAction("Add item")
        if rownum >= 0:
            excluded = self.project.items.ids[rownum] in self.project.items.excluded
            exclude_item_action = menu.addAction("Include this item" if excluded else "Exclude this item")
        remove_item_action = menu.addAction("Remove item")
        menu.addSeparator()
        show_assessments_action = menu.addAction("Show item assessments")
        
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == add_item_action:
            self.add_item()
        elif action == remove_item_action:
            self.remove_item_clicked()
        elif action == show_assessments_action:
            rownum = self.table.currentIndex().row()
            self.mainwindow.assessmentswidget.table.setCurrentIndex(QtCore.QModelIndex())
            self.mainwindow.assessmentswidget.item_cbox.setCurrentIndex(rownum+1)
        elif (rownum >= 0) and (action == exclude_item_action):
            self.exclude_item_clicked()
