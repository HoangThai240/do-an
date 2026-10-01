import os
from flask import (
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
    flash,
    session
)

from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required
)

from app import (
    app,
    dao,
    login,
    db
)

from app.models import (
    UserRole,
    DeTai,
    TrangThaiDeTai,
    User,
    YeuCauChinhSua,
    TrangThaiTienDo,
    GiangVien,
    TrangThaiNghiemThu,
    TrangThaiYeuCauNghiemThu,
    YeuCauNghiemThu,
    LinhVuc,
    KetQuaNghiemThu,
    TienDo,
    TrangThaiDeTai,
    TrangThaiKhieuNai,
)

import random
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from datetime import datetime, timedelta

from dotenv import load_dotenv
import os


load_dotenv()


# ==================================================
# GỬI MÃ OTP QUA GMAIL
# ==================================================

def gui_ma_otp(email, otp):

    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")

    if not mail_username or not mail_password:
        raise Exception(
            "Chưa cấu hình MAIL_USERNAME hoặc MAIL_PASSWORD trong file .env"
        )

    subject = "Mã xác nhận đặt lại mật khẩu - Nghiên Cứu AI"

    body = f"""
Xin chào,

Bạn vừa yêu cầu đặt lại mật khẩu tài khoản trên hệ thống Nghiên Cứu AI.

Mã xác nhận OTP của bạn là:

{otp}

Mã OTP có hiệu lực trong 5 phút.

Nếu bạn không thực hiện yêu cầu này, vui lòng bỏ qua email.

Trân trọng,
Hệ thống Nghiên Cứu AI
"""

    message = MIMEMultipart()

    message["From"] = mail_username
    message["To"] = email
    message["Subject"] = subject

    message.attach(
        MIMEText(
            body,
            "plain",
            "utf-8"
        )
    )

    with smtplib.SMTP(
        "smtp.gmail.com",
        587
    ) as server:

        server.starttls()

        server.login(
            mail_username,
            mail_password
        )

        server.sendmail(
            mail_username,
            email,
            message.as_string()
        )


# ==================================================
# TRANG CHỦ
# ==================================================

@app.route('/')
def index():

    danh_sach_linh_vuc = dao.get_all_linh_vuc()

    danh_sach_de_tai = dao.get_all_de_tai()

    thong_ke = dao.thong_ke_de_tai()

    return render_template(
        'index.html',
        danh_sach_linh_vuc=danh_sach_linh_vuc,
        danh_sach_de_tai=danh_sach_de_tai,
        de_tai=danh_sach_de_tai,
        thong_ke=thong_ke,
        UserRole=UserRole
    )


# ==================================================
# ĐĂNG KÝ
# ==================================================

@app.route(
    '/register',
    methods=['GET', 'POST']
)
def register():

    error = ""

    if request.method == 'POST':

        username = request.form.get(
            'username',
            ''
        ).strip()

        password = request.form.get(
            'password',
            ''
        ).strip()

        ho_ten = request.form.get(
            'ho_ten',
            ''
        ).strip()

        email = request.form.get(
            'email',
            ''
        ).strip()

        if (
            not username
            or not password
            or not ho_ten
        ):

            error = (
                "Vui lòng nhập đầy đủ thông tin!"
            )

        elif len(password) < 6:

            error = (
                "Mật khẩu phải có ít nhất 6 ký tự!"
            )

        else:

            success, message, user = (
                dao.dang_ky(
                    username=username,
                    password=password,
                    ho_ten=ho_ten,
                    email=email if email else None,
                    role=UserRole.SINHVIEN
                )
            )

            if success:

                flash(
                    "Đăng ký tài khoản thành công!",
                    "success"
                )

                return redirect(
                    url_for(
                        'login_process'
                    )
                )

            error = message

    return render_template(
        'register.html',
        error=error
    )


# ==================================================
# ĐĂNG NHẬP
# ==================================================

@app.route(
    '/login',
    methods=['GET', 'POST']
)
def login_process():

    if current_user.is_authenticated:

        if current_user.role == UserRole.ADMIN:

            return redirect(
                url_for(
                    'admin_dashboard'
                )
            )

        if current_user.role == UserRole.GIANGVIEN:
            return redirect(
                url_for(
                    'giang_vien_dashboard'
                )
            )

        if current_user.role == UserRole.SINHVIEN:
            return redirect(
                url_for(
                    'sinh_vien'
                )
            )

        return redirect(
            url_for(
                'index'
            )
        )

    error = ""

    if request.method == 'POST':

        dinh_danh = request.form.get(
            'dinh_danh',
            ''
        ).strip()

        password = request.form.get(
            'password',
            ''
        ).strip()

        if (
            not dinh_danh
            or not password
        ):

            error = (
                "Vui lòng nhập tài khoản và mật khẩu!"
            )

        else:

            user, message = (
                dao.dang_nhap(
                    dinh_danh,
                    password
                )
            )

            if user:

                login_user(
                    user,
                    remember=True
                )

                if user.role == UserRole.ADMIN:
                    return redirect(
                        url_for(
                            'admin_dashboard'
                        )
                    )

                if user.role == UserRole.GIANGVIEN:
                    return redirect(
                        url_for(
                            'giang_vien_dashboard'
                        )
                    )

                if user.role == UserRole.SINHVIEN:
                    return redirect(
                        url_for(
                            'sinh_vien'
                        )
                    )

                return redirect(
                    url_for(
                        'index'
                    )
                )

            error = message

    return render_template(
        'login.html',
        error=error
    )


# ==================================================
# QUÊN MẬT KHẨU
# ==================================================

@app.route(
    '/quen-mat-khau',
    methods=['GET', 'POST']
)
def quen_mat_khau():

    if request.method == 'POST':

        email = request.form.get(
            'email',
            ''
        ).strip()

        if not email:

            flash(
                'Vui lòng nhập email.',
                'error'
            )

            return redirect(
                url_for(
                    'quen_mat_khau'
                )
            )

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            flash(
                'Email không tồn tại trong hệ thống.',
                'error'
            )

            return redirect(
                url_for(
                    'quen_mat_khau'
                )
            )

        otp = str(
            random.randint(
                100000,
                999999
            )
        )

        session['reset_email'] = email
        session['reset_otp'] = otp

        session['reset_otp_expire'] = (
            datetime.now()
            + timedelta(minutes=5)
        ).timestamp()

        session.pop(
            'reset_verified',
            None
        )

        try:

            gui_ma_otp(
                email,
                otp
            )

            flash(
                'Mã OTP đã được gửi đến Gmail của bạn.',
                'success'
            )

            return redirect(
                url_for(
                    'xac_thuc_otp'
                )
            )

        except Exception as e:

            print(
                "Lỗi gửi Gmail:",
                e
            )

            session.pop(
                'reset_email',
                None
            )

            session.pop(
                'reset_otp',
                None
            )

            session.pop(
                'reset_otp_expire',
                None
            )

            session.pop(
                'reset_verified',
                None
            )

            flash(
                'Không thể gửi email. '
                'Vui lòng kiểm tra cấu hình Gmail.',
                'error'
            )

            return redirect(
                url_for(
                    'quen_mat_khau'
                )
            )

    return render_template(
        'quen_mat_khau.html'
    )


# ==================================================
# XÁC THỰC OTP
# ==================================================

@app.route(
    '/xac-thuc-otp',
    methods=['GET', 'POST']
)
def xac_thuc_otp():

    email = session.get(
        'reset_email'
    )

    otp = session.get(
        'reset_otp'
    )

    expire = session.get(
        'reset_otp_expire'
    )

    if (
        not email
        or not otp
        or not expire
    ):

        flash(
            'Phiên xác nhận không hợp lệ.',
            'error'
        )

        return redirect(
            url_for(
                'quen_mat_khau'
            )
        )

    if datetime.now().timestamp() > expire:

        session.pop(
            'reset_email',
            None
        )

        session.pop(
            'reset_otp',
            None
        )

        session.pop(
            'reset_otp_expire',
            None
        )

        session.pop(
            'reset_verified',
            None
        )

        flash(
            'Mã OTP đã hết hạn. Vui lòng yêu cầu mã mới.',
            'error'
        )

        return redirect(
            url_for(
                'quen_mat_khau'
            )
        )

    if request.method == 'POST':

        otp_nhap = request.form.get(
            'otp',
            ''
        ).strip()

        if otp_nhap != otp:

            flash(
                'Mã OTP không chính xác.',
                'error'
            )

            return render_template(
                'xac_thuc_otp.html',
                email=email
            )

        session['reset_verified'] = True

        session.pop(
            'reset_otp',
            None
        )

        session.pop(
            'reset_otp_expire',
            None
        )

        return redirect(
            url_for(
                'dat_lai_mat_khau'
            )
        )

    return render_template(
        'xac_thuc_otp.html',
        email=email
    )


# ==================================================
# ĐẶT LẠI MẬT KHẨU
# ==================================================

@app.route(
    '/dat-lai-mat-khau',
    methods=['GET', 'POST']
)
def dat_lai_mat_khau():

    if not session.get(
        'reset_verified'
    ):

        flash(
            'Bạn chưa xác thực mã OTP.',
            'error'
        )

        return redirect(
            url_for(
                'quen_mat_khau'
            )
        )

    email = session.get(
        'reset_email'
    )

    if not email:

        flash(
            'Phiên đặt lại mật khẩu không hợp lệ.',
            'error'
        )

        return redirect(
            url_for(
                'quen_mat_khau'
            )
        )

    user = User.query.filter_by(
        email=email
    ).first()

    if not user:

        flash(
            'Không tìm thấy tài khoản.',
            'error'
        )

        return redirect(
            url_for(
                'quen_mat_khau'
            )
        )

    if request.method == 'POST':

        password = request.form.get(
            'password',
            ''
        )

        confirm_password = request.form.get(
            'confirm_password',
            ''
        )

        if not password:

            flash(
                'Vui lòng nhập mật khẩu mới.',
                'error'
            )

            return render_template(
                'dat_lai_mat_khau.html'
            )

        if len(password) < 6:

            flash(
                'Mật khẩu phải có ít nhất 6 ký tự.',
                'error'
            )

            return render_template(
                'dat_lai_mat_khau.html'
            )

        if password != confirm_password:

            flash(
                'Mật khẩu xác nhận không khớp.',
                'error'
            )

            return render_template(
                'dat_lai_mat_khau.html'
            )

        try:

            user.set_password(
                password
            )

            db.session.commit()

        except Exception as e:

            db.session.rollback()

            print(
                "Lỗi cập nhật mật khẩu:",
                e
            )

            flash(
                'Không thể cập nhật mật khẩu. '
                'Vui lòng thử lại.',
                'error'
            )

            return render_template(
                'dat_lai_mat_khau.html'
            )

        session.pop(
            'reset_email',
            None
        )

        session.pop(
            'reset_verified',
            None
        )

        session.pop(
            'reset_otp',
            None
        )

        session.pop(
            'reset_otp_expire',
            None
        )

        flash(
            'Đặt lại mật khẩu thành công. '
            'Bạn có thể đăng nhập.',
            'success'
        )

        return redirect(
            url_for(
                'login_process'
            )
        )

    return render_template(
        'dat_lai_mat_khau.html'
    )


# ==================================================
# ĐĂNG XUẤT
# ==================================================

@app.route('/logout')
def logout_process():

    logout_user()

    return redirect(
        url_for(
            'index'
        )
    )

@app.route('/de-tai')
@login_required
def danh_sach_de_tai():

    if current_user.role != UserRole.SINHVIEN:
        abort(403)

    de_tais = (
        DeTai.query
        .filter(
            DeTai.sinhVienId == current_user.id
        )
        .order_by(
            DeTai.id.desc()
        )
        .all()
    )

    linh_vucs = LinhVuc.query.all()

    return render_template(
        'danh_sach_de_tai.html',
        de_tais=de_tais,
        linh_vucs=linh_vucs,
        keyword='',
        linh_vuc_id='',
        la_tim_kiem=False
    )

# ==================================================
# SINH VIÊN - TRANG KIỂM TRA TRÙNG LẶP
# ==================================================

@app.route('/kiem-tra-trung-lap')
@login_required
def trang_kiem_tra_trung_lap():
    print("========== KIỂM TRA ROLE ==========")
    print("User:", current_user.username)
    print("Role:", current_user.role)
    print("Role type:", type(current_user.role))
    print("SINHVIEN:", UserRole.SINHVIEN)
    print("SINHVIEN type:", type(UserRole.SINHVIEN))
    print("===================================")

    # ==========================================
    # CHỈ SINH VIÊN ĐƯỢC SỬ DỤNG
    # ==========================================

    if current_user.role != UserRole.SINHVIEN:
        abort(403)

    # ==========================================
    # LẤY DANH SÁCH ĐỀ TÀI CỦA SINH VIÊN
    # ==========================================

    de_tais = (
        DeTai.query
        .filter(
            DeTai.sinhVienId == current_user.id
        )
        .order_by(
            DeTai.id.desc()
        )
        .all()
    )

    # ==========================================
    # HIỂN THỊ TRANG KIỂM TRA TRÙNG LẶP
    # ==========================================

    return render_template(
        'kiem_tra_trung_lap.html',
        de_tais=de_tais
    )



# ==================================================
# ĐỀ TÀI CỦA TÔI
# ==================================================

@app.route('/de-tai-cua-toi')
@login_required
def de_tai_cua_toi():

    # Chỉ sinh viên mới được xem đề tài của mình
    if current_user.role != UserRole.SINHVIEN:
        abort(403)

    keyword = request.args.get(
        'keyword',
        ''
    ).strip()

    linh_vuc_id = request.args.get(
        'linh_vuc_id',
        ''
    ).strip()

    # ==================================================
    # CHỈ LẤY ĐỀ TÀI CỦA SINH VIÊN ĐANG ĐĂNG NHẬP
    # ==================================================

    query = DeTai.query.filter(
        DeTai.sinhVienId == current_user.id
    )

    # Tìm trong đề tài của mình
    if keyword:
        query = query.filter(
            DeTai.tenDeTai.ilike(
                f'%{keyword}%'
            )
        )

    # Lọc lĩnh vực
    if linh_vuc_id:

        try:

            query = query.filter(
                DeTai.linhVucId == int(linh_vuc_id)
            )

        except ValueError:
            pass

    de_tais = (
        query
        .order_by(
            DeTai.id.desc()
        )
        .all()
    )

    linh_vucs = (
        LinhVuc.query
        .order_by(
            LinhVuc.tenLinhVuc.asc()
        )
        .all()
    )

    return render_template(
        'danh_sach_de_tai.html',
        de_tais=de_tais,
        linh_vucs=linh_vucs,
        keyword=keyword,
        linh_vuc_id=linh_vuc_id,
        la_tim_kiem=False
    )

# ==================================================
# TÌM KIẾM TOÀN BỘ ĐỀ TÀI
# ==================================================

@app.route('/tim-kiem-de-tai')
@login_required
def tim_kiem_de_tai():

    keyword = request.args.get(
        'keyword',
        ''
    ).strip()

    linh_vuc_id = request.args.get(
        'linh_vuc_id',
        ''
    ).strip()

    # ==================================================
    # QUAN TRỌNG:
    # KHÔNG LỌC THEO current_user.id
    # => TÌM TOÀN BỘ ĐỀ TÀI
    # ==================================================

    query = DeTai.query

    # Tìm theo tên đề tài
    if keyword:

        query = query.filter(
            DeTai.tenDeTai.ilike(
                f'%{keyword}%'
            )
        )

    # Lọc theo lĩnh vực
    if linh_vuc_id:

        try:

            query = query.filter(
                DeTai.linhVucId == int(linh_vuc_id)
            )

        except ValueError:
            pass

    # ==================================================
    # SẮP XẾP ĐỀ TÀI MỚI NHẤT
    # ==================================================

    de_tais = (
        query
        .order_by(
            DeTai.id.desc()
        )
        .all()
    )

    # ==================================================
    # DANH SÁCH LĨNH VỰC
    # ==================================================

    linh_vucs = (
        LinhVuc.query
        .order_by(
            LinhVuc.tenLinhVuc.asc()
        )
        .all()
    )

    return render_template(
        'danh_sach_de_tai.html',
        de_tais=de_tais,
        linh_vucs=linh_vucs,
        keyword=keyword,
        linh_vuc_id=linh_vuc_id,
        la_tim_kiem=True
    )

# ==================================================
# CHI TIẾT ĐỀ TÀI
# ==================================================

@app.route('/de-tai/<int:de_tai_id>')
def chi_tiet_de_tai(de_tai_id):
    de_tai = dao.get_de_tai_by_id(de_tai_id)

    if not de_tai:
        abort(404)

    giang_vien = None

    if de_tai.giangVienId:
        giang_vien = (
            GiangVien.query
            .filter_by(userId=de_tai.giangVienId)
            .first()
        )

    return render_template(
        'chi_tiet_de_tai.html',
        de_tai=de_tai,
        giang_vien=giang_vien
    )

# ==================================================
# THÊM ĐỀ TÀI
# ==================================================

@app.route(
    '/de-tai/them',
    methods=['GET', 'POST']
)
@login_required
def them_de_tai():

    # ==================================================
    # CHỈ SINH VIÊN MỚI ĐƯỢC ĐĂNG KÝ ĐỀ TÀI
    # ==================================================

    if current_user.role != UserRole.SINHVIEN:
        abort(403)

    # ==================================================
    # LẤY DANH SÁCH LĨNH VỰC
    # ==================================================

    danh_sach_linh_vuc = dao.get_all_linh_vuc()

    # ==================================================
    # XỬ LÝ FORM
    # ==================================================

    if request.method == 'POST':

        # ----------------------------------------------
        # ĐÚNG VỚI name="" TRONG them_de_tai.html
        # ----------------------------------------------

        ten_de_tai = request.form.get(
            'tenDeTai',
            ''
        ).strip()

        mo_ta = request.form.get(
            'moTa',
            ''
        ).strip()

        linh_vuc_id = request.form.get(
            'linh_vuc_id',
            type=int
        )

        # ----------------------------------------------
        # HIỆN TẠI FORM CHƯA CÓ 2 FIELD NÀY
        # NÊN CHO GIÁ TRỊ RỖNG
        # ----------------------------------------------

        muc_tieu = request.form.get(
            'mucTieu',
            ''
        ).strip()

        tu_khoa = request.form.get(
            'tuKhoa',
            ''
        ).strip()

        # ==================================================
        # KIỂM TRA DỮ LIỆU
        # ==================================================

        if not ten_de_tai:

            return render_template(
                'them_de_tai.html',
                danh_sach_linh_vuc=danh_sach_linh_vuc,
                error='Vui lòng nhập tên đề tài!'
            )

        if not linh_vuc_id:

            return render_template(
                'them_de_tai.html',
                danh_sach_linh_vuc=danh_sach_linh_vuc,
                error='Vui lòng chọn lĩnh vực nghiên cứu!'
            )

        if not mo_ta:

            return render_template(
                'them_de_tai.html',
                danh_sach_linh_vuc=danh_sach_linh_vuc,
                error='Vui lòng nhập mô tả đề tài!'
            )

        # ==================================================
        # LƯU ĐỀ TÀI
        # ==================================================

        success, message, de_tai = dao.them_de_tai(
            ten_de_tai=ten_de_tai,
            mo_ta=mo_ta,
            muc_tieu=muc_tieu,
            tu_khoa=tu_khoa,
            linh_vuc_id=linh_vuc_id,
            sinh_vien_id=current_user.id
        )

        # ==================================================
        # THÊM THÀNH CÔNG
        # ==================================================

        if success:

            flash(
                f"Đăng ký đề tài thành công! "
                f"Đề tài '{de_tai.tenDeTai}' "
                f"đang chờ cán bộ quản lý xét duyệt.",
                'success'
            )

            return redirect(
                url_for('sinh_vien')
            )

        # ==================================================
        # LỖI KHI LƯU
        # ==================================================

        return render_template(
            'them_de_tai.html',
            danh_sach_linh_vuc=danh_sach_linh_vuc,
            error=message
        )

    # ==================================================
    # GET
    # ==================================================

    return render_template(
        'them_de_tai.html',
        danh_sach_linh_vuc=danh_sach_linh_vuc
    )


# ==================================================
# SỬA ĐỀ TÀI
# ==================================================

@app.route(
    '/de-tai/<int:de_tai_id>/sua',
    methods=['GET', 'POST']
)
@login_required
def sua_de_tai(de_tai_id):

    de_tai = dao.get_de_tai_by_id(
        de_tai_id
    )

    if not de_tai:

        abort(404)

    # Chỉ sinh viên sở hữu đề tài hoặc ADMIN
    if (
        current_user.id != de_tai.sinhVienId
        and current_user.role != UserRole.ADMIN
    ):

        abort(403)

    danh_sach_linh_vuc = (
        dao.get_all_linh_vuc()
    )

    if request.method == 'POST':

        ten_de_tai = request.form.get(
            'ten_de_tai',
            ''
        ).strip()

        mo_ta = request.form.get(
            'mo_ta',
            ''
        ).strip()

        muc_tieu = request.form.get(
            'muc_tieu',
            ''
        ).strip()

        tu_khoa = request.form.get(
            'tu_khoa',
            ''
        ).strip()

        linh_vuc_id = request.form.get(
            'linh_vuc_id',
            type=int
        )

        if not ten_de_tai:

            return render_template(
                'sua_de_tai.html',
                de_tai=de_tai,
                danh_sach_linh_vuc=danh_sach_linh_vuc,
                error="Vui lòng nhập tên đề tài!"
            )

        if not linh_vuc_id:

            return render_template(
                'sua_de_tai.html',
                de_tai=de_tai,
                danh_sach_linh_vuc=danh_sach_linh_vuc,
                error="Vui lòng chọn lĩnh vực!"
            )

        success, message = (
            dao.cap_nhat_de_tai(
                de_tai_id=de_tai_id,
                ten_de_tai=ten_de_tai,
                mo_ta=mo_ta,
                muc_tieu=muc_tieu,
                tu_khoa=tu_khoa,
                linh_vuc_id=linh_vuc_id
            )
        )

        if success:

            # Nếu sinh viên chỉnh sửa đề tài,
            # đưa lại trạng thái chờ duyệt.
            if current_user.role == UserRole.SINHVIEN:

                de_tai.trangThai = (
                    TrangThaiDeTai.CHO_DUYET
                )

                db.session.commit()

            flash(
                "Cập nhật đề tài thành công!",
                "success"
            )

            return redirect(
                url_for(
                    'chi_tiet_de_tai',
                    de_tai_id=de_tai_id
                )
            )

        return render_template(
            'sua_de_tai.html',
            de_tai=de_tai,
            danh_sach_linh_vuc=danh_sach_linh_vuc,
            error=message
        )

    return render_template(
        'sua_de_tai.html',
        de_tai=de_tai,
        danh_sach_linh_vuc=danh_sach_linh_vuc
    )

# ==================================================
# ADMIN - XEM GỢI Ý GIẢNG VIÊN CHO ĐỀ TÀI
# ==================================================

@app.route('/admin/de-tai/<int:de_tai_id>/goi-y-giang-vien')
@login_required
def admin_goi_y_giang_vien(de_tai_id):
    if current_user.role != UserRole.ADMIN:
        abort(403)

    de_tai = dao.get_de_tai_by_id(de_tai_id)

    if not de_tai:
        abort(404)

    ket_qua = dao.goi_y_giang_vien(de_tai_id)

    return render_template(
        'goi_y_giang_vien.html',
        de_tai=de_tai,
        ket_qua=ket_qua
    )

# ==================================================
# ADMIN - CHỌN GIẢNG VIÊN CHO ĐỀ TÀI
# ==================================================

@app.route(
    '/admin/de-tai/<int:de_tai_id>/chon-giang-vien',
    methods=['POST']
)
@login_required
def admin_chon_giang_vien(de_tai_id):

    # Kiểm tra quyền quản trị viên
    if current_user.role != UserRole.ADMIN:
        abort(403)

    # Lấy đề tài
    de_tai = dao.get_de_tai_by_id(de_tai_id)

    if not de_tai:
        abort(404)

    # Lấy ID giảng viên từ form
    giang_vien_id = request.form.get('giang_vien_id')

    if not giang_vien_id:
        flash(
            'Vui lòng chọn giảng viên!',
            'error'
        )

        return redirect(
            url_for(
                'admin_goi_y_giang_vien',
                de_tai_id=de_tai_id
            )
        )

    # Chuyển ID sang số nguyên
    try:
        giang_vien_id = int(giang_vien_id)

    except (ValueError, TypeError):

        flash(
            'Giảng viên không hợp lệ!',
            'error'
        )

        return redirect(
            url_for(
                'admin_goi_y_giang_vien',
                de_tai_id=de_tai_id
            )
        )

    # ==================================================
    # GÁN GIẢNG VIÊN VÀ DUYỆT ĐỀ TÀI
    # ==================================================

    success, message = dao.duyet_de_tai(
        de_tai_id,
        giang_vien_id
    )

    if success:
        flash(
            'Đã chọn giảng viên và duyệt đề tài thành công!',
            'success'
        )

        return redirect(
            url_for('admin_dashboard')
        )

    flash(
        message,
        'error'
    )

    return redirect(
        url_for(
            'admin_goi_y_giang_vien',
            de_tai_id=de_tai_id
        )
    )

# ==================================================
# API TÌM KIẾM NGỮ NGHĨA
# ==================================================

@app.route(
    '/api/tim-kiem-ngu-nghia'
)
def api_tim_kiem_ngu_nghia():

    query = request.args.get(
        'q',
        ''
    ).strip()

    if not query:

        return jsonify([])

    danh_sach = (
        dao.tim_kiem_ngu_nghia(
            query
        )
    )

    if current_user.is_authenticated:

        dao.luu_lich_su_tim_kiem(
            current_user.id,
            query
        )

    return jsonify([
        de_tai.to_dict()
        for de_tai in danh_sach
    ])

# ==================================================
# API KIỂM TRA TRÙNG LẶP - SINH VIÊN
# ==================================================

@app.route('/api/de-tai/<int:de_tai_id>/kiem-tra-trung-lap')
@login_required
def api_kiem_tra_trung_lap(de_tai_id):

    # ======================================================
    # CHỈ SINH VIÊN ĐƯỢC KIỂM TRA
    # ======================================================

    if current_user.role != UserRole.SINHVIEN:

        return jsonify({
            "success": False,
            "message": "Chỉ sinh viên mới được sử dụng chức năng kiểm tra trùng lặp!"
        }), 403


    # ======================================================
    # TÌM ĐỀ TÀI
    # ======================================================

    de_tai = dao.get_de_tai_by_id(de_tai_id)

    if not de_tai:

        return jsonify({
            "success": False,
            "message": "Không tìm thấy đề tài!"
        }), 404


    # ======================================================
    # KIỂM TRA QUYỀN SỞ HỮU
    # ======================================================

    if de_tai.sinhVienId != current_user.id:

        return jsonify({
            "success": False,
            "message": "Bạn chỉ được kiểm tra đề tài của mình!"
        }), 403


    # ======================================================
    # TÍNH TRÙNG LẶP
    # ======================================================

    try:

        ket_qua = dao.kiem_tra_va_luu_trung_lap(
            de_tai_id
        )

    except Exception as e:

        print(
            "========================================"
        )

        print(
            "LỖI KIỂM TRA TRÙNG LẶP:"
        )

        print(
            repr(e)
        )

        print(
            "========================================"
        )

        return jsonify({
            "success": False,
            "message": "Không thể kiểm tra trùng lặp!"
        }), 500


    # ======================================================
    # CHUYỂN KẾT QUẢ SANG JSON
    # ======================================================

    data = []


    for item in ket_qua:

        sach = item.get("deTai")


        if not sach:
            continue


        # ==================================================
        # LẤY LĨNH VỰC
        # ==================================================

        linh_vuc = ""

        if getattr(sach, "linh_vuc", None):

            linh_vuc = (
                sach.linh_vuc.tenLinhVuc
                or ""
            )


        # ==================================================
        # LẤY SINH VIÊN
        # ==================================================

        sinh_vien = ""

        if getattr(sach, "sinh_vien", None):

            sinh_vien = (
                sach.sinh_vien.hoTen
                or ""
            )


        # ==================================================
        # LẤY GIẢNG VIÊN
        # ==================================================

        giang_vien = ""

        if getattr(sach, "giang_vien", None):

            giang_vien = (
                sach.giang_vien.hoTen
                or ""
            )


        # ==================================================
        # TRẠNG THÁI
        # ==================================================

        trang_thai = ""

        if getattr(sach, "trangThai", None):

            trang_thai = (
                sach.trangThai.value
                if hasattr(
                    sach.trangThai,
                    "value"
                )
                else str(
                    sach.trangThai
                )
            )


        # ==================================================
        # THÊM KẾT QUẢ
        # ==================================================

        data.append({

            "deTai": {

                "id": sach.id,

                "tenDeTai":
                    sach.tenDeTai or "",

                "linhVuc":
                    linh_vuc,

                "sinhVien":
                    sinh_vien,

                "giangVien":
                    giang_vien,

                "trangThai":
                    trang_thai,

                "mucTieu":
                    sach.mucTieu or "",

                "tuKhoa":
                    sach.tuKhoa or "",

                "moTa":
                    sach.moTa or ""

            },


            "doTuongDong":
                float(
                    item.get(
                        "doTuongDong",
                        0
                    )
                ),


            "trungLapDeTai":
                float(
                    item.get(
                        "trungLapDeTai",
                        0
                    )
                ),


            "trungLapHuongNghienCuu":
                float(
                    item.get(
                        "trungLapHuongNghienCuu",
                        0
                    )
                ),


            "trungLapMucTieu":
                float(
                    item.get(
                        "trungLapMucTieu",
                        0
                    )
                ),


            "trungLapTuKhoa":
                float(
                    item.get(
                        "trungLapTuKhoa",
                        0
                    )
                ),


            "trungLapMoTa":
                float(
                    item.get(
                        "trungLapMoTa",
                        0
                    )
                )

        })


    # ======================================================
    # TRẢ JSON
    # ======================================================

    return jsonify({

        "success": True,

        "deTaiId":
            de_tai_id,

        "data":
            data
    })

# ==================================================
# API GỢI Ý GIẢNG VIÊN
# ==================================================

@app.route(
    '/api/de-tai/<int:de_tai_id>/goi-y-giang-vien'
)
@login_required
def api_goi_y_giang_vien(de_tai_id):

    # Chỉ ADMIN được xem danh sách gợi ý giảng viên
    if current_user.role != UserRole.ADMIN:
        return jsonify({
            "success": False,
            "message": "Bạn không có quyền sử dụng chức năng này!"
        }), 403

    # Lấy đề tài
    de_tai = dao.get_de_tai_by_id(de_tai_id)

    if not de_tai:
        return jsonify({
            "success": False,
            "message": "Không tìm thấy đề tài!"
        }), 404

    # Gọi hàm gợi ý giảng viên từ DAO
    ket_qua = dao.goi_y_giang_vien(de_tai_id)

    data = []

    for item in ket_qua:

        user = item["giangVien"]
        giang_vien_info = item["giangVienInfo"]

        # Đếm số đề tài đang được hướng dẫn
        so_de_tai = DeTai.query.filter_by(
            giangVienId=user.id
        ).count()

        # Kiểm tra giới hạn hướng dẫn
        gioi_han = giang_vien_info.soLuongHuongDanToiDa

        con_kha_nang_huong_dan = (
            so_de_tai < gioi_han
            if gioi_han
            else True
        )

        data.append({
            "id": user.id,
            "userId": user.id,
            "hoTen": user.hoTen,
            "email": user.email,
            "hocVi": giang_vien_info.hocVi,
            "chuyenMon": giang_vien_info.chuyenMon,
            "linhVucNghienCuu": giang_vien_info.linhVucNghienCuu,
            "soLuongDangHuongDan": so_de_tai,
            "soLuongHuongDanToiDa": gioi_han,
            "conKhaNangHuongDan": con_kha_nang_huong_dan,
            "diemPhuHop": item["diemPhuHop"]
        })

    return jsonify({
        "success": True,
        "deTaiId": de_tai_id,
        "data": data
    })


# ==================================================
# DASHBOARD GIẢNG VIÊN
# ==================================================

@app.route('/giang-vien/dashboard')
@login_required
def giang_vien_dashboard():
    if not current_user.is_authenticated:
        return redirect(url_for('login_process'))

    if current_user.role.name != 'GIANGVIEN':
        abort(403)
    # Danh sách đề tài do giảng viên phụ trách
    danh_sach_de_tai = (
        DeTai.query
        .filter_by(
            giangVienId=current_user.id
        )
        .order_by(
            DeTai.ngayTao.desc()
        )
        .all()
    )

    # Danh sách yêu cầu chỉnh sửa của các đề tài
    # mà giảng viên hiện tại đang phụ trách
    danh_sach_yeu_cau_chinh_sua = (
        YeuCauChinhSua.query
        .join(
            DeTai,
            YeuCauChinhSua.deTaiId == DeTai.id
        )
        .filter(
            DeTai.giangVienId == current_user.id
        )
        .order_by(
            YeuCauChinhSua.ngayTao.desc()
        )
        .all()
    )

    # Đếm số yêu cầu chưa xử lý
    so_yeu_cau_chua_xu_ly = (
        YeuCauChinhSua.query
        .join(
            DeTai,
            YeuCauChinhSua.deTaiId == DeTai.id
        )
        .filter(
            DeTai.giangVienId == current_user.id,
            YeuCauChinhSua.daXuLy.is_(False)
        )
        .count()
    )

    danh_sach_yeu_cau_nghiem_thu = (
        dao.get_danh_sach_yeu_cau_nghiem_thu_cua_giang_vien(
            current_user.id
        )
    )
    # Danh sách khiếu nại kết quả nghiệm thu đang chờ xử lý
    danh_sach_khieu_nai = (
        dao.get_khieu_nai_cho_xu_ly()
    )

    return render_template(
        'giang_vien_dashboard.html',
        danh_sach_de_tai=danh_sach_de_tai,
        danh_sach_yeu_cau_chinh_sua=danh_sach_yeu_cau_chinh_sua,
        so_yeu_cau_chua_xu_ly=so_yeu_cau_chua_xu_ly,
        danh_sach_yeu_cau_nghiem_thu=danh_sach_yeu_cau_nghiem_thu,
        danh_sach_khieu_nai=danh_sach_khieu_nai
    )



# ==========================================================
# GIẢNG VIÊN - THEO DÕI TIẾN ĐỘ VÀ NHẬN XÉT
# ==========================================================

@app.route(
    '/giang-vien/de-tai/<int:de_tai_id>/tien-do',
    methods=['GET', 'POST']
)
@login_required
def giang_vien_tien_do(de_tai_id):

    # Chỉ giảng viên mới được sử dụng
    if current_user.role != UserRole.GIANGVIEN:
        return (
            f"Bạn không có quyền truy cập.<br>"
            f"Role hiện tại: {current_user.role}<br>"
            f"Role giảng viên: {UserRole.GIANGVIEN}",
            403
        )

    # Lấy đề tài
    de_tai = dao.get_de_tai_by_id(de_tai_id)

    if not de_tai:
        abort(404)

    # Chỉ giảng viên đang được phân công mới được xem
    if de_tai.giangVienId != current_user.id:
        abort(403)

    # ======================================================
    # GIẢNG VIÊN GỬI NHẬN XÉT
    # ======================================================

    if request.method == 'POST':

        # Lấy ID mốc tiến độ
        tien_do_id = request.form.get(
            'tien_do_id',
            type=int
        )

        # --------------------------------------------------
        # Đây là form NHẬN XÉT của giảng viên
        # Không yêu cầu tieu_de
        # --------------------------------------------------

        if tien_do_id:

            tien_do = dao.get_tien_do_by_id(
                tien_do_id
            )

            if not tien_do:
                abort(404)

            # Đảm bảo mốc tiến độ thuộc đúng đề tài
            if tien_do.deTaiId != de_tai_id:
                abort(403)

            # Lấy nhận xét
            nhan_xet = request.form.get(
                'nhan_xet_giang_vien',
                ''
            ).strip()

            # Không bắt buộc phải nhập tiêu đề
            # Giữ nguyên toàn bộ thông tin tiến độ
            ket_qua = dao.cap_nhat_tien_do(
                tien_do_id=tien_do.id,

                # Giữ nguyên tiêu đề sinh viên
                tieu_de=tien_do.tieuDe,

                # Giữ nguyên nội dung sinh viên
                noi_dung=tien_do.noiDung,

                # Giữ nguyên %
                phan_tram=tien_do.phanTram,

                # Giữ nguyên trạng thái
                trang_thai=tien_do.trangThai,

                # Chỉ thay đổi nhận xét giảng viên
                nhan_xet_giang_vien=nhan_xet
            )

            if ket_qua[0]:

                flash(
                    'Đã lưu nhận xét cho sinh viên!',
                    'success'
                )

            else:

                flash(
                    ket_qua[1],
                    'error'
                )

            return redirect(
                url_for(
                    'giang_vien_tien_do',
                    de_tai_id=de_tai_id
                )
            )

        # Không có tien_do_id
        flash(
            'Không xác định được mốc tiến độ cần nhận xét.',
            'error'
        )

        return redirect(
            url_for(
                'giang_vien_tien_do',
                de_tai_id=de_tai_id
            )
        )

    # ======================================================
    # GET - HIỂN THỊ TIẾN ĐỘ
    # ======================================================

    danh_sach_tien_do = dao.get_tien_do_de_tai(
        de_tai_id
    )

    return render_template(
        'giang_vien_tien_do.html',
        de_tai=de_tai,
        danh_sach_tien_do=danh_sach_tien_do
    )

# ==================================================
# SINH VIÊN GỬI YÊU CẦU NGHIỆM THU
# ==================================================

@app.route(
    '/sinh-vien/de-tai/<int:de_tai_id>/gui-nghiem-thu',
    methods=['POST']
)
@login_required
def sinh_vien_gui_nghiem_thu(de_tai_id):

    if current_user.role != UserRole.SINHVIEN:
        abort(403)

    de_tai = dao.get_de_tai_by_id(
        de_tai_id
    )

    if not de_tai:
        abort(404)

    # Chỉ chủ đề tài mới được gửi
    if de_tai.sinhVienId != current_user.id:
        abort(403)

    # ==================================================
    # PHẢI HOÀN THÀNH TIẾN ĐỘ 100% MỚI ĐƯỢC GỬI
    # YÊU CẦU NGHIỆM THU
    # ==================================================

    danh_sach_tien_do = dao.get_tien_do_de_tai(
        de_tai_id
    )

    tien_do = None

    if danh_sach_tien_do:
        tien_do = max(
            danh_sach_tien_do,
            key=lambda x: (
                x.ngayCapNhat
                if x.ngayCapNhat
                else datetime.min
            )
        )

    if (
            not tien_do
            or tien_do.phanTram is None
            or tien_do.phanTram < 100
    ):
        flash(
            'Đề tài chưa hoàn thành 100% tiến độ nên chưa thể gửi nghiệm thu!',
            'error'
        )

        return redirect(
            url_for(
                'sinh_vien_nghiem_thu'
            )
        )

    # Kiểm tra đã gửi chưa
    yeu_cau = dao.get_yeu_cau_nghiem_thu(
        de_tai_id
    )

    if yeu_cau:

        flash(
            'Đề tài này đã gửi yêu cầu nghiệm thu!',
            'error'
        )

        return redirect(
            url_for(
                'sinh_vien_nghiem_thu'
            )
        )

    noi_dung = request.form.get(
        'noi_dung',
        ''
    ).strip()

    success, message, yeu_cau = (
        dao.tao_yeu_cau_nghiem_thu(
            de_tai_id=de_tai_id,
            nguoi_yeu_cau_id=current_user.id,
            noi_dung=noi_dung
        )
    )

    if success:

        flash(
            message,
            'success'
        )

    else:

        flash(
            message,
            'error'
        )

    return redirect(
        url_for(
            'sinh_vien_nghiem_thu'
        )
    )

@app.route(
    '/giang-vien/de-tai/<int:de_tai_id>/nghiem-thu',
    methods=['GET', 'POST']
)
@login_required
def giang_vien_nghiem_thu(de_tai_id):

    # ==========================================
    # CHỈ GIẢNG VIÊN
    # ==========================================

    if current_user.role != UserRole.GIANGVIEN:
        abort(403)

    # ==========================================
    # LẤY ĐỀ TÀI
    # ==========================================

    de_tai = dao.get_de_tai_by_id(
        de_tai_id
    )

    if not de_tai:
        abort(404)

    # ==========================================
    # CHỈ GIẢNG VIÊN ĐƯỢC PHÂN CÔNG
    # ==========================================

    if de_tai.giangVienId != current_user.id:
        abort(403)

    # ==========================================
    # LẤY TIẾN ĐỘ
    # ==========================================

    danh_sach_tien_do = (
        dao.get_tien_do_de_tai(
            de_tai_id
        )
    )

    tien_do = None

    if danh_sach_tien_do:

        tien_do = max(
            danh_sach_tien_do,
            key=lambda x: (
                x.ngayCapNhat
                if x.ngayCapNhat
                else datetime.min
            )
        )

    # ==========================================
    # PHẢI ĐẠT 100%
    # ==========================================

    if (
        not tien_do
        or tien_do.phanTram is None
        or tien_do.phanTram < 100
    ):

        flash(
            'Đề tài chưa hoàn thành 100% nên chưa thể nghiệm thu.',
            'warning'
        )

        return redirect(
            url_for(
                'giang_vien_tien_do',
                de_tai_id=de_tai_id
            )
        )

    # ==========================================
    # KIỂM TRA ĐÃ NGHIỆM THU CHƯA
    # ==========================================

    ket_qua = dao.get_ket_qua_nghiem_thu(
        de_tai_id
    )

    if ket_qua:

        flash(
            'Đề tài này đã được nghiệm thu.',
            'warning'
        )

        return redirect(
            url_for(
                'giang_vien_dashboard'
            )
        )

    # ==========================================
    # POST
    # ==========================================

    if request.method == 'POST':

        diem_raw = request.form.get(
            'diem',
            ''
        ).strip()

        nhan_xet = request.form.get(
            'nhan_xet',
            ''
        ).strip()

        ket_luan = request.form.get(
            'ket_luan',
            ''
        ).strip()

        trang_thai_form = request.form.get(
            'trang_thai',
            ''
        ).strip()

        # --------------------------------------
        # KIỂM TRA ĐIỂM
        # --------------------------------------

        if not diem_raw:

            flash(
                'Vui lòng nhập điểm nghiệm thu.',
                'error'
            )

            return redirect(
                url_for(
                    'giang_vien_nghiem_thu',
                    de_tai_id=de_tai_id
                )
            )

        try:

            diem = float(diem_raw)

        except ValueError:

            flash(
                'Điểm nghiệm thu không hợp lệ.',
                'error'
            )

            return redirect(
                url_for(
                    'giang_vien_nghiem_thu',
                    de_tai_id=de_tai_id
                )
            )

        # --------------------------------------
        # ĐIỂM 0 - 10
        # --------------------------------------

        if diem < 0 or diem > 10:

            flash(
                'Điểm nghiệm thu phải từ 0 đến 10.',
                'error'
            )

            return redirect(
                url_for(
                    'giang_vien_nghiem_thu',
                    de_tai_id=de_tai_id
                )
            )

        # --------------------------------------
        # KIỂM TRA KẾT QUẢ
        # --------------------------------------

        if trang_thai_form not in (
            'DAT',
            'KHONG_DAT'
        ):

            flash(
                'Vui lòng chọn kết quả nghiệm thu.',
                'error'
            )

            return redirect(
                url_for(
                    'giang_vien_nghiem_thu',
                    de_tai_id=de_tai_id
                )
            )

        try:

            trang_thai = TrangThaiNghiemThu(
                trang_thai_form
            )

        except ValueError:

            flash(
                'Trạng thái nghiệm thu không hợp lệ.',
                'error'
            )

            return redirect(
                url_for(
                    'giang_vien_nghiem_thu',
                    de_tai_id=de_tai_id
                )
            )

        # ======================================
        # LƯU KẾT QUẢ
        # ======================================

        success, message, ket_qua = (
            dao.them_ket_qua_nghiem_thu(

                de_tai_id=de_tai_id,

                nguoi_nghiem_thu_id=current_user.id,

                diem=diem,

                nhan_xet=nhan_xet,

                ket_luan=ket_luan,

                trang_thai=trang_thai
            )
        )

        if not success:

            flash(
                message,
                'error'
            )

            return redirect(
                url_for(
                    'giang_vien_nghiem_thu',
                    de_tai_id=de_tai_id
                )
            )

        flash(
            'Đã nghiệm thu và lưu kết quả thành công!',
            'success'
        )

        return redirect(
            url_for(
                'giang_vien_dashboard'
            )
        )

    # ==========================================
    # GET
    # ==========================================

    return render_template(
        'giang_vien_nghiem_thu.html',
        de_tai=de_tai,
        tien_do=tien_do,
        ket_qua=ket_qua,
        TrangThaiNghiemThu=TrangThaiNghiemThu
    )

# ==================================================
# ADMIN DASHBOARD
# ==================================================

@app.route('/admin/dashboard')
@app.route('/admin')
@login_required
def admin_dashboard():

    if current_user.role != UserRole.ADMIN:

        abort(403)

    thong_ke = (
        dao.thong_ke_de_tai()
    )

    danh_sach_cho_duyet = (
        DeTai.query
        .filter_by(
            trangThai=
            TrangThaiDeTai.CHO_DUYET
        )
        .order_by(
            DeTai.ngayTao.desc()
        )
        .all()
    )

    danh_sach_giang_vien = (
        dao.get_all_giang_vien()
    )

    return render_template(
        'admin_dashboard.html',
        thong_ke=thong_ke,
        danh_sach_cho_duyet=danh_sach_cho_duyet,
        danh_sach_giang_vien=danh_sach_giang_vien
    )


# ==================================================
# ADMIN DUYỆT ĐỀ TÀI
# ==================================================

@app.route(
    '/admin/de-tai/<int:de_tai_id>/duyet',
    methods=['POST']
)
@login_required
def admin_duyet_de_tai(de_tai_id):

    if current_user.role != UserRole.ADMIN:

        abort(403)

    de_tai = dao.get_de_tai_by_id(
        de_tai_id
    )

    if not de_tai:

        abort(404)

    giang_vien_id = request.form.get(
        'giang_vien_id',
        type=int
    )

    success, message = dao.duyet_de_tai(
        de_tai_id,
        giang_vien_id
    )

    if success:

        flash(
            "Duyệt đề tài thành công!",
            "success"
        )

    else:

        flash(
            message,
            "error"
        )

    return redirect(
        url_for(
            'admin_dashboard'
        )
    )


# ==================================================
# ADMIN TỪ CHỐI ĐỀ TÀI
# ==================================================

@app.route(
    '/admin/de-tai/<int:de_tai_id>/tu-choi',
    methods=['POST']
)
@login_required
def admin_tu_choi_de_tai(de_tai_id):

    if current_user.role != UserRole.ADMIN:

        abort(403)

    de_tai = dao.get_de_tai_by_id(
        de_tai_id
    )

    if not de_tai:

        abort(404)

    success, message = (
        dao.tu_choi_de_tai(
            de_tai_id
        )
    )

    if success:

        flash(
            "Đã từ chối đề tài!",
            "success"
        )

    else:

        flash(
            message,
            "error"
        )

    return redirect(
        url_for(
            'admin_dashboard'
        )
    )


# ==================================================
# ADMIN QUẢN LÝ ĐỀ TÀI
# ==================================================

@app.route(
    '/admin/de-tai'
)
@login_required
def admin_quan_ly_de_tai():

    if current_user.role != UserRole.ADMIN:

        abort(403)

    danh_sach = (
        dao.get_all_de_tai()
    )

    return render_template(
        'admin_de_tai.html',
        danh_sach=danh_sach
    )


# ==================================================
# ADMIN XÓA ĐỀ TÀI
# ==================================================

@app.route(
    '/admin/de-tai/<int:de_tai_id>/xoa',
    methods=['POST']
)
@login_required
def admin_xoa_de_tai(de_tai_id):

    if current_user.role != UserRole.ADMIN:

        abort(403)

    de_tai = dao.get_de_tai_by_id(
        de_tai_id
    )

    if not de_tai:

        abort(404)

    success, message = (
        dao.xoa_de_tai(
            de_tai_id
        )
    )

    if success:

        flash(
            "Xóa đề tài thành công!",
            "success"
        )

    else:

        flash(
            message,
            "error"
        )

    return redirect(
        url_for(
            'admin_quan_ly_de_tai'
        )
    )


# ==================================================
# ADMIN QUẢN LÝ NGƯỜI DÙNG
# ==================================================

@app.route(
    '/admin/nguoi-dung'
)
@login_required
def admin_nguoi_dung():

    if current_user.role != UserRole.ADMIN:

        abort(403)

    danh_sach_user = (
        dao.get_all_users()
    )

    return render_template(
        'admin_nguoi_dung.html',
        danh_sach_user=danh_sach_user
    )


# ==================================================
# ADMIN KHÓA USER
# ==================================================

@app.route(
    '/admin/nguoi-dung/<int:user_id>/khoa',
    methods=['POST']
)
@login_required
def admin_khoa_user(user_id):

    if current_user.role != UserRole.ADMIN:

        abort(403)

    if current_user.id == user_id:

        abort(403)

    success, message = (
        dao.khoa_user(
            user_id
        )
    )

    if success:

        flash(
            "Khóa tài khoản thành công!",
            "success"
        )

    else:

        flash(
            message,
            "error"
        )

    return redirect(
        url_for(
            'admin_nguoi_dung'
        )
    )


# ==================================================
# ADMIN MỞ KHÓA USER
# ==================================================

@app.route(
    '/admin/nguoi-dung/<int:user_id>/mo-khoa',
    methods=['POST']
)
@login_required
def admin_mo_khoa_user(user_id):

    if current_user.role != UserRole.ADMIN:

        abort(403)

    success, message = (
        dao.mo_khoa_user(
            user_id
        )
    )

    if success:

        flash(
            "Mở khóa tài khoản thành công!",
            "success"
        )

    else:

        flash(
            message,
            "error"
        )

    return redirect(
        url_for(
            'admin_nguoi_dung'
        )
    )


# ==================================================
# ADMIN QUẢN LÝ LĨNH VỰC
# ==================================================

@app.route(
    '/admin/linh-vuc'
)
@login_required
def admin_linh_vuc():

    if current_user.role != UserRole.ADMIN:

        abort(403)

    danh_sach = (
        dao.get_all_linh_vuc()
    )

    return render_template(
        'admin_linh_vuc.html',
        danh_sach=danh_sach
    )


# ==================================================
# ADMIN THÊM LĨNH VỰC
# ==================================================

@app.route(
    '/admin/linh-vuc/them',
    methods=['GET', 'POST']
)
@login_required
def admin_them_linh_vuc():

    if current_user.role != UserRole.ADMIN:

        abort(403)

    if request.method == 'POST':

        ten_linh_vuc = request.form.get(
            'ten_linh_vuc',
            ''
        ).strip()

        mo_ta = request.form.get(
            'mo_ta',
            ''
        ).strip()

        if not ten_linh_vuc:

            return render_template(
                'them_linh_vuc.html',
                error="Vui lòng nhập tên lĩnh vực!"
            )

        success, message = (
            dao.them_linh_vuc(
                ten_linh_vuc,
                mo_ta
            )
        )

        if success:

            flash(
                "Thêm lĩnh vực thành công!",
                "success"
            )

            return redirect(
                url_for(
                    'admin_linh_vuc'
                )
            )

        return render_template(
            'them_linh_vuc.html',
            error=message
        )

    return render_template(
        'them_linh_vuc.html'
    )


# ==================================================
# ADMIN XÓA LĨNH VỰC
# ==================================================

@app.route(
    '/admin/linh-vuc/<int:linh_vuc_id>/xoa',
    methods=['POST']
)
@login_required
def admin_xoa_linh_vuc(linh_vuc_id):

    if current_user.role != UserRole.ADMIN:

        abort(403)

    success, message = (
        dao.xoa_linh_vuc(
            linh_vuc_id
        )
    )

    if success:

        flash(
            "Xóa lĩnh vực thành công!",
            "success"
        )

    else:

        flash(
            message,
            "error"
        )

    return redirect(
        url_for(
            'admin_linh_vuc'
        )
    )

@app.route(
    '/giang-vien/yeu-cau-chinh-sua/<int:yeu_cau_id>/xem-phan-hoi'
)
@login_required
def giang_vien_xem_phan_hoi(yeu_cau_id):

    if current_user.role != UserRole.GIANGVIEN:
        abort(403)

    yeu_cau = YeuCauChinhSua.query.get_or_404(yeu_cau_id)

    de_tai = DeTai.query.get_or_404(
        yeu_cau.deTaiId
    )

    # Chỉ giảng viên đang phụ trách đề tài
    # mới được xem yêu cầu này
    if de_tai.giangVienId != current_user.id:
        abort(403)

    # Chưa xử lý thì không cho xem phản hồi
    if not yeu_cau.daXuLy:
        flash(
            'Yêu cầu này chưa được xử lý.',
            'warning'
        )

        return redirect(
            url_for('giang_vien_dashboard')
        )

    return render_template(
        'giang_vien_xem_phan_hoi.html',
        yeu_cau=yeu_cau
    )

@app.route('/giang-vien/nghiem-thu')
@login_required
def giang_vien_danh_sach_nghiem_thu():

    if current_user.role != UserRole.GIANGVIEN:
        abort(403)

    danh_sach = (
        dao.get_danh_sach_yeu_cau_nghiem_thu_cua_giang_vien(
            current_user.id
        )
    )

    return render_template(
        'giang_vien_danh_sach_nghiem_thu.html',
        danh_sach=danh_sach
    )

# ==================================================
# DANH SÁCH GIẢNG VIÊN
# ==================================================

@app.route(
    '/giang-vien'
)
def danh_sach_giang_vien():

    giang_viens = (
        dao.get_list_giang_vien()
    )

    return render_template(
        'giang_vien.html',
        giang_viens=giang_viens
    )

# ==================================================
# CHI TIẾT GIẢNG VIÊN
# ==================================================

@app.route(
    '/giang-vien/<int:giang_vien_id>'
)
def chi_tiet_giang_vien(giang_vien_id):

    giang_vien = (
        GiangVien.query
        .filter_by(id=giang_vien_id)
        .first()
    )

    if not giang_vien:
        abort(404)

    return render_template(
        'chi_tiet_giang_vien.html',
        giang_vien=giang_vien
    )


# ==================================================
# FLASK LOGIN
# ==================================================

@login.user_loader
def load_user(user_id):

    try:

        return dao.get_user_by_id(
            int(user_id)
        )

    except (
        ValueError,
        TypeError
    ):

        return None


# ==================================================
# AI TÌM KIẾM
# ==================================================

@app.route(
    '/ai-tim-kiem',
    methods=['GET', 'POST']
)
@login_required
def ai_tim_kiem():
    ket_qua = []

    query = ""

    da_tim_kiem = False

    if request.method == 'POST':

        query = request.form.get(
            'query',
            ''
        ).strip()

        da_tim_kiem = True

        if query:

            ket_qua = (
                dao.tim_kiem_ngu_nghia(
                    query
                )
            )

    return render_template(
        'ai_tim_kiem.html',
        ket_qua=ket_qua,
        query=query,
        da_tim_kiem=da_tim_kiem
    )

# ==================================================
# GIẢNG VIÊN - DANH SÁCH YÊU CẦU CHỈNH SỬA
# ==================================================

@app.route(
    '/giang-vien/yeu-cau-chinh-sua'
)
@login_required
def giang_vien_yeu_cau_chinh_sua():

    # Chỉ giảng viên được xem
    if current_user.role != UserRole.GIANGVIEN:
        abort(403)

    # Lấy các yêu cầu chỉnh sửa
    # thuộc những đề tài mà giảng viên đang hướng dẫn
    danh_sach_yeu_cau = (
        YeuCauChinhSua.query
        .join(
            DeTai,
            YeuCauChinhSua.deTaiId == DeTai.id
        )
        .filter(
            DeTai.giangVienId == current_user.id
        )
        .order_by(
            YeuCauChinhSua.ngayTao.desc()
        )
        .all()
    )

    return render_template(
        'giang_vien_yeu_cau_chinh_sua.html',
        danh_sach_yeu_cau=danh_sach_yeu_cau
    )

@app.route('/sinh-vien/tien-do')
@login_required
def sinh_vien_tien_do():

    if current_user.role != UserRole.SINHVIEN:
        abort(403)

    danh_sach_de_tai = dao.get_de_tai_cua_sinh_vien(
        current_user.id
    )

    tien_do_theo_de_tai = {}
    da_hoan_thanh_tien_do = {}
    yeu_cau_chinh_sua_theo_de_tai = {}

    for de_tai in danh_sach_de_tai:

        danh_sach_tien_do = dao.get_tien_do_de_tai(
            de_tai.id
        )

        tien_do_theo_de_tai[de_tai.id] = danh_sach_tien_do

        tien_do_moi_nhat = None

        if danh_sach_tien_do:
            tien_do_moi_nhat = max(
                danh_sach_tien_do,
                key=lambda x: (
                    x.ngayCapNhat
                    if x.ngayCapNhat
                    else datetime.min
                )
            )

        yeu_cau = dao.get_yeu_cau_chinh_sua_moi_nhat(
            de_tai.id
        )

        yeu_cau_chinh_sua_theo_de_tai[de_tai.id] = yeu_cau

        da_hoan_thanh = bool(
            tien_do_moi_nhat
            and tien_do_moi_nhat.phanTram == 100
            and tien_do_moi_nhat.trangThai
                == TrangThaiTienDo.HOAN_THANH
        )

        if (
            da_hoan_thanh
            and yeu_cau
            and yeu_cau.daXuLy
            and yeu_cau.duocPhepChinhSua
        ):
            da_hoan_thanh = False

        da_hoan_thanh_tien_do[de_tai.id] = da_hoan_thanh

    return render_template(
        'theo_doi_tien_do.html',
        danh_sach_de_tai=danh_sach_de_tai,
        tien_do_theo_de_tai=tien_do_theo_de_tai,
        da_hoan_thanh_tien_do=da_hoan_thanh_tien_do,
        yeu_cau_chinh_sua_theo_de_tai=
            yeu_cau_chinh_sua_theo_de_tai
    )

@app.route(
    '/sinh-vien/de-tai/<int:de_tai_id>/tien-do',
    methods=['POST']
)
@login_required
def cap_nhat_tien_do(de_tai_id):

    if current_user.role != UserRole.SINHVIEN:
        abort(403)


    phan_tram = request.form.get('phanTram')

    if not phan_tram:
        flash(
            "Vui lòng nhập phần trăm hoàn thành!",
            "warning"
        )
        return redirect(
            url_for(
                'sinh_vien_tien_do'
            )
        )


    phan_tram = int(phan_tram)


    if phan_tram < 0 or phan_tram > 100:
        flash(
            "Phần trăm phải từ 0 đến 100!",
            "danger"
        )
        return redirect(
            url_for(
                'sinh_vien_tien_do'
            )
        )


    # tạo tiến độ

    tien_do = TienDo(
        deTaiId=de_tai_id,
        phanTram=phan_tram,
        trangThai=(
            TrangThaiTienDo.HOAN_THANH
            if phan_tram == 100
            else TrangThaiTienDo.DANG_THUC_HIEN
        ),
        ngayCapNhat=datetime.now()
    )


    db.session.add(tien_do)



    # =====================================
    # NẾU HOÀN THÀNH 100%
    # TẠO YÊU CẦU NGHIỆM THU
    # =====================================

    if phan_tram == 100:


        yeu_cau = YeuCauNghiemThu.query.filter_by(
            deTaiId=de_tai_id
        ).first()


        if not yeu_cau:

            yeu_cau = YeuCauNghiemThu(
                deTaiId=de_tai_id,
                nguoiYeuCauId=current_user.id,
                noiDung=(
                    "Đề tài đã hoàn thành 100%, "
                    "kính đề nghị giảng viên nghiệm thu."
                ),
                trangThai=
                TrangThaiYeuCauNghiemThu.CHO_NGHIEM_THU,
                ngayTao=datetime.now()
            )


            db.session.add(yeu_cau)



    db.session.commit()


    flash(
        "Cập nhật tiến độ thành công!",
        "success"
    )


    return redirect(
        url_for(
            'sinh_vien_tien_do'
        )
    )

@app.route(
    '/sinh-vien/yeu-cau-nghiem-thu/<int:de_tai_id>',
    methods=['POST']
)
@login_required
def sinh_vien_yeu_cau_nghiem_thu(de_tai_id):

    if current_user.role != UserRole.SINHVIEN:
        abort(403)


    de_tai = DeTai.query.get_or_404(de_tai_id)


    # kiểm tra đúng sinh viên sở hữu đề tài
    if de_tai.sinhVienId != current_user.id:
        abort(403)


    # lấy tiến độ mới nhất

    tien_do = (
        TienDo.query
        .filter_by(
            deTaiId=de_tai.id
        )
        .order_by(
            TienDo.ngayCapNhat.desc()
        )
        .first()
    )


    # chưa đủ điều kiện

    if (
        not tien_do
        or tien_do.phanTram < 100
    ):

        flash(
            "Đề tài chưa hoàn thành 100%",
            "error"
        )

        return redirect(
            url_for(
                'sinh_vien_tien_do'
            )
        )


    # kiểm tra đã gửi trước đó chưa

    da_gui = YeuCauNghiemThu.query.filter_by(
        deTaiId=de_tai.id
    ).first()


    if da_gui:

        flash(
            "Đề tài đã gửi yêu cầu nghiệm thu!",
            "warning"
        )

        return redirect(
            url_for(
                'sinh_vien_tien_do'
            )
        )


    # tạo yêu cầu nghiệm thu

    yeu_cau = YeuCauNghiemThu(

        deTaiId=de_tai.id,

        nguoiYeuCauId=current_user.id,

        noiDung=
        "Sinh viên gửi yêu cầu nghiệm thu đề tài"

    )


    db.session.add(yeu_cau)

    db.session.commit()


    flash(
        "Đã gửi yêu cầu nghiệm thu cho giảng viên!",
        "success"
    )


    return redirect(
        url_for(
            'sinh_vien_tien_do'
        )
    )

# ==================================================
# GIẢNG VIÊN - XỬ LÝ YÊU CẦU CHỈNH SỬA
# ==================================================

@app.route(
    '/giang-vien/yeu-cau-chinh-sua/<int:yeu_cau_id>/xu-ly',
    methods=['GET', 'POST']
)
@login_required
def giang_vien_xu_ly_yeu_cau(yeu_cau_id):
    print("========== HOME ==========")
    print("USER AUTH:", current_user.is_authenticated)
    print("USER ID:", current_user.id if current_user.is_authenticated else None)
    print("USER ROLE:", current_user.role if current_user.is_authenticated else None)

    if current_user.role != UserRole.GIANGVIEN:
        abort(403)

    yeu_cau = dao.get_yeu_cau_chinh_sua_by_id(yeu_cau_id)

    if not yeu_cau:
        abort(404)

    if yeu_cau.de_tai.giangVienId != current_user.id:
        abort(403)

    if request.method == 'POST':

        phan_hoi = request.form.get(
            'phanHoiGiangVien',
            ''
        ).strip()

        ket_qua = request.form.get('ket_qua')

        if not phan_hoi:
            flash(
                'Vui lòng nhập phản hồi cho sinh viên!',
                'error'
            )
            return redirect(
                url_for(
                    'giang_vien_xu_ly_yeu_cau',
                    yeu_cau_id=yeu_cau.id
                )
            )

        if ket_qua not in ['dong_y', 'tu_choi']:
            flash(
                'Vui lòng chọn kết quả xử lý!',
                'error'
            )
            return redirect(
                url_for(
                    'giang_vien_xu_ly_yeu_cau',
                    yeu_cau_id=yeu_cau.id
                )
            )

        yeu_cau.phanHoiGiangVien = phan_hoi
        yeu_cau.daXuLy = True
        yeu_cau.ngayXuLy = datetime.now()

        if ket_qua == 'dong_y':
            yeu_cau.duocPhepChinhSua = True
            message = 'Đã đồng ý cho sinh viên chỉnh sửa tiến độ!'
        else:
            yeu_cau.duocPhepChinhSua = False
            message = 'Đã từ chối yêu cầu chỉnh sửa!'

        db.session.commit()

        flash(message, 'success')

        return redirect(
            url_for(
                'giang_vien_yeu_cau_chinh_sua'
            )
        )

    return render_template(
        'giang_vien_xu_ly_yeu_cau.html',
        yeu_cau=yeu_cau
    )

@app.route(
    '/giang-vien/khieu-nai/<int:khieu_nai_id>/xu-ly',
    methods=['GET', 'POST']
)
@login_required
def giang_vien_xu_ly_khieu_nai(khieu_nai_id):

    # ======================================================
    # CHỈ GIẢNG VIÊN ĐƯỢC XỬ LÝ
    # ======================================================

    if current_user.role != UserRole.GIANGVIEN:
        abort(403)

    # ======================================================
    # LẤY KHIẾU NẠI
    # ======================================================

    khieu_nai = dao.get_khieu_nai_by_id(
        khieu_nai_id
    )

    if not khieu_nai:
        abort(404)

    # ======================================================
    # LẤY ĐỀ TÀI
    # ======================================================

    de_tai = dao.get_de_tai_by_id(
        khieu_nai.deTaiId
    )

    if not de_tai:
        abort(404)

    # ======================================================
    # CHỈ GIẢNG VIÊN PHỤ TRÁCH ĐỀ TÀI MỚI ĐƯỢC XỬ LÝ
    # ======================================================

    if de_tai.giangVienId != current_user.id:
        abort(403)

    # ======================================================
    # LẤY KẾT QUẢ NGHIỆM THU
    # ======================================================

    ket_qua = dao.get_ket_qua_nghiem_thu(
        khieu_nai.deTaiId
    )

    if not ket_qua:
        flash(
            'Không tìm thấy kết quả nghiệm thu của đề tài.',
            'error'
        )

        return redirect(
            url_for(
                'giang_vien_dashboard'
            )
        )

    # ======================================================
    # POST - GIẢNG VIÊN XỬ LÝ
    # ======================================================

    if request.method == 'POST':

        trang_thai = request.form.get(
            'trang_thai',
            ''
        ).strip()

        phan_hoi = request.form.get(
            'phan_hoi',
            ''
        ).strip()

        diem_moi_raw = request.form.get(
            'diem_moi',
            ''
        ).strip()

        # --------------------------------------------------
        # KIỂM TRA TRẠNG THÁI
        # --------------------------------------------------

        if trang_thai not in [
            'DANG_XU_LY',
            'CHAP_NHAN',
            'TU_CHOI'
        ]:
            flash(
                'Trạng thái xử lý không hợp lệ.',
                'error'
            )

            return redirect(
                url_for(
                    'giang_vien_xu_ly_khieu_nai',
                    khieu_nai_id=khieu_nai_id
                )
            )

        # --------------------------------------------------
        # NẾU CHẤP NHẬN -> BẮT BUỘC NHẬP ĐIỂM MỚI
        # --------------------------------------------------

        diem_moi = None

        if trang_thai == 'CHAP_NHAN':

            if not diem_moi_raw:
                flash(
                    'Vui lòng nhập điểm mới khi chấp nhận khiếu nại.',
                    'error'
                )

                return redirect(
                    url_for(
                        'giang_vien_xu_ly_khieu_nai',
                        khieu_nai_id=khieu_nai_id
                    )
                )

            try:

                diem_moi = float(
                    diem_moi_raw
                )

            except ValueError:

                flash(
                    'Điểm mới phải là số.',
                    'error'
                )

                return redirect(
                    url_for(
                        'giang_vien_xu_ly_khieu_nai',
                        khieu_nai_id=khieu_nai_id
                    )
                )

            # Điểm nghiệm thu từ 0 đến 10
            if diem_moi < 0 or diem_moi > 10:

                flash(
                    'Điểm mới phải nằm trong khoảng từ 0 đến 10.',
                    'error'
                )

                return redirect(
                    url_for(
                        'giang_vien_xu_ly_khieu_nai',
                        khieu_nai_id=khieu_nai_id
                    )
                )

        # --------------------------------------------------
        # NẾU TỪ CHỐI -> GIỮ NGUYÊN ĐIỂM CŨ
        # --------------------------------------------------

        if trang_thai == 'TU_CHOI':

            diem_moi = ket_qua.diem

        # --------------------------------------------------
        # CẬP NHẬT ĐIỂM
        # --------------------------------------------------

        if trang_thai == 'CHAP_NHAN':

            ket_qua.diem = diem_moi

            # Có thể giữ kết luận cũ hoặc cập nhật lại
            # tùy logic hệ thống của bạn.
            ket_qua.ketLuan = (
                'Đã chấp nhận khiếu nại và cập nhật lại điểm.'
            )

        elif trang_thai == 'TU_CHOI':

            ket_qua.ketLuan = (
                'Không chấp nhận khiếu nại. '
                'Giữ nguyên điểm nghiệm thu.'
            )

        # --------------------------------------------------
        # CẬP NHẬT KHIẾU NẠI
        # --------------------------------------------------

        khieu_nai.trangThai = TrangThaiKhieuNai(
            trang_thai
        )

        khieu_nai.phanHoi = phan_hoi

        khieu_nai.nguoiXuLyId = current_user.id

        khieu_nai.ngayXuLy = datetime.now()

        try:

            db.session.commit()

            if trang_thai == 'CHAP_NHAN':

                flash(
                    f'Đã chấp nhận khiếu nại và cập nhật điểm thành {diem_moi:.1f}.',
                    'success'
                )

            elif trang_thai == 'TU_CHOI':

                flash(
                    'Đã từ chối khiếu nại. Điểm được giữ nguyên.',
                    'success'
                )

            else:

                flash(
                    'Đã chuyển khiếu nại sang trạng thái đang xử lý.',
                    'success'
                )

        except Exception as e:

            db.session.rollback()

            flash(
                f'Lỗi khi xử lý khiếu nại: {str(e)}',
                'error'
            )

        return redirect(
            url_for(
                'giang_vien_xu_ly_khieu_nai',
                khieu_nai_id=khieu_nai_id
            )
        )

    # ======================================================
    # GET
    # ======================================================

    return render_template(
        'giang_vien_xu_ly_khieu_nai.html',
        khieu_nai=khieu_nai,
        de_tai=de_tai,
        ket_qua=ket_qua
    )

# ==================================================
# SINH VIÊN - THÊM TIẾN ĐỘ
# ==================================================

@app.route(
    '/sinh-vien/de-tai/<int:de_tai_id>/tien-do/them',
    methods=['POST']
)
@login_required
def sinh_vien_them_tien_do(de_tai_id):

    # Chỉ sinh viên
    if current_user.role != UserRole.SINHVIEN:
        abort(403)

    # Lấy đề tài
    de_tai = dao.get_de_tai_by_id(de_tai_id)

    if not de_tai:
        abort(404)

    # Chỉ chủ đề tài mới được thêm tiến độ
    if de_tai.sinhVienId != current_user.id:
        abort(403)

    # ==================================================
    # KIỂM TRA TIẾN ĐỘ HIỆN TẠI
    # ==================================================

    danh_sach_tien_do = dao.get_tien_do_de_tai(
        de_tai_id
    )

    tien_do_moi_nhat = None

    if danh_sach_tien_do:
        tien_do_moi_nhat = max(
            danh_sach_tien_do,
            key=lambda x: (
                x.ngayCapNhat
                if x.ngayCapNhat
                else datetime.min
            )
        )

    # Lấy yêu cầu chỉnh sửa mới nhất
    yeu_cau = dao.get_yeu_cau_chinh_sua_moi_nhat(
        de_tai_id
    )

    # ==================================================
    # NẾU ĐÃ 100% → KHÓA
    # CHỈ MỞ KHI GIẢNG VIÊN ĐỒNG Ý
    # ==================================================

    da_hoan_thanh = bool(
        tien_do_moi_nhat
        and tien_do_moi_nhat.phanTram == 100
        and tien_do_moi_nhat.trangThai
            == TrangThaiTienDo.HOAN_THANH
    )

    if da_hoan_thanh:

        duoc_phep_chinh_sua = bool(
            yeu_cau
            and yeu_cau.daXuLy
            and yeu_cau.duocPhepChinhSua
        )

        if not duoc_phep_chinh_sua:

            flash(
                'Tiến độ đã hoàn thành 100%. '
                'Vui lòng gửi yêu cầu chỉnh sửa '
                'cho giảng viên!',
                'error'
            )

            return redirect(
                url_for(
                    'sinh_vien_tien_do'
                )
            )

    # ==================================================
    # LẤY DỮ LIỆU FORM
    # ==================================================

    tieu_de = request.form.get(
        'tieu_de',
        ''
    ).strip()

    noi_dung = request.form.get(
        'noi_dung',
        ''
    ).strip()

    phan_tram = request.form.get(
        'phan_tram',
        ''
    ).strip()

    trang_thai = request.form.get(
        'trang_thai',
        TrangThaiTienDo.CHUA_BAT_DAU.value
    )

    # ==================================================
    # KIỂM TRA TIÊU ĐỀ
    # ==================================================

    if not tieu_de:

        flash(
            'Vui lòng nhập tiêu đề tiến độ!',
            'error'
        )

        return redirect(
            url_for(
                'sinh_vien_tien_do'
            )
        )

    # ==================================================
    # KIỂM TRA PHẦN TRĂM
    # ==================================================

    try:

        phan_tram = int(
            phan_tram
        )

    except (
        ValueError,
        TypeError
    ):

        flash(
            'Phần trăm tiến độ không hợp lệ!',
            'error'
        )

        return redirect(
            url_for(
                'sinh_vien_tien_do'
            )
        )

    # Không cho < 0 hoặc > 100
    if phan_tram < 0 or phan_tram > 100:

        flash(
            'Phần trăm tiến độ phải từ 0% đến 100%!',
            'error'
        )

        return redirect(
            url_for(
                'sinh_vien_tien_do'
            )
        )

    # ==================================================
    # KIỂM TRA TRẠNG THÁI
    # ==================================================

    try:

        trang_thai = TrangThaiTienDo(
            trang_thai
        )

    except (
        ValueError,
        TypeError
    ):

        flash(
            'Trạng thái tiến độ không hợp lệ!',
            'error'
        )

        return redirect(
            url_for(
                'sinh_vien_tien_do'
            )
        )

    # ==================================================
    # 100% PHẢI LÀ HOÀN THÀNH
    # ==================================================

    if phan_tram == 100:

        if trang_thai != TrangThaiTienDo.HOAN_THANH:

            flash(
                'Tiến độ 100% phải có trạng thái Hoàn thành!',
                'error'
            )

            return redirect(
                url_for(
                    'sinh_vien_tien_do'
                )
            )

    # ==================================================
    # HOÀN THÀNH PHẢI LÀ 100%
    # ==================================================

    if trang_thai == TrangThaiTienDo.HOAN_THANH:

        if phan_tram != 100:

            flash(
                'Trạng thái Hoàn thành phải có tiến độ 100%!',
                'error'
            )

            return redirect(
                url_for(
                    'sinh_vien_tien_do'
                )
            )

    # ==================================================
    # THÊM TIẾN ĐỘ
    # ==================================================

    ket_qua = dao.them_tien_do(

        de_tai_id=de_tai_id,

        tieu_de=tieu_de,

        noi_dung=noi_dung,

        phan_tram=phan_tram,

        trang_thai=trang_thai
    )

    if ket_qua[0]:

        # ==================================================
        # QUYỀN CHỈNH SỬA CHỈ ĐƯỢC DÙNG 1 LẦN
        # ==================================================

        if (
            yeu_cau
            and yeu_cau.daXuLy
            and yeu_cau.duocPhepChinhSua
        ):

            yeu_cau.duocPhepChinhSua = False

            db.session.commit()

        flash(
            'Thêm tiến độ thành công!',
            'success'
        )

    else:

        flash(
            ket_qua[1],
            'error'
        )

    return redirect(
        url_for(
            'sinh_vien_tien_do'
        )
    )

# ==================================================
# YÊU CẦU CHỈNH SỬA
# ==================================================

@app.route(
    '/sinh-vien/yeu-cau-chinh-sua',
    methods=['GET', 'POST']
)
@login_required
def sinh_vien_yeu_cau_chinh_sua():

    # Chỉ sinh viên mới được sử dụng chức năng này
    if current_user.role != UserRole.SINHVIEN:

        abort(403)

    # Lấy các đề tài của sinh viên hiện tại
    danh_sach_de_tai = (
        dao.get_de_tai_cua_sinh_vien(
            current_user.id
        )
    )

    # ==================================================
    # GỬI YÊU CẦU
    # ==================================================

    if request.method == 'POST':

        de_tai_id = request.form.get(
            'de_tai_id',
            type=int
        )

        noi_dung = request.form.get(
            'noi_dung',
            ''
        ).strip()

        # Kiểm tra đề tài
        if not de_tai_id:

            flash(
                "Vui lòng chọn đề tài!",
                "error"
            )

            return redirect(
                url_for(
                    'sinh_vien_yeu_cau_chinh_sua'
                )
            )

        # Kiểm tra nội dung
        if not noi_dung:

            flash(
                "Vui lòng nhập nội dung yêu cầu chỉnh sửa!",
                "error"
            )

            return redirect(
                url_for(
                    'sinh_vien_yeu_cau_chinh_sua'
                )
            )

        # Kiểm tra đề tài có thuộc sinh viên hiện tại không
        de_tai = dao.get_de_tai_by_id(
            de_tai_id
        )

        if not de_tai:

            flash(
                "Không tìm thấy đề tài!",
                "error"
            )

            return redirect(
                url_for(
                    'sinh_vien_yeu_cau_chinh_sua'
                )
            )

        if de_tai.sinhVienId != current_user.id:

            abort(403)

        # Không cho gửi yêu cầu nếu đề tài chưa được duyệt
        if de_tai.trangThai != TrangThaiDeTai.DA_DUYET:

            flash(
                "Chỉ có thể gửi yêu cầu chỉnh sửa "
                "đối với đề tài đã được duyệt!",
                "error"
            )

            return redirect(
                url_for(
                    'sinh_vien_yeu_cau_chinh_sua'
                )
            )

        # Gọi DAO lưu yêu cầu
        success, message, yeu_cau = (
            dao.them_yeu_cau_chinh_sua(
                de_tai_id=de_tai_id,
                nguoi_yeu_cau_id=current_user.id,
                noi_dung=noi_dung
            )
        )

        if success:

            flash(
                "Gửi yêu cầu chỉnh sửa thành công!",
                "success"
            )

        else:

            flash(
                message,
                "error"
            )

        return redirect(
            url_for(
                'sinh_vien_yeu_cau_chinh_sua'
            )
        )

    # ==================================================
    # LẤY DANH SÁCH YÊU CẦU CỦA SINH VIÊN
    # ==================================================

    danh_sach_yeu_cau = (
        YeuCauChinhSua.query
        .filter_by(
            nguoiYeuCauId=current_user.id
        )
        .order_by(
            YeuCauChinhSua.ngayTao.desc()
        )
        .all()
    )

    return render_template(
        'yeu_cau_chinh_sua.html',
        danh_sach_yeu_cau=danh_sach_yeu_cau,
        danh_sach_de_tai=danh_sach_de_tai
    )

# ==================================================
# SINH VIÊN - THEO DÕI TIẾN ĐỘ
# ==================================================



@app.route('/admin/nghiem-thu')
@login_required
def admin_danh_sach_nghiem_thu():

    # Chỉ ADMIN
    if current_user.role != UserRole.ADMIN:
        abort(403)

    # Lấy tất cả kết quả nghiệm thu đã được lưu
    danh_sach_ket_qua = (
        KetQuaNghiemThu.query
        .order_by(
            KetQuaNghiemThu.ngayNghiemThu.desc()
        )
        .all()
    )

    # Đổi dữ liệu về dạng mà template đang sử dụng
    danh_sach = []

    for ket_qua in danh_sach_ket_qua:

        danh_sach.append({
            'de_tai': ket_qua.de_tai,
            'ket_qua': ket_qua
        })

    return render_template(
        'admin_danh_sach_nghiem_thu.html',
        danh_sach=danh_sach
    )

@app.route(
    '/sinh-vien/de-tai/<int:de_tai_id>/nghiem-thu/dong-y',
    methods=['POST']
)
@login_required
def sinh_vien_dong_y_nghiem_thu(de_tai_id):

    if current_user.role != UserRole.SINHVIEN:
        abort(403)

    de_tai = dao.get_de_tai_by_id(de_tai_id)

    if not de_tai:
        abort(404)

    # Kiểm tra sinh viên có thuộc đề tài này không
    if de_tai.sinhVienId != current_user.id:
        abort(403)

    # Lấy kết quả nghiệm thu
    ket_qua = dao.get_ket_qua_nghiem_thu(de_tai_id)

    if not ket_qua:
        flash(
            'Đề tài chưa có kết quả nghiệm thu.',
            'error'
        )

        return redirect(
            url_for(
                'sinh_vien_nghiem_thu'
            )
        )

    # Kiểm tra đã đồng ý chưa
    if getattr(ket_qua, 'sinhVienDongY', False):

        flash(
            'Bạn đã xác nhận đồng ý với kết quả nghiệm thu.',
            'info'
        )

        return redirect(
            url_for(
                'sinh_vien_nghiem_thu'
            )
        )

    # Lưu xác nhận
    ket_qua.sinhVienDongY = True
    ket_qua.ngaySinhVienDongY = datetime.now()

    try:

        db.session.commit()

        flash(
            'Bạn đã đồng ý với kết quả nghiệm thu.',
            'success'
        )

    except Exception as e:

        db.session.rollback()

        flash(
            f'Lỗi khi lưu xác nhận: {str(e)}',
            'error'
        )

    return redirect(
        url_for(
            'sinh_vien_nghiem_thu'
        )
    )

@app.route('/admin/thong-ke')
@login_required
def admin_thong_ke():
    if current_user.role != UserRole.ADMIN:
        abort(403)

    # ==============================
    # 1. THỐNG KÊ NGƯỜI DÙNG
    # ==============================

    tong_nguoi_dung = User.query.count()

    tong_sinh_vien = User.query.filter(
        User.role == UserRole.SINHVIEN
    ).count()

    tong_giang_vien = User.query.filter(
        User.role == UserRole.GIANGVIEN
    ).count()

    tong_admin = User.query.filter(
        User.role == UserRole.ADMIN
    ).count()

    # ==============================
    # 2. THỐNG KÊ ĐỀ TÀI
    # ==============================

    tong_de_tai = DeTai.query.count()

    cho_duyet = DeTai.query.filter(
        DeTai.trangThai == TrangThaiDeTai.CHO_DUYET
    ).count()

    da_duyet = DeTai.query.filter(
        DeTai.trangThai == TrangThaiDeTai.DA_DUYET
    ).count()

    tu_choi = DeTai.query.filter(
        DeTai.trangThai == TrangThaiDeTai.TU_CHOI
    ).count()

    hoan_thanh = DeTai.query.filter(
        DeTai.trangThai == TrangThaiDeTai.HOAN_THANH
    ).count()

    nhap = DeTai.query.filter(
        DeTai.trangThai == TrangThaiDeTai.NHAP
    ).count()

    # ==============================
    # 3. THỐNG KÊ NGHIỆM THU
    # ==============================

    tong_yeu_cau_nghiem_thu = YeuCauNghiemThu.query.count()

    cho_nghiem_thu = YeuCauNghiemThu.query.filter(
        YeuCauNghiemThu.trangThai == TrangThaiYeuCauNghiemThu.CHO_NGHIEM_THU
    ).count()

    da_xu_ly_nghiem_thu = YeuCauNghiemThu.query.filter(
        YeuCauNghiemThu.trangThai == TrangThaiYeuCauNghiemThu.DA_XU_LY
    ).count()

    tong_ket_qua_nghiem_thu = KetQuaNghiemThu.query.count()

    nghiem_thu_dat = KetQuaNghiemThu.query.filter(
        KetQuaNghiemThu.trangThai == TrangThaiNghiemThu.DAT
    ).count()

    nghiem_thu_khong_dat = KetQuaNghiemThu.query.filter(
        KetQuaNghiemThu.trangThai == TrangThaiNghiemThu.KHONG_DAT
    ).count()

    # ==============================
    # 4. THỐNG KÊ THEO LĨNH VỰC
    # ==============================

    linh_vuc_data = []

    linh_vucs = LinhVuc.query.order_by(
        LinhVuc.tenLinhVuc.asc()
    ).all()

    for linh_vuc in linh_vucs:

        so_luong = DeTai.query.filter(
            DeTai.linhVucId == linh_vuc.id
        ).count()

        linh_vuc_data.append({
            'ten': linh_vuc.tenLinhVuc,
            'soLuong': so_luong
        })

    # ==============================
    # 5. DỮ LIỆU BIỂU ĐỒ TRẠNG THÁI
    # ==============================

    trang_thai_data = [
        {
            'ten': 'Nháp',
            'soLuong': nhap
        },
        {
            'ten': 'Chờ duyệt',
            'soLuong': cho_duyet
        },
        {
            'ten': 'Đã duyệt',
            'soLuong': da_duyet
        },
        {
            'ten': 'Từ chối',
            'soLuong': tu_choi
        },
        {
            'ten': 'Hoàn thành',
            'soLuong': hoan_thanh
        }
    ]

    # ==============================
    # 6. BÁO CÁO TỔNG HỢP
    # ==============================

    bao_cao = {
        'tongNguoiDung': tong_nguoi_dung,
        'sinhVien': tong_sinh_vien,
        'giangVien': tong_giang_vien,
        'admin': tong_admin,

        'tongDeTai': tong_de_tai,
        'nhap': nhap,
        'choDuyet': cho_duyet,
        'daDuyet': da_duyet,
        'tuChoi': tu_choi,
        'hoanThanh': hoan_thanh,

        'tongYeuCauNghiemThu': tong_yeu_cau_nghiem_thu,
        'choNghiemThu': cho_nghiem_thu,
        'daXuLyNghiemThu': da_xu_ly_nghiem_thu,

        'tongKetQuaNghiemThu': tong_ket_qua_nghiem_thu,
        'nghiemThuDat': nghiem_thu_dat,
        'nghiemThuKhongDat': nghiem_thu_khong_dat
    }

    return render_template(
        'admin_thong_ke.html',
        bao_cao=bao_cao,
        trang_thai_data=trang_thai_data,
        linh_vuc_data=linh_vuc_data
    )




# ==================================================
# ADMIN - NGHIỆM THU ĐỀ TÀI
# ==================================================

@app.route(
    '/admin/de-tai/<int:de_tai_id>/nghiem-thu',
    methods=['GET', 'POST']
)
@login_required
def admin_nghiem_thu(de_tai_id):

    # Chỉ ADMIN được nghiệm thu
    if current_user.role != UserRole.ADMIN:
        abort(403)

    # Lấy đề tài
    de_tai = dao.get_de_tai_by_id(de_tai_id)

    if not de_tai:
        abort(404)

    # Lấy kết quả nghiệm thu hiện tại
    ket_qua = dao.get_ket_qua_nghiem_thu(
        de_tai_id
    )

    # ==================================================
    # XỬ LÝ FORM
    # ==================================================

    if request.method == 'POST':

        diem = request.form.get(
            'diem',
            type=float
        )

        nhan_xet = request.form.get(
            'nhan_xet',
            ''
        ).strip()

        ket_luan = request.form.get(
            'ket_luan',
            ''
        ).strip()

        trang_thai_form = request.form.get(
            'trang_thai',
            ''
        ).strip()

        # ==================================================
        # KIỂM TRA ĐIỂM
        # ==================================================

        if diem is None:

            flash(
                'Vui lòng nhập điểm nghiệm thu!',
                'error'
            )

            return redirect(
                url_for(
                    'admin_nghiem_thu',
                    de_tai_id=de_tai_id
                )
            )

        if not 0 <= diem <= 10:

            flash(
                'Điểm nghiệm thu phải từ 0 đến 10!',
                'error'
            )

            return redirect(
                url_for(
                    'admin_nghiem_thu',
                    de_tai_id=de_tai_id
                )
            )

        # ==================================================
        # KIỂM TRA TRẠNG THÁI
        # ==================================================

        if trang_thai_form not in (
            'DAT',
            'KHONG_DAT'
        ):

            flash(
                'Vui lòng chọn kết quả nghiệm thu!',
                'error'
            )

            return redirect(
                url_for(
                    'admin_nghiem_thu',
                    de_tai_id=de_tai_id
                )
            )

        # ==================================================
        # CHUYỂN SANG ENUM
        # ==================================================

        try:

            trang_thai = TrangThaiNghiemThu(
                trang_thai_form
            )

        except ValueError:

            flash(
                'Trạng thái nghiệm thu không hợp lệ!',
                'error'
            )

            return redirect(
                url_for(
                    'admin_nghiem_thu',
                    de_tai_id=de_tai_id
                )
            )

        # ==================================================
        # THÊM / CẬP NHẬT
        # ==================================================

        if ket_qua:

            success, message = (
                dao.cap_nhat_ket_qua_nghiem_thu(
                    de_tai_id=de_tai_id,
                    diem=diem,
                    nhan_xet=nhan_xet,
                    ket_luan=ket_luan,
                    trang_thai=trang_thai
                )
            )

        else:

            success, message, ket_qua = (
                dao.them_ket_qua_nghiem_thu(
                    de_tai_id=de_tai_id,
                    nguoi_nghiem_thu_id=current_user.id,
                    diem=diem,
                    nhan_xet=nhan_xet,
                    ket_luan=ket_luan,
                    trang_thai=trang_thai
                )
            )

        # ==================================================
        # KẾT QUẢ
        # ==================================================

        if success:

            flash(
                'Lưu kết quả nghiệm thu thành công!',
                'success'
            )

            return redirect(
                url_for(
                    'admin_nghiem_thu',
                    de_tai_id=de_tai_id
                )
            )

        flash(
            message,
            'error'
        )

    # ==================================================
    # HIỂN THỊ
    # ==================================================

    return render_template(
        'admin_nghiem_thu.html',
        de_tai=de_tai,
        ket_qua=ket_qua
    )


@app.route('/sinh-vien')
@login_required
def sinh_vien():

    if current_user.role != UserRole.SINHVIEN:
        abort(403)

    danh_sach_de_tai = (
        DeTai.query
        .filter_by(
            sinhVienId=current_user.id
        )
        .order_by(
            DeTai.ngayTao.desc()
        )
        .all()
    )

    tong_de_tai = len(danh_sach_de_tai)

    so_cho_duyet = sum(
        1
        for dt in danh_sach_de_tai
        if dt.trangThai == TrangThaiDeTai.CHO_DUYET
    )

    so_dang_thuc_hien = sum(
        1
        for dt in danh_sach_de_tai
        if dt.trangThai == TrangThaiDeTai.DA_DUYET
    )

    so_hoan_thanh = sum(
        1
        for dt in danh_sach_de_tai
        if dt.trangThai == TrangThaiDeTai.HOAN_THANH
    )

    return render_template(
        'sinh_vien.html',
        danh_sach_de_tai=danh_sach_de_tai,
        tong_de_tai=tong_de_tai,
        so_cho_duyet=so_cho_duyet,
        so_dang_thuc_hien=so_dang_thuc_hien,
        so_hoan_thanh=so_hoan_thanh
    )

# ==================================================
# SINH VIÊN - NGHIỆM THU
# ==================================================

@app.route('/sinh-vien/nghiem-thu')
@login_required
def sinh_vien_nghiem_thu():

    if current_user.role != UserRole.SINHVIEN:
        abort(403)

    danh_sach_de_tai = (
        dao.get_de_tai_cua_sinh_vien(
            current_user.id
        )
    )

    ket_qua_nghiem_thu = {}
    yeu_cau_nghiem_thu = {}
    tien_do_nghiem_thu = {}

    # ==================================================
    # LẤY DANH SÁCH KHIẾU NẠI CỦA SINH VIÊN
    # ==================================================

    danh_sach_khieu_nai = (
        dao.get_khieu_nai_by_sinh_vien(
            current_user.id
        )
    )

    khieu_nai_nghiem_thu = {}

    for khieu_nai in danh_sach_khieu_nai:
        khieu_nai_nghiem_thu[
            khieu_nai.deTaiId
        ] = khieu_nai

    # ==================================================
    # XỬ LÝ TỪNG ĐỀ TÀI
    # ==================================================

    for de_tai in danh_sach_de_tai:

        # ----------------------------------------------
        # KẾT QUẢ NGHIỆM THU
        # ----------------------------------------------

        ket_qua_nghiem_thu[de_tai.id] = (
            dao.get_ket_qua_nghiem_thu(
                de_tai.id
            )
        )

        # ----------------------------------------------
        # YÊU CẦU NGHIỆM THU
        # ----------------------------------------------

        yeu_cau_nghiem_thu[de_tai.id] = (
            dao.get_yeu_cau_nghiem_thu(
                de_tai.id
            )
        )

        # ----------------------------------------------
        # TIẾN ĐỘ
        # ----------------------------------------------

        danh_sach_tien_do = (
            dao.get_tien_do_de_tai(
                de_tai.id
            )
        )

        tien_do_moi_nhat = None

        if danh_sach_tien_do:
            tien_do_moi_nhat = max(
                danh_sach_tien_do,
                key=lambda x: (
                    x.ngayCapNhat
                    if x.ngayCapNhat
                    else datetime.min
                )
            )

        tien_do_nghiem_thu[
            de_tai.id
        ] = tien_do_moi_nhat

    # ==================================================
    # HIỂN THỊ TRANG
    # ==================================================

    return render_template(
        'nghiem_thu.html',
        danh_sach_de_tai=danh_sach_de_tai,
        ket_qua_nghiem_thu=ket_qua_nghiem_thu,
        yeu_cau_nghiem_thu=yeu_cau_nghiem_thu,
        tien_do_nghiem_thu=tien_do_nghiem_thu,
        khieu_nai_nghiem_thu=khieu_nai_nghiem_thu
    )

@app.route(
    '/sinh-vien/de-tai/<int:de_tai_id>/nghiem-thu/khieu-nai',
    methods=['GET', 'POST']
)
@login_required
def sinh_vien_khieu_nai_nghiem_thu(de_tai_id):

    # ==============================================
    # CHỈ SINH VIÊN
    # ==============================================

    if current_user.role != UserRole.SINHVIEN:
        abort(403)

    # ==============================================
    # LẤY ĐỀ TÀI
    # ==============================================

    de_tai = dao.get_de_tai_by_id(de_tai_id)

    if not de_tai:
        abort(404)

    # ==============================================
    # KIỂM TRA SINH VIÊN CÓ PHẢI CHỦ ĐỀ TÀI KHÔNG
    # ==============================================

    if de_tai.sinhVienId != current_user.id:
        abort(403)

    # ==============================================
    # LẤY KẾT QUẢ NGHIỆM THU
    # ==============================================

    ket_qua = dao.get_ket_qua_nghiem_thu(
        de_tai_id
    )

    if not ket_qua:

        flash(
            'Đề tài chưa có kết quả nghiệm thu.',
            'warning'
        )

        return redirect(
            url_for(
                'sinh_vien_ket_qua_nghiem_thu',
                de_tai_id=de_tai_id
            )
        )

    # ==============================================
    # LẤY DANH SÁCH KHIẾU NẠI
    # ==============================================

    danh_sach_khieu_nai = (
        dao.get_khieu_nai_by_de_tai(
            de_tai_id
        )
    )

    # ==============================================
    # KIỂM TRA KHIẾU NẠI ĐANG XỬ LÝ
    # ==============================================

    khieu_nai_dang_xu_ly = next(
        (
            x
            for x in danh_sach_khieu_nai
            if x.nguoiKhieuNaiId == current_user.id
            and x.trangThai in (
                TrangThaiKhieuNai.CHO_XU_LY,
                TrangThaiKhieuNai.DANG_XU_LY
            )
        ),
        None
    )

    # ==============================================
    # NẾU ĐÃ CÓ KHIẾU NẠI
    # ==============================================

    if khieu_nai_dang_xu_ly:

        flash(
            'Bạn đã gửi khiếu nại cho kết quả nghiệm thu này và đang chờ xử lý.',
            'warning'
        )

        return render_template(
            'sinh_vien_khieu_nai_nghiem_thu.html',
            de_tai=de_tai,
            ket_qua=ket_qua,
            danh_sach_khieu_nai=danh_sach_khieu_nai,
            khieu_nai_dang_xu_ly=khieu_nai_dang_xu_ly
        )

    # ==============================================
    # XỬ LÝ FORM
    # ==============================================

    if request.method == 'POST':

        ly_do = request.form.get(
            'ly_do',
            ''
        ).strip()

        minh_chung = request.form.get(
            'minh_chung',
            ''
        ).strip()

        # ------------------------------------------
        # KIỂM TRA LÝ DO
        # ------------------------------------------

        if not ly_do:

            flash(
                'Vui lòng nhập lý do khiếu nại.',
                'error'
            )

            return render_template(
                'sinh_vien_khieu_nai_nghiem_thu.html',
                de_tai=de_tai,
                ket_qua=ket_qua,
                danh_sach_khieu_nai=danh_sach_khieu_nai
            )

        # ------------------------------------------
        # THÊM KHIẾU NẠI
        # ------------------------------------------

        success, message, khieu_nai = (
            dao.them_khieu_nai_nghiem_thu(
                de_tai_id=de_tai_id,
                ket_qua_id=ket_qua.id,
                nguoi_khieu_nai_id=current_user.id,
                ly_do=ly_do,
                minh_chung=minh_chung
            )
        )

        # ------------------------------------------
        # LỖI
        # ------------------------------------------

        if not success:

            flash(
                message,
                'error'
            )

            return render_template(
                'sinh_vien_khieu_nai_nghiem_thu.html',
                de_tai=de_tai,
                ket_qua=ket_qua,
                danh_sach_khieu_nai=danh_sach_khieu_nai
            )

        # ------------------------------------------
        # THÀNH CÔNG
        # ------------------------------------------

        flash(
            'Đã gửi khiếu nại kết quả nghiệm thu thành công.',
            'success'
        )

        danh_sach_khieu_nai = dao.get_khieu_nai_by_de_tai(
            de_tai_id
        )

        khieu_nai_dang_xu_ly = khieu_nai

        return render_template(
            'sinh_vien_khieu_nai_nghiem_thu.html',
            de_tai=de_tai,
            ket_qua=ket_qua,
            danh_sach_khieu_nai=danh_sach_khieu_nai,
            khieu_nai_dang_xu_ly=khieu_nai_dang_xu_ly
        )

    # ==============================================
    # HIỂN THỊ TRANG
    # ==============================================

    return render_template(
        'sinh_vien_khieu_nai_nghiem_thu.html',
        de_tai=de_tai,
        ket_qua=ket_qua,
        danh_sach_khieu_nai=danh_sach_khieu_nai,
        khieu_nai_dang_xu_ly=khieu_nai_dang_xu_ly
    )

@app.route(
    '/giang-vien/khieu-nai-nghiem-thu',
    methods=['GET']
)
@login_required
def giang_vien_danh_sach_khieu_nai():

    # Chỉ giảng viên được xem
    if current_user.role != UserRole.GIANGVIEN:
        abort(403)

    danh_sach_khieu_nai = (
        dao.get_khieu_nai_cho_xu_ly()
    )

    return render_template(
        'giang_vien_danh_sach_khieu_nai.html',
        danh_sach_khieu_nai=danh_sach_khieu_nai
    )

# ==================================================
# DEBUG 403
# ==================================================

@app.errorhandler(403)
def forbidden(e):

    return f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>403 Forbidden</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 40px;
            }}

            h1 {{
                color: #dc2626;
            }}

            .info {{
                background: #f3f4f6;
                padding: 20px;
                border-radius: 10px;
                line-height: 1.8;
            }}
        </style>
    </head>

    <body>

        <h1>403 - Không có quyền truy cập</h1>

        <div class="info">

            <p>
                <strong>Đã đăng nhập:</strong>
                {current_user.is_authenticated}
            </p>

            <p>
                <strong>User ID:</strong>
                {getattr(current_user, 'id', None)}
            </p>

            <p>
                <strong>Họ tên:</strong>
                {getattr(current_user, 'hoTen', None)}
            </p>

            <p>
                <strong>Role:</strong>
                {getattr(current_user, 'role', None)}
            </p>

            <p>
                <strong>URL:</strong>
                {request.path}
            </p>

        </div>

    </body>
    </html>
    """, 403

# ==================================================
# CHẠY CHƯƠNG TRÌNH
# ==================================================

if __name__ == '__main__':

    with app.app_context():

        db.create_all()

    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', '0') == '1'
    )