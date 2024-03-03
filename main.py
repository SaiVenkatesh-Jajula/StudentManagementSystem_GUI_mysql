from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QVBoxLayout,\
    QLineEdit, QComboBox, QPushButton, QToolBar, QStatusBar, QLabel, QGridLayout, QMessageBox
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import Qt
import sys
import mysql.connector


class DatabaseConnection:

    def __init__(self,host = 'localhost',user ='root',password='python',database='school'):
        self.host = host
        self.user =user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password, database=self.database)
        return connection


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(450, 600)
        self.setWindowTitle("StudentManagementSystem")

        # create Menu Bar
        file_menu = self.menuBar().addMenu("&File")
        help_menu = self.menuBar().addMenu("&Help")
        search_menu = self.menuBar().addMenu("&Edit")

        add_student = QAction(QIcon("icons/add.png"), 'Add Student', self)
        add_student.triggered.connect(self.adding_student)
        file_menu.addAction(add_student)

        about = QAction('About', self)
        about.triggered.connect(self.aboutdialog)
        help_menu.addAction(about)


        filter = QAction(QIcon("icons/search.png"),'search', self)
        filter.triggered.connect(self.search_record)
        search_menu.addAction(filter)

        # Create toolbar and toolbar elements
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        toolbar.addAction(add_student)
        toolbar.addAction(filter)

        # Creating a table structure
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(('Id', 'Name', 'Course', 'Mobile'))
        # To remove/hide extra index by default
        self.table.verticalHeader().setVisible(False)

        self.setCentralWidget(self.table)

        # Adding statusbar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell clicked
        self.table.clicked.connect(self.cell_clicked)
    def cell_clicked(self):
        edit_button = QPushButton('edit')
        edit_button.clicked.connect(self.update_record)

        delete_button = QPushButton('delete')
        delete_button.clicked.connect(self.delete_record)

        # Deleting old buttons
        oldbuttons = self.findChildren(QPushButton)
        if oldbuttons:
            for i in oldbuttons:
                self.statusbar.removeWidget(i)

        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

    def update_record(self):
        dialog = UpdateDialog()
        dialog.exec()

    def delete_record(self):
        dialog = DeleteDialog()
        dialog.exec()

    def load_data(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("select * from students")
        all_data = cursor.fetchall()
        # Set rows with None before arranging
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(all_data):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def adding_student(self):
        dialog = InsertDialog()
        dialog.exec()

    def search_record(self):
        dialog = SearchDialog()
        dialog.exec()

    def aboutdialog(self):
        dialog = AboutDialog()
        dialog.exec()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('About Student Management System')
        content = """
    This is Student Mangement System. You can utilize for your own purpose.
    If you need to update this application. You are welcome. This is hosted in GitHub.    
        """
        self.setText(content)
        self.exec()

class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Student Entry")
        # Good Practise for Dialog Window
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        layout = QVBoxLayout()

        # Create widgets
        self.sname = QLineEdit()
        self.sname.setPlaceholderText("Name")
        layout.addWidget(self.sname)

        self.coursecombo = QComboBox()
        self.coursecombo.addItems(['Biology','Maths','Physics','Telugu'])
        layout.addWidget(self.coursecombo)

        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        button = QPushButton("submit")
        button.clicked.connect(self.insert_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def insert_student(self):
        name = self.sname.text()
        course = self.coursecombo.currentText()
        mobile = self.mobile.text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("Insert into students(name,course,mobile) values (%s,%s,%s)", (name, course, mobile))
        connection.commit()
        self.sname.setText("")
        self.mobile.setText("")
        cursor.close()
        connection.close()
        sms.load_data()
        self.close()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        layout = QVBoxLayout()

        self.searchbar = QLineEdit()
        self.searchbar.setPlaceholderText("Name")
        layout.addWidget(self.searchbar)

        searchbutton = QPushButton("Search")
        searchbutton.clicked.connect(self.filter_data)
        layout.addWidget(searchbutton)

        self.setLayout(layout)

    def filter_data(self):
        search_name = self.searchbar.text()
        self.searchbar.setText("")
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("select * from students where name = %s", (search_name,))
        cursor.fetchall()
        cursor.close()
        connection.close()
        items = sms.table.findItems(search_name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            sms.table.item(item.row(), 1).setSelected(True)
        self.close()

class UpdateDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Student Entry")
        # Good Practise for Dialog Window
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        layout = QVBoxLayout()

        index = sms.table.currentRow()
        self.sid = sms.table.item(index,0).text()

        # Create widgets
        # setting default value as previous value
        student_name = sms.table.item(index, 1).text()
        self.sname = QLineEdit(student_name)
        self.sname.setPlaceholderText("Name")
        layout.addWidget(self.sname)

        coursecombo = sms.table.item(index, 2).text()
        self.coursecombo = QComboBox()
        self.coursecombo.addItems(['Biology','Maths','Physics','Telugu'])
        self.coursecombo.setCurrentText(coursecombo)
        layout.addWidget(self.coursecombo)

        mobile = sms.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("update students set name=%s, course=%s, mobile=%s where id=%s",
                       (self.sname.text(),self.coursecombo.currentText(),self.mobile.text(),self.sid))
        connection.commit()
        cursor.close()
        connection.close()
        sms.load_data()
        self.close()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Record")

        grid = QGridLayout()

        index = sms.table.currentRow()
        self.sid = sms.table.item(index,0).text()

        # create widgets
        label1 = QLabel("Confirm to delete the selected row")
        yesbutton = QPushButton('Yes')
        yesbutton.clicked.connect(self.delete_student)
        nobutton = QPushButton('No')
        nobutton.clicked.connect(self.dont_delete_student)

        # add widgets to grid
        grid.addWidget(label1,0,0,1,2)
        grid.addWidget(yesbutton,1,0)
        grid.addWidget(nobutton,1,1)

        self.setLayout(grid)
    def delete_student(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute('delete from students where id = %s',(self.sid,))
        connection.commit()
        cursor.close()
        connection.close()
        sms.load_data()
        # close the dialog after work done
        self.close()

        messagebox = QMessageBox()
        messagebox.setWindowTitle("Success")
        messagebox.setText("Record Deleted Successfully!")
        messagebox.exec()

    def dont_delete_student(self):
        self.close()


app = QApplication(sys.argv)
sms = MainWindow()
sms.load_data()
sms.show()
sys.exit(app.exec())
