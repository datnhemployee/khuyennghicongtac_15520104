# XiQuap
**Lớp:** SE505.K21 (Khóa luận tốt nghiệp)

**Lecturer:** TS. Huỳnh Ngọc Tín

**Setup:** [Download]()

**Tài liệu:** [Read online]()

## Giới thiệu
 Trong nghiên cứu khoa học, việc cộng tác đem lại nhiều lợi ích cho các nhà nghiên cứu khi chung tay thực hiện công trình nghiên cứu của mình. Dần theo thời gian, kho dữ liệu bài báo khoa học trở nên khổng lồ và kích thước tăng đáng kể. Do đó, bài toán khuyến nghị cộng tác dần nhận được quan tâm bởi các nhà khoa học. Và cũng theo xu hướng, sự ra đời phương pháp học sâu Node2vec cũng đang nhận được nhiều sự quan tâm của các nhà nghiên cứu. Nhất là các nghiên cứu viên nghiên cứu đề tài trong lĩnh vực khoa học máy tính. Bản thân Node2vec cũng có một số công trình nghiên cứu kế thừa nhằm giải quyết thách thức và khó khăn mà Node2vec còn bỏ ngỏ. Việc khuyến nghị cộng tác dựa trên tiếp cận học sâu Node2vec sẽ giúp hỗ trợ cộng đồng học thuật trong việc nghiên cứu ứng dụng của Node2vec. Đồng thời, việc so sánh Node2vec với một số phương pháp truyền thống khi giải quyết bài toán khuyến  nghị cộng tác sẽ làm nổi bật ưu nhược điểm của Node2vec so với các phương pháp truyền thống. Nhờ vào đó, các nghiên cứu viên/ nhà phát triển có thể chọn lựa sử dụng giữa Node2vec và phương pháp truyền thống trong khuyến nghị cộng tác.
 
## Công nghệ và môi trường
**Công nghệ** 
 - [Python](https://www.python.org/) *phiên bản 3.7.3*

**Cơ sở dữ liệu** 
 - [Neo4j](https://neo4j.com/developer/) 

**Dependencies**
| Dependency | Version | Link |
|--------------|-------|-------|
| Networkx | 2.2 | [Homepage](https://networkx.github.io/) |
| Numpy | 1.15.1 | [Homepage](https://numpy.org/doc/stable/) |
| Py2neo | 4.3.0 | [Homepage](https://py2neo.org/v4/database.html) |
| Tkinter |-------| [Homepage](https://docs.python.org/3.7/library/tkinter.html#tkinter-modules) |


**Thuật toán khuyến nghị**
| Thuật toán | Mô tả |
|--------------|-------|
| Node2vec | Tham khảo từ [Homepage](https://github.com/aditya-grover/node2vec) |
| Content-based | Mỗi hồ sơ người dùng là vectơ đặc trưng với mỗi phần tử mang giá trị trong tập {0,1} với 1 tại vị trí những bài báo được công bố bởi người dùng đó|
| Adamic-Adar | Tham khảo từ [Homepage](https://networkx.github.io/documentation/networkx-1.10/reference/generated/networkx.algorithms.link_prediction.adamic_adar_index.html)|
| Jaccard Coefficient | Tham khảo từ [Homepage](https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.algorithms.link_prediction.jaccard_coefficient.html)|
| Common Neighbors | sử dụng Networkx tìm breadthfirst neighbor của 2 hop từ mỗi nút và lấy common neighbors|
