from marshmallow import Schema, fields, validate


# ==============================
# USER / ĐĂNG KÝ
# ==============================

class RegisterSchema(Schema):
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50),
        error_messages={
            "required": "Vui lòng nhập tên đăng nhập!"
        }
    )

    password = fields.Str(
        required=True,
        validate=validate.Length(min=6),
        error_messages={
            "required": "Vui lòng nhập mật khẩu!"
        }
    )

    ho_ten = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100),
        error_messages={
            "required": "Vui lòng nhập họ tên!"
        }
    )

    email = fields.Email(
        required=True,
        error_messages={
            "required": "Vui lòng nhập email!",
            "invalid": "Email không hợp lệ!"
        }
    )


# ==============================
# ĐĂNG NHẬP
# ==============================

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)


# ==============================
# TÌM KIẾM ĐỀ TÀI
# ==============================

class TimKiemDeTaiSchema(Schema):

    q = fields.Str(
        load_default=""
    )

    linh_vuc_id = fields.Int(
        allow_none=True
    )

    trang_thai = fields.Str(
        allow_none=True
    )

    page = fields.Int(
        load_default=1,
        validate=validate.Range(min=1)
    )

    page_size = fields.Int(
        load_default=10,
        validate=validate.Range(min=1, max=100)
    )


# ==============================
# THÊM ĐỀ TÀI NGHIÊN CỨU
# ==============================

class DeTaiSchema(Schema):

    ten_de_tai = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=255),
        error_messages={
            "required": "Vui lòng nhập tên đề tài!"
        }
    )

    mo_ta = fields.Str(
        required=True,
        validate=validate.Length(min=20),
        error_messages={
            "required": "Vui lòng nhập mô tả đề tài!"
        }
    )

    muc_tieu = fields.Str(
        allow_none=True
    )

    linh_vuc_id = fields.Int(
        required=True,
        error_messages={
            "required": "Vui lòng chọn lĩnh vực!"
        }
    )

    giang_vien_id = fields.Int(
        allow_none=True
    )


# ==============================
# THÊM GIẢNG VIÊN
# ==============================

class GiangVienSchema(Schema):

    ho_ten = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

    email = fields.Email(
        required=True
    )

    chuyen_mon = fields.Str(
        required=True,
        validate=validate.Length(min=2)
    )

    hoc_vi = fields.Str(
        allow_none=True
    )


# ==============================
# THÊM LĨNH VỰC NGHIÊN CỨU
# ==============================

class LinhVucSchema(Schema):

    ten_linh_vuc = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=100)
    )

    mo_ta = fields.Str(
        allow_none=True
    )


# ==============================
# AI PHÁT HIỆN TRÙNG LẶP
# ==============================

class KiemTraTrungLapSchema(Schema):

    ten_de_tai = fields.Str(
        required=True,
        validate=validate.Length(min=5),
        error_messages={
            "required": "Vui lòng nhập tên đề tài!"
        }
    )

    mo_ta = fields.Str(
        required=True,
        validate=validate.Length(min=20),
        error_messages={
            "required": "Vui lòng nhập mô tả đề tài!"
        }
    )


# ==============================
# AI GỢI Ý GIẢNG VIÊN
# ==============================

class GoiYGiangVienSchema(Schema):

    de_tai_id = fields.Int(
        required=True
    )