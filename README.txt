HƯỚNG DẪN CÀI ĐẶT VÀ VẬN HÀNH HỆ THỐNG
HỆ THỐNG QUẢN LÝ NGHIÊN CỨU KHOA HỌC TÍCH HỢP AI


1. GIỚI THIỆU

Đây là project xây dựng hệ thống quản lý nghiên cứu khoa học bằng Python
và Flask.

Hệ thống hỗ trợ quản lý đề tài nghiên cứu, sinh viên, giảng viên và cán bộ
quản lý.

Các chức năng chính của hệ thống:
- Đăng ký và đăng nhập tài khoản.
- Quản lý đề tài nghiên cứu.
- Đăng ký đề tài.
- Theo dõi tiến độ thực hiện đề tài.
- Tìm kiếm đề tài.
- Tìm kiếm đề tài theo ngữ nghĩa.
- Kiểm tra mức độ tương đồng giữa các đề tài.
- Gợi ý giảng viên hướng dẫn.
- Phê duyệt và quản lý đề tài.


2. CÔNG NGHỆ SỬ DỤNG

- Python
- Flask
- MySQL
- SQLAlchemy
- Flask-Login
- PyMySQL
- Sentence Transformers
- Scikit-learn
- HTML/CSS/JavaScript
- Bootstrap
- PyCharm


3. CẤU TRÚC PROJECT

Các file và thư mục chính:

- index.py
  File chạy chính của hệ thống.
  Chứa mã nguồn chính của hệ thống.

- __init__.py
  Khởi tạo Flask, cấu hình cơ sở dữ liệu và các thành phần liên quan.

- models.py
  Khai báo các model của cơ sở dữ liệu.

- dao.py
  Chứa các hàm truy vấn và xử lý dữ liệu.

- schemas.py
  Chứa các schema được sử dụng trong hệ thống.

- templates/
  Chứa các file giao diện HTML.

- static/
  Chứa CSS, JavaScript và các tài nguyên giao diện.

- requirements.txt
  Danh sách các thư viện Python cần cài đặt.

- README.txt
  Tài liệu hướng dẫn cài đặt và vận hành hệ thống.


4. PHẦN MỀM CẦN THIẾT

Để chạy được project cần cài đặt:

- Python
- PyCharm
- MySQL Server
- MySQL Workbench
- Trình duyệt web


5. MỞ PROJECT

Bước 1:
Mở PyCharm.

Bước 2:
Chọn:

File -> Open

Bước 3:
Chọn thư mục project.

Ví dụ:

C:\Users\thain\PycharmProjects\DoAnNganh

Bước 4:
Sau khi project được mở, kiểm tra các file chính của project như:

index.py
__init__.py
models.py
dao.py
schemas.py
requirements.txt


6. TẠO MÔI TRƯỜNG ẢO

Trong PyCharm chọn:

File -> Settings -> Project -> Python Interpreter

Sau đó chọn:

Add Interpreter -> Add Local Interpreter -> Virtualenv

Tạo môi trường ảo với tên:

.venv

Sau khi tạo xong, mở Terminal trong PyCharm.

Nếu môi trường được chọn đúng, Terminal sẽ hiển thị dạng:

(.venv) PS C:\Users\thain\PycharmProjects\DoAnNganh>


7. CÀI ĐẶT THƯ VIỆN

Mở Terminal trong PyCharm và chạy lệnh:

python -m pip install -r requirements.txt

Chờ quá trình cài đặt hoàn tất.

Có thể kiểm tra các thư viện đã cài đặt bằng lệnh:

pip freeze


8. CẤU HÌNH MYSQL

Project sử dụng MySQL làm cơ sở dữ liệu.

Thông tin kết nối MySQL được cấu hình trong file:

__init__.py

Trước khi chạy hệ thống cần đảm bảo MySQL Server đang hoạt động.

Mở MySQL Workbench và kiểm tra kết nối MySQL.

Trong file __init__.py cần kiểm tra các thông tin kết nối như:

- Tên database.
- Tên tài khoản MySQL.
- Mật khẩu MySQL.
- Địa chỉ máy chủ.
- Cổng kết nối.

Ví dụ:

SQLALCHEMY_DATABASE_URI =  "mysql+pymysql://root:1234@localhost/doannganhdb?charset=utf8mb4"

Nếu chạy project trên máy tính khác, cần thay đổi thông tin kết nối
MySQL trong __init__.py cho phù hợp với máy đang sử dụng.


9. KHỞI TẠO DATABASE

Sau khi cài đặt MySQL, cần tạo database tương ứng với tên database được
cấu hình trong file __init__.py.

Có thể thực hiện bằng MySQL Workbench.

Bước 1:
Mở MySQL Workbench.

Bước 2:
Đăng nhập vào MySQL Server.

Bước 3:
Tạo database theo tên được cấu hình trong project.

Bước 4:
Kiểm tra database đã được tạo thành công.

Bước 5:
Đảm bảo tài khoản MySQL được sử dụng trong __init__.py có quyền truy cập
vào database.


10. CHẠY PROJECT

Sau khi đã cài đặt thư viện và cấu hình MySQL, thực hiện các bước sau:

Bước 1:
Mở project bằng PyCharm.

Bước 2:
Đảm bảo Terminal đang sử dụng môi trường:

(.venv)

Bước 3:
Đảm bảo MySQL Server đang hoạt động.

Bước 4:
Kiểm tra thông tin kết nối MySQL trong:

__init__.py

Bước 5:
Trong PyCharm tìm file:

index.py

Bước 6:
Nhấp chuột phải vào file:

index.py

Bước 7:
Chọn:

Run 'index'

Bước 8:
Chờ chương trình khởi động.

Nếu Flask chạy thành công, Terminal sẽ hiển thị địa chỉ truy cập hệ thống.

Ví dụ:

http://127.0.0.1:5000

Bước 9:
Mở trình duyệt Chrome và truy cập địa chỉ được hiển thị trong Terminal.


11. CÁCH CHẠY PROJECT NHỮNG LẦN SAU

Sau khi project đã được cài đặt đầy đủ, những lần sau chỉ cần:

1. Mở PyCharm.
2. Mở thư mục project.
3. Bật MySQL Server.
4. Kiểm tra môi trường .venv.
5. Kiểm tra kết nối MySQL trong __init__.py.
6. Mở file models.py.
7. Chọn Run 'models'.
8. Mở file index.py.
9. Chọn Run 'index'.
10. Mở địa chỉ localhost trên trình duyệt.


12. CÁC FILE KHÔNG CẦN CHẠY RIÊNG

Không cần chạy riêng các file:

- __init__.py
- dao.py
- schemas.py

Các file trên được hệ thống import và sử dụng trong quá trình chạy
chương trình.

File chạy chính của project là:

index.py


13. CÁC CHỨC NĂNG CHÍNH

13.1. Sinh viên

- Đăng ký tài khoản.
- Đăng nhập.
- Tìm kiếm đề tài.
- Xem thông tin đề tài.
- Đăng ký đề tài.
- Theo dõi tiến độ đề tài.
- Tìm kiếm đề tài theo ngữ nghĩa.
- Kiểm tra mức độ tương đồng.
- Nhận gợi ý giảng viên hướng dẫn.


13.2. Giảng viên

- Đăng nhập.
- Xem các đề tài được phân công.
- Theo dõi đề tài.
- Hỗ trợ sinh viên trong quá trình thực hiện đề tài.


13.3. Cán bộ quản lý

- Quản lý đề tài.
- Kiểm tra đề tài.
- Phê duyệt đề tài.
- Theo dõi tiến độ.
- Kiểm tra mức độ tương đồng giữa các đề tài.
- Xem kết quả gợi ý giảng viên.


14. CHỨC NĂNG AI

14.1. Tìm kiếm ngữ nghĩa

Hệ thống sử dụng Sentence Transformers để xử lý nội dung đề tài thành
vector và tìm kiếm các đề tài có nội dung tương đồng với nội dung người
dùng nhập vào.

Kết quả tìm kiếm được sắp xếp theo mức độ tương đồng.


14.2. Kiểm tra mức độ tương đồng

Hệ thống sử dụng Embedding và Cosine Similarity để tính mức độ tương đồng
giữa các đề tài.

Kết quả được sử dụng để hỗ trợ người quản lý kiểm tra các đề tài có nội
dung tương tự.

Điểm tương đồng không tự động kết luận hai đề tài là trùng lặp.


14.3. Gợi ý giảng viên

Hệ thống dựa trên lĩnh vực của đề tài và các thông tin liên quan để tính
mức độ phù hợp của giảng viên.

Sau đó hệ thống đưa ra danh sách giảng viên được gợi ý để tham khảo.


15. KIỂM THỬ HỆ THỐNG

Các chức năng chính được kiểm thử gồm:

- Đăng nhập.
- Đăng ký đề tài.
- Phê duyệt đề tài.
- Theo dõi tiến độ.
- Tìm kiếm ngữ nghĩa.
- Kiểm tra mức độ tương đồng.
- Gợi ý giảng viên hướng dẫn.

Khi kiểm thử cần kiểm tra cả kết quả hiển thị trên giao diện và dữ liệu
được lưu trong cơ sở dữ liệu.


16. XỬ LÝ MỘT SỐ LỖI THƯỜNG GẶP

Nếu xuất hiện lỗi:

ModuleNotFoundError

Thực hiện:

python -m pip install -r requirements.txt


Nếu không kết nối được MySQL:

- Kiểm tra MySQL Server đã được bật chưa.
- Kiểm tra username MySQL.
- Kiểm tra password MySQL.
- Kiểm tra tên database.
- Kiểm tra port MySQL.
- Kiểm tra thông tin kết nối trong __init__.py.


Nếu Flask không chạy:

- Kiểm tra Terminal có đang sử dụng .venv không.
- Kiểm tra file index.py.
- Kiểm tra các thông báo lỗi trong Terminal.
- Kiểm tra kết nối MySQL.


17. LƯU Ý

- Phải bật MySQL Server trước khi chạy hệ thống.
- Phải cài đặt requirements.txt trước khi chạy project.
- Phải cấu hình đúng thông tin MySQL trong __init__.py.
- Chạy riêng models.py
- File chạy chính của hệ thống là index.py.
- Không nên đưa mật khẩu MySQL hoặc các thông tin bảo mật lên GitHub.


