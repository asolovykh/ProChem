"""Custom Tree Model class for control window"""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2025 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

import sys
from PySide6.QtCore import Qt, QModelIndex, QMimeData, QAbstractItemModel, QByteArray
from PySide6.QtWidgets import QApplication, QTreeView, QAbstractItemView, QMainWindow

__all__ = ["CustomTreeModel"]


class TreeItem:
    def __init__(self, data, parent=None):
        self.parent_item = parent
        self.item_data = data 
        self.child_items = []

    def append_child(self, item):
        self.child_items.append(item)

    def child(self, row):
        return self.child_items[row]

    def child_count(self):
        return len(self.child_items)

    def row(self):
        if self.parent_item:
            return self.parent_item.child_items.index(self)
        return 0

    def data(self, column):
        try:
            return self.item_data[column]
        except IndexError:
            return None

    def insert_child(self, position, item):
        if position < 0 or position > len(self.child_items):
            return False
        item.parent_item = self # Устанавливаем нового родителя
        self.child_items.insert(position, item)
        return True

    def remove_child(self, item):
        if item in self.child_items:
            self.child_items.remove(item)
            return True
        return False

    def __repr__(self):
        return f"TreeItem(data={self.item_data}, parent={self.parent_item})"

class CustomTreeModel(QAbstractItemModel):
    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.column_count = 4 # Фиксируем количество столбцов
        self.root_item = TreeItem(["ID", "V", "Name", "Type"])
        if data is not None:
            self.append_data(data, self.root_item)

    def headerData(self, section, orientation, role=Qt.DisplayRole): # NOTE: overrided method
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return ["ID", "V", "Name", "Type"][section]
            else:
                return QString(f"Row {section + 1}")
        return super().headerData(section, orientation, role)

    def columnCount(self, parent=QModelIndex()): # NOTE: overrided method
        return self.column_count

    def rowCount(self, parent=QModelIndex()): # NOTE: overrided method
        parent_item = self.get_item(parent)
        return parent_item.child_count()

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role != Qt.DisplayRole:
            return None
        item = self.get_item(index)
        return item.data(index.column())

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        parent_item = self.get_item(parent)
        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()
        child_item = self.get_item(index)
        parent_item = child_item.parent_item
        if parent_item == self.root_item:
            return QModelIndex()
        return self.createIndex(parent_item.row(), 0, parent_item)

    def get_item(self, index):
        if index.isValid():
            item = index.internalPointer()
            if item:
                return item
        return self.root_item

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsDropEnabled
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

    def supportedDropActions(self): # NOTE: overrided method
        return Qt.MoveAction

    def mimeData(self, indexes): # NOTE: overrided method
        self._dragged_items = []
        for index in indexes:
             if index.column() == 0:
                item = self.get_item(index)
                if item is not self.root_item:
                   self._dragged_items.append(item)
        mime_data = QMimeData()
        mime_data.setData('application/x-qabstractitemmodeldatalist', QByteArray(b'marker'))
        return mime_data
    
    def dropMimeData(self, data, action, row, column, parent): # NOTE: overrided method
        old_row, new_row = -1, row
        if action == Qt.IgnoreAction:
            return True
        if not data.hasFormat('application/x-qabstractitemmodeldatalist'):
            return False

        moved_items = self._dragged_items
        if not moved_items:
            return False
       
        target_item = self.get_item(parent)
        first_parent = moved_items[0].parent_item

        if target_item in moved_items:
            self._dragged_items = []
            return False
        if target_item == first_parent.parent_item:
            self._dragged_items = []
            return False
        
        if parent.isValid():
            if target_item == first_parent:
                pass
            else:
                self._dragged_items = []
                return False

        for item in sorted(moved_items, key=lambda x: x.row(), reverse=True):
            old_parent = item.parent_item
            old_row = item.row()
            self.beginRemoveRows(self.createIndex(old_parent.row(), 0, old_parent) if old_parent != self.root_item else QModelIndex(), old_row, old_row)
            old_parent.remove_child(item)
            self.endRemoveRows()
        
        self.beginInsertRows(parent, new_row, new_row + len(moved_items) - 1)
        for item in moved_items:
            target_item.insert_child(new_row - 1 if new_row > old_row else new_row, item)
            new_row += 1
        self.endInsertRows()

        self._dragged_items = []
        return True

    def move_item(self, index, direction):
        item = self.get_item(index)
        parent = item.parent_item
        # if parent == self.root_item:
        #     return False
        row = item.row()
        new_row = row - 1 if direction == 'up' else row
        if (row == 0 and direction == 'up') or (row == parent.child_count() - 1 and direction == 'down'):
            return False

        self.beginRemoveRows(self.createIndex(parent.row(), 0, parent) if parent != self.root_item else QModelIndex(), row, row)
        parent.remove_child(item)
        self.endRemoveRows()

        self.beginInsertRows(self.createIndex(parent.row(), 0, parent) if parent != self.root_item else QModelIndex(), new_row, new_row)
        parent.insert_child(new_row, item)
        self.endInsertRows()

        #if direction == 'up':
        #    self.beginMoveRows(self.createIndex(parent.row(), 0, parent), row, row, self.createIndex(parent.row() - 1, 0, parent), row - 1)
        #else:
        #    self.beginMoveRows(self.createIndex(parent.row(), 0, parent), row, row, self.createIndex(parent.row() + 1, 0, parent), row + 1)
        #parent.remove_child(item)
        #parent.insert_child(row - 1 if direction == 'up' else row + 1, item)
        #self.endMoveRows()
        return True

    def append_data(self, data_list, parent):
        for item_data, children_data in data_list:
            parent_item = TreeItem(item_data, parent)
            parent.append_child(parent_item)
            if children_data:
                self.append_data(children_data, parent_item)


if __name__ == "__main__":
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("QAbstractItemModel D&D Example")
            self.setGeometry(100, 100, 400, 300)
            
            # Пример иерархических данных: [([ДанныеРодителя], [ДанныеДетей]), ...]
            # Каждый элемент данных - это кортеж из двух списков/кортежей
            data = [
                ([1, "V","Item 1", "Desc 1"], None),
                ([2, "I", "Item 2 (Parent)", "Desc 2"], [
                    ([1, "I", "Child 2.1", "Desc 2.1"], None),
                    ([2, "I", "Child 2.2", "Desc 2.2"], None),
                    ([3, "I", "Child 2.3", "Desc 2.3"], None),
                    ([4, "I", "Child 2.4", "Desc 2.4"], None)
                ]),
                ([3, "I", "Item 3", "Desc 3"], None),
                ([4, "I", "Item 4", "Desc 4"], None),
                ([5, "I", "Item 5", "Desc 5"], None),
                ([6, "I", "Item 6", "Desc 6"], None),
                ([7, "I", "Item 7", "Desc 7"], None)
            ]

            self.model = CustomTreeModel(data)
            self.tree_view = QTreeView()
            self.tree_view.setModel(self.model)
            
            # Настройка представления для D&D
            self.tree_view.setDragDropMode(QAbstractItemView.InternalMove)
            self.tree_view.setDragEnabled(True)
            self.tree_view.setAcceptDrops(True)
            self.tree_view.setDropIndicatorShown(True)
            self.tree_view.setDefaultDropAction(Qt.MoveAction)

            self.setCentralWidget(self.tree_view)
            print(self.model.move_item(self.model.index(1, 0), direction='up'))


    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
