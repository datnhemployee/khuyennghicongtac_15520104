# ĐỀ TÀI: Khuyến Nghị Cộng tác dựa trên tiếp cận học sâu
**Trường:** Đại học Công Nghệ Thông Tin - Đại học Quốc gia Hồ Chí Minh

**Lớp:** SE505.K21 (Khóa luận tốt nghiệp)

**Giảng viên hướng dẫn:** TS. Huỳnh Ngọc Tín

**Nhóm sinh viên thực hiện:** Nguyễn Hữu Đạt - 15520104

**Khởi động chương trình minh họa:** python src/main.py

**Ghi chú:** 
Do Github không cho phép đăng tệp có kích thước hơn 100MB nên bạn đọc vui lòng tải mô hình đã huấn luyện tại [Google Drive](https://drive.google.com/file/d/122n-UZNBmxoKSiVoixZBPfVCByPvf4Y1/view?usp=sharing) và đặt vào thư mục public/. 

**Tài liệu:** 

 -[Báo cáo docx](https://drive.google.com/file/d/1IzdFMSYUda5PmjjVrTmbfTPRqW0NSzDM/view?usp=sharing)
 
 -[Hướng dẫn sử dụng](https://drive.google.com/file/d/1WhpDVFGPHhlU1LxVVMWa5kPtQmTuv7Gp/view?usp=sharing)
 
 -[Báo cáo pptx](https://drive.google.com/file/d/1V-Xo2Nn-t7QKxX8G1EdzwfQhbsk4BYGJ/view?usp=sharing)

## Giới thiệu đề tài
 Trong nghiên cứu khoa học, việc cộng tác đem lại nhiều lợi ích cho các nhà nghiên cứu khi chung tay thực hiện công trình nghiên cứu của mình. Dần theo thời gian, kho dữ liệu bài báo khoa học trở nên khổng lồ và kích thước tăng đáng kể. Do đó, bài toán khuyến nghị cộng tác dần nhận được quan tâm bởi các nhà khoa học. Và cũng theo xu hướng, sự ra đời phương pháp học sâu Node2vec cũng đang nhận được nhiều sự quan tâm của các nhà nghiên cứu. Nhất là các nghiên cứu viên nghiên cứu đề tài trong lĩnh vực khoa học máy tính. Bản thân Node2vec cũng có một số công trình nghiên cứu kế thừa nhằm giải quyết thách thức và khó khăn mà Node2vec còn bỏ ngỏ. Việc khuyến nghị cộng tác dựa trên tiếp cận học sâu Node2vec sẽ giúp hỗ trợ cộng đồng học thuật trong việc nghiên cứu ứng dụng của Node2vec. Đồng thời, việc so sánh Node2vec với một số phương pháp truyền thống khi giải quyết bài toán khuyến  nghị cộng tác sẽ làm nổi bật ưu nhược điểm của Node2vec so với các phương pháp truyền thống. Nhờ vào đó, các nghiên cứu viên/ nhà phát triển có thể chọn lựa sử dụng giữa Node2vec và phương pháp truyền thống trong khuyến nghị cộng tác.

## Ứng dụng minh họa: weCoNet 
 Nhằm để hiện thực hóa kết quả đầu ra sau khi huấn luyện mô hình Node2vec, em xây dựng phần mềm weCoNet nhằm thực hiện khuyến nghị Top10 nghiên cứu viên cho từng nghiên cứu viên trong tập gồm 319,247 nghiên cứu viên dựa trên mô hình Node2vec đã học được từ mạng đồng tác giả cho trước (mô tả trong Báo cáo Khóa Luận Tốt Nghiệp Khuyến Nghị Cộng Tác Dựa Trên Tiếp Cận Học Sâu). 

**Youtube**
Xem thêm trình chiếu sử dụng phần mềm weCoNet tại: [Youtube](https://youtu.be/RgFHcHSJoew)

**Tập dữ liệu**

| Tên | Số liên kết cộng tác | Thời gian xét | Số nghiên cứu viên | 
|--------------|-------|-------|-------|
| [Huấn luyện](https://raw.githubusercontent.com/datnhemployee/khuyennghicongtac_15520104/master/public/prior_graph.csv) | 1,042,092 | 2014-2015 | 319,247  | 
| [Đánh giá](https://github.com/datnhemployee/khuyennghicongtac_15520104/blob/master/public/test_graph.csv) | 290,502 | 2016 |  114,327  | 

**Chức năng**
+ Xem danh sách khuyến nghị: Phần mềm sẽ cho xem danh sách khuyến nghị Top10 của 1 nghiên cứu viên bất kì từ tập huấn luyện
+ Xem kết quả khuyến nghị: Phần mềm sẽ cho xem kết quả khuyến nghị của từng khuyến nghị. Cụ thể như sau:

| Kí hiệu | Mô tả |
|--------------|-------|
| True-positive | Nghiên cứu viên và ứng viên cộng tác thực sự cộng tác năm 2016 |
| False-positive | Nghiên cứu viên và ứng viên cộng tác KHÔNG cộng tác năm 2016 |
| Acquantaince |  Nghiên cứu viên và ứng viên cộng tác có cộng tác năm 2014-2015 |
  
**Công nghệ** 
 - [Python](https://www.python.org/) *phiên bản 3.7.3*

**Cơ sở dữ liệu** 
 - [Neo4j](https://neo4j.com/developer/) 

**Thư viện**
| Thư viện | Phiên bản | Trang chủ |
|--------------|-------|-------|
| Networkx | 2.2 | [Trang chủ](https://networkx.github.io/) |
| Numpy | 1.15.1 | [Trang chủ](https://numpy.org/doc/stable/) |
| Py2neo | 4.3.0 | [Trang chủ](https://py2neo.org/v4/database.html) |
| Tkinter |-------| [Trang chủ](https://docs.python.org/3.7/library/tkinter.html#tkinter-modules) |

**Thư mục**
| Tên | Ý nghĩa | Đường dẫn |
|--------------|-------|-------|
| src/components | Những thành phần dùng để hiển thị trên màn hình | [Đường dẫn](https://github.com/datnhemployee/khuyennghicongtac_15520104/tree/master/src/components) |
| src/controllers | Xử lý logic giữa phần mềm và cơ sở dữ liệu | [Đường dẫn](https://github.com/datnhemployee/khuyennghicongtac_15520104/tree/master/src/controllers) |
| src/models | Các thuật toán khuyến nghị cộng tác | [Đường dẫn](https://github.com/datnhemployee/khuyennghicongtac_15520104/tree/master/src/models) |
| src/screens | Các màn hình | [Đường dẫn](https://github.com/datnhemployee/khuyennghicongtac_15520104/tree/master/src) |
| src/services | Tương tác cơ sở dữ liệu | [Đường dẫn](https://github.com/datnhemployee/khuyennghicongtac_15520104/tree/master/src/services) |
| src/utils | Công cụ hỗ trợ khác: Thời gian, kết nối CSDL, ... | [Đường dẫn](https://github.com/datnhemployee/khuyennghicongtac_15520104/tree/master/src/utils) |

**Thuật toán khuyến nghị**
| Thuật toán | Mô tả | Mã nguồn |
|--------------|-------|-------|
| Node2vec | Tham khảo từ [trang nguồn](https://github.com/aditya-grover/node2vec) | [node2vec.py](https://github.com/datnhemployee/khuyennghicongtac_15520104/blob/master/src/models/node2vec.py) |
| Content-based | Xem Chương 2 [Báo cáo docx](https://drive.google.com/file/d/1IzdFMSYUda5PmjjVrTmbfTPRqW0NSzDM/view?usp=sharing) | [node2vec.py](https://github.com/datnhemployee/khuyennghicongtac_15520104/blob/master/src/models/content_based.py) |
| Adamic Adar | Xem Chương 2  [Báo cáo docx](https://drive.google.com/file/d/1IzdFMSYUda5PmjjVrTmbfTPRqW0NSzDM/view?usp=sharing) | [adamic.py](https://github.com/datnhemployee/khuyennghicongtac_15520104/blob/master/src/models/adamic.py) |
| Jaccard Coefficient | Xem Chương 2 [Báo cáo docx](https://drive.google.com/file/d/1IzdFMSYUda5PmjjVrTmbfTPRqW0NSzDM/view?usp=sharing) | [jaccard.py](https://github.com/datnhemployee/khuyennghicongtac_15520104/blob/master/src/models/jaccard.py) |
| Common Neighbors | Xem Chương 2 [Báo cáo docx](https://drive.google.com/file/d/1IzdFMSYUda5PmjjVrTmbfTPRqW0NSzDM/view?usp=sharing) | [common_neighbor.py](https://github.com/datnhemployee/khuyennghicongtac_15520104/blob/master/src/models/common_neighbor.py) |


**Kết quả thực nghiệm: **
| Thuật toán | Precision | Recall | F-Measure |
|--------------|-------|-------|-------|
| Content-based | 0.36 | 0.35 | 0.33 |
| Common Neighbors | 0.19|  0.33 | 0.24 |
| Adamic Adar | 0.2  | 0.35 | 0.25 |
| Jaccard Coefficient | 0.17 | 0.29 | 0.21 |
| Node2vec | 0.17  | 0.35 | 0.23 |
