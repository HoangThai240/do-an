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
    TrangThaiTienDo
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


# ==================================================
# DANH SÁCH ĐỀ TÀI
# ==================================================

@app.route('/de-tai')
def danh_sach_de_tai():

    keyword = request.args.get(
        'keyword',
        ''
    ).strip()

    linh_vuc_id = request.args.get(
        'linh_vuc_id',
        ''
    ).strip()

    de_tais = dao.get_list_de_tai(
        keyword=keyword,
        linh_vuc_id=linh_vuc_id
    )

    linh_vucs = dao.get_list_linh_vuc()

    return render_template(
        'danh_sach_de_tai.html',
        de_tais=de_tais,
        linh_vucs=linh_vucs,
        keyword=keyword,
        linh_vuc_id=linh_vuc_id
    )


# ==================================================
# CHI TIẾT ĐỀ TÀI
# ==================================================

@app.route(
    '/de-tai/<int:de_tai_id>'
)
def chi_tiet_de_tai(de_tai_id):

    de_tai = dao.get_de_tai_by_id(
        de_tai_id
    )

    if not de_tai:

        abort(404)

    return render_template(
        'chi_tiet_de_tai.html',
        de_tai=de_tai
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

    # Gán giảng viên và duyệt đề tài
    ket_qua = dao.duyet_de_tai(
        de_tai_id,
        giang_vien_id
    )

    if ket_qua:

        flash(
            'Đã chọn giảng viên và duyệt đề tài thành công!',
            'success'
        )

        return redirect(
            url_for('admin_dashboard')
        )

    flash(
        'Không thể chọn giảng viên. Vui lòng kiểm tra lại!',
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
# API KIỂM TRA TRÙNG LẶP
# ==================================================

@app.route(
    '/api/de-tai/<int:de_tai_id>/kiem-tra-trung-lap'
)
def api_kiem_tra_trung_lap(de_tai_id):

    de_tai = dao.get_de_tai_by_id(
        de_tai_id
    )

    if not de_tai:

        return jsonify({
            "success": False,
            "message": "Không tìm thấy đề tài!"
        }), 404

    ket_qua = dao.kiem_tra_trung_lap(
        de_tai_id
    )

    data = []

    for item in ket_qua:

        data.append({

            "deTai":
                item["deTai"].to_dict(),

            "doTuongDong":
                item["doTuongDong"]

        })

    return jsonify({

        "success": True,

        "data": data

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

@app.route(
    '/giang-vien/dashboard'
)
@login_required
def giang_vien_dashboard():

    if current_user.role != UserRole.GIANGVIEN:

        abort(403)

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

    return render_template(
        'giang_vien_dashboard.html',
        danh_sach_de_tai=danh_sach_de_tai
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
        abort(403)

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
# AI KIỂM TRA TRÙNG LẶP
# ==================================================

@app.route(
    '/ai/trung-lap',
    methods=['GET', 'POST']
)
@login_required
def ai_trung_lap():

    ket_qua = []

    noi_dung = ""

    da_kiem_tra = False

    if request.method == 'POST':

        noi_dung = request.form.get(
            'noi_dung',
            ''
        ).strip()

        da_kiem_tra = True

        if noi_dung:

            ket_qua = (
                dao.kiem_tra_trung_lap_ai(
                    noi_dung
                )
            )

    return render_template(
        'ai_trung_lap.html',
        ket_qua=ket_qua,
        noi_dung=noi_dung,
        da_kiem_tra=da_kiem_tra
    )

# ==================================================
# GIẢNG VIÊN - XỬ LÝ YÊU CẦU CHỈNH SỬA
# ==================================================

@app.route(
    '/giang-vien/yeu-cau-chinh-sua/<int:yeu_cau_id>/xu-ly',
    methods=['POST']
)
@login_required
def giang_vien_xu_ly_yeu_cau(yeu_cau_id):

    if current_user.role != UserRole.GIANGVIEN:
        abort(403)

    yeu_cau = (
        YeuCauChinhSua.query
        .filter_by(id=yeu_cau_id)
        .first()
    )

    if not yeu_cau:
        abort(404)

    # Lấy đề tài
    de_tai = dao.get_de_tai_by_id(
        yeu_cau.deTaiId
    )

    if not de_tai:
        abort(404)

    # Chỉ giảng viên hướng dẫn đề tài mới được xử lý
    if de_tai.giangVienId != current_user.id:
        abort(403)

    phan_hoi = request.form.get(
        'phan_hoi',
        ''
    ).strip()

    if not phan_hoi:

        flash(
            'Vui lòng nhập phản hồi cho sinh viên.',
            'error'
        )

        return redirect(
            url_for(
                'giang_vien_yeu_cau_chinh_sua'
            )
        )

    ket_qua = dao.xu_ly_yeu_cau_chinh_sua(
        yeu_cau_id=yeu_cau_id,
        phan_hoi=phan_hoi
    )

    if ket_qua[0]:

        flash(
            'Đã phản hồi yêu cầu chỉnh sửa.',
            'success'
        )

    else:

        flash(
            ket_qua[1],
            'error'
        )

    return redirect(
        url_for(
            'giang_vien_yeu_cau_chinh_sua'
        )
    )

# ==========================================================
# SINH VIÊN - QUẢN LÝ TIẾN ĐỘ
# ==========================================================

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
    de_tai = dao.get_de_tai_by_id(
        de_tai_id
    )

    if not de_tai:
        abort(404)

    # Chỉ chủ đề tài mới được thêm tiến độ
    if de_tai.sinhVienId != current_user.id:
        abort(403)

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
        0
    )

    trang_thai = request.form.get(
        'trang_thai',
        TrangThaiTienDo.CHUA_BAT_DAU.value
    )

    # Kiểm tra tiêu đề
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

    # Chuyển phần trăm sang số
    try:

        phan_tram = int(
            phan_tram
        )

    except (
        ValueError,
        TypeError
    ):

        phan_tram = 0

    # Giới hạn 0 - 100%
    if phan_tram < 0:
        phan_tram = 0

    if phan_tram > 100:
        phan_tram = 100

    # Chuyển trạng thái sang Enum
    try:

        trang_thai = TrangThaiTienDo(
            trang_thai
        )

    except (
        ValueError,
        TypeError
    ):

        trang_thai = (
            TrangThaiTienDo.CHUA_BAT_DAU
        )

    # Thêm tiến độ
    ket_qua = dao.them_tien_do(

        de_tai_id=de_tai_id,

        tieu_de=tieu_de,

        noi_dung=noi_dung,

        phan_tram=phan_tram,

        trang_thai=trang_thai
    )

    if ket_qua[0]:

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

@app.route(
    '/sinh-vien/tien-do'
)
@login_required
def sinh_vien_tien_do():

    # Chỉ sinh viên mới được sử dụng
    if current_user.role != UserRole.SINHVIEN:

        abort(403)

    # Lấy các đề tài của sinh viên hiện tại
    danh_sach_de_tai = (
        dao.get_de_tai_cua_sinh_vien(
            current_user.id
        )
    )

    # Tạo dữ liệu tiến độ cho từng đề tài
    tien_do_theo_de_tai = {}

    for de_tai in danh_sach_de_tai:

        tien_do_theo_de_tai[de_tai.id] = (
            dao.get_tien_do_de_tai(
                de_tai.id
            )
        )

    return render_template(
        'theo_doi_tien_do.html',
        danh_sach_de_tai=danh_sach_de_tai,
        tien_do_theo_de_tai=tien_do_theo_de_tai
    )


# ==================================================
# SINH VIÊN - NGHIỆM THU
# ==================================================

@app.route(
    '/sinh-vien/nghiem-thu'
)
@login_required
def sinh_vien_nghiem_thu():

    # Chỉ sinh viên mới được sử dụng
    if current_user.role != UserRole.SINHVIEN:

        abort(403)

    # Lấy các đề tài của sinh viên hiện tại
    danh_sach_de_tai = (
        dao.get_de_tai_cua_sinh_vien(
            current_user.id
        )
    )

    # Lấy kết quả nghiệm thu của từng đề tài
    ket_qua_nghiem_thu = {}

    for de_tai in danh_sach_de_tai:

        ket_qua_nghiem_thu[de_tai.id] = (
            dao.get_ket_qua_nghiem_thu(
                de_tai.id
            )
        )

    return render_template(
        'nghiem_thu.html',
        danh_sach_de_tai=danh_sach_de_tai,
        ket_qua_nghiem_thu=ket_qua_nghiem_thu
    )

# ==================================================
# DASHBOARD SINH VIÊN
# ==================================================

@app.route('/sinh-vien')
def sinh_vien():

    if not current_user.is_authenticated:
        return redirect(
            url_for('login_process')
        )

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

    so_cho_duyet = sum(
        1
        for dt in danh_sach_de_tai
        if dt.trangThai
        and dt.trangThai.value == 'CHO_DUYET'
    )

    so_dang_thuc_hien = sum(
        1
        for dt in danh_sach_de_tai
        if dt.trangThai
        and dt.trangThai.value == 'DANG_THUC_HIEN'
    )

    so_hoan_thanh = sum(
        1
        for dt in danh_sach_de_tai
        if dt.trangThai
        and dt.trangThai.value == 'HOAN_THANH'
    )

    return render_template(
        'sinh_vien.html',
        danh_sach_de_tai=danh_sach_de_tai,
        so_cho_duyet=so_cho_duyet,
        so_dang_thuc_hien=so_dang_thuc_hien,
        so_hoan_thanh=so_hoan_thanh
    )

# ==================================================
# CHẠY CHƯƠNG TRÌNH
# ==================================================

if __name__ == '__main__':

    with app.app_context():

        db.create_all()

    app.run(
        debug=True,
        port=5000
    )