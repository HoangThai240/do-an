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

    doTuongDong = Column(
        Float,
        nullable=False
    )

    ngayKiemTra = Column(
        DateTime,
        default=datetime.now
    )

    de_tai_1 = relationship(
        "DeTai",
        foreign_keys=[deTai1Id]
    )

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


# ==================================================
# DỮ LIỆU MẪU
# ==================================================

if __name__ == "__main__":

    from app import app

    with app.app_context():

        try:

            print("=" * 60)
            print("BẮT ĐẦU KHỞI TẠO DATABASE")
            print("=" * 60)

            # ==================================================
            # XÓA DATABASE CŨ
            # ==================================================

            print("\n[1] Đang xóa dữ liệu database cũ...")

            db.drop_all()

            # ==================================================
            # TẠO DATABASE MỚI
            # ==================================================

            print("[2] Đang tạo các bảng database...")

            db.create_all()

            # ==================================================
            # ADMIN
            # ==================================================

            admin = User(
                username="admin",
                hoTen="Quản trị viên",
                email="admin@nckh.vn",
                role=UserRole.ADMIN
            )

            admin.set_password("123456")

            # ==================================================
            # GIẢNG VIÊN
            # ==================================================

            gv1_user = User(
                username="nguyenvana",
                hoTen="TS. Nguyễn Văn A",
                email="nguyenvana@ou.edu.vn",
                role=UserRole.GIANGVIEN
            )

            gv1_user.set_password("123456")

            gv2_user = User(
                username="tranthib",
                hoTen="ThS. Trần Thị B",
                email="tranthib@ou.edu.vn",
                role=UserRole.GIANGVIEN
            )

            gv2_user.set_password("123456")

            gv3_user = User(
                username="leminhc",
                hoTen="TS. Lê Minh C",
                email="leminhc@ou.edu.vn",
                role=UserRole.GIANGVIEN
            )

            gv3_user.set_password("123456")

            # ==================================================
            # SINH VIÊN
            # ==================================================

            sv1 = User(
                username="sinhvien1",
                hoTen="Nguyễn Văn An",
                email="sinhvien1@student.ou.edu.vn",
                role=UserRole.SINHVIEN
            )
            sv1.set_password("123456")

            sv2 = User(
                username="sinhvien2",
                hoTen="Trần Thị Bình",
                email="sinhvien2@student.ou.edu.vn",
                role=UserRole.SINHVIEN
            )
            sv2.set_password("123456")

            sv3 = User(
                username="sinhvien3",
                hoTen="Lê Văn Cường",
                email="sinhvien3@student.ou.edu.vn",
                role=UserRole.SINHVIEN
            )
            sv3.set_password("123456")

            sv4 = User(
                username="sinhvien4",
                hoTen="Phạm Thị Dung",
                email="sinhvien4@student.ou.edu.vn",
                role=UserRole.SINHVIEN
            )
            sv4.set_password("123456")

            sv5 = User(
                username="sinhvien5",
                hoTen="Hoàng Văn Em",
                email="sinhvien5@student.ou.edu.vn",
                role=UserRole.SINHVIEN
            )
            sv5.set_password("123456")

            db.session.add_all([
                admin,
                gv1_user,
                gv2_user,
                gv3_user,
                sv1,
                sv2,
                sv3,
                sv4,
                sv5
            ])

            db.session.flush()

            print("[3] Đã tạo tài khoản mẫu.")

            # ==================================================
            # THÔNG TIN GIẢNG VIÊN
            # ==================================================

            gv1 = GiangVien(
                userId=gv1_user.id,
                hocVi="Tiến sĩ",
                chuyenMon=(
                    "Trí tuệ nhân tạo, Machine Learning, "
                    "Deep Learning, Data Science"
                ),
                linhVucNghienCuu=(
                    "AI, Machine Learning, Deep Learning, NLP"
                ),
                soLuongHuongDanToiDa=10,
                gioiThieu=(
                    "Giảng viên chuyên nghiên cứu về "
                    "trí tuệ nhân tạo và khoa học dữ liệu."
                )
            )

            gv2 = GiangVien(
                userId=gv2_user.id,
                hocVi="Thạc sĩ",
                chuyenMon=(
                    "Công nghệ phần mềm, Phát triển Web, "
                    "Kiến trúc phần mềm"
                ),
                linhVucNghienCuu=(
                    "Web Development, Software Engineering, "
                    "Cloud Computing"
                ),
                soLuongHuongDanToiDa=10,
                gioiThieu=(
                    "Giảng viên chuyên về phát triển "
                    "phần mềm và hệ thống web."
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
                    "Giảng viên chuyên nghiên cứu về "
                    "an toàn và bảo mật hệ thống."
                )
            )

            db.session.add_all([
                gv1,
                gv2,
                gv3
            ])

            # ==================================================
            # LĨNH VỰC NGHIÊN CỨU
            # ==================================================

            print("[4] Đang tạo lĩnh vực nghiên cứu...")

            linh_vuc_ai = LinhVuc(
                tenLinhVuc="Trí tuệ nhân tạo",
                moTa=(
                    "Nghiên cứu về AI, Machine Learning, "
                    "Deep Learning và NLP."
                )
            )

            linh_vuc_web = LinhVuc(
                tenLinhVuc="Công nghệ phần mềm",
                moTa=(
                    "Nghiên cứu phát triển phần mềm "
                    "và hệ thống web."
                )
            )

            linh_vuc_data = LinhVuc(
                tenLinhVuc="Khoa học dữ liệu",
                moTa=(
                    "Phân tích, xử lý và khai thác dữ liệu."
                )
            )

            linh_vuc_security = LinhVuc(
                tenLinhVuc="An toàn thông tin",
                moTa=(
                    "Nghiên cứu bảo mật, an toàn mạng "
                    "và hệ thống."
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

            print("    ✓ Trí tuệ nhân tạo")
            print("    ✓ Công nghệ phần mềm")
            print("    ✓ Khoa học dữ liệu")
            print("    ✓ An toàn thông tin")
            print("    ✓ Phát triển ứng dụng di động")

            # ==================================================
            # CHUYÊN MÔN GIẢNG VIÊN
            # ==================================================

            db.session.add_all([

                GiangVienLinhVuc(
                    giangVienId=gv1_user.id,
                    linhVucId=linh_vuc_ai.id
                ),

                GiangVienLinhVuc(
                    giangVienId=gv1_user.id,
                    linhVucId=linh_vuc_data.id
                ),

                GiangVienLinhVuc(
                    giangVienId=gv2_user.id,
                    linhVucId=linh_vuc_web.id
                ),

                GiangVienLinhVuc(
                    giangVienId=gv2_user.id,
                    linhVucId=linh_vuc_mobile.id
                ),

                GiangVienLinhVuc(
                    giangVienId=gv3_user.id,
                    linhVucId=linh_vuc_security.id
                )

            ])

            # ==================================================
            # ĐỀ TÀI MẪU
            # ==================================================

            danh_sach_de_tai = [

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
                        "chính xác và phù hợp hơn."
                    ),
                    tuKhoa="AI, Semantic Search, NLP",
                    linhVucId=linh_vuc_ai.id,
                    sinhVienId=sv1.id,
                    giangVienId=gv1_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                DeTai(
                    tenDeTai=(
                        "Hệ thống phát hiện đề tài nghiên cứu "
                        "trùng lặp bằng AI"
                    ),
                    moTa=(
                        "Sử dụng trí tuệ nhân tạo để phân tích "
                        "và so sánh mức độ tương đồng giữa "
                        "các đề tài nghiên cứu."
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

                DeTai(
                    tenDeTai=(
                        "Xây dựng chatbot hỗ trợ sinh viên "
                        "bằng trí tuệ nhân tạo"
                    ),
                    moTa=(
                        "Phát triển chatbot sử dụng AI để "
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

                DeTai(
                    tenDeTai=(
                        "Ứng dụng Machine Learning trong "
                        "dự đoán kết quả học tập"
                    ),
                    moTa=(
                        "Sử dụng thuật toán Machine Learning "
                        "để phân tích dữ liệu và dự đoán "
                        "kết quả học tập của sinh viên."
                    ),
                    mucTieu=(
                        "Hỗ trợ sinh viên và nhà trường "
                        "dự đoán kết quả học tập."
                    ),
                    tuKhoa="Machine Learning, Prediction, Student Data",
                    linhVucId=linh_vuc_ai.id,
                    sinhVienId=sv4.id,
                    giangVienId=gv1_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                DeTai(
                    tenDeTai=(
                        "Hệ thống nhận diện khuôn mặt "
                        "bằng Deep Learning"
                    ),
                    moTa=(
                        "Xây dựng hệ thống nhận diện khuôn mặt "
                        "sử dụng mô hình Deep Learning."
                    ),
                    mucTieu=(
                        "Tự động nhận diện và xác thực khuôn mặt."
                    ),
                    tuKhoa="Deep Learning, Face Recognition, AI",
                    linhVucId=linh_vuc_ai.id,
                    sinhVienId=sv5.id,
                    giangVienId=gv1_user.id,
                    trangThai=TrangThaiDeTai.CHO_DUYET
                ),

                DeTai(
                    tenDeTai=(
                        "Xây dựng hệ thống quản lý nghiên cứu "
                        "khoa học trực tuyến"
                    ),
                    moTa=(
                        "Xây dựng website hỗ trợ sinh viên "
                        "quản lý và đăng ký đề tài nghiên cứu "
                        "khoa học."
                    ),
                    mucTieu=(
                        "Số hóa quá trình quản lý đề tài "
                        "nghiên cứu khoa học."
                    ),
                    tuKhoa="Web, Flask, MySQL",
                    linhVucId=linh_vuc_web.id,
                    sinhVienId=sv1.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                DeTai(
                    tenDeTai=(
                        "Xây dựng hệ thống quản lý thư viện số"
                    ),
                    moTa=(
                        "Phát triển hệ thống thư viện trực tuyến "
                        "hỗ trợ quản lý sách và mượn trả sách."
                    ),
                    mucTieu=(
                        "Số hóa và tối ưu hóa việc quản lý thư viện."
                    ),
                    tuKhoa="Flask, MySQL, Library Management",
                    linhVucId=linh_vuc_web.id,
                    sinhVienId=sv2.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                DeTai(
                    tenDeTai=(
                        "Hệ thống quản lý sinh viên trực tuyến"
                    ),
                    moTa=(
                        "Xây dựng website hỗ trợ quản lý thông tin "
                        "và kết quả học tập của sinh viên."
                    ),
                    mucTieu=(
                        "Nâng cao hiệu quả quản lý thông tin sinh viên."
                    ),
                    tuKhoa="Web, Student Management, Flask",
                    linhVucId=linh_vuc_web.id,
                    sinhVienId=sv3.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.CHO_DUYET
                ),

                DeTai(
                    tenDeTai=(
                        "Xây dựng hệ thống quản lý đề tài "
                        "đồ án sinh viên"
                    ),
                    moTa=(
                        "Phát triển hệ thống quản lý đăng ký, "
                        "xét duyệt và theo dõi tiến độ đề tài đồ án."
                    ),
                    mucTieu=(
                        "Hỗ trợ quản lý quy trình thực hiện "
                        "đồ án của sinh viên."
                    ),
                    tuKhoa="Project Management, Web, Flask",
                    linhVucId=linh_vuc_web.id,
                    sinhVienId=sv4.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                DeTai(
                    tenDeTai=(
                        "Hệ thống quản lý lịch làm việc trực tuyến"
                    ),
                    moTa=(
                        "Xây dựng hệ thống hỗ trợ tạo lịch "
                        "và quản lý công việc trực tuyến."
                    ),
                    mucTieu=(
                        "Hỗ trợ người dùng quản lý công việc hiệu quả."
                    ),
                    tuKhoa="Web Application, Calendar, Management",
                    linhVucId=linh_vuc_web.id,
                    sinhVienId=sv5.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.NHAP
                ),

                DeTai(
                    tenDeTai=(
                        "Phân tích dữ liệu học tập của sinh viên"
                    ),
                    moTa=(
                        "Thu thập và phân tích dữ liệu học tập "
                        "để đánh giá kết quả của sinh viên."
                    ),
                    mucTieu=(
                        "Tìm ra các yếu tố ảnh hưởng "
                        "đến kết quả học tập."
                    ),
                    tuKhoa="Data Analysis, Student Data, Python",
                    linhVucId=linh_vuc_data.id,
                    sinhVienId=sv1.id,
                    giangVienId=gv1_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                DeTai(
                    tenDeTai=(
                        "Hệ thống phân tích dữ liệu bán hàng"
                    ),
                    moTa=(
                        "Phân tích dữ liệu bán hàng để hỗ trợ "
                        "doanh nghiệp đưa ra quyết định."
                    ),
                    mucTieu=(
                        "Hỗ trợ dự đoán và tối ưu hoạt động kinh doanh."
                    ),
                    tuKhoa="Data Science, Analytics, Business",
                    linhVucId=linh_vuc_data.id,
                    sinhVienId=sv2.id,
                    giangVienId=gv1_user.id,
                    trangThai=TrangThaiDeTai.CHO_DUYET
                ),

                DeTai(
                    tenDeTai=(
                        "Dự đoán doanh thu bằng Machine Learning"
                    ),
                    moTa=(
                        "Sử dụng Machine Learning để dự đoán "
                        "doanh thu dựa trên dữ liệu lịch sử."
                    ),
                    mucTieu=(
                        "Hỗ trợ doanh nghiệp lập kế hoạch kinh doanh."
                    ),
                    tuKhoa="Machine Learning, Revenue Prediction, Data",
                    linhVucId=linh_vuc_data.id,
                    sinhVienId=sv3.id,
                    giangVienId=gv1_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                DeTai(
                    tenDeTai=(
                        "Xây dựng hệ thống phát hiện xâm nhập mạng"
                    ),
                    moTa=(
                        "Phân tích lưu lượng mạng để phát hiện "
                        "các hành vi truy cập bất thường."
                    ),
                    mucTieu=(
                        "Nâng cao khả năng phát hiện và "
                        "phòng chống tấn công mạng."
                    ),
                    tuKhoa="Cyber Security, Network, IDS",
                    linhVucId=linh_vuc_security.id,
                    sinhVienId=sv4.id,
                    giangVienId=gv3_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                DeTai(
                    tenDeTai=(
                        "Hệ thống quản lý đăng nhập "
                        "và xác thực người dùng"
                    ),
                    moTa=(
                        "Xây dựng hệ thống xác thực người dùng "
                        "và quản lý quyền truy cập."
                    ),
                    mucTieu=(
                        "Nâng cao tính bảo mật của hệ thống."
                    ),
                    tuKhoa="Authentication, Security, User Management",
                    linhVucId=linh_vuc_security.id,
                    sinhVienId=sv5.id,
                    giangVienId=gv3_user.id,
                    trangThai=TrangThaiDeTai.DA_DUYET
                ),

                DeTai(
                    tenDeTai=(
                        "Ứng dụng quản lý chi tiêu cá nhân "
                        "trên điện thoại"
                    ),
                    moTa=(
                        "Phát triển ứng dụng di động giúp người dùng "
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

                DeTai(
                    tenDeTai=(
                        "Ứng dụng đặt lịch khám bệnh trực tuyến"
                    ),
                    moTa=(
                        "Xây dựng ứng dụng hỗ trợ người dùng "
                        "đặt lịch khám và quản lý lịch hẹn."
                    ),
                    mucTieu=(
                        "Giúp người dùng thuận tiện hơn "
                        "trong việc đặt lịch khám."
                    ),
                    tuKhoa="Mobile App, Healthcare, Booking",
                    linhVucId=linh_vuc_mobile.id,
                    sinhVienId=sv2.id,
                    giangVienId=gv2_user.id,
                    trangThai=TrangThaiDeTai.CHO_DUYET
                )

            ]

            db.session.add_all(danh_sach_de_tai)

            # ==================================================
            # COMMIT
            # ==================================================

            db.session.commit()

            # ==================================================
            # KIỂM TRA
            # ==================================================

            print()
            print("=" * 60)
            print("TẠO DATABASE THÀNH CÔNG!")
            print("=" * 60)

            print()
            print(f"Tổng số đề tài: {len(danh_sach_de_tai)}")
            print("Tổng số lĩnh vực: 5")

            print()
            print("TÀI KHOẢN ADMIN")
            print("admin / 123456")

            print()
            print("TÀI KHOẢN GIẢNG VIÊN")
            print("nguyenvana / 123456")
            print("tranthib / 123456")
            print("leminhc / 123456")

            print()
            print("TÀI KHOẢN SINH VIÊN")
            print("sinhvien1 / 123456")
            print("sinhvien2 / 123456")
            print("sinhvien3 / 123456")
            print("sinhvien4 / 123456")
            print("sinhvien5 / 123456")

            print()
            print("LĨNH VỰC:")
            print("1. Trí tuệ nhân tạo")
            print("2. Công nghệ phần mềm")
            print("3. Khoa học dữ liệu")
            print("4. An toàn thông tin")
            print("5. Phát triển ứng dụng di động")

            print()
            print("=" * 60)

        except Exception as e:

            db.session.rollback()

            print()
            print("=" * 60)
            print("LỖI TẠO DATABASE")
            print("=" * 60)
            print(e)

            import traceback
            traceback.print_exc()

            print("=" * 60)