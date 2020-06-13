from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta

Base = declarative_base()


class Repository:
    def __init__(self):
        engine = create_engine('sqlite:///todo.db?check_same_thread=False')
        session = sessionmaker(bind=engine)
        self.session = session()
        Base.metadata.create_all(engine)

    def find_all(self, sort_by_date=False):
        query = self.session.query(Task)
        if sort_by_date:
            query.order_by(Task.deadline)
        return query.all()

    def find_all_by_date(self, one_date):
        return self.session.query(Task).\
            filter(Task.deadline == one_date).\
            all()

    def find_all_before_date(self, one_date):
        return self.session.query(Task).\
            filter(Task.deadline < one_date).\
            all()

    def create(self, task):
        self.session.add(task)
        self.session.commit()

    def delete(self, task):
        self.session.delete(task)
        self.session.commit()


class Menu:
    def __init__(self):
        self.repository = Repository()

    @staticmethod
    def options():
        print("1) Today's tasks")
        print("2) Week's tasks")
        print("3) All tasks")
        print("4) Missed tasks")
        print("5) Add task")
        print("6) Delete task")
        print("0) Exit")

    def ask(self):
        while True:
            self.options()
            option = int(input())
            print()
            self.run(option)
            print()

    def run(self, option):
        if option == 1:
            self.today_tasks()
        elif option == 2:
            self.week_tasks()
        elif option == 3:
            self.all_tasks()
        elif option == 4:
            self.missed_tasks()
        elif option == 5:
            self.create_task()
        elif option == 6:
            self.delete_task()
        elif option == 0:
            exit()

    def today_tasks(self):
        self.date_tasks(date.today())

    def week_tasks(self):
        one_day = date.today()
        for counter in range(7):
            if counter != 0:
                print()
            self.date_tasks(one_day)
            one_day += timedelta(days=1)

    def all_tasks(self):
        print('All tasks:')
        rows = self.repository.find_all()
        if len(rows) == 0:
            print('Nothing to do!')
            return

        counter = 0
        for item in rows:
            counter += 1
            print(f"{counter})", item)

    def date_tasks(self, one_date):
        print(f'{one_date.strftime("%A")} {one_date.day} {one_date.strftime("%b")}:')
        rows = self.repository.find_all_by_date(one_date)

        if len(rows) == 0:
            print('Nothing to do!')
            return

        counter = 0
        for item in rows:
            counter += 1
            print(f"{counter})", item.task)

    def create_task(self):
        print('Enter task')
        name = input()

        print('Enter deadline')
        deadline = date.fromisoformat(input())

        task = Task(task=name, deadline=deadline)
        self.repository.create(task)

        print('The task has been added!')

    def missed_tasks(self):
        print('Missed tasks:')
        one_date = date.today()
        rows = self.repository.find_all_before_date(one_date)
        if len(rows) == 0:
            print('Nothing to missed!')
            return

        counter = 0
        for item in rows:
            counter += 1
            print(f"{counter})", item)

    def delete_task(self):
        print('Chose the number of the tasks you want to delete:')
        rows = self.repository.find_all(sort_by_date=True)
        if len(rows) == 0:
            print('Nothing to delete!')
            return

        counter = 0
        for item in rows:
            counter += 1
            print(f"{counter})", item)

        while True:
            number = int(input())
            if number > len(rows):
                print('Invalid option!')
                continue

            number -= 1
            item = rows[number]
            self.repository.delete(item)
            break


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String)
    deadline = Column(Date, default=date.today())

    def __repr__(self):
        return f'{self.task}. {self.deadline.day} {self.deadline.strftime("%b")}'


menu = Menu()
menu.ask()
