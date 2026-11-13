# Volcanic eruption prediction

Dự đoán thời gian còn lại đến lần phun trào kế tiếp của một núi lửa từ tín hiệu địa chấn, theo bộ dữ liệu của Viện Địa vật lý và Núi lửa Quốc gia Ý. Mỗi thuật ngữ dưới đây ghi tên tiếng Anh dùng trong mã, kèm định nghĩa tiếng Việt.

## Language

### Dữ liệu

**Segment** (phân đoạn):
Một bản ghi liên tục dài 10 phút của 10 cảm biến quanh một núi lửa, có một mã số riêng. Các phân đoạn không nối tiếp nhau về thời gian.
_Avoid_: sample, record, file

**Sensor** (cảm biến):
Một trong 10 máy đo địa chấn ghi tín hiệu của một phân đoạn, đánh số từ 1 đến 10. Một cảm biến có thể thiếu dữ liệu trong một phần hoặc toàn bộ phân đoạn.
_Avoid_: channel, station

**Time to eruption** (thời gian đến lúc phun trào):
Khoảng thời gian từ cuối một phân đoạn đến lần phun trào kế tiếp, tính bằng phần trăm giây. Đây là đại lượng cần dự đoán.
_Avoid_: target, label, time to failure

### Tín hiệu

**Frequency band** (dải tần):
Một khoảng tần số ứng với một loại hoạt động địa chấn của núi lửa. Có năm dải: A, BH, BL, C và D.
_Avoid_: frequency range, bin

**Band A** (dải A):
Từ 10 Hz trở lên. Động đất do đá quanh buồng mắc-ma và ống dẫn bị phá vỡ.

**Band BH** (dải BH):
Từ 5 đến 8 Hz. Động đất do mắc-ma xâm nhập và phá vỡ ống dẫn.

**Band BL** (dải BL):
Từ 1,5 đến 2,5 Hz. Động đất quanh ống dẫn do khí thoát ra khỏi miệng núi lửa trước khi phun nổ.

**Band C** (dải C):
Từ 0,5 đến 1,2 Hz. Chấn động do áp suất khí trong khoang tăng lên, đi kèm dải BH.

**Band D** (dải D):
Từ 2 đến 4 Hz. Chấn động do khí phụt ra, đi kèm dải BL.

**Band feature** (đặc trưng dải tần):
Một con số tóm tắt hoạt động của một cảm biến trong một dải tần trên toàn bộ phân đoạn. Mỗi cặp cảm biến và dải tần có hai đặc trưng: cường độ (`pow`) và số lần vượt ngưỡng (`num`).
_Avoid_: statistic, signal feature

**Feature table** (bảng đặc trưng):
Bảng có một hàng cho mỗi phân đoạn, gồm mã số phân đoạn và toàn bộ đặc trưng dải tần của 10 cảm biến.
_Avoid_: feature set, dataset, train set

### Đánh giá

**Validation error** (sai số kiểm định):
Căn của sai số bình phương trung bình giữa thời gian đến lúc phun trào dự đoán và thực tế, đo trên những phân đoạn không dùng để huấn luyện.
_Avoid_: score, loss
