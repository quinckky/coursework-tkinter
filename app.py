import pickle
import re
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

from ttkthemes import ThemedTk

from student import Student


class StudentCollectionApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.students: list[Student] = []
        self.search_results: list[Student] = []
        self.filename = ""

        self.up_arrow = tk.PhotoImage(file="images/up-arrow.png")
        self.down_arrow = tk.PhotoImage(file="images/down-arrow.png")

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="Файл", menu=self.file_menu)
        self.file_menu.add_command(label="Открыть", accelerator="Ctrl+O", command=self.open_collection)
        self.file_menu.add_command(label="Сохранить", accelerator="Ctrl+S", command=self.save_collection)
        self.file_menu.add_command(label="Сохранить как...", accelerator="Ctrl+Shift+S", command=self.save_collection_as)
        self.file_menu.add_command(label="Закрыть", accelerator="Ctrl+Q", command=self.close_collection)

        self.operations_menu = tk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="Операции", menu=self.operations_menu)
        self.operations_menu.add_command(label="Добавить", accelerator="Ctrl+A", command=self.add_student)
        self.operations_menu.add_command(label="Удалить", accelerator="Ctrl+D", command=self.delete_student)
        self.operations_menu.add_command(label="Поиск", accelerator="Ctrl+F", command=self.search_students)
        self.operations_menu.add_command(label="Показать хороших студентов", command=self.search_good_students)

        self.button_frame = ttk.Frame(self.root, padding=[10, 10])
        self.add_button = ttk.Button(self.button_frame, text="Добавить", command=self.add_student)
        self.add_button.pack(side="left", padx=10, ipadx=30, ipady=10, expand=True)
        self.add_button = ttk.Button(self.button_frame, text="Удалить", command=self.delete_student)
        self.add_button.pack(side="left", padx=10, ipadx=30, ipady=10, expand=True)
        self.add_button = ttk.Button(self.button_frame, text="Поиск", command=self.search_students)
        self.add_button.pack(side="left", padx=10, ipadx=30, ipady=10, expand=True)
        self.button_frame.pack(side="top")

        self.main_label = ttk.Label(self.root, text="Исходные данные")
        self.main_label.pack()

        self.main_tree = ttk.Treeview(self.root, columns=("name", "group", "grades"), show="headings")
        self.main_tree.heading("name", text="ФИО", command=lambda: self.sort_students(self.main_tree, 0))
        self.main_tree.heading("group", text="Группа", command=lambda: self.sort_students(self.main_tree, 1))
        self.main_tree.heading("grades", text="Оценки", command=lambda: self.sort_students(self.main_tree, 2))
        self.main_tree.pack(expand=True, fill="both")

        self.search_label = ttk.Label(self.root, text="Результаты поиска")
        self.search_label.pack()

        self.search_tree = ttk.Treeview(self.root, columns=("name", "group", "grades"), show="headings")
        self.search_tree.heading("name", text="ФИО", command=lambda: self.sort_students(self.search_tree, 0))
        self.search_tree.heading("group", text="Группа", command=lambda: self.sort_students(self.search_tree, 1))
        self.search_tree.heading("grades", text="Оценки", command=lambda: self.sort_students(self.search_tree, 2))
        self.search_tree.pack(expand=True, fill="both")
        
        self.root.bind("<Control-o>", lambda event: self.open_collection())
        self.root.bind("<Control-s>", lambda event: self.save_collection())
        self.root.bind("<Control-Shift-S>", lambda event: self.save_collection_as())
        self.root.bind("<Control-q>", lambda event: self.close_collection())
        self.root.bind("<Control-f>", lambda event: self.search_students())
        self.root.bind("<Control-a>", lambda event: self.add_student())
        self.root.bind("<Control-d>", lambda event: self.delete_student())

    def save_collection_as(self):
        filename = filedialog.asksaveasfilename(defaultextension=".dat")
        if filename:
            with open(filename, "wb") as file:
                pickle.dump(self.students, file)
            messagebox.showinfo("Успех", "Коллекция сохранена!")

    def save_collection(self):
        if self.filename:
            with open(self.filename, "wb") as file:
                pickle.dump(self.students, file)
            messagebox.showinfo("Успех", "Коллекция сохранена!")
        else:
            messagebox.showerror("Ошибка", "Файл для сохранения не открыт!")

    def open_collection(self):
        self.filename = filedialog.askopenfilename()
        if self.filename:
            with open(self.filename, "rb") as file:
                self.students = pickle.load(file)
            self.display_students(self.main_tree, self.students)

    def close_collection(self):
        self.students.clear()
        self.search_results.clear()
        self.filename = None
        self.display_students(self.main_tree, self.students)
        self.display_students(self.search_tree, self.search_results)

    def add_student(self):
        dialog = AddStudentDialog(self.root, self)
        dialog.wait_window()
        new_student = dialog.result
        if new_student is not None:
            self.students.append(new_student)
            self.display_students(self.main_tree, self.students)
            messagebox.showinfo("Успех", "Студент успешно добавлен!")

    def delete_student(self):
        if self.students:
            name = simpledialog.askstring("Удалить", "Введите ФИО студента:").lower()
            if name is None:
                return
            if name:
                students = [student for student in self.students if name in student.name.lower()]
                if students:
                    self.students.remove(students[0])
                    self.display_students(self.main_tree, self.students)
                    messagebox.showinfo("Успех", "Студент успешно удален!")
                else:
                    messagebox.showerror("Ошибка", "Указанного студента не найдено!")
            else:
                messagebox.showerror("Ошибка", "Введите значение!")
        else:
            messagebox.showerror("Ошибка", "Коллекция пуста!")

    def search_students(self):
        if self.students:
            query = simpledialog.askstring("Поиск", "Введите ФИО студента:").lower()
            if query is None:
                return
            if query != "":
                self.search_results = [student for student in self.students if query in student.name.lower()]
                if self.search_results:
                    self.display_students(self.search_tree, self.search_results)
                    messagebox.showinfo("Результаты поиска", f"Найдено {len(self.search_results)} студент(-ов) по запросу.")
                else:
                    messagebox.showinfo("Результаты поиска", "Студентов по запросу не найдено.")
            else:
                messagebox.showerror("Ошибка", "Введите значение!")
        else:
            messagebox.showerror("Ошибка", "Коллекция пуста!")

    def sort_students(self, tree: ttk.Treeview, column: int, *, reverse=False):
        collection = [(tree.set(i, column), i) for i in tree.get_children("")]
        if column == 2:
            def key(x: tuple[str]):
                grades = [int(i) for i in x[0].split()]
                return sum(grades)/len(grades)
        else:
            key = lambda x: x[0]
        collection.sort(key=key, reverse=reverse)
        for index,  (_, i) in enumerate(collection):
            tree.move(i, "", index)
        image = self.up_arrow if reverse else self.down_arrow
        tree.heading(column, command=lambda: self.sort_students(tree, column, reverse=not reverse), image=image)

    def search_good_students(self):
        if self.students:
            self.search_results.clear()
            for student in self.students:
                for grade in student.grades:
                    if grade < 4:
                        break
                else:
                    self.search_results.append(student)

            if self.search_results:
                self.display_students(self.search_tree, self.search_results)
                messagebox.showinfo("Результаты поиска", f"Найдено {len(self.search_results)} студент(-ов).")
            else:
                messagebox.showinfo("Результаты поиска", "Студентов не найдено!")
        else:
            messagebox.showerror("Ошибка", "Коллекция пуста!")
            
    def display_students(self, tree: ttk.Treeview, students: list[Student]):
        tree.delete(*tree.get_children())
        for i, student in enumerate(students):
            tree.insert("", "end", text=str(i), values=(student.name, student.group, student.grades))

class AddStudentDialog(tk.Toplevel):
    def __init__(self, master: tk.Tk, app: StudentCollectionApp):
        super().__init__(master)
        self.title("Добавить")
        self.app = app
        self.result = None

        self.name_frame = ttk.Frame(self)
        self.name_frame.pack(fill=tk.X, padx=10, pady=5)
        self.name_label = ttk.Label(self.name_frame, text="ФИО:")
        self.name_label.pack(side=tk.LEFT)
        self.name_entry = ttk.Entry(self.name_frame)
        self.name_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        self.group_frame = ttk.Frame(self)
        self.group_frame.pack(fill=tk.X, padx=10, pady=5)
        self.group_label = ttk.Label(self.group_frame, text="Группа:")
        self.group_label.pack(side=tk.LEFT)
        self.group_entry = ttk.Entry(self.group_frame)
        self.group_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        self.grades_frame = ttk.Frame(self)
        self.grades_frame.pack(fill=tk.X, padx=10, pady=5)
        self.grades_label = ttk.Label(self.grades_frame, text="Оценки (через запятую):")
        self.grades_label.pack(side=tk.LEFT)
        self.grades_entry = ttk.Entry(self.grades_frame)
        self.grades_entry.pack(side=tk.RIGHT, expand=True, fill=tk.X)

        self.add_button = ttk.Button(self, text="Добавить", command=self.input_student)
        self.add_button.pack(padx=10, pady=5, fill=tk.X)

    def input_student(self):
        name = self.name_entry.get().strip()
        group = self.group_entry.get().strip()
        grades = self.grades_entry.get().strip()

        if not re.match(r"^[А-Яа-яЁё]+\s[А-Яа-яЁё]\.[А-Яа-яЁё]\.$", name):
            messagebox.showerror("Ошибка", "ФИО должно быть в формате \"Фамилия И.О.\"!")
            self.focus_set()
            return
        
        if not re.match(r"^\d{6}$", group):
            messagebox.showerror("Ошибка", "Группа должна быть положительным шестизначным числом!")
            self.focus_set()
            return
        
        if not re.match(r"^(10|[1-9])\s*,\s*(10|[1-9])\s*,\s*(10|[1-9])\s*,\s*(10|[1-9])\s*,\s*(10|[1-9])$", grades):
            messagebox.showerror("Ошибка", "Должно быть 5 оценок, каждая из которых является числом в диапазоне [1; 10]!")
            self.focus_set()
            return
        
        group = int(group)
        grades = [int(grade.strip()) for grade in grades.split(",")]
        self.result = Student(name, group, grades)
        self.destroy()

def start_app():
    root = ThemedTk(theme="breeze")
    root.title("Управление коллекцией студентов")
    root.iconbitmap(default="images/app.ico")
    app = StudentCollectionApp(root)
    root.mainloop()
    