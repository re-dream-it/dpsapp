from tkinter import *
from tkinter import ttk
from db import DB
from tkinter.messagebox import showerror, showwarning, showinfo
from tkinter import font
from datetime import datetime

#------ INIT ------#

# Подключение к БД
db = DB('dps.db')

# Main window
root = Tk()
root.title("ГИБДД")
root.geometry("1100x500")

# Стилизация
font_normal = font.Font(family= "Segoe UI", size=10, weight="normal", slant="roman")
root.option_add("*Font", font_normal)

font_bold = font.Font(family= "Segoe UI Semibold", size=10, weight="normal", slant="roman")

# Создание Notebook (вкладок)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill=BOTH, padx=3, pady=5)

#------ Функции и переменные ------#

entry_dl_id = StringVar(value='')
insert_dl_id = StringVar(value='')
insert_district_id = StringVar(value='')
insert_reason = StringVar(value='')
insert_amount = StringVar(value='')
confirmed = {'dl_id': StringVar(value='№В/У: '), 
             'fio': StringVar(value='ФИО: '),
             'issue_date': StringVar(value='Дата выдачи: '),
             'categories': StringVar(value='Категории: ')}

def get_dl_info():
    global confirmed, entry_dl_id, tree
    dl_id = entry_dl_id.get()

    driverinfo = db.get_dl(dl_id)

    if driverinfo == None:
        showerror(title="Ошибка запроса", message=f"Не найдено В/У с номером: {dl_id}")
        return
    
    confirmed['dl_id'].set(f"№В/У: {dl_id}")
    confirmed['fio'].set(f"ФИО: {driverinfo[2]} {driverinfo[3]} {driverinfo[4]}")
    confirmed['issue_date'].set(f"Дата выдачи: {driverinfo[1]}")
    confirmed['categories'].set(f"Категории: {driverinfo[5]}")

    tickets = db.get_dl_tickets(dl_id)
    print(tickets)

    tree.delete(*tree.get_children())

    for ticket in tickets:
        tree.insert("", END, values=ticket)

def insert_ticket():
    global insert_dl_id, insert_district_id, insert_reason, insert_amount

    if db.get_dl(insert_dl_id.get()) == None:
        showerror(title="Ошибка запроса", message=f"Не найдено В/У с номером: {insert_dl_id.get()}")
        return
    

    date = datetime.now().strftime('%Y-%m-%d')

    try:
        res = db.add_ticket(insert_district_id.get(), insert_dl_id.get(), insert_reason.get(), date, insert_amount.get())
        if res:
            showinfo(title="Внесение штрафа", message="Штраф был успешно внесен!")

    except Exception as e:
        showerror(title="Ошибка запроса", message='Неверно указан код района/сумма штрафа!')
        return


#------ Вкладка 1: Информация о В/У ------#

tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Информация о В/У")

ttk.Label(tab1, text='Укажите номер В/У:').pack(anchor=NW, pady=3)
ttk.Entry(tab1, textvariable=entry_dl_id).pack(anchor=NW, pady=3)
ttk.Button(tab1, text='Проверить', command=get_dl_info).pack(anchor=NW, pady=3)

ttk.Label(tab1, text='').pack(anchor=NW, pady=2)

ttk.Label(tab1, text='Сведения о водителе:', font=font_bold).pack(anchor=NW, pady=3)
for i in confirmed:
    ttk.Label(tab1, textvariable=confirmed[i]).pack(anchor=NW)

ttk.Label(tab1, text='').pack(anchor=NW, pady=2)

ttk.Label(tab1, text='Штрафы водителя:', font=font_bold).pack(anchor=NW, pady=3)

columns = ('date', 'id', 'reason', 'amount', 'drawnby')

tree = ttk.Treeview(tab1, columns=columns, show="headings",)
tree.pack(anchor=NW, fill=BOTH, expand=1)

tree.heading("date", text="Дата")
tree.heading("id", text="№")
tree.heading("reason", text="Причина")
tree.heading("amount", text="Cумма")
tree.heading("drawnby", text="Выписан")

tree.column('#1', stretch=NO, width=120, anchor=CENTER)
tree.column('#2', stretch=NO, width=100, anchor=CENTER)
tree.column('#3', stretch=YES, width=450)
tree.column('#4', stretch=NO, width=80, anchor=CENTER)
tree.column('#5', stretch=YES, width=300)


#------ Вкладка 2: Внесение штрафа ------#

tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Внесение штрафа")

# Добавление виджетов на вторую вкладку
ttk.Label(tab2, text='Заполните данные:', font=font_bold).grid(column=0, row=0, pady=10, padx=10, sticky=W)

ttk.Entry(tab2, textvariable=insert_dl_id).grid(column=0, row=1, padx=10)
ttk.Label(tab2, text='Номер В/У').grid(column=0, row=2)

ttk.Entry(tab2, textvariable=insert_district_id).grid(column=1, row=1, padx=10)
ttk.Label(tab2, text='Код района').grid(column=1, row=2, padx=10)

ttk.Entry(tab2, textvariable=insert_reason).grid(column=2, row=1, padx=10)
ttk.Label(tab2, text='Причина').grid(column=2, row=2, padx=10)

ttk.Entry(tab2, textvariable=insert_amount).grid(column=3, row=1, padx=10)
ttk.Label(tab2, text='Сумма').grid(column=3, row=2, padx=10)

ttk.Button(tab2, text='Внести', command=insert_ticket).grid(column=4, row=1, padx=20, rowspan=2)


#------ Запуск основного цикла ------#

root.mainloop()