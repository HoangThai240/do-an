from datetime import datetime
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
    YeuCauNghiemThu,
    TrangThaiYeuCauNghiemThu,
    TienDo,
    TrangThaiTienDo,
    KhieuNaiNghiemThu,
    TrangThaiKhieuNai,
    YeuCauChinhSua,
    KetQuaNghiemThu,
    TrangThaiNghiemThu,
    ThongBao,
    LoaiThongBao,
    TaiLieu
)

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


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

        reset_embedding_cache()

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

        reset_embedding_cache()

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

        reset_embedding_cache()

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


# ============================================================
# MODEL AI DÙNG CHO TÌM KIẾM NGỮ NGHĨA
# ============================================================

_model_embedding = None


def get_embedding_model():
    global _model_embedding

    if _model_embedding is None:
        _model_embedding = SentenceTransformer(
            'paraphrase-multilingual-MiniLM-L12-v2'
        )

    return _model_embedding


# ============================================================
# TẠO NỘI DUNG ĐỂ AI HIỂU ĐỀ TÀI
# ============================================================

def tao_text_de_tai(de_tai):

    parts = []

    if de_tai.tenDeTai:
        parts.append(
            f"Tên đề tài: {de_tai.tenDeTai}"
        )

    if de_tai.moTa:
        parts.append(
            f"Mô tả: {de_tai.moTa}"
        )

    if de_tai.mucTieu:
        parts.append(
            f"Mục tiêu: {de_tai.mucTieu}"
        )

    if de_tai.tuKhoa:
        parts.append(
            f"Từ khóa: {de_tai.tuKhoa}"
        )

    return ". ".join(parts)


# ============================================================
# MODEL AI DÙNG CHO TÌM KIẾM NGỮ NGHĨA
# ============================================================

_model_embedding = None

# Cache danh sách đề tài
_de_tai_cache = None

# Cache embedding của các đề tài
_embedding_cache = None


# ============================================================
# LOAD MODEL AI
# ============================================================

def get_embedding_model():

    global _model_embedding

    if _model_embedding is None:

        print("========================================")
        print("ĐANG TẢI MODEL AI...")
        print("========================================")

        _model_embedding = SentenceTransformer(
            'paraphrase-multilingual-MiniLM-L12-v2'
        )

        print("ĐÃ TẢI MODEL AI")
        print("========================================")

    return _model_embedding


# ============================================================
# TẠO NỘI DUNG ĐỂ AI HIỂU ĐỀ TÀI
# ============================================================

def tao_text_de_tai(de_tai):

    parts = []

    if de_tai.tenDeTai:

        parts.append(
            f"Tên đề tài: {de_tai.tenDeTai}"
        )

    if de_tai.moTa:

        parts.append(
            f"Mô tả: {de_tai.moTa}"
        )

    if de_tai.mucTieu:

        parts.append(
            f"Mục tiêu: {de_tai.mucTieu}"
        )

    if de_tai.tuKhoa:

        parts.append(
            f"Từ khóa: {de_tai.tuKhoa}"
        )

    return ". ".join(parts)


# ============================================================
# TẠO CACHE EMBEDDING CHO CÁC ĐỀ TÀI
# ============================================================

def tao_embedding_cache():

    global _de_tai_cache
    global _embedding_cache

    print("========================================")
    print("ĐANG TẠO EMBEDDING CHO CÁC ĐỀ TÀI...")
    print("========================================")

    # Lấy tất cả đề tài
    danh_sach_de_tai = (
        DeTai.query
        .order_by(DeTai.ngayTao.desc())
        .all()
    )

    if not danh_sach_de_tai:

        _de_tai_cache = []
        _embedding_cache = None

        print("Không có đề tài để tạo embedding.")

        return

    # Load model
    model = get_embedding_model()

    # Tạo nội dung cho từng đề tài
    texts = [
        tao_text_de_tai(de_tai)
        for de_tai in danh_sach_de_tai
    ]

    # Tạo embedding MỘT LẦN
    _embedding_cache = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # Lưu danh sách đề tài
    _de_tai_cache = danh_sach_de_tai

    print(
        f"ĐÃ TẠO EMBEDDING CHO "
        f"{len(danh_sach_de_tai)} ĐỀ TÀI"
    )

    print("========================================")


# ============================================================
# XÓA CACHE AI
# ============================================================

def reset_embedding_cache():

    global _de_tai_cache
    global _embedding_cache

    _de_tai_cache = None
    _embedding_cache = None

    print("ĐÃ RESET CACHE AI")


# ============================================================
# TÌM KIẾM NGỮ NGHĨA
# ============================================================

def tim_kiem_ngu_nghia(
    query,
    nguong=0.35,
    so_luong=10
):

    # --------------------------------------------------------
    # 1. Kiểm tra câu hỏi
    # --------------------------------------------------------

    if not query:

        return []

    query = query.strip()

    if not query:

        return []


    # --------------------------------------------------------
    # 2. Nếu chưa có cache thì tạo cache
    # --------------------------------------------------------

    if (
        _de_tai_cache is None
        or _embedding_cache is None
    ):

        tao_embedding_cache()


    # --------------------------------------------------------
    # 3. Không có đề tài
    # --------------------------------------------------------

    if not _de_tai_cache:

        return []


    # --------------------------------------------------------
    # 4. Load model
    # --------------------------------------------------------

    model = get_embedding_model()


    # --------------------------------------------------------
    # 5. Chỉ encode câu hỏi người dùng
    # --------------------------------------------------------

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )


    # --------------------------------------------------------
    # 6. Tính Cosine Similarity
    # --------------------------------------------------------

    scores = cosine_similarity(
        query_embedding,
        _embedding_cache
    )[0]


    # --------------------------------------------------------
    # 7. Ghép đề tài + điểm tương đồng
    # --------------------------------------------------------

    ket_qua = []

    for de_tai, score in zip(
        _de_tai_cache,
        scores
    ):

        score = float(score)

        if score >= nguong:

            ket_qua.append(
                (
                    de_tai,
                    score
                )
            )


    # --------------------------------------------------------
    # 8. Sắp xếp điểm cao → thấp
    # --------------------------------------------------------

    ket_qua.sort(
        key=lambda x: x[1],
        reverse=True
    )


    # --------------------------------------------------------
    # 9. Giới hạn số kết quả
    # --------------------------------------------------------

    ket_qua = ket_qua[:so_luong]


    # --------------------------------------------------------
    # 10. Trả về danh sách DeTai
    # --------------------------------------------------------

    return [
        de_tai
        for de_tai, score in ket_qua
    ]

# ==========================================================
# TÍNH ĐỘ TƯƠNG ĐỒNG
# ==========================================================

def tinh_do_tuong_dong(text1, text2):
    """
    Tính độ tương đồng giữa 2 chuỗi bằng Jaccard.
    Kết quả: 0 - 100 (%)
    """

    if not text1 or not text2:
        return 0.0

    text1 = str(text1).lower().strip()
    text2 = str(text2).lower().strip()

    if not text1 or not text2:
        return 0.0

    words1 = set(text1.split())
    words2 = set(text2.split())

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    if not union:
        return 0.0

    score = len(intersection) / len(union)

    return round(score * 100, 2)


# ==========================================================
# TÍNH 5 TIÊU CHÍ TRÙNG LẶP
# ==========================================================

def tinh_5_tieu_chi_trung_lap(de_tai_1, de_tai_2):

    # ------------------------------------------------------
    # 1. TRÙNG LẶP ĐỀ TÀI
    # ------------------------------------------------------

    diem_de_tai = tinh_do_tuong_dong(
        de_tai_1.tenDeTai,
        de_tai_2.tenDeTai
    )

    # ------------------------------------------------------
    # 2. TRÙNG LẶP HƯỚNG NGHIÊN CỨU
    # ------------------------------------------------------

    linh_vuc_1 = ""
    linh_vuc_2 = ""

    if de_tai_1.linh_vuc:
        linh_vuc_1 = (
            de_tai_1.linh_vuc.tenLinhVuc or ""
        )

    if de_tai_2.linh_vuc:
        linh_vuc_2 = (
            de_tai_2.linh_vuc.tenLinhVuc or ""
        )

    huong_nghien_cuu_1 = " ".join([
        linh_vuc_1,
        de_tai_1.tuKhoa or "",
        de_tai_1.moTa or ""
    ])

    huong_nghien_cuu_2 = " ".join([
        linh_vuc_2,
        de_tai_2.tuKhoa or "",
        de_tai_2.moTa or ""
    ])

    diem_huong_nghien_cuu = tinh_do_tuong_dong(
        huong_nghien_cuu_1,
        huong_nghien_cuu_2
    )

    # ------------------------------------------------------
    # 3. TRÙNG LẶP MỤC TIÊU
    # ------------------------------------------------------

    diem_muc_tieu = tinh_do_tuong_dong(
        de_tai_1.mucTieu,
        de_tai_2.mucTieu
    )

    # ------------------------------------------------------
    # 4. TRÙNG LẶP TỪ KHÓA
    # ------------------------------------------------------

    diem_tu_khoa = tinh_do_tuong_dong(
        de_tai_1.tuKhoa,
        de_tai_2.tuKhoa
    )

    # ------------------------------------------------------
    # 5. TRÙNG LẶP MÔ TẢ
    # ------------------------------------------------------

    diem_mo_ta = tinh_do_tuong_dong(
        de_tai_1.moTa,
        de_tai_2.moTa
    )

    # ------------------------------------------------------
    # ĐIỂM TỔNG
    # ------------------------------------------------------

    do_tuong_dong = round(
        diem_de_tai * 0.20
        + diem_huong_nghien_cuu * 0.25
        + diem_muc_tieu * 0.20
        + diem_tu_khoa * 0.15
        + diem_mo_ta * 0.20,
        2
    )

    return {
        "trungLapDeTai": diem_de_tai,
        "trungLapHuongNghienCuu": diem_huong_nghien_cuu,
        "trungLapMucTieu": diem_muc_tieu,
        "trungLapTuKhoa": diem_tu_khoa,
        "trungLapMoTa": diem_mo_ta,
        "doTuongDong": do_tuong_dong
    }

# ==========================================================
# LƯU KIỂM TRA TRÙNG LẶP
# ==========================================================

def luu_kiem_tra_trung_lap(
    de_tai_1_id,
    de_tai_2_id,
    diem
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

        kiem_tra = KiemTraTrungLap.query.filter(
            or_(
                (
                    (KiemTraTrungLap.deTai1Id == de_tai_1_id)
                    &
                    (KiemTraTrungLap.deTai2Id == de_tai_2_id)
                ),
                (
                    (KiemTraTrungLap.deTai1Id == de_tai_2_id)
                    &
                    (KiemTraTrungLap.deTai2Id == de_tai_1_id)
                )
            )
        ).first()

        if not kiem_tra:

            kiem_tra = KiemTraTrungLap(

                deTai1Id=de_tai_1_id,

                deTai2Id=de_tai_2_id,

                doTuongDong=
                    diem["doTuongDong"],

                trungLapDeTai=
                    diem["trungLapDeTai"],

                trungLapHuongNghienCuu=
                    diem["trungLapHuongNghienCuu"],

                trungLapMucTieu=
                    diem["trungLapMucTieu"],

                trungLapTuKhoa=
                    diem["trungLapTuKhoa"],

                trungLapMoTa=
                    diem["trungLapMoTa"]
            )

            db.session.add(
                kiem_tra
            )

        else:

            kiem_tra.doTuongDong = (
                diem["doTuongDong"]
            )

            kiem_tra.trungLapDeTai = (
                diem["trungLapDeTai"]
            )

            kiem_tra.trungLapHuongNghienCuu = (
                diem["trungLapHuongNghienCuu"]
            )

            kiem_tra.trungLapMucTieu = (
                diem["trungLapMucTieu"]
            )

            kiem_tra.trungLapTuKhoa = (
                diem["trungLapTuKhoa"]
            )

            kiem_tra.trungLapMoTa = (
                diem["trungLapMoTa"]
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
# KIỂM TRA + TÍNH + LƯU
# ==========================================================

def kiem_tra_va_luu_trung_lap(de_tai_id):

    print("\n========================================")
    print("BAT DAU KIEM TRA TRUNG LAP")
    print("De tai ID:", de_tai_id)
    print("========================================")

    de_tai = get_de_tai_by_id(de_tai_id)

    if not de_tai:
        print("KHONG TIM THAY DE TAI")
        return []

    print("Tim thay de tai:")
    print("ID:", de_tai.id)
    print("Ten:", de_tai.tenDeTai)

    danh_sach = DeTai.query.filter(
        DeTai.id != de_tai_id,
        DeTai.trangThai.in_([
            TrangThaiDeTai.CHO_DUYET,
            TrangThaiDeTai.DA_DUYET,
            TrangThaiDeTai.HOAN_THANH
        ])
    ).all()

    print("So de tai dung de so sanh:", len(danh_sach))

    ket_qua = []

    for item in danh_sach:

        print("----------------------------------------")
        print("Dang so sanh:")
        print("De tai hien tai:", de_tai.id)
        print("De tai so sanh:", item.id)
        print("Ten:", item.tenDeTai)

        try:

            print("1. Bat dau tinh 5 tieu chi...")

            diem = tinh_5_tieu_chi_trung_lap(
                de_tai,
                item
            )

            print("2. Tinh xong:")
            print(diem)

            print("3. Dang luu ket qua...")

            luu_thanh_cong = luu_kiem_tra_trung_lap(
                de_tai_id,
                item.id,
                diem
            )

            print(
                "4. Luu ket qua:",
                luu_thanh_cong
            )

            ket_qua.append({
                "deTai": item,

                "doTuongDong": float(
                    diem.get("doTuongDong", 0)
                ),

                "trungLapDeTai": float(
                    diem.get("trungLapDeTai", 0)
                ),

                "trungLapHuongNghienCuu": float(
                    diem.get("trungLapHuongNghienCuu", 0)
                ),

                "trungLapMucTieu": float(
                    diem.get("trungLapMucTieu", 0)
                ),

                "trungLapTuKhoa": float(
                    diem.get("trungLapTuKhoa", 0)
                ),

                "trungLapMoTa": float(
                    diem.get("trungLapMoTa", 0)
                )
            })

            print("5. Da them vao ket qua")

        except Exception as e:

            print("LOI KHI XU LY DE TAI:", item.id)
            print("LOI:", e)

            continue

    ket_qua.sort(
        key=lambda x: x["doTuongDong"],
        reverse=True
    )

    print("\n========================================")
    print("HOAN THANH KIEM TRA TRUNG LAP")
    print("Tong ket qua:", len(ket_qua))
    print("========================================\n")

    return ket_qua[:5]

# ==========================================================
# KIỂM TRA ĐỀ TÀI MỚI - DÀNH CHO SINH VIÊN
# ==========================================================

def kiem_tra_trung_lap_de_tai_moi(
    ten_de_tai,
    mo_ta,
    muc_tieu,
    tu_khoa,
    linh_vuc_id=None
):

    linh_vuc_moi = ""

    # Lấy tên lĩnh vực của đề tài mới
    if linh_vuc_id:

        try:
            linh_vuc_id = int(linh_vuc_id)
        except (ValueError, TypeError):
            linh_vuc_id = None

    if linh_vuc_id:

        linh_vuc = get_linh_vuc_by_id(
            linh_vuc_id
        )

        if linh_vuc:
            linh_vuc_moi = (
                linh_vuc.tenLinhVuc or ""
            )

    ket_qua = []

    # Lấy tất cả đề tài đã có trong hệ thống
    danh_sach_de_tai = DeTai.query.all()

    for de_tai in danh_sach_de_tai:

        # ==================================================
        # 1. TRÙNG LẶP ĐỀ TÀI
        # ==================================================

        diem_de_tai = tinh_do_tuong_dong(
            ten_de_tai,
            de_tai.tenDeTai
        )

        # ==================================================
        # 2. TRÙNG LẶP HƯỚNG NGHIÊN CỨU
        # ==================================================

        linh_vuc_cu = ""

        if de_tai.linh_vuc:

            linh_vuc_cu = (
                de_tai.linh_vuc.tenLinhVuc or ""
            )

        huong_nghien_cuu_moi = " ".join([
            linh_vuc_moi,
            tu_khoa or "",
            mo_ta or ""
        ])

        huong_nghien_cuu_cu = " ".join([
            linh_vuc_cu,
            de_tai.tuKhoa or "",
            de_tai.moTa or ""
        ])

        diem_huong_nghien_cuu = tinh_do_tuong_dong(
            huong_nghien_cuu_moi,
            huong_nghien_cuu_cu
        )

        # ==================================================
        # 3. TRÙNG LẶP MỤC TIÊU
        # ==================================================

        diem_muc_tieu = tinh_do_tuong_dong(
            muc_tieu,
            de_tai.mucTieu
        )

        # ==================================================
        # 4. TRÙNG LẶP TỪ KHÓA
        # ==================================================

        diem_tu_khoa = tinh_do_tuong_dong(
            tu_khoa,
            de_tai.tuKhoa
        )

        # ==================================================
        # 5. TRÙNG LẶP NỘI DUNG MÔ TẢ
        # ==================================================

        diem_mo_ta = tinh_do_tuong_dong(
            mo_ta,
            de_tai.moTa
        )

        # ==================================================
        # TÍNH ĐIỂM TỔNG
        # ==================================================

        do_tuong_dong = round(
            diem_de_tai * 0.20
            + diem_huong_nghien_cuu * 0.25
            + diem_muc_tieu * 0.20
            + diem_tu_khoa * 0.15
            + diem_mo_ta * 0.20,
            2
        )

        # Chỉ lấy những đề tài có tương đồng
        if do_tuong_dong > 0:

            ket_qua.append({

                "deTai": de_tai,

                "trungLapDeTai":
                    diem_de_tai,

                "trungLapHuongNghienCuu":
                    diem_huong_nghien_cuu,

                "trungLapMucTieu":
                    diem_muc_tieu,

                "trungLapTuKhoa":
                    diem_tu_khoa,

                "trungLapMoTa":
                    diem_mo_ta,

                "doTuongDong":
                    do_tuong_dong
            })

    # Sắp xếp từ cao xuống thấp
    ket_qua.sort(
        key=lambda x: x["doTuongDong"],
        reverse=True
    )

    return ket_qua

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

def them_ket_qua_nghiem_thu(
    de_tai_id,
    nguoi_nghiem_thu_id,
    diem,
    nhan_xet,
    ket_luan,
    trang_thai
):
    try:
        ket_qua = KetQuaNghiemThu(
            deTaiId=de_tai_id,
            nguoiNghiemThuId=nguoi_nghiem_thu_id,
            diem=diem,
            nhanXet=nhan_xet,
            ketLuan=ket_luan,
            trangThai=trang_thai
        )

        db.session.add(ket_qua)
        db.session.commit()

        return True, "Lưu kết quả nghiệm thu thành công.", ket_qua

    except Exception as e:
        db.session.rollback()
        return False, f"Lỗi khi lưu kết quả nghiệm thu: {str(e)}", None

# ==================================================
# YÊU CẦU NGHIỆM THU
# ==================================================

def get_yeu_cau_nghiem_thu(de_tai_id):

    return YeuCauNghiemThu.query.filter_by(
        deTaiId=de_tai_id
    ).first()


def tao_yeu_cau_nghiem_thu(
    de_tai_id,
    nguoi_yeu_cau_id,
    noi_dung=None
):

    try:

        yeu_cau = get_yeu_cau_nghiem_thu(
            de_tai_id
        )

        if yeu_cau:

            return (
                False,
                "Đề tài này đã gửi yêu cầu nghiệm thu!",
                yeu_cau
            )

        yeu_cau = YeuCauNghiemThu(

            deTaiId=de_tai_id,

            nguoiYeuCauId=nguoi_yeu_cau_id,

            noiDung=noi_dung,

            trangThai=(
                TrangThaiYeuCauNghiemThu
                .CHO_NGHIEM_THU
            )
        )

        db.session.add(yeu_cau)

        db.session.commit()

        return (
            True,
            "Gửi yêu cầu nghiệm thu thành công!",
            yeu_cau
        )

    except Exception as e:

        db.session.rollback()

        return (
            False,
            str(e),
            None
        )


def get_danh_sach_yeu_cau_nghiem_thu():

    return (
        YeuCauNghiemThu.query
        .order_by(
            YeuCauNghiemThu.ngayTao.desc()
        )
        .all()
    )

def get_danh_sach_yeu_cau_nghiem_thu_cua_giang_vien(giang_vien_id):
    return (
        YeuCauNghiemThu.query
        .join(
            DeTai,
            YeuCauNghiemThu.deTaiId == DeTai.id
        )
        .filter(
            DeTai.giangVienId == giang_vien_id,
            YeuCauNghiemThu.trangThai ==
            TrangThaiYeuCauNghiemThu.CHO_NGHIEM_THU
        )
        .order_by(
            YeuCauNghiemThu.ngayTao.desc()
        )
        .all()
    )

def cap_nhat_yeu_cau_nghiem_thu(
    yeu_cau_id,
    trang_thai
):

    try:

        yeu_cau = YeuCauNghiemThu.query.get(
            yeu_cau_id
        )

        if not yeu_cau:

            return (
                False,
                "Không tìm thấy yêu cầu nghiệm thu!"
            )

        yeu_cau.trangThai = trang_thai

        yeu_cau.ngayXuLy = datetime.now()

        db.session.commit()

        return (
            True,
            "Cập nhật yêu cầu nghiệm thu thành công!"
        )

    except Exception as e:

        db.session.rollback()

        return (
            False,
            str(e)
        )

def get_ket_qua_nghiem_thu(de_tai_id):

    return KetQuaNghiemThu.query.filter_by(
        deTaiId=de_tai_id
    ).first()


def tao_ket_qua_nghiem_thu(
    de_tai_id,
    nguoi_nghiem_thu_id,
    diem,
    nhan_xet=None,
    ket_luan=None
):

    try:

        ket_qua = get_ket_qua_nghiem_thu(
            de_tai_id
        )

        if ket_qua:

            ket_qua.nguoiNghiemThuId = (
                nguoi_nghiem_thu_id
            )

            ket_qua.diem = diem

            ket_qua.nhanXet = nhan_xet

            ket_qua.ketLuan = ket_luan

            ket_qua.ngayNghiemThu = datetime.now()

        else:

            if diem >= 5:

                trang_thai = (
                    TrangThaiNghiemThu.DAT
                )

            else:

                trang_thai = (
                    TrangThaiNghiemThu.KHONG_DAT
                )

            ket_qua = KetQuaNghiemThu(

                deTaiId=de_tai_id,

                nguoiNghiemThuId=(
                    nguoi_nghiem_thu_id
                ),

                diem=diem,

                nhanXet=nhan_xet,

                ketLuan=ket_luan,

                trangThai=trang_thai,

                ngayNghiemThu=datetime.now()
            )

            db.session.add(ket_qua)

        # Đảm bảo trạng thái luôn được cập nhật
        if diem >= 5:

            ket_qua.trangThai = (
                TrangThaiNghiemThu.DAT
            )

        else:

            ket_qua.trangThai = (
                TrangThaiNghiemThu.KHONG_DAT
            )

        db.session.commit()

        return (
            True,
            "Lưu kết quả nghiệm thu thành công!",
            ket_qua
        )

    except Exception as e:

        db.session.rollback()

        return (
            False,
            str(e),
            None
        )

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

def get_yeu_cau_chinh_sua_moi_nhat(de_tai_id):
    return (
        YeuCauChinhSua.query
        .filter_by(deTaiId=de_tai_id)
        .order_by(YeuCauChinhSua.ngayTao.desc())
        .first()
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

        if phan_tram < 0 or phan_tram > 100:
            return (
                False,
                "Phần trăm tiến độ phải từ 0 đến 100%!"
            )

        # ==============================
        # CẬP NHẬT TIẾN ĐỘ
        # ==============================

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
    diem,
    nhan_xet=None,
    ket_luan=None,
    trang_thai=TrangThaiNghiemThu.CHUA_NGHIEM_THU
):
    try:
        # ==========================================
        # 1. LẤY ĐỀ TÀI
        # ==========================================

        de_tai = DeTai.query.get(de_tai_id)

        if not de_tai:
            return False, "Không tìm thấy đề tài!", None


        # ==========================================
        # 2. KIỂM TRA ĐIỂM
        # ==========================================

        if diem is None:
            return False, "Vui lòng nhập điểm nghiệm thu!", None

        try:
            diem = float(diem)
        except (ValueError, TypeError):
            return False, "Điểm nghiệm thu không hợp lệ!", None

        if diem < 0 or diem > 10:
            return False, "Điểm nghiệm thu phải từ 0 đến 10!", None


        # ==========================================
        # 3. KIỂM TRA TIẾN ĐỘ
        # ==========================================

        danh_sach_tien_do = (
            TienDo.query
            .filter_by(deTaiId=de_tai_id)
            .order_by(TienDo.ngayCapNhat.desc())
            .all()
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
            return (
                False,
                "Đề tài chưa hoàn thành 100% nên chưa thể nghiệm thu!",
                None
            )


        # ==========================================
        # 4. KIỂM TRA TRẠNG THÁI NGHIỆM THU
        # ==========================================

        if trang_thai not in (
            TrangThaiNghiemThu.DAT,
            TrangThaiNghiemThu.KHONG_DAT
        ):
            return (
                False,
                "Trạng thái nghiệm thu không hợp lệ!",
                None
            )


        # ==========================================
        # 5. TÌM KẾT QUẢ NGHIỆM THU CŨ
        # ==========================================

        ket_qua = KetQuaNghiemThu.query.filter_by(
            deTaiId=de_tai_id
        ).first()


        # ==========================================
        # 6. CẬP NHẬT KẾT QUẢ CŨ
        # ==========================================

        if ket_qua:

            ket_qua.nguoiNghiemThuId = (
                nguoi_nghiem_thu_id
            )

            ket_qua.diem = diem

            ket_qua.nhanXet = nhan_xet

            ket_qua.ketLuan = ket_luan

            ket_qua.trangThai = trang_thai

            ket_qua.ngayNghiemThu = datetime.now()


        # ==========================================
        # 7. TẠO KẾT QUẢ MỚI
        # ==========================================

        else:

            ket_qua = KetQuaNghiemThu(
                deTaiId=de_tai_id,
                nguoiNghiemThuId=nguoi_nghiem_thu_id,
                diem=diem,
                nhanXet=nhan_xet,
                ketLuan=ket_luan,
                trangThai=trang_thai,
                ngayNghiemThu=datetime.now()
            )

            db.session.add(ket_qua)


        # ==========================================
        # 8. XỬ LÝ TRẠNG THÁI ĐỀ TÀI
        # ==========================================

        if trang_thai == TrangThaiNghiemThu.DAT:

            de_tai.trangThai = (
                TrangThaiDeTai.HOAN_THANH
            )

        elif trang_thai == TrangThaiNghiemThu.KHONG_DAT:

            # Không được chuyển sang hoàn thành
            # Giữ nguyên trạng thái hiện tại


            de_tai.trangThai = TrangThaiDeTai.DA_DUYET


        # ==========================================
        # 9. LƯU DATABASE
        # ==========================================

        db.session.commit()


        # ==========================================
        # 10. TRẢ KẾT QUẢ
        # ==========================================

        return (
            True,
            "Lưu kết quả nghiệm thu thành công!",
            ket_qua
        )


    except Exception as e:

        db.session.rollback()

        print(
            "Lỗi thêm kết quả nghiệm thu:",
            e
        )

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

        ket_qua = get_ket_qua_nghiem_thu(
            de_tai_id
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

        print(
            "Lỗi cập nhật kết quả nghiệm thu:",
            e
        )

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

def them_khieu_nai_nghiem_thu(
    de_tai_id,
    ket_qua_id,
    nguoi_khieu_nai_id,
    ly_do,
    minh_chung=None
):
    try:
        khieu_nai = KhieuNaiNghiemThu(
            deTaiId=de_tai_id,
            ketQuaId=ket_qua_id,
            nguoiKhieuNaiId=nguoi_khieu_nai_id,
            lyDo=ly_do,
            minhChung=minh_chung,
            trangThai=TrangThaiKhieuNai.CHO_XU_LY
        )

        db.session.add(khieu_nai)
        db.session.commit()

        return True, "Gửi khiếu nại thành công.", khieu_nai

    except Exception as e:
        db.session.rollback()

        return (
            False,
            f"Lỗi khi gửi khiếu nại: {str(e)}",
            None
        )

def get_khieu_nai_by_sinh_vien(
    nguoi_khieu_nai_id
):
    return (
        KhieuNaiNghiemThu.query
        .filter_by(
            nguoiKhieuNaiId=nguoi_khieu_nai_id
        )
        .order_by(
            KhieuNaiNghiemThu.ngayTao.desc()
        )
        .all()
    )

def get_khieu_nai_by_de_tai(
    de_tai_id
):
    return (
        KhieuNaiNghiemThu.query
        .filter_by(
            deTaiId=de_tai_id
        )
        .order_by(
            KhieuNaiNghiemThu.ngayTao.desc()
        )
        .all()
    )

def get_khieu_nai_by_id(
    khieu_nai_id
):
    return (
        KhieuNaiNghiemThu.query
        .filter_by(
            id=khieu_nai_id
        )
        .first()
    )

def get_khieu_nai_cho_xu_ly():
    return (
        KhieuNaiNghiemThu.query
        .filter_by(
            trangThai=TrangThaiKhieuNai.CHO_XU_LY
        )
        .order_by(
            KhieuNaiNghiemThu.ngayTao.asc()
        )
        .all()
    )