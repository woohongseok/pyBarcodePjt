import sys
import cv2
import glob
import os
import pyzbar.pyzbar as pyzbar
from playsound import playsound
from PyQt5 import uic
from PyQt5.QtCore import QDate, QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QLabel,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import QImage, QPixmap, QFont
import datetime as dt
from pathlib import Path

form_class = uic.loadUiType("barcode.ui")[0]

try:
    # 현재 날자의 폴더 생성
    Path("barcodeTXT").mkdir(parents=True, exist_ok=True)
    barcodeFileName = dt.datetime.now().strftime("%Y%m%d")

    barcodeFolder = Path("barcodeTXT")
    barcodeFolder.mkdir(parents=True, exist_ok=True)

    # 쓰기 권한 부여
    barcodeFolder.chmod(0o777)  # 모든 권한(읽기, 쓰기, 실행)을 부여합니다.

    # 파일 시스템 열기
    f = open("barcodeTXT/" + barcodeFileName + ".txt", "r", encoding="utf8")
    dataList = f.readlines()
except Exception as e:
    dataList = False
else:
    f.close()


# 화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()

        # ui 파일 받아옴
        self.setupUi(self)

        # 검색 클릭 이벤트
        self.searchBtn.clicked.connect(self.onClick)
        self.refreshBtn.clicked.connect(lambda: self.makeLayout(mode="refresh"))

        # LineEdit 엔터 이벤트
        lineEdit = self.inputCode.returnPressed.connect(self.onClick)

        # 현재 날짜
        currentDate = QDate.currentDate()
        self.setDate.setDate(currentDate)

        # camera는 Label임
        self.label = self.camera

        # 100ms마다 update_frame 함수 호출
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(100)

        # 0번 카메라 캡처 객체 생성
        self.cap = cv2.VideoCapture(0)

        # 레이아웃 생성
        self.makeLayout()

        # 바코드가 인식되었는지 여부를 저장할 변수
        self.barcodeDetected = False

        # 바코드 줄 저장
        self.barcodeLine = []

        # 이벤트 처리 함수 연결
        self.actionfind_code_files.triggered.connect(self.on_menu_clicked)

    def on_menu_clicked(self):
        path = os.path.realpath("barcodeTXT")
        os.startfile(path)

    def makeLayout(self, mode="None"):
        if mode == "search":
            if self.barcodeLine:
                # 수직 레이아웃 생성
                layout = QVBoxLayout()

                for line in self.barcodeLine:
                    textEdit = QLabel(line.rstrip(), self)
                    font = QFont("Verdana", 15)
                    textEdit.setFont(font)
                    layout.addWidget(textEdit)

                # 기존 위젯 제거
                old_widget = self.scrollArea.takeWidget()
                if old_widget:
                    old_widget.deleteLater()

                # 위젯 생성 및 레이아웃 설정
                widget = QWidget()
                widget.setLayout(layout)

                # 스크롤 영역에 위젯 설정
                self.scrollArea.setWidget(widget)
                print("makeLayout")
        elif mode == "refresh":
            date = self.setDate.date().toString().split()
            dateFormat = date[3] + date[1] + date[2]
            print(dateFormat)
            try:
                # 파일 시스템 열기
                f = open("barcodeTXT/" + dateFormat + ".txt", "r", encoding="utf8")
                dataList = f.readlines()
                if dataList:
                    # 수직 레이아웃 생성
                    layout = QVBoxLayout()
                    textEdit_list = []

                    for line in dataList:
                        textEdit = QLabel(line.rstrip(), self)
                        font = QFont("Verdana", 15)
                        textEdit.setFont(font)
                        textEdit_list.append(textEdit)

                    # 기존 위젯 제거
                    old_widget = self.scrollArea.takeWidget()
                    if old_widget:
                        old_widget.deleteLater()

                    # 리스트에 있는 모든 textEdit을 레이아웃에 추가
                    for textEdit in textEdit_list:
                        layout.addWidget(textEdit)

                    # 위젯 생성 및 레이아웃 설정
                    widget = QWidget()
                    widget.setLayout(layout)

                    # 스크롤 영역에 위젯 설정
                    self.scrollArea.setWidget(widget)
                print("refresh")
            except Exception as e:
                dataList = False
                QMessageBox.warning(
                    self, "날자에러", "해당 날자의 파일이 없거나 처음 실행됐습니다.", QMessageBox.Ok
                )
                # 현재 날자로 설정
                currentDate = QDate.currentDate()
                self.setDate.setDate(currentDate)
                self.makeLayout(mode=None)
            else:
                f.close()
        else:
            print("else")
            try:
                # 파일 시스템 열기
                f = open("barcodeTXT/" + barcodeFileName + ".txt", "r", encoding="utf8")
                dataList = f.readlines()
            except Exception as e:
                dataList = False
            else:
                f.close()

            if dataList:
                # 수직 레이아웃 생성
                layout = QVBoxLayout()
                textEdit_list = []

                for line in dataList:
                    textEdit = QLabel(line.rstrip(), self)
                    font = QFont("Verdana", 15)
                    textEdit.setFont(font)
                    textEdit_list.append(textEdit)

                # 기존 위젯 제거
                old_widget = self.scrollArea.takeWidget()
                if old_widget:
                    old_widget.deleteLater()

                # 리스트에 있는 모든 textEdit을 레이아웃에 추가
                for textEdit in textEdit_list:
                    layout.addWidget(textEdit)

                # 위젯 생성 및 레이아웃 설정
                widget = QWidget()
                widget.setLayout(layout)

                # 스크롤 영역에 위젯 설정
                self.scrollArea.setWidget(widget)
                print("else")

    def onClick(self):
        date = self.setDate.date().toString().split()
        dateFormat = date[3] + date[1] + date[2]
        text = str(self.inputCode.text())
        self.barcodeLine = []
        if text.isdigit():
            try:
                # 파일 시스템 열기
                f = open("barcodeTXT/" + dateFormat + ".txt", "r", encoding="utf8")
                dataList = f.readlines()
                for line in dataList:
                    if text in line:
                        self.barcodeLine.append(line)
                        self.makeLayout(mode="search")
                        print("onClick")
                if len(self.barcodeLine) == 0:
                    QMessageBox.warning(
                        self, "검색에러", "검색어에 해당하는 데이터가 없습니다.", QMessageBox.Ok
                    )
                    # 현재 날자로 설정
                    currentDate = QDate.currentDate()
                    self.setDate.setDate(currentDate)
                    self.makeLayout(mode="refresh")
                    print(self.barcodeLine)
            except Exception as e:
                dataList = False
                QMessageBox.warning(
                    self, "검색에러", "검색어에 해당하는 데이터가 없습니다.", QMessageBox.Ok
                )
                # 현재 날자로 설정
                currentDate = QDate.currentDate()
                self.setDate.setDate(currentDate)
                self.makeLayout(mode="refresh")
                self.makeLayout(mode=None)
            else:
                f.close()
        else:
            QMessageBox.warning(self, "숫자에러", "오직 숫자만 입력이 가능합니다.", QMessageBox.Ok)

    # 카메라 기능
    def updateFrame(self):
        # boolean ret 제대로 읽었는지
        # frame 그 자체를 말함
        ret, frame = self.cap.read()
        if ret:
            # 바코드 인식
            barcodeDecode = pyzbar.decode(frame)

            # obj는 디코딩 하여 반환된 객체
            for obj in barcodeDecode:
                codeNum = obj.data.decode("utf-8")
                # 소리 출력
                playsound("./qrbarcode_beep.mp3")

                # 레이아웃 실행
                self.makeLayout()

                # 현재 날자로 설정
                currentDate = QDate.currentDate()
                self.setDate.setDate(currentDate)
                self.makeLayout(mode="refresh")

                # 텍스트 파일에 추가
                with open(
                    "barcodeTXT/" + barcodeFileName + ".txt", "a", encoding="utf8"
                ) as f:
                    saveData = (
                        codeNum
                        + " "
                        + dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                        + "\n"
                    )
                    f.write(saveData)

                # dataList 업데이트
                self.updateDataList()

                # layout 업데이트
                self.makeLayout()

            # 영상송출을 위한 코드
            # openCV는 BGR로 읽어오기 때문에 RGB로 변환하여 PyQt5에 전달
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            # QPixmap으로 변환
            pixmap = QPixmap.fromImage(q_image)
            # aspectRatioMode 영상 비율을 640 480 으로 유지
            self.label.setPixmap(pixmap.scaled(640, 480, aspectRatioMode=True))

    def updateDataList(self):
        # 파일 시스템 열기
        try:
            f = open("barcodeTXT/" + barcodeFileName + ".txt", "r", encoding="utf8")
            self.dataList = f.readlines()
        except Exception as e:
            self.dataList = []

        if self.dataList:
            f.close()


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    # WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    myWindow.show()

    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()
