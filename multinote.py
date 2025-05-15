import json
import os
import tkinter as tk
from tkinter import *
from tkinter.messagebox import askyesno, showinfo
import customtkinter
from pathlib import Path

# Создание объекта главного окна
root = customtkinter.CTk()
root.title("MultiNote")
root.geometry("300x400")
root.resizable(0, 0)
try:
    root.iconbitmap('multi.ico')  # Устанавливаем иконку для окна
except:
    pass  # Игнорируем ошибку, если иконки нет

# Определяем путь к папке с заметками
DOCUMENTS_DIR = Path.home() / "Documents"
NOTES_DIR = DOCUMENTS_DIR / "Multinote"
SAVED_NOTES_DIR = NOTES_DIR / "Saved Notes"

# Создаем папки, если они не существуют
NOTES_DIR.mkdir(parents=True, exist_ok=True)

# Класс для работы с заметками
class Notes():
    def __init__(self):
        self.notes_file = NOTES_DIR / "notes.json"
        self.notes = []
        self.load_notes()

    # Загрузка заметок из JSON файла
    def load_notes(self):
        if self.notes_file.exists():
            with open(self.notes_file, 'r', encoding='utf-8') as f:
                self.notes = json.load(f)
        else:
            self.notes = []

    # Сохранение заметок в JSON файл
    def save_notes(self):
        with open(self.notes_file, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, ensure_ascii=False, indent=4)

    # Обновление списка заметок
    def update_notes_list(self):
        notes_list.delete(0, customtkinter.END)  # Очищаем список заметок
        for note in self.notes:
            notes_list.insert(customtkinter.END, note['name'])  # Добавляем имя с конца полученного списка

    # Сохранение новой заметки
    def save_note(self):
        note_name = note_entry.get()  # Получаем текст заметки из поля ввода
        forbidden_chars = ['"', '\\', '|', '*', '#', ':', '/', '<', '>', '^', '?', '[', ']']
        for_sym = (' '.join(forbidden_chars))
        
        for char in forbidden_chars:  # Проверяем на наличие запрещенных символов
            if char in note_name:
                error_label.config(text=f"Ошибка: Заметка не должна содержать специальные символы: {for_sym}", wraplength=285)
                return
        
        # Проверяем, существует ли уже заметка с таким именем
        for note in self.notes:
            if note['name'] == note_name:
                error_label.config(text="Ошибка: Заметка с таким именем уже существует", wraplength=285)
                return
        
        # Добавляем новую заметку
        self.notes.append({
            'name': note_name,
            'description': '',
            'color': 'White'
        })
        
        self.save_notes()  # Сохраняем в файл
        self.update_notes_list()  # Обновляем список заметок
        note_entry.delete(0, customtkinter.END)  # Очищаем поле ввода
        error_label.config(text="")  # Очищаем сообщение об ошибке


# Класс для работы с отдельной заметкой
class Note(Notes):
    def __init__(self):
        super().__init__()

    # Отображение деталей заметки
    def show_note_details(self, event):
        try:
            name_index = notes_list.curselection()[0]  # Получаем индекс выбранной заметки
            selected_name = notes_list.get(name_index)  # Получаем название выбранной заметки
        except IndexError:
            return  # Если ничего не выбрано, просто выходим
    
        window = Toplevel()  # Создаем новое окно (используем Toplevel вместо Tk)
        try:
            window.iconbitmap('multi.ico')
        except:
            pass
        window.title(f"{selected_name}")  # Задаем заголовок окна
        window.geometry("300x385")
        window.resizable(0, 0)

        editor = Text(window, wrap="word", bd=0)  # Создаем текстовое поле
        editor.pack(fill=BOTH, expand=True)

        # Находим выбранную заметку
        selected_note = None
        for note in self.notes:
            if note['name'] == selected_name:
                selected_note = note
                break

        if not selected_note:
            window.destroy()
            return

        # Устанавливаем цвет фона
        if selected_note['color'] == "Light cyan":
            editor.config(background="#E0FFFF")
        elif selected_note['color'] == "Creamy yellow":
            editor.config(background="#FFF7D1")
        elif selected_note['color'] == "Platinum":
            editor.config(background="#E4F9E0")
        else:
            editor.config(background="#FFFFFF")

        # Вставляем текст заметки
        if selected_note['description']:
            editor.insert("1.0", selected_note['description'])

        # Удаление заметки
        def delete_note(event=None):
            self.notes = [note for note in self.notes if note['name'] != selected_name]
            self.save_notes()
            self.update_notes_list()
            window.destroy()

        # Автосохранение заметки
        def auto_save_description(event=None):
            new_description = editor.get("1.0", "end-1c")  # -1c чтобы убрать лишний перенос строки
            for note in self.notes:
                if note['name'] == selected_name:
                    note['description'] = new_description
                    break
            self.save_notes()

        editor.bind("<KeyRelease>", auto_save_description)

        # Подтверждение удаления
        def msbox_war():
            result = askyesno(title="Предупреждение", message="Вы действительно хотите удалить данную заметку?")
            if result:
                delete_note()

        # Сохранение заметки в файл
        def save_noted(name, desc):
            content = desc.get("1.0", "end-1c")
            if not content.strip():
                showinfo(title="Информация", message="Напишите что-нибудь для сохранения файла.")
            else:
                file_name = SAVED_NOTES_DIR / f"{name}.txt"
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.write(content)

        # Создание меню
        menubar = Menu(window)
        window.config(menu=menubar)
        
        # Раздел Menu
        notemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Menu", menu=notemenu)
        notemenu2 = Menu(notemenu, tearoff=0)

        # Подменю
        notemenu.add_cascade(label="Color", menu=notemenu2)
        notemenu.add_command(label="Delete Note", command=msbox_war)

        # Изменение цвета заметки
        def save_color(color):
            for note in self.notes:
                if note['name'] == selected_name:
                    note['color'] = color
                    break
            self.save_notes()
            
            if color == "Light cyan":
                editor.config(background="#E0FFFF")
            elif color == "Creamy yellow":
                editor.config(background="#FFF7D1")
            elif color == "Platinum":
                editor.config(background="#E4F9E0")
            else:
                editor.config(background="#FFFFFF")

        # Пункты меню для выбора цвета
        notemenu2.add_command(label="White", command=lambda: save_color("White"))
        notemenu2.add_command(label="Creamy yellow", command=lambda: save_color("Creamy yellow"))
        notemenu2.add_command(label="Platinum", command=lambda: save_color("Platinum"))
        notemenu2.add_command(label="Light cyan", command=lambda: save_color("Light cyan"))

        # Обработчик закрытия окна
        def on_closing():
            auto_save_description()  # Сохраняем изменения перед закрытием
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", on_closing)

# Основной код приложения
if __name__ == '__main__':
    app = Notes()
    napp = Note()

    # Главное меню
    mainmenu = Menu(root)
    root.config(menu=mainmenu)
    mainmenu.add_command(label="Create Note", command=app.save_note)

    # Поле ввода имени заметки
    note_entry = customtkinter.CTkEntry(root, width=270)
    note_entry.pack(pady=[10, 0])

    # Поле ошибки
    error_label = Label(root, text="", fg="red", bg="#ebebeb")
    error_label.pack(fill=X, padx=[15, 15])

    # Список заметок
    notes_list = tk.Listbox(root, width=45, height=20, bd=0)
    notes_list.pack(fill=BOTH, pady=[5, 10], padx=[15, 15])

    # Обработка двойного клика
    notes_list.bind("<Double-ButtonPress-1>", napp.show_note_details)

    # Обновление списка
    app.update_notes_list()

    # Главный цикл
    root.mainloop()