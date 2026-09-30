from datetime import datetime
from enum import Enum as RoleEnum

from flask_login import UserMixin

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    Enum,
    ForeignKey,
    Float
)

from sqlalchemy.orm import relationship

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app import db


# ==================================================
# BASE MODEL
# ==================================================

class BaseModel(db.Model):
    __abstract__ = True

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )


# ==================================================
# ENUM VAI TRÒ
# ==================================================

class UserRole(RoleEnum):

    ADMIN = 1

    GIANGVIEN = 2

    SINHVIEN = 3


# ==================================================
# TRẠNG THÁI ĐỀ TÀI
# ==================================================

class TrangThaiDeTai(str, RoleEnum):

    NHAP = "NHAP"

    CHO_DUYET = "CHO_DUYET"

    DA_DUYET = "DA_DUYET"

    TU_CHOI = "TU_CHOI"

    HOAN_THANH = "HOAN_THANH"


# ==================================================
# TRẠNG THÁI TIẾN ĐỘ
# ==================================================

class TrangThaiTienDo(str, RoleEnum):

    CHUA_BAT_DAU = "CHUA_BAT_DAU"

    DANG_THUC_HIEN = "DANG_THUC_HIEN"

    HOAN_THANH_MOT_PHAN = "HOAN_THANH_MOT_PHAN"

    HOAN_THANH = "HOAN_THANH"

    DA_NGHIEM_THU = "DA_NGHIEM_THU"


# ==================================================
# TRẠNG THÁI NGHIỆM THU
# ==================================================

class TrangThaiNghiemThu(str, RoleEnum):

    CHUA_NGHIEM_THU = "CHUA_NGHIEM_THU"

    DAT = "DAT"

    KHONG_DAT = "KHONG_DAT"


# ==================================================
# LOẠI THÔNG BÁO
# ==================================================

class LoaiThongBao(str, RoleEnum):

    HE_THONG = "HE_THONG"

    DUYET_DE_TAI = "DUYET_DE_TAI"

    TU_CHOI_DE_TAI = "TU_CHOI_DE_TAI"

    YEU_CAU_CHINH_SUA = "YEU_CAU_CHINH_SUA"

    PHAN_CONG = "PHAN_CONG"

    TIEN_DO = "TIEN_DO"

    NGHIEM_THU = "NGHIEM_THU"


# ==================================================
# USER
# ==================================================

class User(UserMixin, BaseModel):

    __tablename__ = "user"

    username = Column(
        String(50),
        unique=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    hoTen = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(100),
        unique=True,
        nullable=True
    )

    soDienThoai = Column(
        String(20),
        nullable=True
    )

    role = Column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.SINHVIEN
    )

    avatar = Column(
        String(255),
        nullable=True
    )

    active = Column(
        Boolean,
        default=True
    )

    ngayTao = Column(
        DateTime,
        default=datetime.now
    )

    def get_id(self):

        return str(
            self.id
        )

    def set_password(
        self,
        password
    ):

        self.password = (
            generate_password_hash(
                password
            )
        )

    def check_password(
        self,
        password
    ):

        return check_password_hash(
            self.password,
            password
        )

    def __str__(self):

        return self.hoTen


# ==================================================
# LĨNH VỰC NGHIÊN CỨU
# ==================================================

class LinhVuc(BaseModel):

    __tablename__ = "linhvuc"

    tenLinhVuc = Column(
        String(150),
        unique=True,
        nullable=False
    )

    moTa = Column(
        Text,
        nullable=True
    )

    danhSachDeTai = relationship(
        "DeTai",
        back_populates="linh_vuc",
        lazy=True
    )

    def to_dict(self):

        return {

            "id": self.id,

            "tenLinhVuc": self.tenLinhVuc,

            "moTa": self.moTa
        }

# ==================================================
# THÔNG TIN GIẢNG VIÊN
# ==================================================

class GiangVien(BaseModel):

    __tablename__ = "giangvien"

    userId = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False,
        unique=True
    )

    hocVi = Column(
        String(100),
        nullable=True
    )

    chuyenMon = Column(
        String(255),
        nullable=True
    )

    linhVucNghienCuu = Column(
        Text,
        nullable=True
    )

    soLuongHuongDanToiDa = Column(
        Integer,
        default=10
    )

    gioiThieu = Column(
        Text,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="thongTinGiangVien"
    )

# ==================================================
# TRẠNG THÁI YÊU CẦU NGHIỆM THU
# ==================================================

class TrangThaiYeuCauNghiemThu(str, RoleEnum):

    CHO_NGHIEM_THU = "CHO_NGHIEM_THU"

    DA_XU_LY = "DA_XU_LY"


# ==================================================
# YÊU CẦU NGHIỆM THU
# ==================================================

class YeuCauNghiemThu(BaseModel):

    __tablename__ = "yeucaunghiemthu"

    deTaiId = Column(
        Integer,
        ForeignKey("detai.id"),
        nullable=False,
        unique=True
    )

    nguoiYeuCauId = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    noiDung = Column(
        Text,
        nullable=True
    )

    trangThai = Column(
        Enum(TrangThaiYeuCauNghiemThu),
        nullable=False,
        default=TrangThaiYeuCauNghiemThu.CHO_NGHIEM_THU
    )

    ngayTao = Column(
        DateTime,
        default=datetime.now
    )

    ngayXuLy = Column(
        DateTime,
        nullable=True
    )

    de_tai = relationship(
        "DeTai",
        back_populates="yeuCauNghiemThu"
    )

    nguoiYeuCau = relationship(
        "User",
        back_populates="danhSachYeuCauNghiemThu"
    )

# ==================================================
# LĨNH VỰC CHUYÊN MÔN GIẢNG VIÊN
# ==================================================

class GiangVienLinhVuc(BaseModel):

    __tablename__ = "giangvien_linhvuc"

    giangVienId = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    linhVucId = Column(
        Integer,
        ForeignKey("linhvuc.id"),
        nullable=False
    )

    giang_vien = relationship(
        "User",
        back_populates="danhSachChuyenMon"
    )

    linh_vuc = relationship(
        "LinhVuc",
        back_populates="danhSachGiangVien"
    )


# ==================================================
# ĐỀ TÀI NGHIÊN CỨU
# ==================================================

class DeTai(BaseModel):

    __tablename__ = "detai"

    tenDeTai = Column(
        String(500),
        nullable=False
    )

    moTa = Column(
        Text,
        nullable=True
    )

    mucTieu = Column(
        Text,
        nullable=True
    )

    tuKhoa = Column(
        String(500),
        nullable=True
    )

    linhVucId = Column(
        Integer,
        ForeignKey("linhvuc.id"),
        nullable=True
    )

    sinhVienId = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    giangVienId = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=True
    )

    trangThai = Column(
        Enum(TrangThaiDeTai),
        nullable=False,
        default=TrangThaiDeTai.NHAP
    )

    ngayTao = Column(
        DateTime,
        default=datetime.now
    )

    ngayCapNhat = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    linh_vuc = relationship(
        "LinhVuc",
        back_populates="danhSachDeTai"
    )

    sinh_vien = relationship(
        "User",
        foreign_keys=[sinhVienId],
        back_populates="danhSachDeTai"
    )

    giang_vien = relationship(
        "User",
        foreign_keys=[giangVienId],
        back_populates="danhSachHuongDan"
    )

    danhSachGoiYGiangVien = relationship(
        "GoiYGiangVien",
        back_populates="de_tai",
        cascade="all, delete-orphan"
    )

    danhSachTienDo = relationship(
        "TienDo",
        back_populates="de_tai",
        cascade="all, delete-orphan"
    )

    danhSachYeuCauChinhSua = relationship(
        "YeuCauChinhSua",
        back_populates="de_tai",
        cascade="all, delete-orphan"
    )

    ketQuaNghiemThu = relationship(
        "KetQuaNghiemThu",
        back_populates="de_tai",
        uselist=False,
        cascade="all, delete-orphan"
    )

    yeuCauNghiemThu = relationship(
        "YeuCauNghiemThu",
        back_populates="de_tai",
        uselist=False,
        cascade="all, delete-orphan"
    )


    danhSachThongBao = relationship(
        "ThongBao",
        back_populates="de_tai",
        cascade="all, delete-orphan"
    )

    danhSachTaiLieu = relationship(
        "TaiLieu",
        back_populates="de_tai",
        cascade="all, delete-orphan"
    )

    def to_dict(self):

        return {

            "id": self.id,

            "tenDeTai": self.tenDeTai,

            "moTa": self.moTa,

            "mucTieu": self.mucTieu,

            "tuKhoa": self.tuKhoa,

            "linhVucId": self.linhVucId,

            "linhVuc": (
                self.linh_vuc.tenLinhVuc
                if self.linh_vuc
                else None
            ),

            "sinhVienId": self.sinhVienId,

            "sinhVien": (
                self.sinh_vien.hoTen
                if self.sinh_vien
                else None
            ),

            "giangVienId": self.giangVienId,

            "giangVien": (
                self.giang_vien.hoTen
                if self.giang_vien
                else None
            ),

            "trangThai": (
                self.trangThai.value
                if self.trangThai
                else None
            ),

            "ngayTao": (
                self.ngayTao.strftime("%d/%m/%Y")
                if self.ngayTao
                else None
            )
        }


# ==================================================
# KIỂM TRA TRÙNG LẶP ĐỀ TÀI
# ==================================================

class KiemTraTrungLap(BaseModel):

    __tablename__ = "kiemtratrunglap"

    # Hai đề tài được đem ra so sánh
    deTai1Id = Column(
        Integer,
        ForeignKey("detai.id"),
        nullable=False
    )

    deTai2Id = Column(
        Integer,
        ForeignKey("detai.id"),
        nullable=False
    )

    # 1. Mức độ trùng lặp tổng thể
    doTuongDong = Column(
        Float,
        nullable=False
    )

    # 2. Trùng lặp đề tài
    trungLapDeTai = Column(
        Float,
        nullable=False,
        default=0
    )

    # 3. Trùng lặp hướng nghiên cứu
    trungLapHuongNghienCuu = Column(
        Float,
        nullable=False,
        default=0
    )

    # 4. Trùng lặp mục tiêu nghiên cứu
    trungLapMucTieu = Column(
        Float,
        nullable=False,
        default=0
    )

    # 5. Trùng lặp từ khóa / chủ đề
    trungLapTuKhoa = Column(
        Float,
        nullable=False,
        default=0
    )

    # 6. Trùng lặp nội dung mô tả
    trungLapMoTa = Column(
        Float,
        nullable=False,
        default=0
    )

    ngayKiemTra = Column(
        DateTime,
        default=datetime.now
    )

    # Quan hệ với đề tài 1
    de_tai_1 = relationship(
        "DeTai",
        foreign_keys=[deTai1Id]
    )

    # Quan hệ với đề tài 2
    de_tai_2 = relationship(
        "DeTai",
        foreign_keys=[deTai2Id]
    )


# ==================================================
# GỢI Ý GIẢNG VIÊN
# ==================================================

class GoiYGiangVien(BaseModel):

    __tablename__ = "goiygiangvien"

    deTaiId = Column(
        Integer,
        ForeignKey("detai.id"),
        nullable=False
    )

    giangVienId = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    diemPhuHop = Column(
        Float,
        nullable=False
    )

    lyDo = Column(
        Text,
        nullable=True
    )

    ngayTao = Column(
        DateTime,
        default=datetime.now
    )

    de_tai = relationship(
        "DeTai",
        back_populates="danhSachGoiYGiangVien"
    )

    giang_vien = relationship(
        "User",
        back_populates="danhSachGoiY"
    )


# ==================================================
# LỊCH SỬ TÌM KIẾM
# ==================================================

class LichSuTimKiem(BaseModel):

    __tablename__ = "lichsutimkiem"

    userId = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    tuKhoa = Column(
        String(500),
        nullable=False
    )

    ngayTao = Column(
        DateTime,
        default=datetime.now
    )

    user = relationship(
        "User",
        back_populates="danhSachTimKiem"
    )


# ==================================================
# TIẾN ĐỘ ĐỀ TÀI
# ==================================================

class TienDo(BaseModel):

    __tablename__ = "tiendo"

    deTaiId = Column(
        Integer,
        ForeignKey("detai.id"),
        nullable=False
    )

    tieuDe = Column(
        String(255),
        nullable=False
    )

    noiDung = Column(
        Text,
        nullable=True
    )

    phanTram = Column(
        Integer,
        default=0
    )

    trangThai = Column(
        Enum(TrangThaiTienDo),
        nullable=False,
        default=TrangThaiTienDo.CHUA_BAT_DAU
    )

    nhanXetGiangVien = Column(
        Text,
        nullable=True
    )

    ngayCapNhat = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

    de_tai = relationship(
        "DeTai",
        back_populates="danhSachTienDo"
    )


# ==================================================
# YÊU CẦU CHỈNH SỬA ĐỀ TÀI
# ==================================================

class YeuCauChinhSua(BaseModel):

    __tablename__ = "yeucauchinhsua"

    deTaiId = Column(
        Integer,
        ForeignKey("detai.id"),
        nullable=False
    )

    nguoiYeuCauId = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    noiDung = Column(
        Text,
        nullable=False
    )

    # Giảng viên phản hồi
    phanHoiGiangVien = Column(
        Text,
        nullable=True
    )

    # Đã được giảng viên xử lý hay chưa
    daXuLy = Column(
        Boolean,
        default=False
    )

    # Thời gian giảng viên xử lý
    ngayXuLy = Column(
        DateTime,
        nullable=True
    )

    ngayTao = Column(
        DateTime,
        default=datetime.now
    )

    de_tai = relationship(
        "DeTai",
        back_populates="danhSachYeuCauChinhSua"
    )

    nguoiYeuCau = relationship(
        "User",
        back_populates="danhSachYeuCauChinhSua"
    )
    duocPhepChinhSua = Column(
        Boolean,
        default=False
    )


# ==================================================
# KẾT QUẢ NGHIỆM THU
# ==================================================

class KetQuaNghiemThu(BaseModel):

    __tablename__ = "ketquanghiemthu"

    deTaiId = Column(
        Integer,
        ForeignKey("detai.id"),
        nullable=False,
        unique=True
    )

    nguoiNghiemThuId = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    diem = Column(
        Float,
        nullable=True
    )

    nhanXet = Column(
        Text,
        nullable=True
    )

    ketLuan = Column(
        Text,
        nullable=True
    )

    trangThai = Column(
        Enum(TrangThaiNghiemThu),
        nullable=False,
        default=TrangThaiNghiemThu.CHUA_NGHIEM_THU
    )

    ngayNghiemThu = Column(
        DateTime,
        nullable=True
    )

    # ==========================================
    # SINH VIÊN XÁC NHẬN KẾT QUẢ
    # ==========================================

    sinhVienDongY = Column(
        Boolean,
        nullable=False,
        default=False
    )

    ngaySinhVienDongY = Column(
        DateTime,
        nullable=True
    )

    de_tai = relationship(
        "DeTai",
        back_populates="ketQuaNghiemThu"
    )

    nguoiNghiemThu = relationship(
        "User",
        back_populates="danhSachNghiemThu"
    )


# ==================================================
# THÔNG BÁO
# ==================================================

class ThongBao(BaseModel):

    __tablename__ = "thongbao"

    userId = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    tieuDe = Column(
        String(255),
        nullable=False
    )

    noiDung = Column(
        Text,
        nullable=False
    )

    loai = Column(
        Enum(LoaiThongBao),
        nullable=False,
        default=LoaiThongBao.HE_THONG
    )

    deTaiId = Column(
        Integer,
        ForeignKey("detai.id"),
        nullable=True
    )

    daDoc = Column(
        Boolean,
        default=False
    )

    ngayTao = Column(
        DateTime,
        default=datetime.now
    )

    user = relationship(
        "User",
        back_populates="danhSachThongBao"
    )

    de_tai = relationship(
        "DeTai",
        back_populates="danhSachThongBao"
    )


# ==================================================
# TÀI LIỆU ĐỀ TÀI
# ==================================================

class TaiLieu(BaseModel):

    __tablename__ = "tailieu"

    deTaiId = Column(
        Integer,
        ForeignKey("detai.id"),
        nullable=False
    )

    nguoiTaiId = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    tenTaiLieu = Column(
        String(255),
        nullable=False
    )

    duongDan = Column(
        String(500),
        nullable=False
    )

    loaiFile = Column(
        String(100),
        nullable=True
    )

    ngayTai = Column(
        DateTime,
        default=datetime.now
    )

    de_tai = relationship(
        "DeTai",
        back_populates="danhSachTaiLieu"
    )

    nguoiTai = relationship(
        "User",
        back_populates="danhSachTaiLieu"
    )


# ==================================================
# QUAN HỆ USER
# ==================================================

User.thongTinGiangVien = relationship(
    "GiangVien",
    back_populates="user",
    uselist=False
)

User.danhSachDeTai = relationship(
    "DeTai",
    foreign_keys="DeTai.sinhVienId",
    back_populates="sinh_vien"
)

User.danhSachHuongDan = relationship(
    "DeTai",
    foreign_keys="DeTai.giangVienId",
    back_populates="giang_vien"
)

User.danhSachChuyenMon = relationship(
    "GiangVienLinhVuc",
    back_populates="giang_vien"
)

User.danhSachGoiY = relationship(
    "GoiYGiangVien",
    back_populates="giang_vien"
)

User.danhSachTimKiem = relationship(
    "LichSuTimKiem",
    back_populates="user"
)

User.danhSachYeuCauChinhSua = relationship(
    "YeuCauChinhSua",
    back_populates="nguoiYeuCau"
)

User.danhSachNghiemThu = relationship(
    "KetQuaNghiemThu",
    back_populates="nguoiNghiemThu"
)

User.danhSachYeuCauNghiemThu = relationship(
    "YeuCauNghiemThu",
    back_populates="nguoiYeuCau"
)

User.danhSachThongBao = relationship(
    "ThongBao",
    back_populates="user"
)

User.danhSachTaiLieu = relationship(
    "TaiLieu",
    back_populates="nguoiTai"
)


# ==================================================
# QUAN HỆ LĨNH VỰC
# ==================================================

LinhVuc.danhSachGiangVien = relationship(
    "GiangVienLinhVuc",
    back_populates="linh_vuc"
)

class TrangThaiKhieuNai(RoleEnum):
    CHO_XU_LY = "CHO_XU_LY"
    DANG_XU_LY = "DANG_XU_LY"
    CHAP_NHAN = "CHAP_NHAN"
    TU_CHOI = "TU_CHOI"

# ==================================================
# KHIẾU NẠI KẾT QUẢ NGHIỆM THU
# ==================================================

class KhieuNaiNghiemThu(BaseModel):

    __tablename__ = "khieunai_nghiemthu"

    # ----------------------------------------------
    # ĐỀ TÀI BỊ KHIẾU NẠI
    # ----------------------------------------------
    deTaiId = Column(
        Integer,
        ForeignKey("detai.id"),
        nullable=False
    )

    # ----------------------------------------------
    # KẾT QUẢ NGHIỆM THU BỊ KHIẾU NẠI
    # ----------------------------------------------
    ketQuaId = Column(
        Integer,
        ForeignKey("ketquanghiemthu.id"),
        nullable=False
    )

    # ----------------------------------------------
    # SINH VIÊN GỬI KHIẾU NẠI
    # ----------------------------------------------
    nguoiKhieuNaiId = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False
    )

    # ----------------------------------------------
    # LÝ DO KHIẾU NẠI
    # ----------------------------------------------
    lyDo = Column(
        Text,
        nullable=False
    )

    # ----------------------------------------------
    # MINH CHỨNG
    # Có thể để trống nếu sinh viên không upload
    # ----------------------------------------------
    minhChung = Column(
        String(500),
        nullable=True
    )

    # ----------------------------------------------
    # TRẠNG THÁI XỬ LÝ
    # ----------------------------------------------
    trangThai = Column(
        Enum(TrangThaiKhieuNai),
        nullable=False,
        default=TrangThaiKhieuNai.CHO_XU_LY
    )

    # ----------------------------------------------
    # PHẢN HỒI CỦA NGƯỜI XỬ LÝ
    # ----------------------------------------------
    phanHoi = Column(
        Text,
        nullable=True
    )

    # ----------------------------------------------
    # NGƯỜI XỬ LÝ KHIẾU NẠI
    # ----------------------------------------------
    nguoiXuLyId = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=True
    )

    # ----------------------------------------------
    # THỜI GIAN GỬI
    # ----------------------------------------------
    ngayTao = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    # ----------------------------------------------
    # THỜI GIAN XỬ LÝ
    # ----------------------------------------------
    ngayXuLy = Column(
        DateTime,
        nullable=True
    )

    # ----------------------------------------------
    # RELATIONSHIP
    # ----------------------------------------------

    de_tai = relationship(
        "DeTai"
    )

    ket_qua = relationship(
        "KetQuaNghiemThu"
    )

    nguoiKhieuNai = relationship(
        "User",
        foreign_keys=[nguoiKhieuNaiId]
    )

    nguoiXuLy = relationship(
        "User",
        foreign_keys=[nguoiXuLyId]
    )

# ==================================================
# DỮ LIỆU MẪU
# ==================================================

if __name__ == "__main__":

    from app import app

    with app.app_context():

        try:

            print("=" * 70)
            print("BẮT ĐẦU KHỞI TẠO DATABASE + DỮ LIỆU TEST")
            print("=" * 70)

            # ==================================================
            # 1. XÓA DATABASE CŨ
            # ==================================================

            print("\n[1] Xóa database cũ...")

            db.drop_all()

            # ==================================================
            # 2. TẠO DATABASE MỚI
            # ==================================================

            print("[2] Tạo các bảng mới...")

            db.create_all()

            # ==================================================
            # 3. TẠO ADMIN
            # ==================================================

            print("[3] Tạo tài khoản Admin...")

            admin = User(
                username="admin",
                hoTen="Quản trị viên",
                email="admin@nckh.vn",
                soDienThoai="0900000001",
                role=UserRole.ADMIN,
                active=True
            )

            admin.set_password("123456")

            # ==================================================
            # 4. TẠO GIẢNG VIÊN
            # ==================================================

            print("[4] Tạo tài khoản giảng viên...")

            gv1_user = User(
                username="nguyenvana",
                hoTen="TS. Nguyễn Văn A",
                email="nguyenvana@ou.edu.vn",
                soDienThoai="0900000011",
                role=UserRole.GIANGVIEN,
                active=True
            )
            gv1_user.set_password("123456")

            gv2_user = User(
                username="tranthib",
                hoTen="ThS. Trần Thị B",
                email="tranthib@ou.edu.vn",
                soDienThoai="0900000012",
                role=UserRole.GIANGVIEN,
                active=True
            )
            gv2_user.set_password("123456")

            gv3_user = User(
                username="leminhc",
                hoTen="TS. Lê Minh C",
                email="leminhc@ou.edu.vn",
                soDienThoai="0900000013",
                role=UserRole.GIANGVIEN,
                active=True
            )
            gv3_user.set_password("123456")

            gv4_user = User(
                username="phamhoangd",
                hoTen="TS. Phạm Hoàng D",
                email="phamhoangd@ou.edu.vn",
                soDienThoai="0900000014",
                role=UserRole.GIANGVIEN,
                active=True
            )
            gv4_user.set_password("123456")

            # ==================================================
            # 5. TẠO SINH VIÊN
            # ==================================================

            print("[5] Tạo tài khoản sinh viên...")

            sv1 = User(
                username="sinhvien1",
                hoTen="Nguyễn Văn An",
                email="sinhvien1@student.ou.edu.vn",
                soDienThoai="0900000021",
                role=UserRole.SINHVIEN,
                active=True
            )
            sv1.set_password("123456")

            sv2 = User(
                username="sinhvien2",
                hoTen="Trần Thị Bình",
                email="sinhvien2@student.ou.edu.vn",
                soDienThoai="0900000022",
                role=UserRole.SINHVIEN,
                active=True
            )
            sv2.set_password("123456")

            sv3 = User(
                username="sinhvien3",
                hoTen="Lê Văn Cường",
                email="sinhvien3@student.ou.edu.vn",
                soDienThoai="0900000023",
                role=UserRole.SINHVIEN,
                active=True
            )
            sv3.set_password("123456")

            sv4 = User(
                username="sinhvien4",
                hoTen="Phạm Thị Dung",
                email="sinhvien4@student.ou.edu.vn",
                soDienThoai="0900000024",
                role=UserRole.SINHVIEN,
                active=True
            )
            sv4.set_password("123456")

            sv5 = User(
                username="sinhvien5",
                hoTen="Hoàng Văn Em",
                email="sinhvien5@student.ou.edu.vn",
                soDienThoai="0900000025",
                role=UserRole.SINHVIEN,
                active=True
            )
            sv5.set_password("123456")

            sv6 = User(
                username="sinhvien6",
                hoTen="Đỗ Minh Phúc",
                email="sinhvien6@student.ou.edu.vn",
                soDienThoai="0900000026",
                role=UserRole.SINHVIEN,
                active=True
            )
            sv6.set_password("123456")

            sv7 = User(
                username="sinhvien7",
                hoTen="Võ Ngọc Anh",
                email="sinhvien7@student.ou.edu.vn",
                soDienThoai="0900000027",
                role=UserRole.SINHVIEN,
                active=True
            )
            sv7.set_password("123456")

            # ==================================================
            # 6. LƯU USER
            # ==================================================

            db.session.add_all([
                admin,

                gv1_user,
                gv2_user,
                gv3_user,
                gv4_user,

                sv1,
                sv2,
                sv3,
                sv4,
                sv5,
                sv6,
                sv7
            ])

            db.session.flush()

            print("    ✓ 1 Admin")
            print("    ✓ 4 Giảng viên")
            print("    ✓ 7 Sinh viên")

            # ==================================================
            # 7. THÔNG TIN GIẢNG VIÊN
            # ==================================================

            print("[6] Tạo thông tin giảng viên...")

            gv1 = GiangVien(
                userId=gv1_user.id,
                hocVi="Tiến sĩ",
                chuyenMon=(
                    "Trí tuệ nhân tạo, Machine Learning, "
                    "Deep Learning, NLP"
                ),
                linhVucNghienCuu=(
                    "AI, Machine Learning, Deep Learning, NLP"
                ),
                soLuongHuongDanToiDa=10,
                gioiThieu=(
                    "Giảng viên chuyên nghiên cứu về trí tuệ nhân tạo, "
                    "Machine Learning và xử lý ngôn ngữ tự nhiên."
                )
            )

            gv2 = GiangVien(
                userId=gv2_user.id,
                hocVi="Thạc sĩ",
                chuyenMon=(
                    "Công nghệ phần mềm, Web, "
                    "Software Engineering, Cloud"
                ),
                linhVucNghienCuu=(
                    "Web Development, Software Engineering, "
                    "Cloud Computing"
                ),
                soLuongHuongDanToiDa=10,
                gioiThieu=(
                    "Giảng viên chuyên về phát triển phần mềm "
                    "và hệ thống web."
                )
            )

            gv3 = GiangVien(
                userId=gv3_user.id,
                hocVi="Tiến sĩ",
                chuyenMon=(
                    "An toàn thông tin, Mạng máy tính, "
                    "Cyber Security"
                ),
                linhVucNghienCuu=(
                    "Information Security, Network Security, "
                    "Cyber Security"
                ),
                soLuongHuongDanToiDa=10,
                gioiThieu=(
                    "Giảng viên chuyên nghiên cứu về bảo mật "
                    "và an toàn hệ thống."
                )
            )

            gv4 = GiangVien(
                userId=gv4_user.id,
                hocVi="Tiến sĩ",
                chuyenMon=(
                    "Khoa học dữ liệu, Phân tích dữ liệu, "
                    "Big Data, Data Mining"
                ),
                linhVucNghienCuu=(
                    "Data Science, Big Data, Data Mining, Analytics"
                ),
                soLuongHuongDanToiDa=10,
                gioiThieu=(
                    "Giảng viên chuyên về khoa học dữ liệu "
                    "và phân tích dữ liệu."
                )
            )

            db.session.add_all([
                gv1,
                gv2,
                gv3,
                gv4
            ])

            # ==================================================
            # 8. LĨNH VỰC
            # ==================================================

            print("[7] Tạo lĩnh vực nghiên cứu...")

            linh_vuc_ai = LinhVuc(
                tenLinhVuc="Trí tuệ nhân tạo",
                moTa=(
                    "Nghiên cứu AI, Machine Learning, "
                    "Deep Learning và NLP."
                )
            )

            linh_vuc_web = LinhVuc(
                tenLinhVuc="Công nghệ phần mềm",
                moTa=(
                    "Nghiên cứu phát triển phần mềm, "
                    "website và hệ thống thông tin."
                )
            )

            linh_vuc_data = LinhVuc(
                tenLinhVuc="Khoa học dữ liệu",
                moTa=(
                    "Phân tích, xử lý, trực quan hóa "
                    "và khai thác dữ liệu."
                )
            )

            linh_vuc_security = LinhVuc(
                tenLinhVuc="An toàn thông tin",
                moTa=(
                    "Nghiên cứu bảo mật, an toàn mạng "
                    "và bảo vệ hệ thống."
                )
            )

            linh_vuc_mobile = LinhVuc(
                tenLinhVuc="Phát triển ứng dụng di động",
                moTa=(
                    "Nghiên cứu và phát triển ứng dụng "
                    "trên nền tảng di động."
                )
            )

            db.session.add_all([
                linh_vuc_ai,
                linh_vuc_web,
                linh_vuc_data,
                linh_vuc_security,
                linh_vuc_mobile
            ])

            db.session.flush()

            # ==================================================
            # 9. CHUYÊN MÔN GIẢNG VIÊN
            # ==================================================

            print("[8] Gán lĩnh vực chuyên môn cho giảng viên...")

            db.session.add_all([

                # GV1 - AI
                GiangVienLinhVuc(
                    giangVienId=gv1_user.id,
                    linhVucId=linh_vuc_ai.id
                ),

                GiangVienLinhVuc(
                    giangVienId=gv1_user.id,
                    linhVucId=linh_vuc_data.id
                ),

                # GV2 - Web + Mobile
                GiangVienLinhVuc(
                    giangVienId=gv2_user.id,
                    linhVucId=linh_vuc_web.id
                ),

                GiangVienLinhVuc(
                    giangVienId=gv2_user.id,
                    linhVucId=linh_vuc_mobile.id
                ),

                # GV3 - Security
                GiangVienLinhVuc(
                    giangVienId=gv3_user.id,
                    linhVucId=linh_vuc_security.id
                ),

                # GV4 - Data + AI
                GiangVienLinhVuc(
                    giangVienId=gv4_user.id,
                    linhVucId=linh_vuc_data.id
                ),

                GiangVienLinhVuc(
                    giangVienId=gv4_user.id,
                    linhVucId=linh_vuc_ai.id
                )
            ])

            # ==================================================
            # 10. ĐỀ TÀI
            # ==================================================

            print("[9] Tạo đề tài mẫu...")

            danh_sach_de_tai = [

                # --------------------------------------------------
                # 1 - ĐÃ DUYỆT
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Ứng dụng trí tuệ nhân tạo "
                        "trong tìm kiếm ngữ nghĩa"
                    ),
                    moTa=(
                        "Xây dựng hệ thống tìm kiếm thông tin "
                        "bằng trí tuệ nhân tạo và xử lý "
                        "ngôn ngữ tự nhiên."
                    ),
                    mucTieu=(
                        "Hỗ trợ người dùng tìm kiếm thông tin "
                        "chính xác và phù hợp."
                    ),
                    tuKhoa="AI, Semantic Search, NLP",
                    linhVucId=linh_vuc_ai.id,
                    sinhVienId=sv1.id,
                    giangVienId=gv1_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                # --------------------------------------------------
                # 2 - CHỜ DUYỆT
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Hệ thống phát hiện đề tài nghiên cứu "
                        "trùng lặp bằng AI"
                    ),
                    moTa=(
                        "Sử dụng AI để phân tích và so sánh "
                        "mức độ tương đồng giữa các đề tài."
                    ),
                    mucTieu=(
                        "Phát hiện các đề tài có nội dung "
                        "tương tự hoặc trùng lặp."
                    ),
                    tuKhoa="AI, NLP, Similarity Detection",
                    linhVucId=linh_vuc_ai.id,
                    sinhVienId=sv2.id,
                    giangVienId=gv1_user.id,
                    trangThai=TrangThaiDeTai.CHO_DUYET
                ),

                # --------------------------------------------------
                # 3 - ĐÃ DUYỆT
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Xây dựng chatbot hỗ trợ sinh viên "
                        "bằng trí tuệ nhân tạo"
                    ),
                    moTa=(
                        "Phát triển chatbot sử dụng AI "
                        "hỗ trợ giải đáp câu hỏi cho sinh viên."
                    ),
                    mucTieu=(
                        "Tự động hóa việc hỗ trợ và tư vấn "
                        "thông tin cho sinh viên."
                    ),
                    tuKhoa="Chatbot, AI, NLP",
                    linhVucId=linh_vuc_ai.id,
                    sinhVienId=sv3.id,
                    giangVienId=gv1_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                # --------------------------------------------------
                # 4 - ĐANG THỰC HIỆN
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Ứng dụng Machine Learning "
                        "trong dự đoán kết quả học tập"
                    ),
                    moTa=(
                        "Sử dụng Machine Learning để phân tích "
                        "dữ liệu và dự đoán kết quả học tập."
                    ),
                    mucTieu=(
                        "Hỗ trợ dự đoán kết quả học tập "
                        "của sinh viên."
                    ),
                    tuKhoa="Machine Learning, Prediction",
                    linhVucId=linh_vuc_ai.id,
                    sinhVienId=sv4.id,
                    giangVienId=gv1_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                # --------------------------------------------------
                # 5 - CHỜ DUYỆT
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Hệ thống nhận diện khuôn mặt "
                        "bằng Deep Learning"
                    ),
                    moTa=(
                        "Xây dựng hệ thống nhận diện khuôn mặt "
                        "sử dụng Deep Learning."
                    ),
                    mucTieu=(
                        "Tự động nhận diện và xác thực khuôn mặt."
                    ),
                    tuKhoa="Deep Learning, Face Recognition",
                    linhVucId=linh_vuc_ai.id,
                    sinhVienId=sv5.id,
                    giangVienId=gv1_user.id,
                    trangThai=TrangThaiDeTai.CHO_DUYET
                ),

                # --------------------------------------------------
                # 6 - ĐÃ DUYỆT
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Xây dựng hệ thống quản lý "
                        "nghiên cứu khoa học trực tuyến"
                    ),
                    moTa=(
                        "Website hỗ trợ sinh viên quản lý "
                        "và đăng ký đề tài nghiên cứu khoa học."
                    ),
                    mucTieu=(
                        "Số hóa quá trình quản lý đề tài."
                    ),
                    tuKhoa="Web, Flask, MySQL",
                    linhVucId=linh_vuc_web.id,
                    sinhVienId=sv1.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                # --------------------------------------------------
                # 7 - ĐÃ DUYỆT
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Xây dựng hệ thống quản lý thư viện số"
                    ),
                    moTa=(
                        "Phát triển hệ thống thư viện trực tuyến "
                        "hỗ trợ quản lý sách và mượn trả."
                    ),
                    mucTieu=(
                        "Số hóa và tối ưu hóa việc quản lý thư viện."
                    ),
                    tuKhoa="Flask, MySQL, Library",
                    linhVucId=linh_vuc_web.id,
                    sinhVienId=sv2.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                # --------------------------------------------------
                # 8 - CHỜ DUYỆT
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Hệ thống quản lý sinh viên trực tuyến"
                    ),
                    moTa=(
                        "Website quản lý thông tin "
                        "và kết quả học tập sinh viên."
                    ),
                    mucTieu=(
                        "Nâng cao hiệu quả quản lý thông tin."
                    ),
                    tuKhoa="Web, Student Management",
                    linhVucId=linh_vuc_web.id,
                    sinhVienId=sv3.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.CHO_DUYET
                ),

                # --------------------------------------------------
                # 9 - HOÀN THÀNH
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Xây dựng hệ thống quản lý đề tài "
                        "đồ án sinh viên"
                    ),
                    moTa=(
                        "Hệ thống quản lý đăng ký, xét duyệt "
                        "và theo dõi tiến độ đồ án."
                    ),
                    mucTieu=(
                        "Hỗ trợ quản lý toàn bộ quy trình đồ án."
                    ),
                    tuKhoa="Project Management, Web",
                    linhVucId=linh_vuc_web.id,
                    sinhVienId=sv4.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.HOAN_THANH
                ),

                # --------------------------------------------------
                # 10 - NHÁP
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Hệ thống quản lý lịch làm việc trực tuyến"
                    ),
                    moTa=(
                        "Xây dựng hệ thống hỗ trợ tạo lịch "
                        "và quản lý công việc."
                    ),
                    mucTieu=(
                        "Hỗ trợ người dùng quản lý công việc."
                    ),
                    tuKhoa="Web, Calendar, Management",
                    linhVucId=linh_vuc_web.id,
                    sinhVienId=sv5.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.NHAP
                ),

                # --------------------------------------------------
                # 11 - ĐÃ DUYỆT
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Phân tích dữ liệu học tập "
                        "của sinh viên"
                    ),
                    moTa=(
                        "Thu thập và phân tích dữ liệu học tập "
                        "để đánh giá kết quả sinh viên."
                    ),
                    mucTieu=(
                        "Tìm ra các yếu tố ảnh hưởng "
                        "đến kết quả học tập."
                    ),
                    tuKhoa="Data Analysis, Student Data",
                    linhVucId=linh_vuc_data.id,
                    sinhVienId=sv6.id,
                    giangVienId=gv4_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                # --------------------------------------------------
                # 12 - CHỜ DUYỆT
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Hệ thống phân tích dữ liệu bán hàng"
                    ),
                    moTa=(
                        "Phân tích dữ liệu bán hàng "
                        "để hỗ trợ doanh nghiệp."
                    ),
                    mucTieu=(
                        "Hỗ trợ doanh nghiệp ra quyết định."
                    ),
                    tuKhoa="Data Science, Analytics",
                    linhVucId=linh_vuc_data.id,
                    sinhVienId=sv7.id,
                    giangVienId=gv4_user.id,
                    trangThai=TrangThaiDeTai.CHO_DUYET
                ),

                # --------------------------------------------------
                # 13 - HOÀN THÀNH
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Dự đoán doanh thu "
                        "bằng Machine Learning"
                    ),
                    moTa=(
                        "Sử dụng Machine Learning để dự đoán "
                        "doanh thu dựa trên dữ liệu lịch sử."
                    ),
                    mucTieu=(
                        "Hỗ trợ lập kế hoạch kinh doanh."
                    ),
                    tuKhoa="Machine Learning, Revenue, Data",
                    linhVucId=linh_vuc_data.id,
                    sinhVienId=sv3.id,
                    giangVienId=gv4_user.id,
                    trangThai=TrangThaiDeTai.HOAN_THANH
                ),

                # --------------------------------------------------
                # 14 - ĐÃ DUYỆT
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Xây dựng hệ thống "
                        "phát hiện xâm nhập mạng"
                    ),
                    moTa=(
                        "Phân tích lưu lượng mạng để phát hiện "
                        "các hành vi truy cập bất thường."
                    ),
                    mucTieu=(
                        "Nâng cao khả năng phát hiện "
                        "tấn công mạng."
                    ),
                    tuKhoa="Cyber Security, Network, IDS",
                    linhVucId=linh_vuc_security.id,
                    sinhVienId=sv4.id,
                    giangVienId=gv3_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                # --------------------------------------------------
                # 15 - ĐÃ DUYỆT
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Hệ thống quản lý đăng nhập "
                        "và xác thực người dùng"
                    ),
                    moTa=(
                        "Xây dựng hệ thống xác thực "
                        "và quản lý quyền truy cập."
                    ),
                    mucTieu=(
                        "Nâng cao tính bảo mật của hệ thống."
                    ),
                    tuKhoa="Authentication, Security",
                    linhVucId=linh_vuc_security.id,
                    sinhVienId=sv5.id,
                    giangVienId=gv3_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                # --------------------------------------------------
                # 16 - TỪ CHỐI
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Nghiên cứu hệ thống bảo mật "
                        "không phù hợp"
                    ),
                    moTa=(
                        "Đề tài mẫu để kiểm thử trường hợp "
                        "đề tài bị từ chối."
                    ),
                    mucTieu=(
                        "Kiểm thử quy trình từ chối đề tài."
                    ),
                    tuKhoa="Security, Testing",
                    linhVucId=linh_vuc_security.id,
                    sinhVienId=sv6.id,
                    giangVienId=gv3_user.id,
                    trangThai=TrangThaiDeTai.TU_CHOI
                ),

                # --------------------------------------------------
                # 17 - ĐÃ DUYỆT
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Ứng dụng quản lý chi tiêu cá nhân "
                        "trên điện thoại"
                    ),
                    moTa=(
                        "Ứng dụng giúp người dùng "
                        "theo dõi thu nhập và chi tiêu."
                    ),
                    mucTieu=(
                        "Hỗ trợ quản lý tài chính cá nhân."
                    ),
                    tuKhoa="Mobile, Finance, Android",
                    linhVucId=linh_vuc_mobile.id,
                    sinhVienId=sv1.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                # --------------------------------------------------
                # 18 - CHỜ DUYỆT
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Ứng dụng đặt lịch khám "
                        "bệnh trực tuyến"
                    ),
                    moTa=(
                        "Ứng dụng hỗ trợ người dùng "
                        "đặt lịch khám và quản lý lịch hẹn."
                    ),
                    mucTieu=(
                        "Giúp người dùng thuận tiện "
                        "trong việc đặt lịch khám."
                    ),
                    tuKhoa="Mobile, Healthcare, Booking",
                    linhVucId=linh_vuc_mobile.id,
                    sinhVienId=sv2.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.CHO_DUYET
                ),

                # --------------------------------------------------
                # 19 - HOÀN THÀNH
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Ứng dụng học ngoại ngữ "
                        "trên thiết bị di động"
                    ),
                    moTa=(
                        "Ứng dụng hỗ trợ người học "
                        "luyện từ vựng và giao tiếp."
                    ),
                    mucTieu=(
                        "Hỗ trợ người dùng học ngoại ngữ "
                        "mọi lúc mọi nơi."
                    ),
                    tuKhoa="Mobile, Language Learning",
                    linhVucId=linh_vuc_mobile.id,
                    sinhVienId=sv7.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.HOAN_THANH
                ),

                # --------------------------------------------------
                # 20 - NHÁP
                # --------------------------------------------------

                DeTai(
                    tenDeTai=(
                        "Phân tích dữ liệu mạng xã hội "
                        "phục vụ nghiên cứu"
                    ),
                    moTa=(
                        "Nghiên cứu dữ liệu mạng xã hội "
                        "và hành vi người dùng."
                    ),
                    mucTieu=(
                        "Phân tích xu hướng và hành vi người dùng."
                    ),
                    tuKhoa="Data Mining, Social Media",
                    linhVucId=linh_vuc_data.id,
                    sinhVienId=sv7.id,
                    giangVienId=gv4_user.id,
                    trangThai=TrangThaiDeTai.NHAP
                )
            ]

            db.session.add_all(danh_sach_de_tai)

            db.session.flush()

            print(
                f"    ✓ Đã tạo {len(danh_sach_de_tai)} đề tài"
            )
            # ==================================================
            # 21 - ĐỀ TÀI TEST TRÙNG LẶP
            # ==================================================

            dt_test_1 = DeTai(
                tenDeTai=(
                    "Xây dựng hệ thống quản lý đề tài "
                    "nghiên cứu khoa học bằng trí tuệ nhân tạo"
                ),
                moTa=(
                    "Xây dựng hệ thống quản lý đề tài nghiên cứu "
                    "khoa học bằng trí tuệ nhân tạo nhằm hỗ trợ "
                    "sinh viên đăng ký và quản lý đề tài."
                ),
                mucTieu=(
                    "Xây dựng hệ thống quản lý đề tài nghiên cứu "
                    "khoa học và ứng dụng trí tuệ nhân tạo để "
                    "hỗ trợ sinh viên tìm kiếm đề tài."
                ),
                tuKhoa=(
                    "AI, nghiên cứu khoa học, quản lý đề tài, sinh viên"
                ),
                linhVucId=linh_vuc_ai.id,
                sinhVienId=sv1.id,
                giangVienId=gv1_user.id,
                trangThai=TrangThaiDeTai.DA_DUYET
            )

            dt_test_2 = DeTai(
                tenDeTai=(
                    "Xây dựng hệ thống quản lý đề tài "
                    "nghiên cứu khoa học ứng dụng AI"
                ),
                moTa=(
                    "Xây dựng hệ thống quản lý đề tài nghiên cứu "
                    "khoa học bằng trí tuệ nhân tạo nhằm hỗ trợ "
                    "sinh viên đăng ký và quản lý đề tài."
                ),
                mucTieu=(
                    "Xây dựng hệ thống quản lý đề tài nghiên cứu "
                    "khoa học và ứng dụng trí tuệ nhân tạo để "
                    "hỗ trợ sinh viên tìm kiếm đề tài."
                ),
                tuKhoa=(
                    "AI, nghiên cứu khoa học, quản lý đề tài, sinh viên"
                ),
                linhVucId=linh_vuc_ai.id,
                sinhVienId=sv2.id,
                giangVienId=gv1_user.id,
                trangThai=TrangThaiDeTai.DA_DUYET
            )

            db.session.add_all([
                dt_test_1,
                dt_test_2
            ])

            db.session.flush()

            # ==================================================
            # GÁN BIẾN ĐỀ TÀI CHO DỄ DÙNG
            # ==================================================

            dt1 = danh_sach_de_tai[0]
            dt2 = danh_sach_de_tai[1]
            dt3 = danh_sach_de_tai[2]
            dt4 = danh_sach_de_tai[3]
            dt5 = danh_sach_de_tai[4]
            dt6 = danh_sach_de_tai[5]
            dt7 = danh_sach_de_tai[6]
            dt8 = danh_sach_de_tai[7]
            dt9 = danh_sach_de_tai[8]
            dt10 = danh_sach_de_tai[9]
            dt11 = danh_sach_de_tai[10]
            dt12 = danh_sach_de_tai[11]
            dt13 = danh_sach_de_tai[12]
            dt14 = danh_sach_de_tai[13]
            dt15 = danh_sach_de_tai[14]
            dt16 = danh_sach_de_tai[15]
            dt17 = danh_sach_de_tai[16]
            dt18 = danh_sach_de_tai[17]
            dt19 = danh_sach_de_tai[18]
            dt20 = danh_sach_de_tai[19]

            # ==================================================
            # 11. GỢI Ý GIẢNG VIÊN
            # ==================================================

            print("[10] Tạo dữ liệu gợi ý giảng viên...")

            db.session.add_all([

                GoiYGiangVien(
                    deTaiId=dt1.id,
                    giangVienId=gv1_user.id,
                    diemPhuHop=95.0,
                    lyDo="Chuyên môn AI và tìm kiếm ngữ nghĩa phù hợp với đề tài."
                ),

                GoiYGiangVien(
                    deTaiId=dt1.id,
                    giangVienId=gv4_user.id,
                    diemPhuHop=82.0,
                    lyDo="Có chuyên môn về khoa học dữ liệu và AI."
                ),

                GoiYGiangVien(
                    deTaiId=dt2.id,
                    giangVienId=gv1_user.id,
                    diemPhuHop=97.0,
                    lyDo="Chuyên môn Machine Learning và NLP rất phù hợp."
                ),

                GoiYGiangVien(
                    deTaiId=dt2.id,
                    giangVienId=gv4_user.id,
                    diemPhuHop=86.0,
                    lyDo="Có chuyên môn về phân tích dữ liệu."
                ),

                GoiYGiangVien(
                    deTaiId=dt6.id,
                    giangVienId=gv2_user.id,
                    diemPhuHop=96.0,
                    lyDo="Chuyên môn phát triển phần mềm và Web."
                ),

                GoiYGiangVien(
                    deTaiId=dt6.id,
                    giangVienId=gv1_user.id,
                    diemPhuHop=70.0,
                    lyDo="Có kinh nghiệm về hệ thống AI."
                ),

                GoiYGiangVien(
                    deTaiId=dt11.id,
                    giangVienId=gv4_user.id,
                    diemPhuHop=98.0,
                    lyDo="Chuyên môn chính là Data Science."
                ),

                GoiYGiangVien(
                    deTaiId=dt11.id,
                    giangVienId=gv1_user.id,
                    diemPhuHop=84.0,
                    lyDo="Có chuyên môn AI và Machine Learning."
                ),

                GoiYGiangVien(
                    deTaiId=dt14.id,
                    giangVienId=gv3_user.id,
                    diemPhuHop=99.0,
                    lyDo="Chuyên môn An toàn thông tin và Network Security."
                ),

                GoiYGiangVien(
                    deTaiId=dt15.id,
                    giangVienId=gv3_user.id,
                    diemPhuHop=96.0,
                    lyDo="Chuyên môn Authentication và Security."
                ),

                GoiYGiangVien(
                    deTaiId=dt17.id,
                    giangVienId=gv2_user.id,
                    diemPhuHop=94.0,
                    lyDo="Chuyên môn phát triển ứng dụng."
                ),

                GoiYGiangVien(
                    deTaiId=dt20.id,
                    giangVienId=gv4_user.id,
                    diemPhuHop=93.0,
                    lyDo="Chuyên môn Data Mining và phân tích dữ liệu."
                )
            ])

            # ==================================================
            # 12. KIỂM TRA TRÙNG LẶP
            # ==================================================

            print("[11] Tạo dữ liệu kiểm tra trùng lặp...")

            db.session.add_all([

                KiemTraTrungLap(
                    deTai1Id=dt1.id,
                    deTai2Id=dt2.id,
                    doTuongDong=0.87
                ),

                KiemTraTrungLap(
                    deTai1Id=dt1.id,
                    deTai2Id=dt3.id,
                    doTuongDong=0.64
                ),

                KiemTraTrungLap(
                    deTai1Id=dt4.id,
                    deTai2Id=dt11.id,
                    doTuongDong=0.78
                ),

                KiemTraTrungLap(
                    deTai1Id=dt6.id,
                    deTai2Id=dt8.id,
                    doTuongDong=0.82
                ),

                KiemTraTrungLap(
                    deTai1Id=dt14.id,
                    deTai2Id=dt15.id,
                    doTuongDong=0.73
                ),

                KiemTraTrungLap(
                    deTai1Id=dt17.id,
                    deTai2Id=dt18.id,
                    doTuongDong=0.45
                )
            ])

            # ==================================================
            # 13. LỊCH SỬ TÌM KIẾM
            # ==================================================

            print("[12] Tạo lịch sử tìm kiếm...")

            db.session.add_all([

                LichSuTimKiem(
                    userId=sv1.id,
                    tuKhoa="trí tuệ nhân tạo"
                ),

                LichSuTimKiem(
                    userId=sv1.id,
                    tuKhoa="machine learning"
                ),

                LichSuTimKiem(
                    userId=sv2.id,
                    tuKhoa="web"
                ),

                LichSuTimKiem(
                    userId=sv2.id,
                    tuKhoa="an toàn thông tin"
                ),

                LichSuTimKiem(
                    userId=sv3.id,
                    tuKhoa="chatbot"
                ),

                LichSuTimKiem(
                    userId=sv3.id,
                    tuKhoa="data science"
                ),

                LichSuTimKiem(
                    userId=sv4.id,
                    tuKhoa="machine learning"
                ),

                LichSuTimKiem(
                    userId=sv5.id,
                    tuKhoa="security"
                ),

                LichSuTimKiem(
                    userId=sv6.id,
                    tuKhoa="data mining"
                ),

                LichSuTimKiem(
                    userId=sv7.id,
                    tuKhoa="mobile"
                )
            ])

            # ==================================================
            # 14. TIẾN ĐỘ
            # ==================================================

            print("[13] Tạo dữ liệu tiến độ...")

            db.session.add_all([

                # DT1
                TienDo(
                    deTaiId=dt1.id,
                    tieuDe="Phân tích yêu cầu",
                    noiDung="Đã phân tích yêu cầu và xác định phạm vi hệ thống.",
                    phanTram=25,
                    trangThai=TrangThaiTienDo.DANG_THUC_HIEN,
                    nhanXetGiangVien="Cần bổ sung thêm yêu cầu về dữ liệu."
                ),

                TienDo(
                    deTaiId=dt1.id,
                    tieuDe="Thiết kế hệ thống",
                    noiDung="Đã hoàn thành thiết kế kiến trúc hệ thống.",
                    phanTram=60,
                    trangThai=TrangThaiTienDo.HOAN_THANH_MOT_PHAN,
                    nhanXetGiangVien="Thiết kế tương đối đầy đủ."
                ),

                TienDo(
                    deTaiId=dt1.id,
                    tieuDe="Phát triển chức năng",
                    noiDung="Đang xây dựng chức năng tìm kiếm ngữ nghĩa.",
                    phanTram=75,
                    trangThai=TrangThaiTienDo.DANG_THUC_HIEN,
                    nhanXetGiangVien="Tiếp tục hoàn thiện chức năng."
                ),

                # DT3
                TienDo(
                    deTaiId=dt3.id,
                    tieuDe="Phân tích",
                    noiDung="Hoàn thành phân tích yêu cầu.",
                    phanTram=100,
                    trangThai=TrangThaiTienDo.HOAN_THANH,
                    nhanXetGiangVien="Đã hoàn thành."
                ),

                # DT4
                TienDo(
                    deTaiId=dt4.id,
                    tieuDe="Thu thập dữ liệu",
                    noiDung="Đã thu thập dữ liệu học tập.",
                    phanTram=100,
                    trangThai=TrangThaiTienDo.HOAN_THANH,
                    nhanXetGiangVien="Dữ liệu đạt yêu cầu."
                ),

                TienDo(
                    deTaiId=dt4.id,
                    tieuDe="Huấn luyện mô hình",
                    noiDung="Đang huấn luyện mô hình Machine Learning.",
                    phanTram=80,
                    trangThai=TrangThaiTienDo.DANG_THUC_HIEN,
                    nhanXetGiangVien="Cần đánh giá thêm độ chính xác."
                ),

                # DT9 - hoàn thành
                TienDo(
                    deTaiId=dt9.id,
                    tieuDe="Hoàn thành hệ thống",
                    noiDung="Hệ thống đã hoàn thành.",
                    phanTram=100,
                    trangThai=TrangThaiTienDo.HOAN_THANH,
                    nhanXetGiangVien="Đủ điều kiện nghiệm thu."
                ),

                TienDo(
                    deTaiId=dt9.id,
                    tieuDe="Nghiệm thu",
                    noiDung="Đã hoàn thành nghiệm thu.",
                    phanTram=100,
                    trangThai=TrangThaiTienDo.DA_NGHIEM_THU,
                    nhanXetGiangVien="Đạt yêu cầu."
                ),

                # DT14
                TienDo(
                    deTaiId=dt14.id,
                    tieuDe="Khảo sát hệ thống",
                    noiDung="Đang khảo sát và phân tích lưu lượng mạng.",
                    phanTram=30,
                    trangThai=TrangThaiTienDo.DANG_THUC_HIEN,
                    nhanXetGiangVien="Tiếp tục thu thập dữ liệu."
                ),

                # DT17
                TienDo(
                    deTaiId=dt17.id,
                    tieuDe="Thiết kế ứng dụng",
                    noiDung="Đã hoàn thành giao diện ứng dụng.",
                    phanTram=50,
                    trangThai=TrangThaiTienDo.HOAN_THANH_MOT_PHAN,
                    nhanXetGiangVien="Cần bổ sung chức năng báo cáo."
                )
            ])

            # ==================================================
            # 15. YÊU CẦU CHỈNH SỬA
            # ==================================================

            print("[14] Tạo yêu cầu chỉnh sửa...")

            db.session.add_all([

                YeuCauChinhSua(
                    deTaiId=dt1.id,
                    nguoiYeuCauId=sv1.id,
                    noiDung=(
                        "Cần bổ sung phần mô tả phương pháp "
                        "tìm kiếm ngữ nghĩa."
                    ),
                    phanHoiGiangVien=(
                        "Đã xem yêu cầu. Sinh viên bổ sung "
                        "phần phương pháp theo góp ý."
                    ),
                    daXuLy=True,
                    ngayXuLy=datetime.now()
                ),

                YeuCauChinhSua(
                    deTaiId=dt4.id,
                    nguoiYeuCauId=sv4.id,
                    noiDung=(
                        "Xin góp ý thêm về dữ liệu dùng "
                        "để huấn luyện mô hình."
                    ),
                    phanHoiGiangVien=(
                        "Nên bổ sung thêm dữ liệu từ học kỳ gần nhất."
                    ),
                    daXuLy=True,
                    ngayXuLy=datetime.now()
                ),

                YeuCauChinhSua(
                    deTaiId=dt6.id,
                    nguoiYeuCauId=sv1.id,
                    noiDung=(
                        "Đề nghị xem xét lại kiến trúc "
                        "hệ thống Web."
                    ),
                    phanHoiGiangVien=None,
                    daXuLy=False
                ),

                YeuCauChinhSua(
                    deTaiId=dt14.id,
                    nguoiYeuCauId=sv4.id,
                    noiDung=(
                        "Xin hướng dẫn thêm cách đánh giá "
                        "độ chính xác của hệ thống."
                    ),
                    phanHoiGiangVien=None,
                    daXuLy=False
                ),

                YeuCauChinhSua(
                    deTaiId=dt17.id,
                    nguoiYeuCauId=sv1.id,
                    noiDung=(
                        "Cần bổ sung chức năng thống kê "
                        "chi tiêu theo tháng."
                    ),
                    phanHoiGiangVien=(
                        "Đã đồng ý. Bổ sung biểu đồ thống kê."
                    ),
                    daXuLy=True,
                    ngayXuLy=datetime.now()
                )
            ])

            # ==================================================
            # 16. KẾT QUẢ NGHIỆM THU
            # ==================================================

            print("[15] Tạo kết quả nghiệm thu...")

            db.session.add_all([

                # Chưa nghiệm thu
                KetQuaNghiemThu(
                    deTaiId=dt1.id,
                    nguoiNghiemThuId=gv1_user.id,
                    diem=None,
                    nhanXet=None,
                    ketLuan=None,
                    trangThai=TrangThaiNghiemThu.CHUA_NGHIEM_THU,
                    ngayNghiemThu=None
                ),

                # Đạt
                KetQuaNghiemThu(
                    deTaiId=dt9.id,
                    nguoiNghiemThuId=gv2_user.id,
                    diem=8.5,
                    nhanXet=(
                        "Đề tài hoàn thành đầy đủ các chức năng "
                        "theo yêu cầu."
                    ),
                    ketLuan="Đạt yêu cầu nghiệm thu.",
                    trangThai=TrangThaiNghiemThu.DAT,
                    ngayNghiemThu=datetime.now()
                ),

                # Đạt
                KetQuaNghiemThu(
                    deTaiId=dt13.id,
                    nguoiNghiemThuId=gv4_user.id,
                    diem=9.0,
                    nhanXet=(
                        "Mô hình dự đoán có kết quả tốt."
                    ),
                    ketLuan="Đạt yêu cầu.",
                    trangThai=TrangThaiNghiemThu.DAT,
                    ngayNghiemThu=datetime.now()
                ),

                # Không đạt
                KetQuaNghiemThu(
                    deTaiId=dt19.id,
                    nguoiNghiemThuId=gv2_user.id,
                    diem=5.0,
                    nhanXet=(
                        "Ứng dụng còn thiếu một số chức năng."
                    ),
                    ketLuan="Cần chỉnh sửa và nghiệm thu lại.",
                    trangThai=TrangThaiNghiemThu.KHONG_DAT,
                    ngayNghiemThu=datetime.now()
                )
            ])

            # ==================================================
            # 17. THÔNG BÁO
            # ==================================================

            print("[16] Tạo thông báo...")

            db.session.add_all([

                # ADMIN
                ThongBao(
                    userId=admin.id,
                    tieuDe="Hệ thống hoạt động bình thường",
                    noiDung=(
                        "Dữ liệu hệ thống đã được khởi tạo "
                        "thành công."
                    ),
                    loai=LoaiThongBao.HE_THONG,
                    daDoc=False
                ),

                # Sinh viên 1
                ThongBao(
                    userId=sv1.id,
                    tieuDe="Đề tài đã được duyệt",
                    noiDung=(
                        "Đề tài 'Ứng dụng trí tuệ nhân tạo "
                        "trong tìm kiếm ngữ nghĩa' đã được duyệt."
                    ),
                    loai=LoaiThongBao.DUYET_DE_TAI,
                    deTaiId=dt1.id,
                    daDoc=False
                ),

                ThongBao(
                    userId=sv1.id,
                    tieuDe="Đã phân công giảng viên",
                    noiDung=(
                        "Bạn được hướng dẫn bởi "
                        "TS. Nguyễn Văn A."
                    ),
                    loai=LoaiThongBao.PHAN_CONG,
                    deTaiId=dt1.id,
                    daDoc=True
                ),

                ThongBao(
                    userId=sv1.id,
                    tieuDe="Yêu cầu chỉnh sửa",
                    noiDung=(
                        "Giảng viên yêu cầu bổ sung "
                        "phương pháp tìm kiếm."
                    ),
                    loai=LoaiThongBao.YEU_CAU_CHINH_SUA,
                    deTaiId=dt1.id,
                    daDoc=False
                ),

                ThongBao(
                    userId=sv1.id,
                    tieuDe="Cập nhật tiến độ",
                    noiDung=(
                        "Tiến độ đề tài của bạn đã được cập nhật."
                    ),
                    loai=LoaiThongBao.TIEN_DO,
                    deTaiId=dt1.id,
                    daDoc=True
                ),

                # Sinh viên 2
                ThongBao(
                    userId=sv2.id,
                    tieuDe="Đề tài đang chờ duyệt",
                    noiDung=(
                        "Đề tài của bạn đang được cán bộ "
                        "xem xét."
                    ),
                    loai=LoaiThongBao.HE_THONG,
                    deTaiId=dt2.id,
                    daDoc=False
                ),

                ThongBao(
                    userId=sv2.id,
                    tieuDe="Đề tài đã được duyệt",
                    noiDung=(
                        "Đề tài quản lý thư viện số đã được duyệt."
                    ),
                    loai=LoaiThongBao.DUYET_DE_TAI,
                    deTaiId=dt7.id,
                    daDoc=True
                ),

                # Sinh viên 3
                ThongBao(
                    userId=sv3.id,
                    tieuDe="Đề tài đã được duyệt",
                    noiDung=(
                        "Đề tài chatbot của bạn đã được duyệt."
                    ),
                    loai=LoaiThongBao.DUYET_DE_TAI,
                    deTaiId=dt3.id,
                    daDoc=False
                ),

                ThongBao(
                    userId=sv3.id,
                    tieuDe="Cập nhật tiến độ",
                    noiDung=(
                        "Giảng viên đã cập nhật tiến độ đề tài."
                    ),
                    loai=LoaiThongBao.TIEN_DO,
                    deTaiId=dt3.id,
                    daDoc=False
                ),

                # Sinh viên 4
                ThongBao(
                    userId=sv4.id,
                    tieuDe="Yêu cầu chỉnh sửa",
                    noiDung=(
                        "Vui lòng bổ sung dữ liệu "
                        "huấn luyện mô hình."
                    ),
                    loai=LoaiThongBao.YEU_CAU_CHINH_SUA,
                    deTaiId=dt4.id,
                    daDoc=False
                ),

                ThongBao(
                    userId=sv4.id,
                    tieuDe="Thông tin nghiệm thu",
                    noiDung=(
                        "Đề tài của bạn đang được chuẩn bị nghiệm thu."
                    ),
                    loai=LoaiThongBao.NGHIEM_THU,
                    deTaiId=dt4.id,
                    daDoc=False
                ),

                # Sinh viên 5
                ThongBao(
                    userId=sv5.id,
                    tieuDe="Đề tài đang chờ duyệt",
                    noiDung=(
                        "Đề tài nhận diện khuôn mặt "
                        "đang chờ duyệt."
                    ),
                    loai=LoaiThongBao.HE_THONG,
                    deTaiId=dt5.id,
                    daDoc=True
                ),

                # Sinh viên 6
                ThongBao(
                    userId=sv6.id,
                    tieuDe="Đề tài bị từ chối",
                    noiDung=(
                        "Đề tài của bạn chưa đáp ứng "
                        "yêu cầu và cần chỉnh sửa."
                    ),
                    loai=LoaiThongBao.TU_CHOI_DE_TAI,
                    deTaiId=dt16.id,
                    daDoc=False
                ),

                # Sinh viên 7
                ThongBao(
                    userId=sv7.id,
                    tieuDe="Đề tài đang chờ duyệt",
                    noiDung=(
                        "Đề tài phân tích dữ liệu bán hàng "
                        "đang chờ duyệt."
                    ),
                    loai=LoaiThongBao.DUYET_DE_TAI,
                    deTaiId=dt12.id,
                    daDoc=False
                ),

                # GV1
                ThongBao(
                    userId=gv1_user.id,
                    tieuDe="Có đề tài mới được phân công",
                    noiDung=(
                        "Bạn được phân công hướng dẫn "
                        "một đề tài mới."
                    ),
                    loai=LoaiThongBao.PHAN_CONG,
                    deTaiId=dt1.id,
                    daDoc=False
                ),

                ThongBao(
                    userId=gv1_user.id,
                    tieuDe="Sinh viên gửi yêu cầu chỉnh sửa",
                    noiDung=(
                        "Có yêu cầu chỉnh sửa mới "
                        "từ sinh viên."
                    ),
                    loai=LoaiThongBao.YEU_CAU_CHINH_SUA,
                    deTaiId=dt4.id,
                    daDoc=False
                ),

                # GV2
                ThongBao(
                    userId=gv2_user.id,
                    tieuDe="Có đề tài cần hướng dẫn",
                    noiDung=(
                        "Bạn có đề tài mới cần xem xét."
                    ),
                    loai=LoaiThongBao.PHAN_CONG,
                    deTaiId=dt6.id,
                    daDoc=False
                ),

                # GV3
                ThongBao(
                    userId=gv3_user.id,
                    tieuDe="Cập nhật tiến độ đề tài",
                    noiDung=(
                        "Có cập nhật tiến độ từ sinh viên."
                    ),
                    loai=LoaiThongBao.TIEN_DO,
                    deTaiId=dt14.id,
                    daDoc=False
                ),

                # GV4
                ThongBao(
                    userId=gv4_user.id,
                    tieuDe="Đề tài cần nghiệm thu",
                    noiDung=(
                        "Có đề tài cần được nghiệm thu."
                    ),
                    loai=LoaiThongBao.NGHIEM_THU,
                    deTaiId=dt13.id,
                    daDoc=False
                )
            ])

            # ==================================================
            # 18. TÀI LIỆU
            # ==================================================

            print("[17] Tạo dữ liệu tài liệu...")

            db.session.add_all([

                TaiLieu(
                    deTaiId=dt1.id,
                    nguoiTaiId=sv1.id,
                    tenTaiLieu="Đề cương đề tài tìm kiếm ngữ nghĩa.pdf",
                    duongDan="uploads/demo/de_cuong_tim_kiem_ngu_nghia.pdf",
                    loaiFile="PDF"
                ),

                TaiLieu(
                    deTaiId=dt1.id,
                    nguoiTaiId=sv1.id,
                    tenTaiLieu="Tài liệu tham khảo AI.pdf",
                    duongDan="uploads/demo/tai_lieu_ai.pdf",
                    loaiFile="PDF"
                ),

                TaiLieu(
                    deTaiId=dt4.id,
                    nguoiTaiId=sv4.id,
                    tenTaiLieu="Báo cáo Machine Learning.pdf",
                    duongDan="uploads/demo/bao_cao_machine_learning.pdf",
                    loaiFile="PDF"
                ),

                TaiLieu(
                    deTaiId=dt6.id,
                    nguoiTaiId=sv1.id,
                    tenTaiLieu="Thiết kế hệ thống Web.pdf",
                    duongDan="uploads/demo/thiet_ke_web.pdf",
                    loaiFile="PDF"
                ),

                TaiLieu(
                    deTaiId=dt7.id,
                    nguoiTaiId=sv2.id,
                    tenTaiLieu="Tài liệu thư viện số.docx",
                    duongDan="uploads/demo/thu_vien_so.docx",
                    loaiFile="DOCX"
                ),

                TaiLieu(
                    deTaiId=dt9.id,
                    nguoiTaiId=sv4.id,
                    tenTaiLieu="Báo cáo hoàn thành đồ án.pdf",
                    duongDan="uploads/demo/bao_cao_do_an.pdf",
                    loaiFile="PDF"
                ),

                TaiLieu(
                    deTaiId=dt11.id,
                    nguoiTaiId=sv6.id,
                    tenTaiLieu="Báo cáo phân tích dữ liệu.pdf",
                    duongDan="uploads/demo/phan_tich_du_lieu.pdf",
                    loaiFile="PDF"
                ),

                TaiLieu(
                    deTaiId=dt13.id,
                    nguoiTaiId=sv3.id,
                    tenTaiLieu="Báo cáo dự đoán doanh thu.pdf",
                    duongDan="uploads/demo/du_doan_doanh_thu.pdf",
                    loaiFile="PDF"
                ),

                TaiLieu(
                    deTaiId=dt14.id,
                    nguoiTaiId=sv4.id,
                    tenTaiLieu="Báo cáo an toàn mạng.pdf",
                    duongDan="uploads/demo/an_toan_mang.pdf",
                    loaiFile="PDF"
                ),

                TaiLieu(
                    deTaiId=dt17.id,
                    nguoiTaiId=sv1.id,
                    tenTaiLieu="Thiết kế ứng dụng mobile.pdf",
                    duongDan="uploads/demo/ung_dung_mobile.pdf",
                    loaiFile="PDF"
                ),

                TaiLieu(
                    deTaiId=dt19.id,
                    nguoiTaiId=sv7.id,
                    tenTaiLieu="Báo cáo ứng dụng học ngoại ngữ.pdf",
                    duongDan="uploads/demo/hoc_ngoai_ngu.pdf",
                    loaiFile="PDF"
                )
            ])

            # ==================================================
            # 19. COMMIT TOÀN BỘ
            # ==================================================

            print("[18] Lưu toàn bộ dữ liệu...")

            db.session.commit()

            # ==================================================
            # 20. THỐNG KÊ
            # ==================================================

            print()
            print("=" * 70)
            print("DATABASE ĐÃ ĐƯỢC TẠO THÀNH CÔNG")
            print("=" * 70)

            print()
            print("THỐNG KÊ:")
            print("----------------------------------------")
            print(f"User:                 {User.query.count()}")
            print(f"Giảng viên:           {GiangVien.query.count()}")
            print(f"Lĩnh vực:             {LinhVuc.query.count()}")
            print(f"Đề tài:               {DeTai.query.count()}")
            print(f"Gợi ý giảng viên:     {GoiYGiangVien.query.count()}")
            print(f"Kiểm tra trùng lặp:   {KiemTraTrungLap.query.count()}")
            print(f"Lịch sử tìm kiếm:     {LichSuTimKiem.query.count()}")
            print(f"Tiến độ:              {TienDo.query.count()}")
            print(f"Yêu cầu chỉnh sửa:    {YeuCauChinhSua.query.count()}")
            print(f"Kết quả nghiệm thu:   {KetQuaNghiemThu.query.count()}")
            print(f"Thông báo:            {ThongBao.query.count()}")
            print(f"Tài liệu:             {TaiLieu.query.count()}")

            print()
            print("TÀI KHOẢN TEST")
            print("----------------------------------------")

            print("ADMIN")
            print("  Username: admin")
            print("  Password: 123456")

            print()
            print("GIẢNG VIÊN")
            print("  nguyenvana / 123456")
            print("  tranthib   / 123456")
            print("  leminhc    / 123456")
            print("  phamhoangd / 123456")

            print()
            print("SINH VIÊN")
            print("  sinhvien1 / 123456")
            print("  sinhvien2 / 123456")
            print("  sinhvien3 / 123456")
            print("  sinhvien4 / 123456")
            print("  sinhvien5 / 123456")
            print("  sinhvien6 / 123456")
            print("  sinhvien7 / 123456")

            print()
            print("TRẠNG THÁI ĐỀ TÀI")
            print("----------------------------------------")
            print("  NHAP")
            print("  CHO_DUYET")
            print("  DA_DUYET")
            print("  TU_CHOI")
            print("  HOAN_THANH")

            print()
            print("TRẠNG THÁI TIẾN ĐỘ")
            print("----------------------------------------")
            print("  CHUA_BAT_DAU")
            print("  DANG_THUC_HIEN")
            print("  HOAN_THANH_MOT_PHAN")
            print("  HOAN_THANH")
            print("  DA_NGHIEM_THU")

            print()
            print("TRẠNG THÁI NGHIỆM THU")
            print("----------------------------------------")
            print("  CHUA_NGHIEM_THU")
            print("  DAT")
            print("  KHONG_DAT")

            print()
            print("=" * 70)
            print("HOÀN TẤT!")
            print("=" * 70)

        except Exception as e:

            db.session.rollback()

            print()
            print("=" * 70)
            print("LỖI KHI TẠO DATABASE")
            print("=" * 70)

            print(e)

            import traceback

            traceback.print_exc()

            print("=" * 70)