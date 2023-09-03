from datetime import datetime

from saleapp.models import User, UserRole, Room, Message, Airport, Flight, PriceOfFlight, Airline, PlaneTicket, \
    Flight_AirportMedium, Rank, PurchaseOrder
from flask_login import current_user
from sqlalchemy import func, and_, desc
from saleapp import app, db
import json
import hashlib
from sqlalchemy.sql import extract
from saleapp.encoding import encoding_no2
from saleapp.decoding import decoding_no2
from sqlalchemy import text

def get_host_room_avatar(room_id):
    user = Message.query.filter(Message.room_id.__eq__(room_id),
                                Message.content.__eq__('')).first()

    username = get_user_by_id(user.user_id);

    return username.avatar

def get_id_by_username(username):
    id = User.query.filter(User.username.__eq__(encoding_no2(username)))

    id.username = decoding_no2(id.username)
    id.email = decoding_no2(id.email)
    id.name = decoding_no2(id.name)

    return id.first()

def add_user(name, username, password, diachi, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=encoding_no2(name.strip()), username=encoding_no2(username), password=password, diachi=diachi,
                email=encoding_no2(kwargs.get('email')), avatar=kwargs.get('avatar'))


    # print(diachi)
    db.session.add(user)
    db.session.commit()

    room = Room(name="Room của " + (name).strip())

    db.session.add(room)

    db.session.commit()

    message = Message(room_id = room.id, user_id= user.id)

    db.session.add(message)

    db.session.commit()

def add_user_phan_manh(stt, name, username, password, diachi, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    data= kwargs.get('data')

    table_names = ['user_angiang', 'user_ba ria – vung tau', 'user_bac giang', 'user_bac kan', 'user_bac lieu',
                   'user_bac ninh', 'user_ben tre', 'user_binh dinh', 'user_binh duong', 'user_binh phuoc',
                   'user_binh thuan', 'user_ca mau', 'user_can tho', 'user_cao bang', 'user_da nang', 'user_dak lak',
                   'user_dak nong', 'user_dien bien', 'user_dong nai', 'user_dong thap', 'user_gia lai',
                   'user_ha giang', 'user_ha nam', 'user_ha noi', 'user_ha tinh', 'user_hai duong', 'user_hai phong',
                   'user_hau giang', 'user_hoa binh', 'user_hung yen', 'user_khanh hoa', 'user_kien giang',
                   'user_kon tum', 'user_lai chau', 'user_lam dong', 'user_lang son', 'user_lao cai', 'user_long an',
                   'user_nam dinh', 'user_nghe an', 'user_ninh binh', 'user_ninh thuan', 'user_phu tho', 'user_phu yen',
                   'user_quang binh', 'user_quang nam', 'user_quang ngai', 'user_quang ninh', 'user_quang tri',
                   'user_soc trang', 'user_son la', 'user_tay ninh', 'user_thai binh', 'user_thai nguyen',
                   'user_thanh hoa', 'user_thanh pho ho chi minh', 'user_thua thien hue', 'user_tien giang',
                   'user_tra vinh', 'user_tuyen quang', 'user_vinh long', 'user_vinh phuc', 'user_yen bai'][stt]

    query = text(f"INSERT INTO {table_names} (name, username, password, diachi, email, avatar, active, joined_date) "
                 "VALUES (:name, :username, :password, :diachi, :email, :avatar, :active, :joined_date)")

    db.session.execute(query, {'name': name, 'username': username, 'password': password,'diachi': diachi,'email': kwargs.get('email'),'avatar': kwargs.get('avatar'), 'active': 1, 'joined_date': datetime.now()})

    db.session.commit()
    print(db.engine.table_names()[stt])

def select_tu_dia_chi(stt):
    table_names = ['user_angiang', 'user_bacgiang', 'user_backan', 'user_baclieu', 'user_bacninh', 'user_bariavungtau',
                   'user_bentre', 'user_binhdinh', 'user_binhduong', 'user_binhphuoc', 'user_binhthuan', 'user_camau',
                   'user_cantho', 'user_caobang', 'user_daklak', 'user_daknong', 'user_danang', 'user_dienbien',
                   'user_dongnai', 'user_dongthap', 'user_gialai', 'user_hagiang', 'user_haiduong', 'user_haiphong',
                   'user_hanam', 'user_hanoi', 'user_hatinh', 'user_haugiang', 'user_hoabinh', 'user_hungyen',
                   'user_khanhhoa', 'user_kiengiang', 'user_kontum', 'user_laichau', 'user_lamdong', 'user_langson',
                   'user_laocai', 'user_longan', 'user_namdinh', 'user_nghean', 'user_ninhbinh', 'user_ninhthuan',
                   'user_phutho', 'user_phuyen', 'user_quangbinh', 'user_quangnam', 'user_quangngai', 'user_quangninh',
                   'user_quangtri', 'user_soctrang', 'user_sonla', 'user_tayninh', 'user_thaibinh', 'user_thainguyen',
                   'user_thanhhoa', 'user_thanhphohochiminh', 'user_thuathienhue', 'user_tiengiang', 'user_travinh',
                   'user_tuyenquang', 'user_vinhlong', 'user_vinhphuc', 'user_yenbai'][stt]
    print(table_names)
    query = f"SELECT * FROM {table_names}"
    result = db.engine.execute(query)

    # Tạo danh sách các cột
    columns = result.keys()

    # Tạo danh sách các dòng
    rows = []
    for row in result:
        # Tạo một từ điển (dictionary) để lưu trữ giá trị từng cột trong từng dòng
        row_data = {}
        for column in columns:
            # Lấy giá trị từng cột
            value = row[column]
            # Lưu trữ giá trị vào từ điển
            row_data[column] = value
        # Thêm từ điển vào danh sách các dòng
        rows.append(row_data)

    print(columns, rows)
    return {'columns': columns, 'rows': rows}


def save_chat_message(room_id, message, user_id):
    message = Message(content=encoding_no2(message), room_id=room_id, user_id=user_id)

    db.session.add(message)

    db.session.commit()

def load_message(room_id):
    message = Message.query.filter(Message.room_id.__eq__(room_id))

    for m in message:
        m.content = decoding_no2(m.content)

    return message.all()

def load_user_send(room_id):
    message = Message.query.filter(Message.room_id.__eq__(room_id))

    for m in message:
        m.content = decoding_no2(m.content)

    return message.all()
def get_chatroom_by_user_id(id):
    id_room = Message.query.filter(Message.user_id.__eq__(id))

    print(id_room)
    return id_room.first()

def get_chatroom_by_room_id(id):
    id_room = Message.query.filter(Message.room_id.__eq__(id))

    print(id_room.first())
    return id_room.first()

def get_chatroom_by_id(id):
    id_room = Room.query.filter(Room.id.__eq__(id))
    id_room[0]

    return id_room.first();


def change_room_status(id, change):
    id_room = Room.query.filter(Room.id.__eq__(id)).first()


    id_room.is_reply = change

    db.session.commit()

def check_login(username, password, role=UserRole.USER):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(encoding_no2(username)),
                                 User.password.__eq__(password),
                                 User.user_role.__eq__(role)).first()

def check_admin_login(username, password):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())

        return User.query.filter(User.username.__eq__(encoding_no2(username)),
                                 User.password.__eq__(password),
                                 User.user_role != UserRole.USER).first()

def get_unreply_room():
    room = Room.query.filter(Room.is_reply.__eq__(False))\
            .order_by(Room.date.desc())

    return room.all()

def get_user_by_id(user_id):
    get_u = User.query.get(user_id)
    return get_u

def load_airports():
    return Airport.query.all()

def load_flights():
    return Flight.query.all()

def get_prices_of_flight(flight_id):
    return PriceOfFlight.query.filter(PriceOfFlight.flight_id.__eq__(flight_id)).all()

def statistic_revenue_follow_month(from_airport=None,to_airport=None, date=None):
    stats = db.session.query(Airline.id, func.sum(PlaneTicket.subTotal), func.count(Flight.id.distinct()),
                             func.count(PlaneTicket.id)) \
        .join(Flight, Flight.airline_id.__eq__(Airline.id), isouter=True) \
        .join(PlaneTicket, PlaneTicket.flight_id.__eq__(Flight.id), isouter=True) \
        .join(PurchaseOrder, PurchaseOrder.id.__eq__(PlaneTicket.order_id), isouter=True)\
        .group_by(Airline.id)

    if from_airport and to_airport and date:
        fa = Airport.query.filter(Airport.location.__eq__(from_airport)).first()
        ta = Airport.query.filter(Airport.location.__eq__(to_airport)).first()
        date = datetime.strptime(date, "%Y-%m")
        stats = stats.filter(Airline.departing_airport_id == fa.id,
                             Airline.arriving_airport_id == ta.id)
        stats = stats.filter(extract('year', PurchaseOrder.orderDate) == date.year,
                             extract('month', PurchaseOrder.orderDate) == date.month)

    return stats.all()


def load_airports():
    return Airport.query.all()


def get_apm_by_flight_id(flight_id):
    return Flight_AirportMedium.query.filter(
        Flight_AirportMedium.flight_id.__eq__(flight_id)
    ).all()


def del_price(price_id):
    p = PriceOfFlight.query.filter(PriceOfFlight.id.__eq__(price_id)).limit(2)
    for pr in p:
        db.session.delete(pr)
    db.session.commit()


def del_apm(flight_id, airport_id):
    apm = Flight_AirportMedium.query.filter(
        Flight_AirportMedium.flight_id.__eq__(flight_id),
        Flight_AirportMedium.airport_medium_id.__eq__(airport_id)
    ).first()
    db.session.delete(apm)
    db.session.commit()


def del_flight(flight_id):
    f = Flight.query.get(flight_id)
    db.session.delete(f)
    db.session.commit()


def take_time(str_date, format):
    default_date = datetime(1900, 1, 1)
    date = datetime.strptime(str_date, format)
    time = date - default_date
    return time


def check_time_flight(departing_at, arriving_at):
    duration = arriving_at - departing_at
    rt = take_time("00:30:00", "%H:%M:%S")
    if rt:
        if duration.total_seconds() > rt.total_seconds():
            msg = "success"
        else:
            msg = "Thời gian bay chưa đạt tối thiểu"
    else:
        msg = "Hiện chưa có quy định về thời gian bay tối thiểu"

    return msg


def check_plane_in_flight(departing_at, arriving_at, plane):
    planes = Flight.query.filter(Flight.airplane_id.__eq__(plane)).all()
    if planes:
        for p in planes:
            if arriving_at < p.departing_at or p.arriving_at < departing_at:
                msg = "success"
            else:
                msg = "Máy bay đã có lịch bay trong khoảng thời gian này"
                break
    else:
        msg = "success"

    return msg


def check_flight(departing_at, arriving_at, plane):
    if departing_at and arriving_at:
        msg = check_time_flight(departing_at, arriving_at)
        if msg == 'success':
            msg = check_plane_in_flight(departing_at, arriving_at, plane)
    else:
        msg = "Thông tin chuyến bay chưa được điền đầy đủ!"
    return msg


def save_flight(departing_at, arriving_at, plane, airline):
    al = Airline.query.all()
    al_id = ''
    for a in al:
        name = f'{a.departing_airport.name} - {a.arriving_airport.name}'
        if name.__eq__(airline):
            al_id=a.id
            break

    f = Flight(departing_at=departing_at, arriving_at=arriving_at,
               airplane_id=plane, airline_id=al_id)
    db.session.add(f)
    db.session.commit()


def update_flight(model,departing_at, arriving_at, plane, airline):
    al = Airline.query.all()
    al_id = ''
    for a in al:
        name = f'{a.departing_airport.name} - {a.arriving_airport.name}'
        if name.__eq__(airline):
            al_id = a.id
            break
    model.departing_at = departing_at
    model.arriving_at = arriving_at
    model.airplane_id = plane
    model.airline_id = al_id
    db.session.commit()


def check_time_stop(begin, finish, flight_id):
    rt_begin = take_time("00:20:00", "%H:%M:%S")
    rt_finish = take_time("00:30:00", "%H:%M:%S")

    stop_duration = finish - begin
    if stop_duration.total_seconds() >= rt_begin.total_seconds() \
            and stop_duration.total_seconds() <= rt_finish.total_seconds():
        f = Flight.query.get(flight_id)
        if begin > f.departing_at and finish < f.arriving_at:
            check_duration_msg = 'success'
        else:
            check_duration_msg = 'Thời gian dừng không phù hợp với thời gian bay'
    else:
        check_duration_msg = 'Thời gian dừng không đúng quy định'

    return check_duration_msg


def check_airport_in_medium(airline, stop_airport, flight_id):
    al = Airline.query.all()
    al_fr_ap = ''
    al_to_ap = ''
    for a in al:
        name = f'{a.departing_airport.name} - {a.arriving_airport.name}'
        if name.__eq__(airline):
            al_fr_ap = a.departing_airport_id
            al_to_ap = a.arriving_airport_id
            break
    ap = Airport.query.filter(Airport.name.__eq__(stop_airport)).first()
    if ap.id != al_fr_ap and ap.id != al_to_ap:
        apm = Flight_AirportMedium.query.filter(
            Flight_AirportMedium.flight_id.__eq__(flight_id),
            Flight_AirportMedium.airport_id.__eq__(ap.id)
        ).first()
        if apm:
            check_am_msg = 'Sân bay này đã được chọn làm trung gian. Vui lòng chọn sân bay khác!'
        else:
            check_am_msg = 'success'
    else:
        check_am_msg = 'Sân bay dừng đã thuộc tuyến bay'

    return check_am_msg


def check_stop_station(begin, finish, airline, stop_airport, flight_id):
    if begin and finish:
        check_am_msg = check_time_stop(begin, finish, flight_id)
        if check_am_msg == 'success':
            check_am_msg = check_airport_in_medium(airline, stop_airport, flight_id)
    else:
        check_am_msg = 'Thông tin trạm dừng chưa được điền đầy đủ'
    return check_am_msg


def save_airport_medium(min_stop, max_stop, description, flight_id, airport):
    ap = Airport.query.filter(Airport.name.__eq__(airport)).first()
    apm = Flight_AirportMedium(stop_time_begin=min_stop, stop_time_finish=max_stop,
               description=description, flight_id=flight_id, airport_id=ap.id)
    db.session.add(apm)
    db.session.commit()


def update_apm(model, stop_time_begin, stop_time_finish, description, flight_id, airport):
    ap = Airport.query.filter(Airport.name.__eq__(airport)).first()
    model.stop_time_begin = stop_time_begin
    model.stop_time_finish = stop_time_finish
    model.description = description
    model.flight_id = flight_id
    model.airport_medium_id = ap.id
    db.session.commit()


def save_price(rank, flight_id, price):
    r = Rank.query.filter(Rank.id.__eq__(rank)).first()
    p = PriceOfFlight(rank_id=r.id, flight_id=flight_id, price=price)
    db.session.add(p)
    db.session.commit()


def change_info(user_id, username, hoten, email, diachi):
    user = get_user_by_id(user_id);

    user.name = encoding_no2(hoten)
    user.username = encoding_no2(username)
    user.email = encoding_no2(email)
    user.diachi = diachi

    db.session.commit()

    return 1;
def change_info_and_pass(user_id, username, hoten, password, email, diachi):
    user = get_user_by_id(user_id);

    user.name = encoding_no2(hoten)
    user.username = encoding_no2(username)
    user.password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user.email = encoding_no2(email)
    user.diachi = diachi

    db.session.commit()

    return 1;
