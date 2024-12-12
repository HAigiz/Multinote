#Импорт необходимых модулей
import psycopg2
import tkinter as tk
from tkinter import *
import customtkinter
from tkinter.messagebox import askyesno, showinfo
import os

# Создание объекта главного окна
root = customtkinter.CTk()
root.title("MultiNote")
root.geometry("300x400")
root.resizable(0, 0)
root.iconbitmap('multi.ico')    #Устанавливаем иконку для окна

# Класс для работы с заметками
class Notes():
    def __init__(self):
        self.conn = None
        self.cur = None

    # Метод для подключения к БД
    def db_start(self):
        self.conn = psycopg2.connect(
            dbname="multinote",
            user="tester",
            password="5426",
            host="localhost",
            client_encoding="utf8"
        )

        # Откроем курсор для выполнения операций с базой данных.
        self.cur = self.conn.cursor()
        
        # Создаем таблицу notes с столбцами id, name, description, color
        self.cur.execute("CREATE TABLE IF NOT EXISTS notes (id SERIAL, name VARCHAR, description VARCHAR, color VARCHAR);")

        # Фиксируем изменения в БД
        self.conn.commit()
    
    # Метод для сохранения заметки
    def update_notes_list(self):
        notes_list.delete(0, customtkinter.END) # Очищаем список заметок
        self.cur.execute("SELECT * FROM notes") # Выбираем все заметки в БД
        notes = self.cur.fetchall() # Получаем все выбранные заметки
        for note in notes:
            note_text = note[1] # Получаем имя заметки
            notes_list.insert(customtkinter.END, note_text) # Добавляем имя с конца полученного списка
    
    # Метод для сохранения заметки
    def save_note(self):
        note = note_entry.get() # Получаем текст заметки из поля ввода
        forbidden_chars = ['"', '\\', '|', '*', '#', ':' , '/', '<', '>', '^', '?', '[', ']']
        for_sym = (' '.join(forbidden_chars))
        for char in forbidden_chars:    # Проверяем на наличие запрещенных символов
            if char in note:
                error_label.config(text=f"Ошибка: Заметка не должна содержать специальные символы: {for_sym}", wraplength=285)
                return
            
        self.cur.execute("INSERT INTO notes (name) VALUES (%s)", (note,))   #добавляем заметку в БД
        self.conn.commit() # Фиксируем изменения
        self.update_notes_list()    # Обновляем список заметок
        note_entry.delete(0, customtkinter.END) # Очищаем поле ввода
        error_label.config(text="") # Очищаем сообщение об ошибке


# Класс для работы с отдельной заметкой
class Note(Notes):
    def __init__(self):
        super().__init__()

    # Метод для отображения деталей заметки
    def show_note_details(self, event):

        name_index = notes_list.curselection()  # Получаем индекс выбранной заметки
        if name_index:
            selected_name = notes_list.get(name_index)  # Получаем название выбранной заметки
    
        window = Tk()   # Создаем новое окно
        window.iconbitmap('multi.ico')
        window.title(f"{selected_name}")    # Задаем заголовок окна
        window.geometry("300x385")
        window.resizable(0, 0)

        editor = Text(window, wrap = "word", bd=0)  # Создаем текстовое поле
        editor.pack()

        self.cur.execute(f"SELECT color FROM notes WHERE name = '{selected_name}'") # SQL запрос для получения цвета
        check = self.cur.fetchone()[0]  # Получаем результат и сохраняем

        # Проверяем наличие цвета
        if check == "Light cyan":
            editor.config(background="#E0FFFF")
        elif check == "Creamy yellow":
            editor.config(background="#FFF7D1")
        elif check == "Platinum":
            editor.config(background="#E4F9E0")
        else:
            editor.config(background="#FFFFFF")

        # Извлекаем информацию о описании заметки
        self.cur.execute(f"SELECT description FROM notes WHERE name = '{selected_name}'")
        check = self.cur.fetchone()[0]

        #данная строчка кода, чтобы не выводил ошибки, что description пустой и не возможно с ним работать
        if check:   
            self.cur.execute(f"SELECT description FROM notes WHERE name = '{selected_name}'")
            self.description = self.cur.fetchone()[0]  # Получаем значение столбца "description"
            editor.insert("1.0", self.description)  #Вводим её в поле ввода
        
        # Метод для удаления заметки
        def delete_note(event=None):
            self.cur.execute(f"DELETE FROM notes WHERE name = '{selected_name}'")
            self.conn.commit()
            self.update_notes_list()
            window.destroy()    # Закрытие текузей заметки

        # Метод для автосохранения поля ввода сраху в БД
        def auto_save_description(event=None):
            new_description = editor.get("1.0", "end")
            self.cur.execute("UPDATE notes SET description = %s WHERE name = %s", (new_description, selected_name))
            self.conn.commit()

        editor.bind("<KeyRelease>", auto_save_description)  #Самовызов при каждом изменении поля ввода
        
        # Метод для сообщения о предупреждении
        def msbox_war():
            result = askyesno(title="Предупреждение", message = "Вы действительно хотите удалить данную заметку?")
            if result: delete_note()

        # Метод для сохранения описания заметки в отдельный файл с расширением .txt
        def save_noted(name, desc):
            some = desc.get("1.0", "end")   # Для того, чтобы брать значение именно с самого поля ввода, а не БД. Иначе будут сохранять только данные при запуске описания заметки
            if len(some) == 1:  # Проверка на пустое ли поле ввода у заметки
                showinfo(title="Информация", message = "Напишите что-нибудь для сохранения файла.")
            else:
                folder_name = "Saved Notes"
                if not os.path.exists(folder_name): #Проверка на наличие созданой папки
                    os.makedirs(folder_name)

                # Сохранение файла в директории Saved Notes
                file_name = os.path.join(folder_name, f"{name}.txt")
                with open(file_name, 'w', encoding='utf8') as file:
                    file.write(some)

        # Создание главного меню, к которому будут прикрепляться разделы в будущем
        menubar = Menu(window)
        window.config(menu=menubar)
        
        # Создание раздела Menu
        notemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label = "Menu", menu = notemenu)
        notemenu2 = Menu(notemenu, tearoff=0)

        # Прописываем подразделы для Menu
        notemenu.add_cascade(label = "Color", menu = notemenu2)
        notemenu.add_command(label = "Delete Note", command = msbox_war) #Нужно создать MessageBox
        
        # Создаем команду для сохранения заметки в главном меню
        menubar.add_command(label = "Save as", command=lambda: save_noted(selected_name, editor))

        # Сохранение цвета заметки при выборе
        def save_color(color, name):
            name_index = notes_list.curselection()
            if name_index:
                selected_name = notes_list.get(name_index) 
            self.cur.execute("UPDATE notes SET color = %s WHERE name = %s ", (color, name))
            self.conn.commit() 

        # Создание подменю "Color" с определенными цветами и после сохраняем выбраный цвет в БД
        notemenu2.add_command(label="White", command=lambda: (editor.config(background="#FFFFFF"), save_color("White", selected_name)))
        notemenu2.add_command(label="Creamy yellow", command=lambda: (editor.config(background="#FFF7D1"), save_color("Creamy yellow", selected_name)))
        notemenu2.add_command(label="Platinum", command=lambda: (editor.config(background="#E4F9E0"), save_color("Platinum", selected_name)))
        notemenu2.add_command(label="Light cyan", command=lambda: (editor.config(background="#E0FFFF"), save_color("Light cyan", selected_name)))

        window.mainloop()

# Выполняем действия при прямом запуске
if __name__ == '__main__':
    # Определяем классы, как отдельные переменные
    app = Notes()
    napp = Note()

    # Запускаем взаимодействие с БД
    app.db_start()
    napp.db_start()

    # Создаем главное меню для окна root
    mainmenu = Menu(root)
    root.config(menu=mainmenu)

    # Создаем команду создания заметки
    mainmenu.add_command(label="Create Note", command=app.save_note)

    # Поле ввода имени заметки
    note_entry = customtkinter.CTkEntry(root, 
                                        width=270)
    note_entry.pack(pady=[10, 0])

    # Поле ошибки при вводе спец. символов
    error_label = Label(root, text="", fg="red", bg = "#ebebeb")
    error_label.pack(fill=X, padx = [15, 15])

    # Список имеющихся заметок
    notes_list = tk.Listbox(root, width=45, 
                            height=20, 
                            bd = 0)
    notes_list.pack(fill=BOTH, pady=[5, 10], padx=[15, 15])

    # Открытие описания заметки при 2 нажатии
    notes_list.bind("<Double-ButtonPress-1>", napp.show_note_details)

    # Обновляем список заметок
    app.update_notes_list()

    # Запускае главный цикл обработки событий для отображения и взаимодействия с приложением
    root.mainloop()

    # Закрываем подключение с БД
    app.conn.close()