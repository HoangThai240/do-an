from sqlalchemy import or_, func

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app import db

from difflib import SequenceMatcher

from app.models import (
    User,
    UserRole,
    LinhVuc,
    GiangVien,
    GiangVienLinhVuc,
    DeTai,
    TrangThaiDeTai,
    KiemTraTrungLap,
    GoiYGiangVien,
    LichSuTimKiem,

    TienDo,
    TrangThaiTienDo,

    YeuCauChinhSua,

    KetQuaNghiemThu,
    TrangThaiNghiemThu,

    ThongBao,
    LoaiThongBao,
    TaiLieu
)


# ==========================================================
# DATABASE
# ==========================================================

def commit():
    db.session.commit()


def rollback():
    db.session.rollback()


# ==========================================================
# USER - ĐĂNG KÝ / ĐĂNG NHẬP
# ==========================================================

def get_user_by_id(user_id):

    return db.session.get(
        User,
        user_id
    )


def dang_ky(
    username,
    password,
    ho_ten,
    email=None,
    role=UserRole.SINHVIEN
):

    try:

        username = (username or "").strip()
        ho_ten = (ho_ten or "").strip()
        email = (email or "").strip() or None

        if not username:
            return (
                False,
                "Tên đăng nhập không được để trống!",
                None
            )

        if not password:
            return (
                False,
                "Mật khẩu không được để trống!",
                None
            )

        # Kiểm tra username
        user = User.query.filter_by(
            username=username
        ).first()

        if user:
            return (
                False,
                "Tên đăng nhập đã tồn tại!",
                None
            )

        # Kiểm tra email
        if email:

            user = User.query.filter_by(
                email=email
            ).first()

            if user:
                return (
                    False,
                    "Email đã tồn tại!",
                    None
                )

        user = User(
            username=username,
            password=generate_password_hash(password),
            hoTen=ho_ten,
            email=email,
            role=role,
            active=True
        )

        db.session.add(user)

        commit()

        return (
            True,
            "Đăng ký thành công!",
            user
        )

    except Exception as e:

        rollback()

        print("Lỗi đăng ký:", e)

        return (
            False,
            "Có lỗi xảy ra khi đăng ký!",
            None
        )


def dang_nhap(
    dinh_danh,
    password
):

    dinh_danh = (dinh_danh or "").strip()

    if not dinh_danh or not password:

        return (
            None,
            "Vui lòng nhập đầy đủ thông tin!"
        )

    user = User.query.filter(
        or_(
            User.username == dinh_danh,
            User.email == dinh_danh
        )
    ).first()

    if not user:

        return (
            None,
            "Tài khoản không tồn tại!"
        )

    if not user.active:

        return (
            None,
            "Tài khoản đã bị khóa!"
        )

    try:

        password_correct = check_password_hash(
            user.password,
            password
        )

    except Exception:

        password_correct = False

    if not password_correct:

        return (
            None,
            "Mật khẩu không đúng!"
        )

    return (
        user,
        "Đăng nhập thành công!"
    )


def get_user_by_email(email):

    if not email:
        return None

    return User.query.filter_by(
        email=email
    ).first()


def update_password(
    user,
    new_password
):

    try:

        if not user:
            return (
                False,
                "Không tìm thấy tài khoản!"
            )

        if not new_password:
            return (
                False,
                "Mật khẩu không được để trống!"
            )

        user.password = generate_password_hash(
            new_password
        )

        commit()

        return (
            True,
            "Đổi mật khẩu thành công!"
        )

    except Exception as e:

        rollback()

        print(
            "Lỗi cập nhật mật khẩu:",
            e
        )

        return (
            False,
            str(e)
        )


def get_all_users():

    return User.query.order_by(
        User.ngayTao.desc()
    ).all()


def get_all_giang_vien():

    return User.query.filter_by(
        role=UserRole.GIANGVIEN,
        active=True
    ).order_by(
        User.hoTen.asc()
    ).all()


# ==========================================================
# KHÓA / MỞ KHÓA USER
# ==========================================================

def khoa_user(user_id):

    try:

        user = get_user_by_id(user_id)

        if not user:

            return (
                False,
                "Không tìm thấy người dùng!"
            )

        user.active = False

        commit()

        return (
            True,
            "Khóa tài khoản thành công!"
        )

    except Exception as e:

        rollback()

        print(
            "Lỗi khóa tài khoản:",
            e
        )

        return (
            False,
            str(e)
        )


def mo_khoa_user(user_id):

    try:

        user = get_user_by_id(user_id)

        if not user:

            return (
                False,
                "Không tìm thấy người dùng!"
            )

        user.active = True

        commit()

        return (
            True,
            "Mở khóa tài khoản thành công!"
        )

    except Exception as e:

        rollback()

        print(
            "Lỗi mở khóa tài khoản:",
            e
        )

        return (
            False,
            str(e)
        )


# ==========================================================
# LĨNH VỰC
# ==========================================================

def get_all_linh_vuc():

    return LinhVuc.query.order_by(
        LinhVuc.tenLinhVuc.asc()
    ).all()


def get_list_linh_vuc():

    return LinhVuc.query.order_by(
        LinhVuc.tenLinhVuc.asc()
    ).all()


def get_linh_vuc_by_id(
    linh_vuc_id
):

    return db.session.get(
        LinhVuc,
        linh_vuc_id
    )


def them_linh_vuc(
    ten_linh_vuc,
    mo_ta=None
):

    try:

        ten_linh_vuc = (
            ten_linh_vuc or ""
        ).strip()

        if not ten_linh_vuc:

            return (
                False,
                "Tên lĩnh vực không được để trống!"
            )

        linh_vuc = LinhVuc.query.filter(
            func.lower(
                LinhVuc.tenLinhVuc
            ) == ten_linh_vuc.lower()
        ).first()

        if linh_vuc:

            return (
                False,
                "Lĩnh vực đã tồn tại!"
            )

        linh_vuc = LinhVuc(
            tenLinhVuc=ten_linh_vuc,
            moTa=mo_ta
        )

        db.session.add(linh_vuc)

        commit()

        return (
            True,
            "Thêm lĩnh vực thành công!"
        )

    except Exception as e:

        rollback()

        print(
            "Lỗi thêm lĩnh vực:",
            e
        )

        return (
            False,
            str(e)
        )


def cap_nhat_linh_vuc(
    linh_vuc_id,
    ten_linh_vuc,
    mo_ta
):

    try:

        linh_vuc = get_linh_vuc_by_id(
            linh_vuc_id
        )

        if not linh_vuc:

            return (
                False,
                "Không tìm thấy lĩnh vực!"
            )

        ten_linh_vuc = (
            ten_linh_vuc or ""
        ).strip()

        if not ten_linh_vuc:

            return (
                False,
                "Tên lĩnh vực không được để trống!"
            )

        # Không cho trùng tên với lĩnh vực khác
        trung = LinhVuc.query.filter(
            func.lower(
                LinhVuc.tenLinhVuc
            ) == ten_linh_vuc.lower(),
            LinhVuc.id != linh_vuc_id
        ).first()

        if trung:

            return (
                False,
                "Tên lĩnh vực đã tồn tại!"
            )

        linh_vuc.tenLinhVuc = ten_linh_vuc
        linh_vuc.moTa = mo_ta

        commit()

        return (
            True,
            "Cập nhật lĩnh vực thành công!"
        )

    except Exception as e:

        rollback()

        return (
            False,
            str(e)
        )


def xoa_linh_vuc(
    linh_vuc_id
):

    try:

        linh_vuc = get_linh_vuc_by_id(
            linh_vuc_id
        )

        if not linh_vuc:

            return (
                False,
                "Không tìm thấy lĩnh vực!"
            )

        # Không cho xóa nếu đang có đề tài
        so_de_tai = DeTai.query.filter_by(
            linhVucId=linh_vuc_id
        ).count()

        if so_de_tai > 0:

            return (
                False,
                "Không thể xóa lĩnh vực đang có đề tài!"
            )

        db.session.delete(linh_vuc)

        commit()

        return (
            True,
            "Xóa lĩnh vực thành công!"
        )

    except Exception as e:

        rollback()

        print(
            "Lỗi xóa lĩnh vực:",
            e
        )

        return (
            False,
            str(e)
        )


# ==========================================================
# GIẢNG VIÊN
# ==========================================================

def get_giang_vien_by_user_id(
    user_id
):

    return GiangVien.query.filter_by(
        userId=user_id
    ).first()


def get_all_thong_tin_giang_vien():

    return GiangVien.query.order_by(
        GiangVien.id.asc()
    ).all()


def get_list_giang_vien():

    return GiangVien.query.order_by(
        GiangVien.id.asc()
    ).all()


# ==========================================================
# CHUYÊN MÔN GIẢNG VIÊN
# ==========================================================

def get_linh_vuc_giang_vien(
    giang_vien_id
):
    """
    LƯU Ý:

    GiangVienLinhVuc.giangVienId
    tham chiếu tới User.id.

    Vì vậy tham số giang_vien_id ở đây
    thực tế phải là USER ID.
    """

    return GiangVienLinhVuc.query.filter_by(
        giangVienId=giang_vien_id
    ).all()


def cap_nhat_chuyen_mon_giang_vien(
    giang_vien_id,
    danh_sach_linh_vuc
):

    try:

        # giang_vien_id = User.id
        user = get_user_by_id(
            giang_vien_id
        )

        if not user:

            return (
                False,
                "Không tìm thấy người dùng!"
            )

        if user.role != UserRole.GIANGVIEN:

            return (
                False,
                "Người dùng không phải giảng viên!"
            )

        # Xóa chuyên môn cũ
        GiangVienLinhVuc.query.filter_by(
            giangVienId=giang_vien_id
        ).delete(
            synchronize_session=False
        )

        # Thêm chuyên môn mới
        for linh_vuc_id in (
            danh_sach_linh_vuc or []
        ):

            try:
                linh_vuc_id = int(linh_vuc_id)
            except (ValueError, TypeError):
                continue

            linh_vuc = get_linh_vuc_by_id(
                linh_vuc_id
            )

            if not linh_vuc:
                continue

            chuyen_mon = GiangVienLinhVuc(
                giangVienId=giang_vien_id,
                linhVucId=linh_vuc_id
            )

            db.session.add(chuyen_mon)

        commit()

        return (
            True,
            "Cập nhật chuyên môn thành công!"
        )

    except Exception as e:

        rollback()

        print(
            "Lỗi cập nhật chuyên môn:",
            e
        )

        return (
            False,
            str(e)
        )


# ==========================================================
# ĐỀ TÀI
# ==========================================================

def get_all_de_tai():

    return DeTai.query.order_by(
        DeTai.ngayTao.desc()
    ).all()


def get_de_tai_by_id(
    de_tai_id
):

    return db.session.get(
        DeTai,
        de_tai_id
    )


def them_de_tai(
    ten_de_tai,
    mo_ta,
    muc_tieu,
    tu_khoa,
    linh_vuc_id,
    sinh_vien_id
):

    try:

        linh_vuc = get_linh_vuc_by_id(
            linh_vuc_id
        )

        if not linh_vuc:

            return (
                False,
                "Lĩnh vực không tồn tại!",
                None
            )

        sinh_vien = get_user_by_id(
            sinh_vien_id
        )

        if not sinh_vien:

            return (
                False,
                "Không tìm thấy sinh viên!",
                None
            )

        if sinh_vien.role != UserRole.SINHVIEN:

            return (
                False,
                "Người tạo đề tài không phải sinh viên!",
                None
            )

        de_tai = DeTai(

            tenDeTai=ten_de_tai,

            moTa=mo_ta,

            mucTieu=muc_tieu,

            tuKhoa=tu_khoa,

            linhVucId=linh_vuc_id,

            sinhVienId=sinh_vien_id,

            giangVienId=None,

            trangThai=TrangThaiDeTai.CHO_DUYET
        )

        db.session.add(de_tai)

        commit()

        return (
            True,
            "Tạo đề tài thành công!",
            de_tai
        )

    except Exception as e:

        rollback()

        print(
            "LỖI THÊM ĐỀ TÀI:",
            e
        )

        return (
            False,
            "Có lỗi xảy ra khi tạo đề tài!",
            None
        )


def cap_nhat_de_tai(
    de_tai_id,
    ten_de_tai,
    mo_ta,
    muc_tieu,
    tu_khoa,
    linh_vuc_id
):

    try:

        de_tai = get_de_tai_by_id(
            de_tai_id
        )

        if not de_tai:

            return (
                False,
                "Không tìm thấy đề tài!"
            )

        linh_vuc = get_linh_vuc_by_id(
            linh_vuc_id
        )

        if not linh_vuc:

            return (
                False,
                "Lĩnh vực không tồn tại!"
            )

        de_tai.tenDeTai = ten_de_tai
        de_tai.moTa = mo_ta
        de_tai.mucTieu = muc_tieu
        de_tai.tuKhoa = tu_khoa
        de_tai.linhVucId = linh_vuc_id

        commit()

        return (
            True,
            "Cập nhật đề tài thành công!"
        )

    except Exception as e:

        rollback()

        print(
            "Lỗi cập nhật đề tài:",
            e
        )

        return (
            False,
            str(e)
        )


def xoa_de_tai(
    de_tai_id
):

    try:

        de_tai = get_de_tai_by_id(
            de_tai_id
        )

        if not de_tai:

            return (
                False,
                "Không tìm thấy đề tài!"
            )

        db.session.delete(de_tai)

        commit()

        return (
            True,
            "Xóa đề tài thành công!"
        )

    except Exception as e:

        rollback()

        print(
            "LỖI XÓA ĐỀ TÀI:",
            e
        )

        return (
            False,
            str(e)
        )


# ==========================================================
# TÌM KIẾM ĐỀ TÀI
# ==========================================================

def tim_kiem_de_tai(
    tu_khoa="",
    linh_vuc_id=None,
    trang_thai=None
):

    query = DeTai.query

    if tu_khoa:

        tu_khoa = tu_khoa.strip()

        if tu_khoa:

            keyword = f"%{tu_khoa}%"

            query = query.filter(
                or_(
                    DeTai.tenDeTai.ilike(keyword),
                    DeTai.moTa.ilike(keyword),
                    DeTai.mucTieu.ilike(keyword),
                    DeTai.tuKhoa.ilike(keyword)
                )
            )

    if linh_vuc_id:

        try:

            linh_vuc_id = int(linh_vuc_id)

            query = query.filter(
                DeTai.linhVucId == linh_vuc_id
            )

        except (ValueError, TypeError):

            pass

    if trang_thai:

        try:

            trang_thai_enum = TrangThaiDeTai(
                trang_thai
            )

            query = query.filter(
                DeTai.trangThai == trang_thai_enum
            )

        except (ValueError, TypeError):

            pass

    return query.order_by(
        DeTai.ngayTao.desc()
    ).all()


# ==========================================================
# DANH SÁCH / TÌM KIẾM ĐỀ TÀI
# ==========================================================

def get_list_de_tai(
    keyword=None,
    linh_vuc_id=None,
    ten_de_tai=None
):
    """
    Hỗ trợ:

        get_list_de_tai(keyword="AI")

    hoặc:

        get_list_de_tai(ten_de_tai="AI")

    """

    query = DeTai.query

    # Tương thích với code cũ
    if ten_de_tai is not None:
        keyword = ten_de_tai

    if keyword:

        keyword = keyword.strip()

        if keyword:

            keyword_like = f"%{keyword}%"

            query = query.filter(
                or_(
                    DeTai.tenDeTai.ilike(
                        keyword_like
                    ),

                    DeTai.moTa.ilike(
                        keyword_like
                    ),

                    DeTai.mucTieu.ilike(
                        keyword_like
                    ),

                    DeTai.tuKhoa.ilike(
                        keyword_like
                    )
                )
            )

    if linh_vuc_id:

        try:

            linh_vuc_id = int(
                linh_vuc_id
            )

            query = query.filter(
                DeTai.linhVucId ==
                linh_vuc_id
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    return query.order_by(
        DeTai.ngayTao.desc()
    ).all()


# ==========================================================
# TÌM KIẾM NGỮ NGHĨA
# ==========================================================

def tim_kiem_ngu_nghia(
    query
):

    if not query:

        return []

    query = query.strip()

    if not query:

        return []

    keyword = f"%{query}%"

    return (
        DeTai.query.filter(

            or_(
                DeTai.tenDeTai.ilike(
                    keyword
                ),

                DeTai.moTa.ilike(
                    keyword
                ),

                DeTai.mucTieu.ilike(
                    keyword
                ),

                DeTai.tuKhoa.ilike(
                    keyword
                )
            )

        ).order_by(
            DeTai.ngayTao.desc()
        ).all()
    )


# ==========================================================
# TÍNH ĐỘ TƯƠNG ĐỒNG
# ==========================================================

def tinh_do_tuong_dong(
    text1,
    text2
):

    if not text1 or not text2:

        return 0

    words1 = set(
        text1.lower().split()
    )

    words2 = set(
        text2.lower().split()
    )

    intersection = (
        words1.intersection(
            words2
        )
    )

    union = (
        words1.union(
            words2
        )
    )

    if not union:

        return 0

    score = (
        len(intersection)
        / len(union)
    )

    return round(
        score * 100,
        2
    )


# ==========================================================
# KIỂM TRA ĐỀ TÀI TRÙNG LẶP
# ==========================================================

def kiem_tra_trung_lap(
    de_tai_id
):

    de_tai = get_de_tai_by_id(
        de_tai_id
    )

    if not de_tai:

        return []

    ket_qua = []

    danh_sach = DeTai.query.filter(
        DeTai.id != de_tai_id
    ).all()

    noi_dung_1 = (

        f"{de_tai.tenDeTai or ''} "

        f"{de_tai.moTa or ''} "

        f"{de_tai.mucTieu or ''} "

        f"{de_tai.tuKhoa or ''}"
    )

    for item in danh_sach:

        noi_dung_2 = (

            f"{item.tenDeTai or ''} "

            f"{item.moTa or ''} "

            f"{item.mucTieu or ''} "

            f"{item.tuKhoa or ''}"
        )

        do_tuong_dong = (
            tinh_do_tuong_dong(
                noi_dung_1,
                noi_dung_2
            )
        )

        if do_tuong_dong > 0:

            ket_qua.append({

                "deTai": item,

                "doTuongDong":
                    do_tuong_dong
            })

    ket_qua.sort(

        key=lambda x:
            x["doTuongDong"],

        reverse=True
    )

    return ket_qua


# ==========================================================
# LƯU KIỂM TRA TRÙNG LẶP
# ==========================================================

def luu_kiem_tra_trung_lap(
    de_tai_1_id,
    de_tai_2_id,
    do_tuong_dong
):

    try:

        de_tai_1 = get_de_tai_by_id(
            de_tai_1_id
        )

        de_tai_2 = get_de_tai_by_id(
            de_tai_2_id
        )

        if not de_tai_1 or not de_tai_2:

            return False

        kiem_tra = KiemTraTrungLap(

            deTai1Id=de_tai_1_id,

            deTai2Id=de_tai_2_id,

            doTuongDong=do_tuong_dong
        )

        db.session.add(
            kiem_tra
        )

        commit()

        return True

    except Exception as e:

        rollback()

        print(
            "Lỗi lưu kiểm tra trùng lặp:",
            e
        )

        return False


# ==========================================================
# GỢI Ý GIẢNG VIÊN
# ==========================================================

def goi_y_giang_vien(de_tai_id):

    de_tai = get_de_tai_by_id(de_tai_id)

    if not de_tai:
        return []

    # Lấy các giảng viên đang hoạt động
    danh_sach_user = User.query.filter_by(
        role=UserRole.GIANGVIEN,
        active=True
    ).all()

    ket_qua = []

    # Nội dung của đề tài
    noi_dung_de_tai = " ".join([
        de_tai.tenDeTai or "",
        de_tai.moTa or "",
        de_tai.mucTieu or "",
        de_tai.tuKhoa or ""
    ]).lower()

    tu_khoa_de_tai = set(noi_dung_de_tai.split())

    for user in danh_sach_user:

        # Lấy thông tin giảng viên
        giang_vien_info = GiangVien.query.filter_by(
            userId=user.id
        ).first()

        if not giang_vien_info:
            continue

        # ==========================================================
        # 1. ĐIỂM LĨNH VỰC
        # ==========================================================

        diem_linh_vuc = 0

        chuyen_mon_list = GiangVienLinhVuc.query.filter_by(
            giangVienId=user.id
        ).all()

        linh_vuc_ids = [
            item.linhVucId
            for item in chuyen_mon_list
        ]

        if de_tai.linhVucId in linh_vuc_ids:
            diem_linh_vuc = 30


        # ==========================================================
        # 2. ĐIỂM CHUYÊN MÔN
        # ==========================================================

        diem_chuyen_mon = 0

        noi_dung_chuyen_mon = (
            (giang_vien_info.chuyenMon or "") + " " +
            (giang_vien_info.linhVucNghienCuu or "")
        ).lower()

        tu_khoa_chuyen_mon = set(
            noi_dung_chuyen_mon.split()
        )

        so_tu_khoa_trung = len(
            tu_khoa_chuyen_mon.intersection(
                tu_khoa_de_tai
            )
        )

        # Tối đa 30 điểm
        diem_chuyen_mon = min(
            so_tu_khoa_trung * 5,
            30
        )


        # ==========================================================
        # 3. ĐIỂM KINH NGHIỆM
        # ==========================================================
        #
        # Hiện tại model chưa có trường riêng về số năm kinh nghiệm.
        # Vì vậy sử dụng số lượng đề tài đã/đang hướng dẫn
        # làm thông tin tham khảo về kinh nghiệm.
        # ==========================================================

        so_de_tai = DeTai.query.filter_by(
            giangVienId=user.id
        ).count()

        if so_de_tai >= 5:
            diem_kinh_nghiem = 15

        elif so_de_tai >= 3:
            diem_kinh_nghiem = 12

        elif so_de_tai >= 1:
            diem_kinh_nghiem = 8

        else:
            diem_kinh_nghiem = 5


        # ==========================================================
        # 4. ĐIỂM TẢI HƯỚNG DẪN
        # ==========================================================

        gioi_han = giang_vien_info.soLuongHuongDanToiDa

        if gioi_han is None or gioi_han <= 0:
            gioi_han = 10


        # Giảng viên còn ít đề tài sẽ được ưu tiên hơn
        ty_le_tai = so_de_tai / gioi_han

        if ty_le_tai >= 1:
            diem_tai_huong_dan = 0

        elif ty_le_tai >= 0.8:
            diem_tai_huong_dan = 2

        elif ty_le_tai >= 0.5:
            diem_tai_huong_dan = 5

        elif ty_le_tai >= 0.3:
            diem_tai_huong_dan = 8

        else:
            diem_tai_huong_dan = 10


        # ==========================================================
        # 5. TÍNH TỔNG ĐIỂM
        # ==========================================================

        diem_phu_hop = (
            diem_linh_vuc
            + diem_chuyen_mon
            + diem_kinh_nghiem
            + diem_tai_huong_dan
        )

        # Giới hạn tối đa 100 điểm
        diem_phu_hop = min(
            diem_phu_hop,
            100
        )


        # ==========================================================
        # 6. TẠO LÝ DO GỢI Ý
        # ==========================================================

        ly_do = []

        if diem_linh_vuc > 0:
            ly_do.append(
                "Phù hợp với lĩnh vực của đề tài"
            )

        if diem_chuyen_mon > 0:
            ly_do.append(
                "Có chuyên môn/hướng nghiên cứu liên quan"
            )

        if diem_kinh_nghiem >= 12:
            ly_do.append(
                "Có kinh nghiệm hướng dẫn đề tài"
            )

        if diem_tai_huong_dan >= 8:
            ly_do.append(
                "Còn khả năng nhận thêm đề tài"
            )

        if not ly_do:
            ly_do.append(
                "Được hệ thống lựa chọn để tham khảo"
            )


        # ==========================================================
        # 7. THÊM KẾT QUẢ
        # ==========================================================

        ket_qua.append({
            "giangVien": user,
            "giangVienInfo": giang_vien_info,

            "diemPhuHop": diem_phu_hop,

            "diemLinhVuc": diem_linh_vuc,
            "diemChuyenMon": diem_chuyen_mon,
            "diemKinhNghiem": diem_kinh_nghiem,
            "diemTaiHuongDan": diem_tai_huong_dan,

            "soLuongDangHuongDan": so_de_tai,
            "soLuongHuongDanToiDa": gioi_han,

            "conKhaNangHuongDan": (
                so_de_tai < gioi_han
            ),

            "lyDo": ly_do
        })


    # ==============================================================
    # 8. SẮP XẾP GIẢNG VIÊN THEO ĐIỂM GIẢM DẦN
    # ==============================================================

    ket_qua.sort(
        key=lambda x: x["diemPhuHop"],
        reverse=True
    )

    return ket_qua

# ==========================================================
# LƯU GỢI Ý GIẢNG VIÊN
# ==========================================================

def luu_goi_y_giang_vien(
    de_tai_id,
    giang_vien_id,
    diem,
    ly_do=None
):

    try:

        de_tai = get_de_tai_by_id(
            de_tai_id
        )

        if not de_tai:

            return False

        # giang_vien_id = User.id
        user = get_user_by_id(
            giang_vien_id
        )

        if not user:

            return False

        if user.role != UserRole.GIANGVIEN:

            return False

        goi_y = GoiYGiangVien(

            deTaiId=de_tai_id,

            giangVienId=giang_vien_id,

            diemPhuHop=diem,

            lyDo=ly_do
        )

        db.session.add(goi_y)

        commit()

        return True

    except Exception as e:

        rollback()

        print(
            "Lỗi lưu gợi ý giảng viên:",
            e
        )

        return False



# ==========================================================
# DUYỆT ĐỀ TÀI
# ==========================================================

def duyet_de_tai(
    de_tai_id,
    giang_vien_id=None
):

    try:

        de_tai = get_de_tai_by_id(
            de_tai_id
        )

        if not de_tai:

            return (
                False,
                "Không tìm thấy đề tài!"
            )

        # Nếu có chọn giảng viên
        if giang_vien_id:

            giang_vien = get_user_by_id(
                giang_vien_id
            )

            if not giang_vien:

                return (
                    False,
                    "Không tìm thấy giảng viên!"
                )

            if (
                giang_vien.role
                != UserRole.GIANGVIEN
            ):

                return (
                    False,
                    "Người được chọn không phải giảng viên!"
                )

            if not giang_vien.active:

                return (
                    False,
                    "Giảng viên đã bị khóa!"
                )

            de_tai.giangVienId = (
                giang_vien_id
            )

        else:

            return (
                False,
                "Vui lòng chọn giảng viên!"
            )

        de_tai.trangThai = (
            TrangThaiDeTai.DA_DUYET
        )

        commit()

        return (
            True,
            "Duyệt đề tài thành công!"
        )

    except Exception as e:

        rollback()

        print(
            "Lỗi duyệt đề tài:",
            e
        )

        return (
            False,
            str(e)
        )


# ==========================================================
# TỪ CHỐI ĐỀ TÀI
# ==========================================================

def tu_choi_de_tai(
    de_tai_id
):

    try:

        de_tai = get_de_tai_by_id(
            de_tai_id
        )

        if not de_tai:

            return (
                False,
                "Không tìm thấy đề tài!"
            )

        de_tai.trangThai = (
            TrangThaiDeTai.TU_CHOI
        )

        commit()

        return (
            True,
            "Đã từ chối đề tài!"
        )

    except Exception as e:

        rollback()

        print(
            "Lỗi từ chối đề tài:",
            e
        )

        return (
            False,
            str(e)
        )


# ==========================================================
# THỐNG KÊ
# ==========================================================

def thong_ke_de_tai():

    tong_de_tai = (
        DeTai.query.count()
    )

    nhap = (
        DeTai.query.filter_by(
            trangThai=TrangThaiDeTai.NHAP
        ).count()
    )

    cho_duyet = (
        DeTai.query.filter_by(
            trangThai=TrangThaiDeTai.CHO_DUYET
        ).count()
    )

    da_duyet = (
        DeTai.query.filter_by(
            trangThai=TrangThaiDeTai.DA_DUYET
        ).count()
    )

    tu_choi = (
        DeTai.query.filter_by(
            trangThai=TrangThaiDeTai.TU_CHOI
        ).count()
    )

    hoan_thanh = (
        DeTai.query.filter_by(
            trangThai=TrangThaiDeTai.HOAN_THANH
        ).count()
    )

    return {

        "tongDeTai":
            tong_de_tai,

        "nhap":
            nhap,

        "choDuyet":
            cho_duyet,

        "daDuyet":
            da_duyet,

        "tuChoi":
            tu_choi,

        "hoanThanh":
            hoan_thanh
    }


# ==========================================================
# LỊCH SỬ TÌM KIẾM
# ==========================================================

def luu_lich_su_tim_kiem(
    user_id,
    tu_khoa
):

    try:

        if not tu_khoa:
            return False

        lich_su = LichSuTimKiem(

            userId=user_id,

            tuKhoa=tu_khoa
        )

        db.session.add(lich_su)

        commit()

        return True

    except Exception as e:

        rollback()

        print(
            "Lỗi lưu lịch sử tìm kiếm:",
            e
        )

        return False


# ==========================================================
# AI - KIỂM TRA TRÙNG LẶP
# ==========================================================

def kiem_tra_trung_lap_ai(
    noi_dung
):

    if not noi_dung:

        return []

    danh_sach_de_tai = (
        DeTai.query.all()
    )

    if not danh_sach_de_tai:

        return []

    noi_dung = (
        noi_dung.lower().strip()
    )

    ket_qua = []

    for de_tai in danh_sach_de_tai:

        ten_de_tai = (
            de_tai.tenDeTai or ""
        )

        mo_ta = (
            de_tai.moTa or ""
        )

        muc_tieu = (
            de_tai.mucTieu or ""
        )

        tu_khoa = (
            de_tai.tuKhoa or ""
        )

        noi_dung_de_tai = (

            ten_de_tai
            + " "
            + mo_ta
            + " "
            + muc_tieu
            + " "
            + tu_khoa

        ).lower().strip()

        if not noi_dung_de_tai:

            continue

        do_tuong_dong = (
            SequenceMatcher(
                None,
                noi_dung,
                noi_dung_de_tai
            ).ratio()
            * 100
        )

        phan_tram = round(
            do_tuong_dong,
            2
        )

        if phan_tram >= 20:

            ket_qua.append({

                "ten_de_tai":
                    ten_de_tai,

                "phan_tram":
                    phan_tram
            })

    ket_qua.sort(

        key=lambda x:
            x["phan_tram"],

        reverse=True
    )

    return ket_qua


# ==========================================================
# TIẾN ĐỘ ĐỀ TÀI
# ==========================================================

def get_tien_do_de_tai(
    de_tai_id
):

    return TienDo.query.filter_by(

        deTaiId=de_tai_id

    ).order_by(

        TienDo.ngayCapNhat.desc()

    ).all()


def get_tien_do_by_id(
    tien_do_id
):

    return db.session.get(
        TienDo,
        tien_do_id
    )


def them_tien_do(
    de_tai_id,
    tieu_de,
    noi_dung=None,
    phan_tram=0,
    trang_thai=TrangThaiTienDo.CHUA_BAT_DAU
):

    try:

        # Kiểm tra đề tài
        de_tai = get_de_tai_by_id(
            de_tai_id
        )

        if not de_tai:

            return (
                False,
                "Không tìm thấy đề tài!",
                None
            )

        # Kiểm tra tiêu đề
        tieu_de = (
            tieu_de or ""
        ).strip()

        if not tieu_de:

            return (
                False,
                "Tiêu đề tiến độ không được để trống!",
                None
            )

        # Kiểm tra phần trăm
        try:

            phan_tram = int(
                phan_tram
            )

        except (
            ValueError,
            TypeError
        ):

            phan_tram = 0

        # Giới hạn 0 - 100
        phan_tram = max(
            0,
            min(
                phan_tram,
                100
            )
        )

        tien_do = TienDo(

            deTaiId=de_tai_id,

            tieuDe=tieu_de,

            noiDung=noi_dung,

            phanTram=phan_tram,

            trangThai=trang_thai
        )

        db.session.add(
            tien_do
        )

        commit()

        return (
            True,
            "Thêm tiến độ thành công!",
            tien_do
        )

    except Exception as e:

        rollback()

        print(
            "Lỗi thêm tiến độ:",
            e
        )

        return (
            False,
            str(e),
            None
        )


def cap_nhat_tien_do(
    tien_do_id,
    tieu_de,
    noi_dung,
    phan_tram,
    trang_thai,
    nhan_xet_giang_vien=None
):

    try:

        tien_do = get_tien_do_by_id(
            tien_do_id
        )

        if not tien_do:

            return (
                False,
                "Không tìm thấy tiến độ!"
            )

        # Kiểm tra tiêu đề
        tieu_de = (
            tieu_de or ""
        ).strip()

        if not tieu_de:

            return (
                False,
                "Tiêu đề tiến độ không được để trống!"
            )

        # Kiểm tra phần trăm
        try:

            phan_tram = int(
                phan_tram
            )

        except (
            ValueError,
            TypeError
        ):

            return (
                False,
                "Phần trăm tiến độ không hợp lệ!"
            )

        if phan_tram < 0:
            phan_tram = 0

        if phan_tram > 100:
            phan_tram = 100

        tien_do.tieuDe = tieu_de

        tien_do.noiDung = noi_dung

        tien_do.phanTram = phan_tram

        tien_do.trangThai = trang_thai

        tien_do.nhanXetGiangVien = (
            nhan_xet_giang_vien
        )

        commit()

        return (
            True,
            "Cập nhật tiến độ thành công!"
        )

    except Exception as e:

        rollback()

        print(
            "Lỗi cập nhật tiến độ:",
            e
        )

        return (
            False,
            str(e)
        )


def xoa_tien_do(
    tien_do_id
):

    try:

        tien_do = get_tien_do_by_id(
            tien_do_id
        )

        if not tien_do:

            return (
                False,
                "Không tìm thấy tiến độ!"
            )

        db.session.delete(tien_do)

        commit()

        return (
            True,
            "Xóa tiến độ thành công!"
        )

    except Exception as e:

        rollback()

        return (
            False,
            str(e)
        )


# ==========================================================
# YÊU CẦU CHỈNH SỬA
# ==========================================================

def get_yeu_cau_chinh_sua(
    de_tai_id
):

    return YeuCauChinhSua.query.filter_by(

        deTaiId=de_tai_id

    ).order_by(

        YeuCauChinhSua.ngayTao.desc()

    ).all()


def get_yeu_cau_chinh_sua_by_id(
    yeu_cau_id
):

    return db.session.get(
        YeuCauChinhSua,
        yeu_cau_id
    )

def get_yeu_cau_chinh_sua_cua_giang_vien(giang_vien_id):
    return (
        YeuCauChinhSua.query
        .join(
            DeTai,
            YeuCauChinhSua.deTaiId == DeTai.id
        )
        .filter(
            DeTai.giangVienId == giang_vien_id
        )
        .order_by(
            YeuCauChinhSua.ngayTao.desc()
        )
        .all()
    )

def them_yeu_cau_chinh_sua(
    de_tai_id,
    nguoi_yeu_cau_id,
    noi_dung
):

    try:

        yeu_cau = YeuCauChinhSua(

            deTaiId=de_tai_id,

            nguoiYeuCauId=
                nguoi_yeu_cau_id,

            noiDung=noi_dung,

            daXuLy=False
        )

        db.session.add(yeu_cau)

        commit()

        return (
            True,
            "Gửi yêu cầu chỉnh sửa thành công!",
            yeu_cau
        )

    except Exception as e:

        rollback()

        return (
            False,
            str(e),
            None
        )


def xu_ly_yeu_cau_chinh_sua(
    yeu_cau_id
):

    try:

        yeu_cau = (
            get_yeu_cau_chinh_sua_by_id(
                yeu_cau_id
            )
        )

        if not yeu_cau:

            return (
                False,
                "Không tìm thấy yêu cầu!"
            )

        yeu_cau.daXuLy = True

        commit()

        return (
            True,
            "Đã xử lý yêu cầu!"
        )

    except Exception as e:

        rollback()

        return (
            False,
            str(e)
        )


# ==========================================================
# NGHIỆM THU
# ==========================================================

def get_ket_qua_nghiem_thu(
    de_tai_id
):

    return KetQuaNghiemThu.query.filter_by(

        deTaiId=de_tai_id

    ).first()


def them_ket_qua_nghiem_thu(
    de_tai_id,
    nguoi_nghiem_thu_id,
    diem=None,
    nhan_xet=None,
    ket_luan=None,
    trang_thai=TrangThaiNghiemThu.CHUA_NGHIEM_THU
):

    try:

        ket_qua = KetQuaNghiemThu(

            deTaiId=de_tai_id,

            nguoiNghiemThuId=
                nguoi_nghiem_thu_id,

            diem=diem,

            nhanXet=nhan_xet,

            ketLuan=ket_luan,

            trangThai=trang_thai
        )

        db.session.add(ket_qua)

        commit()

        return (
            True,
            "Lưu kết quả nghiệm thu thành công!",
            ket_qua
        )

    except Exception as e:

        rollback()

        return (
            False,
            str(e),
            None
        )


def cap_nhat_ket_qua_nghiem_thu(
    de_tai_id,
    diem,
    nhan_xet,
    ket_luan,
    trang_thai
):

    try:

        ket_qua = (
            get_ket_qua_nghiem_thu(
                de_tai_id
            )
        )

        if not ket_qua:

            return (
                False,
                "Chưa có kết quả nghiệm thu!"
            )

        ket_qua.diem = diem

        ket_qua.nhanXet = nhan_xet

        ket_qua.ketLuan = ket_luan

        ket_qua.trangThai = trang_thai

        commit()

        return (
            True,
            "Cập nhật kết quả nghiệm thu thành công!"
        )

    except Exception as e:

        rollback()

        return (
            False,
            str(e)
        )


# ==========================================================
# THÔNG BÁO
# ==========================================================

def get_thong_bao_user(
    user_id
):

    return ThongBao.query.filter_by(

        userId=user_id

    ).order_by(

        ThongBao.ngayTao.desc()

    ).all()


def get_thong_bao_chua_doc(
    user_id
):

    return ThongBao.query.filter_by(

        userId=user_id,

        daDoc=False

    ).order_by(

        ThongBao.ngayTao.desc()

    ).all()


def dem_thong_bao_chua_doc(
    user_id
):

    return ThongBao.query.filter_by(

        userId=user_id,

        daDoc=False

    ).count()


def tao_thong_bao(
    user_id,
    tieu_de,
    noi_dung,
    loai=LoaiThongBao.HE_THONG,
    de_tai_id=None
):

    try:

        thong_bao = ThongBao(

            userId=user_id,

            tieuDe=tieu_de,

            noiDung=noi_dung,

            loai=loai,

            deTaiId=de_tai_id,

            daDoc=False
        )

        db.session.add(thong_bao)

        commit()

        return (
            True,
            "Tạo thông báo thành công!",
            thong_bao
        )

    except Exception as e:

        rollback()

        return (
            False,
            str(e),
            None
        )


def danh_dau_thong_bao_da_doc(
    thong_bao_id
):

    try:

        thong_bao = db.session.get(
            ThongBao,
            thong_bao_id
        )

        if not thong_bao:

            return (
                False,
                "Không tìm thấy thông báo!"
            )

        thong_bao.daDoc = True

        commit()

        return (
            True,
            "Đã đánh dấu đã đọc!"
        )

    except Exception as e:

        rollback()

        return (
            False,
            str(e)
        )


def danh_dau_tat_ca_thong_bao_da_doc(
    user_id
):

    try:

        ThongBao.query.filter_by(

            userId=user_id,

            daDoc=False

        ).update(

            {
                "daDoc": True
            },

            synchronize_session=False
        )

        commit()

        return (
            True,
            "Đã đọc tất cả thông báo!"
        )

    except Exception as e:

        rollback()

        return (
            False,
            str(e)
        )


# ==========================================================
# TÀI LIỆU
# ==========================================================

def get_tai_lieu_de_tai(
    de_tai_id
):

    return TaiLieu.query.filter_by(

        deTaiId=de_tai_id

    ).order_by(

        TaiLieu.ngayTai.desc()

    ).all()


def get_tai_lieu_by_id(
    tai_lieu_id
):

    return db.session.get(
        TaiLieu,
        tai_lieu_id
    )


def them_tai_lieu(
    de_tai_id,
    nguoi_tai_id,
    ten_tai_lieu,
    duong_dan,
    loai_file=None
):

    try:

        tai_lieu = TaiLieu(

            deTaiId=de_tai_id,

            nguoiTaiId=nguoi_tai_id,

            tenTaiLieu=ten_tai_lieu,

            duongDan=duong_dan,

            loaiFile=loai_file
        )

        db.session.add(tai_lieu)

        commit()

        return (
            True,
            "Tải tài liệu thành công!",
            tai_lieu
        )

    except Exception as e:

        rollback()

        return (
            False,
            str(e),
            None
        )


def xoa_tai_lieu(
    tai_lieu_id
):

    try:

        tai_lieu = get_tai_lieu_by_id(
            tai_lieu_id
        )

        if not tai_lieu:

            return (
                False,
                "Không tìm thấy tài liệu!"
            )

        db.session.delete(tai_lieu)

        commit()

        return (
            True,
            "Xóa tài liệu thành công!"
        )

    except Exception as e:

        rollback()

        return (
            False,
            str(e)
        )


# ==========================================================
# TIỆN ÍCH DUYỆT ĐỀ TÀI
# ==========================================================

def get_de_tai_cho_duyet():

    return DeTai.query.filter_by(

        trangThai=
            TrangThaiDeTai.CHO_DUYET

    ).order_by(

        DeTai.ngayTao.asc()

    ).all()


def get_de_tai_da_duyet():

    return DeTai.query.filter_by(

        trangThai=
            TrangThaiDeTai.DA_DUYET

    ).order_by(

        DeTai.ngayCapNhat.desc()

    ).all()


def get_de_tai_cua_sinh_vien(
    sinh_vien_id
):

    return DeTai.query.filter_by(

        sinhVienId=sinh_vien_id

    ).order_by(

        DeTai.ngayTao.desc()

    ).all()


def get_de_tai_cua_giang_vien(
    giang_vien_id
):

    # giang_vien_id = User.id
    return DeTai.query.filter_by(

        giangVienId=giang_vien_id

    ).order_by(

        DeTai.ngayTao.desc()

    ).all()