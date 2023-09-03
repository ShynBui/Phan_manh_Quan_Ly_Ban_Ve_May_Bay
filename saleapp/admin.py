from datetime import datetime
from gettext import gettext
from math import ceil

import numpy as np
from flask_admin.helpers import get_redirect_target
from flask_admin.model.helpers import get_mdict_item_or_list
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeLocalField, SelectField, FloatField
from wtforms.validators import InputRequired, Length

from saleapp.decoding import decoding_no2
from saleapp.models import UserRole, Flight_AirportMedium, Flight, PriceOfFlight, PlaneTicket, Airline, Airport, Airplane, Rank
from saleapp import app, db, untils
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import request, redirect, flash


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class AuthenticatedView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated

class ChatAdmin(BaseView):
    @expose('/')
    def index(self):

        room = untils.get_unreply_room()
        user = untils.get_user_by_id(current_user.id)

        user.name = decoding_no2(user.name)
        # print(room)

        return self.render('admin/chat_admin.html', room=room, user=user)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

# import pandas as pd
# class Static(BaseView):
#     @expose('/', methods=["GET", "POST"])
#     def index(self):
#
#         data = pd.read_excel('data/tentinh.xlsx')
#         tentinh = data['ten']
#         stt = data['STT']
#
#         return self.render('admin/chat_admin.html', tentinh=tentinh,stt=stt, len=63)
#
#     def is_accessible(self):
#         return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class MyAdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')


admin = Admin(app=app, name='QUẢN TRỊ MÁY BAY', template_mode='bootstrap4',
              index_view=MyAdminIndex())

class StatsView(AuthenticatedView):
    @expose('/', methods=["GET", "POST"])
    def index(self):
        total = 0.0
        from_airport = request.form.get('start')
        to_airport = request.form.get('finish')
        date = request.form.get('month')
        statistics = untils.statistic_revenue_follow_month(from_airport=from_airport,
                                                           to_airport=to_airport, date=date)
        for s in statistics:
            if s[1]:
                total = total + s[1]
        return self.render('admin/statistic.html', statistics=statistics, total=total)
import pandas as pd
class Stats(AuthenticatedView):
    @expose('/', methods=["GET", "POST"])
    def index(self):
        data = pd.read_excel('data/tentinh.xlsx')
        tentinh = data['ten']
        stt = data['STT']
        table_names = ['user_angiang', 'user_bacgiang', 'user_backan', 'user_baclieu', 'user_bacninh', 'user_bariavungtau', 'user_bentre', 'user_binhdinh', 'user_binhduong', 'user_binhphuoc', 'user_binhthuan', 'user_camau', 'user_cantho', 'user_caobang', 'user_daklak', 'user_daknong', 'user_danang', 'user_dienbien', 'user_dongnai', 'user_dongthap', 'user_gialai', 'user_hagiang', 'user_haiduong', 'user_haiphong', 'user_hanam', 'user_hanoi', 'user_hatinh', 'user_haugiang', 'user_hoabinh', 'user_hungyen', 'user_khanhhoa', 'user_kiengiang', 'user_kontum', 'user_laichau', 'user_lamdong', 'user_langson', 'user_laocai', 'user_longan', 'user_namdinh', 'user_nghean', 'user_ninhbinh', 'user_ninhthuan', 'user_phutho', 'user_phuyen', 'user_quangbinh', 'user_quangnam', 'user_quangngai', 'user_quangninh', 'user_quangtri', 'user_soctrang', 'user_sonla', 'user_tayninh', 'user_thaibinh', 'user_thainguyen', 'user_thanhhoa', 'user_thanhphohochiminh', 'user_thuathienhue', 'user_tiengiang', 'user_travinh', 'user_tuyenquang', 'user_vinhlong', 'user_vinhphuc', 'user_yenbai']
        if request.method == 'POST':
            diachi = request.form.get('diachi')
            print(diachi)
            result = (untils.select_tu_dia_chi(stt =int(diachi) - 1))
            columns = result['columns']
            result = result['rows']
            list_id = []
            list_name = []
            list_username = []
            list_password = []
            list_email = []

            for i in result:
                list_id.append(i['id'])
                list_name.append(i['name'])
                list_username.append(i['username'])
                list_password.append(i['password'])
                list_email.append(i['email'])
            return self.render('admin/stat.html', tentinh=tentinh, stt=stt, len=63,
                               result=result, list_id=list_id,list_name=list_name,
                               list_username=list_username,list_password=list_password, list_email=list_email, len_list= len(list_id))
        return self.render('admin/stat.html',tentinh=tentinh,stt=stt, len=63, result=np.NaN,list_id=[],list_name=[],
                               list_username=[],list_password=[], list_email=[], len_list= len([]))

class ModelView(AuthenticatedModelView):
    column_display_pk = True
    can_view_details = True
    can_export = True
    # edit_modal = True
    page_size = 10
    column_filters = ['id']
    column_searchable_list = ['id']


class FlightForm(FlaskForm):
    departing_at = DateTimeLocalField(name="departing_at", format="%Y-%m-%dT%H:%M",
                                      validators=[InputRequired()])
    arriving_at = DateTimeLocalField(name="arriving_at", format="%Y-%m-%dT%H:%M",
                                     validators=[InputRequired()])
    planes = SelectField('planes', choices=[])
    airlines = SelectField('airlines', choices=[])
    money = FloatField('money', validators=[InputRequired()])
    money1 = FloatField('money1', validators=[InputRequired()])

    stop_time_begin = DateTimeLocalField(name="stop_time_begin", format="%Y-%m-%dT%H:%M")
    stop_time_finish = DateTimeLocalField(name="stop_time_finish", format="%Y-%m-%dT%H:%M")

    description = StringField(name="description")
    airport = SelectField('airports', choices=[])


class FlightManagementView(ModelView):
    column_filters = ['id', 'departing_at', 'arriving_at']
    form_excluded_columns = ['airportMediums', 'tickets', 'prices']
    column_labels = {
        'id': 'Mã chuyến bay',
        'departing_at': 'Thời gian khởi hành',
        'arriving_at': 'Thời gian đến'
    }

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_create:
            return redirect(return_url)

        sts_msg = ''
        am_msg = ''
        form = FlightForm()

        form.planes.choices = [p.id for p in Airplane.query.all()]
        form.airlines.choices = [a for a in Airline.query.all()]
        form.airport.choices = [ap.name for ap in Airport.query.all()]

        if request.method == "POST":
            departing_at = form.departing_at.data
            arriving_at = form.arriving_at.data
            plane = form.planes.data
            airline = form.airlines.data
            money = form.money.data
            money1 = form.money1.data
            stb = form.stop_time_begin.data
            stf = form.stop_time_finish.data
            des = form.description.data
            ap = form.airport.data

            sts_msg = untils.check_flight(departing_at, arriving_at, plane)

            if sts_msg == 'success':
                try:
                    untils.save_flight(departing_at, arriving_at, plane, airline)
                    f = db.session.query(Flight).order_by(Flight.id.desc()).first()
                    untils.save_price(2, f.id, money)
                    untils.save_price(1, f.id, money1)

                except:
                    prices = (db.session.query(PriceOfFlight).order_by(PriceOfFlight.id.desc()).limit(2))
                    for p in prices:
                        print(p)
                        untils.del_price(p.id)
                    sts_msg = 'Đã có lỗi xảy ra khi lưu chuyến bay! Vui lòng quay lại sau!'

                if stb and stf:
                    am_msg = untils.check_stop_station(stb,stf, airline, ap, f.id)
                    if am_msg == 'success':
                        try:
                            untils.save_airport_medium(stb, stf, des, f.id, ap)
                        except:
                            prices = (db.session.query(PriceOfFlight).order_by(PriceOfFlight.id.desc()).limit(2))
                            for p in prices:
                                untils.del_price(p.id)
                            untils.del_flight(f.id)
                            am_msg = 'Đã có lỗi xảy ra khi lưu sân bay trung gian! Vui lòng quay lại sau!'
                    else:
                        prices = (db.session.query(PriceOfFlight).order_by(PriceOfFlight.id.desc()).limit(2))
                        for p in prices:
                            untils.del_price(p.id)
                        untils.del_flight(f.id)
                        am_msg = am_msg

        return self.render('admin/create.html', form=form,
                           sts_msg=sts_msg, am_msg=am_msg, return_url=return_url)

    @expose('/details/')
    def details_view(self):
        return_url = get_redirect_target() or self.get_url('.index_view')

        if not self.can_view_details:
            return redirect(return_url)

        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext('Record does not exist.'), 'error')
            return redirect(return_url)

        apm_list = Flight_AirportMedium.query.filter(
            Flight_AirportMedium.flight_id.__eq__(id)
        ).all()

        price = PriceOfFlight.query.filter(PriceOfFlight.flight_id.__eq__(id))

        return self.render("admin/flight-details.html",
                           model=model, price=price,
                           details_columns=self._details_columns,
                           get_value=self.get_detail_value,
                           apm_list=apm_list,
                           return_url=return_url)


class CustomerView(ModelView):
    column_labels = {
        'id': 'Mã vé',
        'subTotal': 'Tổng tiền'
    }

class TicketView(ModelView):
    column_labels = {
        'id': 'Mã vé',
        'subTotal': 'Tổng tiền'
    }

admin.add_view(FlightManagementView(Flight, db.session, name='Quản lý chuyến bay', endpoint='flights'))
admin.add_view(TicketView(PlaneTicket, db.session, name='Quản lý vé', endpoint='tickets'))
admin.add_view(ChatAdmin(name='ChatAdmin'))
admin.add_view(StatsView(name='Thống kê'))
admin.add_view(Stats(name='Stat'))
admin.add_view(LogoutView(name='Logout'))

