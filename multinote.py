import psycopg2
import tkinter as tk
from tkinter import *
import customtkinter
from tkinter.messagebox import askyesno

# Создание объекта главного окна
root = customtkinter.CTk()
root.title("MultiNote")
root.geometry("300x400")
root.resizable(0, 0)
root.iconbitmap('multi.ico')

class Notes():
    def __init__(self):
        self.conn = None
        self.cur = None

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
        
        self.cur.execute("CREATE TABLE IF NOT EXISTS notes (id SERIAL PRIMARY KEY, name VARCHAR, description text, color VARCHAR);")
        
        self.conn.commit()
    
    def update_notes_list(self):
        notes_list.delete(0, customtkinter.END)
        self.cur.execute("SELECT * FROM notes")
        notes = self.cur.fetchall()
        for note in notes:
            note_text = note[1]
            notes_list.insert(customtkinter.END, note_text)

    def save_note(self):
        note = note_entry.get()
        self.cur.execute(f"INSERT INTO notes (name) VALUES ('{note}')")
        self.conn.commit()
        self.update_notes_list()
        note_entry.delete(0, customtkinter.END)


class Note(Notes):
    def __init__(self):
        super().__init__()

    def save_color(self, color):
        name_index = notes_list.curselection()
        if name_index:
            selected_name = notes_list.get(name_index) 
        self.cur.execute(f"UPDATE notes SET color = '{color}' WHERE name = '{selected_name}'")
        self.conn.commit()    

    def show_note_details(self, event):

        name_index = notes_list.curselection()
        if name_index:
            selected_name = notes_list.get(name_index)

        window = Tk()
        window.iconbitmap('multi.ico')
        window.title(f"{selected_name}")
        window.geometry("300x385")
        window.resizable(0, 0)

        editor = Text(window, wrap = "word", bd=0)
        editor.pack()

        self.cur.execute(f"SELECT color FROM notes WHERE name = '{selected_name}'")
        check = self.cur.fetchone()[0]

        if check == "Light cyan":
            editor.config(background="#E0FFFF")
        elif check == "Creamy yellow":
            editor.config(background="#FFF7D1")
        elif check == "Platinum":
            editor.config(background="#E4F9E0")
        else:
            editor.config(background="#FFFFFF")

        self.cur.execute(f"SELECT description FROM notes WHERE name = '{selected_name}'")
        check = self.cur.fetchone()[0]

        if check:   #данная строчка, чтобы не выводил ошибки, что description пустой и не возможно с ним работать
            self.cur.execute(f"SELECT description FROM notes WHERE name = '{selected_name}'")
            description = self.cur.fetchone()[0]  # Получаем значение столбца "description"
            editor.insert("1.0", description)
        

        def delete_note(event=None):
            name = notes_list.curselection()
            if name:
                selected_note = notes_list.get(name)
                self.cur.execute(f"DELETE FROM notes WHERE name='{selected_note}'")
                self.conn.commit()
                self.update_notes_list()
                window.destroy()

        def auto_save_description(event=None):
            new_description = editor.get("1.0", "end")
            self.cur.execute(f"UPDATE notes SET description = '{new_description}' WHERE name = '{selected_name}'")
            self.conn.commit()

        editor.bind("<KeyRelease>", auto_save_description)

        def msbox_war():
            result = askyesno(title="Предупреждение", message = "Вы действительно хотите удалить данную заметку?")
            if result: delete_note()

        menubar = Menu(window)
        window.config(menu=menubar)

        notemenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label = "Menu", menu = notemenu)
        notemenu2 = Menu(notemenu, tearoff=0)

        notemenu.add_cascade(label = "Color", menu = notemenu2)
        notemenu.add_command(label = "Delete Note", command = msbox_war) #Нужно создать MessageBox

        # Создание подменю "Color" с определенными цветами
        notemenu2.add_command(label="White", command=lambda: (editor.config(background="#FFFFFF"), self.save_color("White")))

        notemenu2.add_command(label="Creamy yellow", command=lambda: (editor.config(background="#FFF7D1"), self.save_color("Creamy yellow")))

        notemenu2.add_command(label="Platinum", command=lambda: (editor.config(background="#E4F9E0"), self.save_color("Platinum")))

        notemenu2.add_command(label="Light cyan", command=lambda: (editor.config(background="#E0FFFF"), self.save_color("Light cyan")))

        window.mainloop()


if __name__ == '__main__':
    app = Notes()
    napp = Note()
    app.db_start()
    napp.db_start()

    mainmenu = Menu(root)
    root.config(menu=mainmenu)

    mainmenu.add_command(label="Create Note", command=app.save_note)

    note_entry = customtkinter.CTkEntry(root, 
                                        width=270)
    note_entry.pack(pady=10)

    notes_list = tk.Listbox(root, width=45, 
                            height=21, 
                            bd = 0)
    notes_list.pack()

    notes_list.bind("<Double-ButtonPress-1>", napp.show_note_details)

    app.update_notes_list()

    root.mainloop()

    app.conn.close()