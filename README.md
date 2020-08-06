# XiQuap
**Trường:** Đại học Công Nghệ Thông Tin - Đại học Quốc gia Hồ Chí Minh

**Lớp:** SE505.K21 (Khóa luận tốt nghiệp)

**Giảng viên hướng dẫn:** TS. Huỳnh Ngọc Tín

**Nhóm sinh viên thực hiện:** Nguyễn Hữu Đạt - 15520104

**Khởi động chương trình demo:** python src/main.py

**Tài liệu:** 

 -[Báo cáo docx](https://drive.google.com/file/d/1qtW4-EopPExuZQ-HbrL4VEooSL_2MOq7/view?usp=sharing)
 
 -[Hướng dẫn sử dụng](https://drive.google.com/file/d/1NEpGDwKX6g5ZSnEf15R1P8_swls0Avdq/view?usp=sharing)
 
 -[Báo cáo pptx](https://drive.google.com/file/d/1704SV3O3eWeqpz-ONEbQtXOIKzyfm-gJ/view?usp=sharing)

## Giới thiệu đề tài
 Trong nghiên cứu khoa học, việc cộng tác đem lại nhiều lợi ích cho các nhà nghiên cứu khi chung tay thực hiện công trình nghiên cứu của mình. Dần theo thời gian, kho dữ liệu bài báo khoa học trở nên khổng lồ và kích thước tăng đáng kể. Do đó, bài toán khuyến nghị cộng tác dần nhận được quan tâm bởi các nhà khoa học. Và cũng theo xu hướng, sự ra đời phương pháp học sâu Node2vec cũng đang nhận được nhiều sự quan tâm của các nhà nghiên cứu. Nhất là các nghiên cứu viên nghiên cứu đề tài trong lĩnh vực khoa học máy tính. Bản thân Node2vec cũng có một số công trình nghiên cứu kế thừa nhằm giải quyết thách thức và khó khăn mà Node2vec còn bỏ ngỏ. Việc khuyến nghị cộng tác dựa trên tiếp cận học sâu Node2vec sẽ giúp hỗ trợ cộng đồng học thuật trong việc nghiên cứu ứng dụng của Node2vec. Đồng thời, việc so sánh Node2vec với một số phương pháp truyền thống khi giải quyết bài toán khuyến  nghị cộng tác sẽ làm nổi bật ưu nhược điểm của Node2vec so với các phương pháp truyền thống. Nhờ vào đó, các nghiên cứu viên/ nhà phát triển có thể chọn lựa sử dụng giữa Node2vec và phương pháp truyền thống trong khuyến nghị cộng tác.

## Phần mềm demo
 Nhằm để hiện thực hóa kết quả đầu ra sau khi huấn luyện mô hình Node2vec, em xây dựng phần mềm weCoNet nhằm thực hiện khuyến nghị Top10 nghiên cứu viên cho từng nghiên cứu viên trong tập gồm 319,247 nghiên cứu viên dựa trên mô hình Node2vec đã học được từ mạng đồng tác giả cho trước (mô tả trong Báo cáo Khóa Luận Tốt Nghiệp Khuyến Nghị Cộng Tác Dựa Trên Tiếp Cận Học Sâu). Ngoài ra, đính kèm là thuật toán huấn luyện Node2vec, Common Neighbors, Jaccard Coefficient và Adamic Adar nhằm phục vụ cộng đồng học thuật trong cách huấn luyện và đánh giá một số thuật toán khuyến nghị phổ biến và State-of-the-art, Node2vec.
 
## Công nghệ và môi trường
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
| src/controllers | Xử lý logic giữa phần mềm và cơ sở dữ liệu | [Homepage](https://github.com/datnhemployee/khuyennghicongtac_15520104/tree/master/src/controllers) |
| src/models | Các thuật toán khuyến nghị cộng tác | [Homepage](https://github.com/datnhemployee/khuyennghicongtac_15520104/tree/master/src/models) |
| src/screens | Các màn hình | [Homepage](https://github.com/datnhemployee/khuyennghicongtac_15520104/tree/master/src) |
| src/services | Tương tác cơ sở dữ liệu | [Homepage](https://github.com/datnhemployee/khuyennghicongtac_15520104/tree/master/src/services) |
| src/utils | Công cụ hỗ trợ khác: Thời gian, kết nối CSDL, ... | [Homepage](https://github.com/datnhemployee/khuyennghicongtac_15520104/tree/master/src/utils) |

**Thuật toán khuyến nghị**
| Thuật toán | Mô tả | Mã nguồn |
|--------------|-------|-------|
| Node2vec | Tham khảo từ [Homepage](https://github.com/aditya-grover/node2vec) | [node2vec.py](https://github.com/datnhemployee/khuyennghicongtac_15520104/blob/master/src/models/node2vec.py) |
| Content-based | Mỗi hồ sơ người dùng là vectơ đặc trưng với mỗi phần tử mang giá trị trong tập {0,1} với 1 tại vị trí những bài báo được công bố bởi người dùng đó| [content_based.py](https://github.com/datnhemployee/khuyennghicongtac_15520104/blob/master/src/models/content_based.py)
| Adamic-Adar | Tham khảo từ [Homepage](https://networkx.github.io/documentation/networkx-1.10/reference/generated/networkx.algorithms.link_prediction.adamic_adar_index.html)| [adamic.py](https://github.com/datnhemployee/khuyennghicongtac_15520104/blob/master/src/models/adamic.py) |
| Jaccard Coefficient | Tham khảo từ [Homepage](https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.algorithms.link_prediction.jaccard_coefficient.html)| [jaccard.py](https://github.com/datnhemployee/khuyennghicongtac_15520104/blob/master/src/models/jaccard.py) |
| Common Neighbors | sử dụng Networkx tìm breadthfirst neighbor của 2 hop từ mỗi nút và lấy common neighbors| [common_neghbor.py](https://github.com/datnhemployee/khuyennghicongtac_15520104/blob/master/src/models/common_neighbor.py) |
