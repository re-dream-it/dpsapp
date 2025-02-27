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
root.geometry("1200x500")

# Стилизация
font_normal = font.Font(family= "Segoe UI", size=10, weight="normal", slant="roman")
root.option_add("*Font", font_normal)

font_bold = font.Font(family= "Segoe UI Semibold", size=10, weight="normal", slant="roman")

# Создание Notebook (вкладок)
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill=BOTH, padx=3, pady=5)

#------ Функции и переменные ------#

entry_dl_id = StringVar(value='')

insert = {'dl_id': StringVar(value=''),
          'district_id': StringVar(value=''),
          'reason': StringVar(value=''),
          'amount': StringVar(value='')}

categories_list = db.get_categroies()
categories = {}
for cat in categories_list:
    to_upd = {f"{cat[1]}": IntVar()}
    categories.update(to_upd)

insert_dl = {'fio': StringVar(value=''),
             'issue_date': StringVar(value=''),
             'categories': categories}

confirmed = {'dl_id': StringVar(value='№В/У: '), 
             'fio': StringVar(value='ФИО: '),
             'issue_date': StringVar(value='Дата выдачи: '),
             'categories': StringVar(value='Категории: ')}

def add_dl():
    global insert_dl
    date = datetime.now().strftime('%Y-%m-%d')
    dl_id = db.get_last_dlid()[0]+1

    fio = insert_dl['fio'].get().split(' ')
    db.add_dl(date, fio[0], fio[1], fio[2])

    for cat_name, is_on in insert_dl['categories'].items():
        if is_on.get() == 1:
            cat_id = db.get_cat_id(cat_name)[0]
            db.add_dl_cat_relation(dl_id, cat_id)
    
    showinfo(title="Успешная регистрация", message=f"Водительское удостоверение №{dl_id} было успешно зарегистрировано!")

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

    tree.delete(*tree.get_children())

    for ticket in tickets:
        tree.insert("", END, values=ticket)

def delete_ticket():
    ticket_id = tree.item(tree.selection())['values'][1]
    db.delete_ticket(ticket_id)

    showinfo(title="Внесение штрафа", message="Штраф был успешно удален!")

    get_dl_info()

def update():
    tab4.update()
    tickets = db.get_tickets()

    tree2.delete(*tree2.get_children())

    for ticket in tickets:
        tree2.insert("", END, values=(ticket[0], ticket[3], ticket[4], ticket[2], ticket[5], ticket[6]))

def insert_ticket():
    global insert

    if db.get_dl(insert['dl_id'].get()) == None:
        showerror(title="Ошибка запроса", message=f"Не найдено В/У с номером: {insert['dl_id'].get()}")
        return

    date = datetime.now().strftime('%Y-%m-%d')
    dist_id = db.get_dist_id(insert['district_id'].get())[0]

    try:
        res = db.add_ticket(dist_id, insert['dl_id'].get(), insert['reason'].get(), date, insert['amount'].get())
        if res: showinfo(title="Внесение штрафа", message="Штраф был успешно внесен!")

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

tree = ttk.Treeview(tab1, columns=columns, show="headings", height=5)
tree.pack(anchor=NW, fill=BOTH, expand=1)

ttk.Button(tab1, text='Удалить запись', command=delete_ticket).pack(anchor=NW, pady=3)

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

ttk.Entry(tab2, textvariable=insert['dl_id']).grid(column=0, row=1, padx=10)
ttk.Label(tab2, text='Номер В/У').grid(column=0, row=2)

dist_list = []
for dist in db.get_districts():
    dist_list.append(dist[1])

ttk.Combobox(tab2, values=dist_list, textvariable=insert['district_id'], width='50').grid(column=1, row=1, padx=10)
ttk.Label(tab2, text='Районное отделение').grid(column=1, row=2, padx=10)

ttk.Entry(tab2, textvariable=insert['reason']).grid(column=2, row=1, padx=10)
ttk.Label(tab2, text='Причина').grid(column=2, row=2, padx=10)

ttk.Entry(tab2, textvariable=insert['amount']).grid(column=3, row=1, padx=10)
ttk.Label(tab2, text='Сумма').grid(column=3, row=2, padx=10)

ttk.Button(tab2, text='Внести', command=insert_ticket).grid(column=4, row=1, padx=20, rowspan=2)


#------ Вкладка 3: Регистрация ------#

tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="Внесение В/У")

# Добавление виджетов на вторую вкладку
ttk.Label(tab3, text='Заполните данные:', font=font_bold).grid(column=0, row=0, pady=10, padx=10, sticky=W)

ttk.Entry(tab3, textvariable=insert_dl['fio']).grid(column=0, row=1, padx=10)
ttk.Label(tab3, text='ФИО').grid(column=0, row=2, pady=3)


for i, cat in enumerate(categories_list):
    ttk.Checkbutton(tab3, text=cat[1], variable=insert_dl['categories'][cat[1]]).grid(column=i+2, row=1, padx=10)
    span = i

ttk.Label(tab3, text='Категории').grid(column=1, row=2, columnspan=span*2, pady=3)



ttk.Button(tab3, text='Внести', command=add_dl).grid(column=0, row=3, padx=10, pady=20, rowspan=1, sticky=W)


#------ Вкладка 4: Сводка ------#

tab4 = ttk.Frame(notebook)
notebook.add(tab4, text="Сводка")

ttk.Label(tab4, text='Сводка по городу', font=font_bold).pack(anchor=N, pady=3)

ttk.Label(tab4, text='Итого по отделениям:', font=font_bold).pack(anchor=NW, pady=3)

total_sum = [0, 0]
for dist in db.get_districts():
    dist_sum = db.get_dist_summary(dist[0])
    ttk.Label(tab4, text=f"{dist[1]}: {dist_sum[1]} штрафа(ов) на сумму {dist_sum[0]} руб.").pack(anchor=NW, pady=3)
    total_sum = [total_sum[0] + dist_sum[0], total_sum[1] + dist_sum[1]]

ttk.Label(tab4, text='').pack(anchor=NW, pady=2)

ttk.Label(tab4, text=f'Итого по городу: {total_sum[1]} штрафа(ов) на сумму {total_sum[0]} руб.', font=font_bold).pack(anchor=NW, pady=3)

ttk.Label(tab4, text='').pack(anchor=NW, pady=2)

ttk.Label(tab4, text='Штрафы:', font=font_bold).pack(anchor=NW, pady=3)

columns = ('id', 'reason', 'date', 'dl_id', 'amount', 'drawnby')

tree2 = ttk.Treeview(tab4, columns=columns, show="headings", height=5)
tree2.pack(anchor=NW, fill=BOTH, expand=1)

update()

ttk.Button(tab4, text='Обновить', command=update).pack(anchor=NW, pady=3)


tree2.heading("id", text="№")
tree2.heading("reason", text="Причина")
tree2.heading("date", text="Дата")
tree2.heading("dl_id", text="№В/У")
tree2.heading("amount", text="Cумма")
tree2.heading("drawnby", text="Выписан")

tree2.column('#1', stretch=YES, width=80, anchor=CENTER)
tree2.column('#2', stretch=YES, width=450)
tree2.column('#3', stretch=NO, width=120, anchor=CENTER)
tree2.column('#4', stretch=YES, width=120, anchor=CENTER)
tree2.column('#5', stretch=NO, width=80, anchor=CENTER)
tree2.column('#6', stretch=YES, width=300)



#------ Запуск основного цикла ------#

root.mainloop()