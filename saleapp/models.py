import hashlib
from saleapp.encoding import encoding_no2
from saleapp.decoding import decoding_no2
from sqlalchemy import DECIMAL, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship, backref
from saleapp import db, app
from datetime import datetime
from enum import Enum as UserEnum
from flask_login import UserMixin
import pandas as pd
import sys

class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(UserEnum):
    ADMIN = 1
    USER = 2
    STAFF = 3
    IMPORTER = 4


class User(BaseModel, UserMixin):
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(Text, default='https://as1.ftcdn.net/v2/jpg/03/46/83/96/1000_F_346839683_6nAPzbhpSkIpb8pmAwufkC7c5eD7wYws.jpg')
    email = Column(String(50))
    active = Column(Boolean, default=True)
    joined_date = Column(DateTime, default=datetime.now())
    diachi = Column(String(100), nullable=False)
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    message = relationship('Message', backref='user', lazy=True)
    orders = relationship('PurchaseOrder', backref='user', lazy=True)

    def __str__(self):
        return str(self.name)


class Customer(BaseModel):
    serial = Column(String(25), nullable=False)
    name = Column(String(50), nullable=False)
    gender = Column(String(10), nullable=False)
    dob = Column(DateTime, nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    tickets = relationship('PlaneTicket', backref='customer', lazy=True)

    def __str__(self):
        return str(self.name)


class Airplane(BaseModel):
    name = Column(String(50), nullable=False, unique=True)
    image = Column(String(100))
    flights = relationship('Flight', backref='airplane', lazy=True, passive_deletes=True, cascade="all, delete")

    def __str__(self):
        return str(self.name)


class Airport(BaseModel):
    name = Column(String(50), nullable=False)
    image = Column(String(100))
    code = Column(String(10), nullable=False, unique=True)
    location = Column(String(100), nullable=False)
    FAMediums = relationship('Flight_AirportMedium', backref='airport', lazy=True)
    departing_airline = relationship("Airline", primaryjoin="Airline.departing_airport_id==Airport.id",
                                     backref="departing_airport", lazy=True)
    arriving_airline = relationship("Airline", primaryjoin="Airline.arriving_airport_id==Airport.id",
                                    backref="arriving_airport", lazy=True)

    def __str__(self):
        return str(self.name)


class Rank(BaseModel):
    name = Column(String(25), nullable=False)
    seats = relationship('Seat', backref='rank', lazy=True)
    prices = relationship('PriceOfFlight', backref='rank', lazy=True)

    def __str__(self):
        return str(self.name)


class Seat(BaseModel):
    name = Column(String(3), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    rank_id = Column(Integer, ForeignKey(Rank.id), nullable=False)
    tickets = relationship('PlaneTicket', backref='seat', lazy=True)

    def __str__(self):
        return str(self.name)


class PurchaseOrder(BaseModel):
    total = Column(Float, nullable=False)
    orderDate = Column(DateTime, default=datetime.now())
    tickets = relationship('PlaneTicket', backref='order', lazy=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

    def __str__(self):
        return str(self.id)


class Airline(BaseModel):
    departing_airport_id = Column(Integer, ForeignKey(Airport.id), nullable=False)
    arriving_airport_id = Column(Integer, ForeignKey(Airport.id), nullable=False)
    flights = relationship('Flight', primaryjoin="Flight.airline_id==Airline.id"
                           , backref='airline', lazy=True, passive_deletes=True, cascade="all, delete")

    def __str__(self):
        return str(f'{self.departing_airport.name} - {self.arriving_airport.name}')


class Flight(BaseModel):
    departing_at = Column(DateTime, nullable=False)
    arriving_at = Column(DateTime, nullable=False)
    airplane_id = Column(Integer, ForeignKey(Airplane.id), nullable=False)
    airline_id = Column(Integer, ForeignKey(Airline.id), nullable=False)
    airportMediums = relationship('Flight_AirportMedium', backref='flight', lazy=True, passive_deletes=True, cascade="all, delete")
    tickets = relationship('PlaneTicket', backref='flight', lazy=True, passive_deletes=True, cascade="all, delete")
    prices = relationship('PriceOfFlight', backref='flight', lazy=True, passive_deletes=True, cascade="all, delete")

    def __str__(self):
        return str(self.id)


class PriceOfFlight(BaseModel):
    rank_id = Column(Integer, ForeignKey(Rank.id), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.id, ondelete="CASCADE", onupdate="cascade"), nullable=False)
    price = Column(Float, nullable=False)

    def __str__(self):
        return str(self.price)


class Flight_AirportMedium(BaseModel):
    stop_time_begin = Column(DateTime, nullable=False)
    stop_time_finish = Column(DateTime, nullable=False)
    description = Column(Text)
    airport_id = Column(Integer, ForeignKey(Airport.id, ondelete="CASCADE", onupdate="cascade"), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.id, ondelete="CASCADE", onupdate="cascade"), nullable=False)

    def __str__(self):
        return str(self.airport.name)


class PlaneTicket(BaseModel):
    subTotal = Column(Float, nullable=False)
    seat_id = Column(Integer, ForeignKey(Seat.id), nullable=False)
    customer_id = Column(Integer, ForeignKey(Customer.id), nullable=False)
    order_id = Column(Integer, ForeignKey(PurchaseOrder.id), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.id, ondelete="CASCADE", onupdate="cascade"), nullable=False)

    def __str__(self):
        return str(self.id)


class Room(db.Model):
    __tablename__ = 'room'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    is_reply = Column(Boolean, default=True)
    date = Column(DateTime, default=datetime.now())
    message = relationship('Message', backref='room', lazy=True)

    def __str__(self):
        return str(self.name)

class Message(db.Model):
    __tablename__ = 'message'

    id = id = Column(Integer, primary_key=True, autoincrement=True)
    room_id = Column(Integer, ForeignKey(Room.id), nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)

    content = Column(String(255), default= '')
    date = Column(DateTime, default= datetime.now())

    def __str__(self):
        return str(self.content)

import re
if __name__ == '__main__':
    with app.app_context():

        # tao phan manh ngang
        table = pd.read_excel('./data/tentinh.xlsx')['TenTinh'].tolist()
        print(table)

        for table_name in table:
            table_name = re.sub(r'\W+', '', table_name).replace(" ", "")
            table_class = type(
                ('User_' + table_name).capitalize(),
                (db.Model,),
                {
                    'id': db.Column(db.Integer, primary_key=True),
                    'name': db.Column(db.String(50)),
                    'username': Column(String(50), nullable=False, unique=True),
                    'password': Column(String(50), nullable=False),
                    'avatar': Column(Text,
                                     default='https://as1.ftcdn.net/v2/jpg/03/46/83/96/1000_F_346839683_6nAPzbhpSkIpb8pmAwufkC7c5eD7wYws.jpg'),
                    'email': Column(String(50)),
                    'active': Column(Boolean, default=True),
                    'joined_date': Column(DateTime, default=datetime.now()),
                    'diachi': Column(String(100), nullable=False),
                    'user_role': Column(Enum(UserRole), default=UserRole.USER),
                    '__tablename__': 'User_' + table_name.replace(" ", ""),
                    '__str__': lambda self: str(self.name)

                }
            )
            setattr(sys.modules[__name__], ('User_' + table_name.replace(" ", "")).capitalize(), table_class)
        table_names = db.engine.table_names()
        print(table_names)

        db.drop_all()
        db.create_all()

        password = str(hashlib.md5('1'.encode('utf-8')).hexdigest())
        u1 = User(name=encoding_no2('An'), username=encoding_no2('u1'), password=password,email=encoding_no2('123@gmail.com'), diachi='AnGiang',
                  user_role=UserRole.USER)
        u2 = User(name=encoding_no2('Binh'), username=encoding_no2('u2'), password=password,email=encoding_no2('12@gmail.com'), diachi='DongNai',
                  user_role=UserRole.STAFF)
        u3 = User(name=encoding_no2('Dong'), username=encoding_no2('u3'), password=password,email=encoding_no2('12e@gmail.com'), diachi='BinhDinh',
                  user_role=UserRole.ADMIN)
        db.session.add_all([u1, u2, u3])
        db.session.commit()


        room1 = Room(name="Room của " + decoding_no2(u1.name.strip()))
        room2 = Room(name="Room của " + decoding_no2(u2.name.strip()))
        room3 = Room(name="Room của " + decoding_no2(u3.name.strip()))

        db.session.add_all([room1, room2, room3])

        db.session.commit()

        message1 = Message(room_id = room1.id, user_id= u1.id)
        message2 = Message(room_id = room2.id, user_id= u2.id)
        message3 = Message(room_id = room3.id, user_id= u3.id)

        db.session.add_all([message1, message2, message3])

        db.session.commit()

        a1 = Airplane(name="A001")
        a2 = Airplane(name="A002")
        a3 = Airplane(name="A003")
        a4 = Airplane(name="A004")
        a5 = Airplane(name="A005")
        db.session.add_all([a1, a2, a3, a4, a5])

        ap1 = Airport(name="Sân bay QT Nội Bài", code="HAN", location="Hà Nội")
        ap2 = Airport(name="Sân bay QT Tân Sơn Nhất", code="SGN", location="Hồ Chí Minh")
        ap3 = Airport(name="Sân bay QT Đà Nẵng", code="DAD", location="Đà Nẵng")
        ap4 = Airport(name="Sân bay QT Phú Quốc", code="PQC", location="Phú Quốc")
        ap = [ap1, ap2, ap3, ap4]
        db.session.add_all(ap)

        r1 = Rank(name="Thương gia")
        r2 = Rank(name="Phổ thông")
        db.session.add_all([r1, r2])

        # Khởi tạo ghế thương gia
        for i in range(4):
            for j in range(4):
                col = chr(65 + j)
                name = str(col) + "0" + str(i+1)
                s = Seat(name=name, rank_id=1)
                db.session.add(s)

        # Khởi tạo ghế phổ thông
        for i in range(4, 14):
            for j in range(4):
                col = chr(65 + j)
                if i < 9:
                    row = "0" + str(i+1)
                else:
                    row = str(i+1)
                name = str(col) + row
                s = Seat(name=name, rank_id=2)
                db.session.add(s)


        # Khởi tạo airline
        for i in range(len(ap)):
            for j in range(len(ap)):
                if i != j:
                    al = Airline(departing_airport_id=i + 1, arriving_airport_id=j + 1)
                    db.session.add(al)

        # # Khởi tạo flight
        # f1 = Flight(departing_at="2023-03-03 05:00", arriving_at="2023-03-03 07:15", airplane_id=1, airline_id=2)
        # p11 = PriceOfFlight(rank_id=1, flight=f1, price="6000")
        # p12 = PriceOfFlight(rank_id=2, flight=f1, price="1900")
        # db.session.add_all([f1, p11, p12])
        #
        # f2 = Flight(departing_at="2023-03-03 07:00", arriving_at="2023-03-03 09:15", airplane_id=2, airline_id=4)
        # p21 = PriceOfFlight(rank_id=1, flight=f2, price="6000")
        # p22 = PriceOfFlight(rank_id=2, flight=f2, price="2300")
        # db.session.add_all([f2, p21, p22])
        #
        # f3 = Flight(departing_at="2023-03-03 11:45", arriving_at="2023-03-03 19:40", airplane_id=3, airline_id=4)
        # p31 = PriceOfFlight(rank_id=1, flight=f3, price="9000")
        # p32 = PriceOfFlight(rank_id=2, flight=f3, price="2600")
        # fa31 = Flight_AirportMedium(stop_time_begin="2023-03-03 13:35", stop_time_finish="2023-03-03 18:45",
        #                             airport_id=3, flight=f3)
        # db.session.add_all([f3, p31, p32, fa31])
        dem = 1
        for i in range(1, 15):
            if dem > 12 :
                dem = 1
            f1 = Flight(departing_at="2023-04-" + str(i) + " 05:00", arriving_at="2023-04-" + str(i) + " 07:15", airplane_id=1, airline_id=dem)
            p11 = PriceOfFlight(rank_id=1, flight=f1, price="6000")
            p12 = PriceOfFlight(rank_id=2, flight=f1, price="1900")
            db.session.add_all([f1, p11, p12])

            f2 = Flight(departing_at="2023-04-" + str(i) + " 07:00", arriving_at="2023-04-" + str(i) + " 09:15", airplane_id=2, airline_id=dem)
            p21 = PriceOfFlight(rank_id=1, flight=f2, price="6000")
            p22 = PriceOfFlight(rank_id=2, flight=f2, price="2300")
            db.session.add_all([f2, p21, p22])

            f3 = Flight(departing_at="2023-04-" + str(i) + " 11:45", arriving_at="2023-04-" + str(i) + " 19:40", airplane_id=3, airline_id=dem)
            p31 = PriceOfFlight(rank_id=1, flight=f3, price="9000")
            p32 = PriceOfFlight(rank_id=2, flight=f3, price="2600")
            fa31 = Flight_AirportMedium(stop_time_begin="2023-04-" + str(i) + " 13:35", stop_time_finish="2023-04-" + str(i) + " 13:55",
                                        airport_id=3, flight=f3)
            db.session.add_all([f3, p31, p32, fa31])

            f4 = Flight(departing_at="2023-04-" + str(i) + " 07:00", arriving_at="2023-04-" + str(i) + " 09:15", airplane_id=4, airline_id=dem)
            p41 = PriceOfFlight(rank_id=1, flight=f4, price="6000")
            p42 = PriceOfFlight(rank_id=2, flight=f4, price="2300")
            db.session.add_all([f4, p41, p42])

            dem+=1
        dem = 1
        for i in range(1, 15):
            if dem > 12 :
                dem = 1
            f1 = Flight(departing_at="2023-04-" + str(i) + " 18:00", arriving_at="2023-04-" + str(i) + " 22:15", airplane_id=1, airline_id=dem)
            p11 = PriceOfFlight(rank_id=1, flight=f1, price="6000")
            p12 = PriceOfFlight(rank_id=2, flight=f1, price="1900")
            db.session.add_all([f1, p11, p12])

            f2 = Flight(departing_at="2023-04-" + str(i) + " 13:00", arriving_at="2023-04-" + str(i) + " 19:15", airplane_id=2, airline_id=dem)
            p21 = PriceOfFlight(rank_id=1, flight=f2, price="6000")
            p22 = PriceOfFlight(rank_id=2, flight=f2, price="2300")
            db.session.add_all([f2, p21, p22])

            f3 = Flight(departing_at="2023-04-" + str(i) + " 00:45", arriving_at="2023-04-" + str(i) + " 7:40", airplane_id=3, airline_id=dem)
            p31 = PriceOfFlight(rank_id=1, flight=f3, price="9000")
            p32 = PriceOfFlight(rank_id=2, flight=f3, price="2600")
            fa31 = Flight_AirportMedium(stop_time_begin="2023-04-" + str(i) + " 3:35", stop_time_finish="2023-04-" + str(i) + " 4:00",
                                        airport_id=3, flight=f3)
            db.session.add_all([f3, p31, p32, fa31])

            f4 = Flight(departing_at="2023-04-" + str(i) + " 16:00", arriving_at="2023-04-" + str(i) + " 23:15", airplane_id=4, airline_id=dem)
            p41 = PriceOfFlight(rank_id=1, flight=f4, price="6000")
            p42 = PriceOfFlight(rank_id=2, flight=f4, price="2300")
            db.session.add_all([f4, p41, p42])

            dem+=1

        db.session.commit()
