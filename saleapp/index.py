import math
from datetime import datetime
from flask import render_template, request, redirect, session, jsonify, url_for
from saleapp import app, admin, login, untils, socketio, dao, utils, sendmail, decoding
from saleapp.models import UserRole
from flask_login import login_user, logout_user, login_required, current_user
import cloudinary.uploader
from flask_socketio import SocketIO, emit, join_room
from saleapp.encoding import encoding_no2
from saleapp.decoding import decoding_no2
import pandas as pd

@app.route("/", methods=('GET', 'POST'))
def home():
    data_fill = []
    len_of_flights = len(data_fill)
    if request.method == "POST":
        flights = untils.load_flights()
        start = request.form['start']
        finish = request.form['finish']
        date = request.form['date']
        date = datetime.strptime(date, "%Y-%m-%d").date()
        for f in flights:
            f_d = f.departing_at.date()
            if f.airline.departing_airport.location == start and f.airline.arriving_airport.location == finish \
                    and f_d == date:
                if 'vip' in request.form:
                    p = untils.get_prices_of_flight(f.id)
                    for pr in p:
                        if pr.rank.name == 'Thương gia':
                            data_fill.append(f)
                else:
                    data_fill.append(f)
        len_of_flights = len(data_fill)
    return render_template('index.html', data_fill=data_fill, len_of_flights=len_of_flights)


@app.route("/news")
def news():
    return render_template('news.html')


# socket

@app.route("/chatroom")
def chat_room():
    if current_user.is_authenticated:
        pass
    else:
        return redirect(url_for('user_signin'))

    user_name = decoding_no2(current_user.name)
    room = untils.get_chatroom_by_user_id(id=current_user.id)
    list_user = untils.load_message(room.room_id)

    print(room.room_id)

    user_send = [decoding_no2(untils.get_user_by_id(x.user_id).name) for x in list_user]

    user_image = [untils.get_user_by_id(x.user_id).avatar for x in list_user]

    user_id = [x.user_id for x in list_user]

    host_avatar = untils.get_host_room_avatar(room.room_id);

    user_send.pop(0)
    user_image.pop(0)
    user_id.pop(0)

    print(user_send)

    if user_name and room:

        # print(untils.load_message(room.room_id)[0].content)

        return render_template('chatroom.html', user_name=(user_name), room=room.room_id, name=current_user.name,
                               message=list_user, room_id=int(room.room_id),
                               user_send=user_send, n=len(user_send), user_image=user_image, user_id=user_id,
                               room_name=untils.get_chatroom_by_id(room.room_id),
                               host_avatar=host_avatar);
    else:
        return redirect(url_for('home'))


@app.route("/admin/chatadmin/<int:room_id>")
def chat_room_admin(room_id):
    if current_user.user_role == UserRole.ADMIN:
        print(room_id)
        user_name = decoding_no2(current_user.name)
        room = untils.get_chatroom_by_room_id(id=room_id)
        list_user = untils.load_message(room.room_id)

        user_send = [decoding_no2(untils.get_user_by_id(x.user_id).name) for x in list_user]

        user_image = [untils.get_user_by_id(x.user_id).avatar for x in list_user]

        user_id = [x.user_id for x in list_user]

        user_send.pop(0)
        user_image.pop(0)
        user_id.pop(0)

        host_avatar = untils.get_host_room_avatar(room.room_id);

        if user_name and room:
            return render_template('chatroom.html', user_name=user_name, room=room.room_id, name=current_user.name,
                                   message=list_user, room_id=int(room.room_id),
                                   user_send=user_send, n=len(user_send), user_image=user_image, user_id=user_id,
                                   room_name=untils.get_chatroom_by_id(room.room_id),
                                   host_avatar=host_avatar);

    return redirect(url_for('home'));


@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],
                                                                    data['room'],
                                                                    data['message']))

    app.logger.info("{}".format(data['user_avatar']))
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('save_message')
def handle_save_message_event(data):
    # app.logger.info("2.all_mess: " + str(data['all_message']))
    app.logger.info("2.room_id: " + str(data['room']))

    untils.save_chat_message(room_id=int(data['room']), message=data['message'], user_id=current_user.id)

    if (current_user.user_role == UserRole.ADMIN):
        print("Dd")
        untils.change_room_status(data['room'], 1)

    if (current_user.user_role == UserRole.USER):
        print("Dd1")
        untils.change_room_status(data['room'], 0)


@socketio.on('join_room')
def handle_send_room_event(data):
    app.logger.info(data['username'] + " has sent message to the room " + data['room'] + ": ")
    join_room(data['room'])

    socketio.emit('join_room_announcement', data, room=data['room'])


@app.route('/register', methods=['get', 'post'])
def user_register():
    data = pd.read_excel('data/tentinh.xlsx')
    tentinh = data['ten']
    stt = data['STT']
    table_names = ['user_angiang', 'user_ba ria – vung tau', 'user_bac giang', 'user_bac kan', 'user_bac lieu', 'user_bac ninh', 'user_ben tre', 'user_binh dinh', 'user_binh duong', 'user_binh phuoc', 'user_binh thuan', 'user_ca mau', 'user_can tho', 'user_cao bang', 'user_da nang', 'user_dak lak', 'user_dak nong', 'user_dien bien', 'user_dong nai', 'user_dong thap', 'user_gia lai', 'user_ha giang', 'user_ha nam', 'user_ha noi', 'user_ha tinh', 'user_hai duong', 'user_hai phong', 'user_hau giang', 'user_hoa binh', 'user_hung yen', 'user_khanh hoa', 'user_kien giang', 'user_kon tum', 'user_lai chau', 'user_lam dong', 'user_lang son', 'user_lao cai', 'user_long an', 'user_nam dinh', 'user_nghe an', 'user_ninh binh', 'user_ninh thuan', 'user_phu tho', 'user_phu yen', 'user_quang binh', 'user_quang nam', 'user_quang ngai', 'user_quang ninh', 'user_quang tri', 'user_soc trang', 'user_son la', 'user_tay ninh', 'user_thai binh', 'user_thai nguyen', 'user_thanh hoa', 'user_thanh pho ho chi minh', 'user_thua thien hue', 'user_tien giang', 'user_tra vinh', 'user_tuyen quang', 'user_vinh long', 'user_vinh phuc', 'user_yen bai']

    err_msg = "Mật khảu phải có đủ 8 kí tự, có số, chữ hoa, và kí tự đặc biệt"
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        diachi = request.form.get('diachi')
        confirm = request.form.get('confirm')
        avatar_path = None

        print(diachi)
        # if len(password) == 0:
        #     err_msg = "Mật khảu phải có đủ 8 kí tự, có số, chữ hoa, và kí tự đặc biệt"
        #     return render_template('register.html', err_msg=err_msg,tentinh=tentinh,stt=stt, len=63)

        # if len(password) < 8:
        #     err_msg = "Mật khẩu phải nhiều hơn 8 kí tự";
        #     return render_template('register.html', err_msg=err_msg,tentinh=tentinh,stt=stt, len=63)

        # flag = False
        # for i in password:
        #     if i == i.upper() and i.isalpha():
        #         flag = True
        #         break
        #
        # if (flag == False):
        #     err_msg = "Mật khẩu phải có chữ hoa";
        #     return render_template('register.html', err_msg=err_msg,tentinh=tentinh,stt=stt, len=63)
        #
        # flagSo = False
        # flagSpec = False
        #
        # for i in password:
        #     if i.isdigit():
        #         flagSo = True
        #     if 32 <= ord(i) <= 47 or 58 <= ord(i) <= 64:
        #         flagSpec = True
        #
        # if(flagSo == False):
        #     err_msg = "Mật khẩu phải có số";
        #     return render_template('register.html', err_msg=err_msg,tentinh=tentinh,stt=stt, len=63)
        #
        # if (flagSpec == False):
        #     err_msg = "Mật khẩu phải có kí tự đặc biệt";
        #     return render_template('register.html', err_msg=err_msg,tentinh=tentinh,stt=stt, len=63)



    try:
        if str(password) == str(confirm):
            avatar = request.files.get('avatar')
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                avatar_path = res['secure_url']

            untils.add_user(name=name,
                            username=username,
                            password=password,
                            diachi=tentinh[int(diachi) - 1],
                            email=email,
                            avatar=avatar_path)

            untils.add_user_phan_manh(stt=int(diachi) - 1,
                            name=name,
                            username=username,
                            password=password,
                            diachi=tentinh[int(diachi) - 1],
                            email=email,
                            avatar=avatar_path, data=data)
            return redirect(url_for('user_signin'))
        else:
            err_msg = "Mat khau khong khop"
            # print(err_msg)
    except Exception as ex:
        err_msg = "Mật khấu phải có đủ 8 kí tự, có số, chữ hoa, và kí tự đặc biệt"
        print(ex)


    return render_template('register.html', err_msg=err_msg,tentinh=tentinh,stt=stt, len=63)


@app.route('/user-login', methods=['get', 'post'])
def user_signin():
    err_msg = ""

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = untils.check_login(username=username, password=password)
        if user:
            login_user(user=user)
            next = request.args.get('next', 'home')
            return redirect(url_for(next))
        else:
            err_msg = "Sai tên đăng nhập hoặc mật khẩu"

    return render_template('login.html', err_msg=err_msg)


@app.route('/admin-login', methods=["POST", "GET"])
def signin_admin():
    username = request.form.get('username')
    password = request.form.get('password')

    # user = untils.check_login(username=username, password=password, role=UserRole.ADMIN)
    user = untils.check_admin_login(username=username, password=password)
    if user:
        print(1)
        login_user(user=user)

    return redirect('/admin')


@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect(url_for('home'))


@login.user_loader
def user_load(user_id):
    return untils.get_user_by_id(user_id=user_id)


@app.route('/buy-ticket')
def buy_ticket():
    airports = dao.get_airport()
    return render_template('buyticket.html', airports=airports)


@app.route('/buy-ticket/step-2')
def buy_ticket2():
    FROM = request.args.get('from')
    TO = request.args.get('to')
    date = request.args.get('date')
    flights = dao.get_flights(FROM, TO, date)
    for f in flights:
        seats = dao.get_seat()
        vip_seats_count = 0
        seats_count = 0
        for s in seats:
            if dao.is_seat_available(seat_id=s.id, flight_id=f.id):
                if s.rank_id == 1:
                    vip_seats_count += 1
                else:
                    seats_count += 1
        f.fa_amount = len(f.airportMediums)
        f.vip_seats_count = vip_seats_count
        f.seats_count = seats_count
        if vip_seats_count == 0 and seats_count == 0:
            flights.remove(f)
    return render_template('buyticket2.html', flights=flights)


@app.route('/api/cart/select-flight-<flight_id>')
def select_flight(flight_id):
    key = app.config['CART_KEY']
    if key not in session:
        session[key] = {}
    cart = session.get(key)
    cart["flight_id"] = flight_id
    session[key] = cart
    return jsonify(cart)


@app.route('/api/cart/select-seat-<seat_id>', methods=['POST'])
def select_seat(seat_id):
    key = app.config['CART_KEY']
    if key not in session or "flight_id" not in session[key]:
        return jsonify({"status": 404})

    cart = session[key]
    data = request.json
    if "seats" not in session[key]:
        cart["seats"] = {}
    price = dao.get_price(flight_id=cart["flight_id"], rank_id=str(data['rank_id']))
    if seat_id not in cart["seats"]:
        cart["seats"][seat_id] = {
            "id": str(data['id']),
            "name": str(data['name']),
            "rank_id": data['rank_id'],
            "rank": str(dao.get_rank(data['rank_id'])),
            "price": price.price
        }
        session[key] = cart
        return jsonify({"status": 201, "cart": session[key]})
    else:
        del cart["seats"][seat_id]
        session[key] = cart
        return jsonify({"status": 200, "cart": session[key], "seat_id": seat_id})


@app.route('/api/cart/total')
def total():
    key = app.config['CART_KEY']
    cart = session.get(key)
    return jsonify(utils.cart_stats(cart["seats"]))


@app.route('/buy-ticket/step-3/')
def buy_ticket3():
    key = app.config['CART_KEY']
    if key not in session or "flight_id" not in session[key]:
        return redirect("/buy-ticket")
    cart = session.get(key)
    if "seats" in cart:
        del cart["seats"]
    session[key] = cart
    flight_id = cart["flight_id"]
    vip_seats = dao.get_seat(rank_id=1)
    seats = dao.get_seat(rank_id=2)
    for vs in vip_seats:
        vs.available = dao.is_seat_available(seat_id=vs.id, flight_id=flight_id)
    for s in seats:
        s.available = dao.is_seat_available(seat_id=s.id, flight_id=flight_id)

    vs_mtrx = []
    i = 0
    while True:
        char = str(chr(65 + i))
        col = [vs for vs in vip_seats if vs.name.startswith(char)]
        if not col:
            break
        vs_mtrx.append(col)
        i = i + 1

    i = 0
    s_mtrx = []
    while True:
        char = str(chr(65 + i))
        col = [s for s in seats if s.name.startswith(char)]
        if not col:
            break
        s_mtrx.append(col)
        i = i + 1
    return render_template('selectseat.html', vip_seats=vs_mtrx, seats=s_mtrx, vs_count=len(vs_mtrx[0]),
                           s_count=len(s_mtrx[0]))


@app.route("/buy-ticket/step-4")
def cus_form():
    key = app.config['CART_KEY']
    if key not in session or "flight_id" not in session[key] or "seats" not in session[key] or len(
            session[key]["seats"]) == 0:
        return redirect("/buy-ticket")
    key = app.config['CART_KEY']
    seats = session[key]["seats"]
    return render_template('fillform.html', seats=seats)


@app.route("/api/index/")
def airports():
    data = []

    for a in untils.load_airports():
        data.append({
            'id': a.id,
            'location': a.location
        })

    return jsonify(data)


@app.route("/api/index/price/")
def prices():
    data = []

    for f in untils.load_flights():
        p = untils.get_prices_of_flight(f.id)
        for pr in p:
            data.append({
                'flight_id': pr.flight_id,
                'rank': pr.rank.name,
                'price': pr.price
            })

    return jsonify(data)


@app.route("/api/cart/pay", methods=['POST'])
def pay():
    data = request.json
    key = app.config['CART_KEY']
    cart = session.get(key)
    for s in cart["seats"]:
        cart["seats"][s]['customer'] = data['data'][s]
    total_price = utils.cart_stats(cart["seats"])['total_price']
    dao.save_order(cart=cart, total_price=total_price)
    o = dao.get_newest_order(user_id=current_user.id)

    del session[key]
    return jsonify({"order_id": o.id})


@app.route("/orders")
def get_orders():
    id = current_user.id
    ords = dao.get_order(user_id=id)
    for o in ords:
        for t in o.tickets:
            o.flight = t.flight
            break

    return render_template('orders.html', orders=ords)


@app.route('/order/<order_id>')
def detail_order(order_id):
    id = current_user.id

    ords = dao.get_order(user_id=id, order_id=order_id)
    for ticket in ords.tickets:
        ticket.customer.name = decoding.decoding_no1(ticket.customer.name)
        ticket.customer.serial = decoding.decoding_no1(ticket.customer.serial)
    return render_template('tickets.html', tickets=ords.tickets)


@app.route('/api/otp', methods=["POST"])
def send_otp():
    data = request.json
    email = data["email"]
    name = data["name"]
    otp = utils.generateOTP()
    sendmail.send(name, email, otp)

    return jsonify({"otp": otp})


@app.route('/change-profile', methods=['post', 'get'])
def change_profile():
    user = untils.get_user_by_id(current_user.id)
    user.username = decoding_no2(user.username);
    user.name = decoding_no2(user.name);
    user.email = decoding_no2(user.email);
    password = user.password


    return render_template('change_profile.html', user=user, password="*" * 8)


@app.route('/profile', methods=['post', 'get'])
def profile():
    user = untils.get_user_by_id(current_user.id)

    username = request.form.get('username')
    hoten = request.form.get('name')
    password = request.form.get('password')
    email = request.form.get('email')
    diachi = request.form.get('diachi')



    if username:
        if password.__eq__(user.password):

            untils.change_info(user_id=current_user.id, username=username, hoten=hoten, email=email, diachi=diachi)
        else:
            untils.change_info_and_pass(user_id=current_user.id, username=username, hoten=hoten, password=password,
                                        email=email, diachi=diachi)
        user.username = decoding_no2(user.username);
        user.name = decoding_no2(user.name);
        user.email = decoding_no2(user.email);
        return render_template('profile.html', user=user)
    user.username = decoding_no2(user.username);
    user.name = decoding_no2(user.name);
    user.email = decoding_no2(user.email);
    return render_template('profile.html', user=user)


if __name__ == '__main__':
    socketio.run(app, debug=True)
