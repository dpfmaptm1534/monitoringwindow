# 🖥️ Universal Screen Monitor (OCR & Color Watcher)

<p align="center">
<img src="[https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white](https://www.google.com/search?q=https://img.shields.io/badge/Python-3.8%2B-3776AB%3Flogo%3Dpython%26logoColor%3Dwhite)">
<img src="[https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?logo=opencv&logoColor=white](https://www.google.com/search?q=https://img.shields.io/badge/OpenCV-Computer%2520Vision-5C3EE8%3Flogo%3Dopencv%26logoColor%3Dwhite)">
<img src="[https://img.shields.io/badge/Tesseract-OCR-green](https://www.google.com/search?q=https://img.shields.io/badge/Tesseract-OCR-green)">
</p>

**Universal Screen Monitor**는 API 접근이 불가능한 원격 데스크톱(RDP), 레거시 프로그램, 게임, 주식 차트 등의 화면을 실시간으로 감시하는 **비전 기반(Vision-based) 모니터링 도구**입니다.

사용자가 지정한 화면 영역(ROI)의 **숫자, 텍스트, 색상 변화**를 감지하여 설정된 조건(임계값 초과, 텍스트 변경 등)을 만족할 경우 즉각적인 시청각 알림을 제공합니다.

<img width="893" height="394" alt="image" src="https://github.com/user-attachments/assets/9e8f62fd-dca4-451a-b1d3-d33018796bca" />
<img width="400" height="224" alt="image" src="https://github.com/user-attachments/assets/2050c812-d61c-42fb-8554-f2f93a56c487" />


---

## ✨ Key Features (주요 기능)

* **🔍 만능 감시 (OCR & Color):**
* **OCR 모드:** Tesseract 엔진을 사용하여 화면 속 숫자와 텍스트를 실시간으로 읽어냅니다.
* **색상 감지 모드:** 신호등, 상태바 등 텍스트가 없는 영역의 색상 변화를 감지합니다.


* **🎯 직관적인 영역 설정 (ROI Selection):**
* 마우스 드래그만으로 감시할 영역을 손쉽게 지정할 수 있습니다.
* 타겟 윈도우가 이동하더라도 감시 영역이 창을 따라 자동으로 보정됩니다.


* **⚙️ 강력한 조건 설정:**
* **숫자:** 초과(`>`), 미만(`<`), 일치(`=`), 범위 이탈(`Out of Range`)
* **텍스트:** 포함(`Contains`), 불일치(`Not Equal`)
* **색상:** 변화 감지(`Change Detection`)


* **🚨 듀얼 알림 시스템:**
* **화면 오버레이:** 작업 중에도 놓치지 않도록 최상위 레이어에 **붉은색 경고 팝업**을 띄웁니다.
* **사운드 알림:** 조건 만족 시 경고음(Beep)을 출력합니다 (ON/OFF 가능).


* **🛡️ 충돌 방지 & 안정성:**
* 멀티스레딩(Multi-threading) 구조로 GUI 멈춤 없이 부드럽게 동작합니다.
* 관리자 권한 자동 획득 기능을 포함하여 시스템 창(작업 관리자 등)도 감시 가능합니다.



---

## 📦 Prerequisites (준비 사항)

이 프로그램을 실행하기 위해서는 다음 항목들이 필요합니다.

### 1. Tesseract-OCR 설치 (필수)

이 프로그램은 글자 인식을 위해 **Tesseract 엔진**이 필요합니다.

* **[Tesseract 다운로드 링크](https://www.google.com/search?q=https://github.com/UB-Mannheim/tesseract/wiki)**
* 설치 후 경로(`C:\Program Files\Tesseract-OCR\tesseract.exe`)를 확인해주세요.
* *Note: 설치 시 'Additional script data'에서 `Korean`을 체크하면 한글 인식률이 높아집니다.*

### 2. Python 라이브러리 설치

```bash
pip install -r requirements.txt

```

*(만약 requirements.txt가 없다면 아래 명령어로 직접 설치하세요)*

```bash
pip install opencv-python pytesseract mss numpy pygetwindow winsound

```

---

## 🚀 How to Run (사용 방법)

1. **코드 경로 수정:**
`main.py` 파일을 열고 Tesseract 설치 경로가 본인의 환경과 맞는지 확인하세요.
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

```


2. **프로그램 실행:**
```bash
python main.py

```


*(프로그램이 관리자 권한을 요청하면 '예'를 눌러주세요.)*
3. **타겟 윈도우 선택:**
* 실행 중인 프로그램 목록이 뜨면 감시하고 싶은 창(예: 원격 데스크톱, 게임 등)을 선택합니다.


4. **감시 항목 추가 및 설정:**
* **[+ 감시 추가]** 버튼을 클릭합니다.
* **[영역 잡기]** 버튼을 누르고 화면에서 감시할 부분(숫자나 글자)을 드래그한 뒤 `Space` 또는 `Enter`를 누릅니다.
* **감시 모드**를 선택합니다 (예: `숫자 > 초과`).
* **조건값(Target)**을 입력합니다. (예: `100` 입력 시, 읽은 값이 100을 넘으면 알림)



---

## 💡 Configuration Guide (설정 가이드)

| 모드 (Mode) | 설명 | 예시 시나리오 |
| --- | --- | --- |
| **숫자 < 미만** | 읽은 숫자가 설정값보다 작으면 알림 | HP가 30% 미만일 때, 재고가 10개 미만일 때 |
| **숫자 > 초과** | 읽은 숫자가 설정값보다 크면 알림 | CPU 온도가 80도 초과일 때, 주가가 목표가 도달 시 |
| **숫자 범위 밖** | 숫자가 설정된 최소~최대 범위를 벗어나면 알림 | 전압이 220V ±10% 범위를 벗어날 때 |
| **텍스트 불일치** | 특정 텍스트가 변경되면 알림 | 상태창이 "Online"에서 다른 글자로 바뀔 때 |
| **색상 변화** | 지정한 영역의 색상이 기준 색과 다르면 알림 | 신호등이 초록색에서 빨간색으로 바뀔 때 |

---

## 🛠 Troubleshooting (문제 해결)

* **Q. "TesseractNotFoundError" 에러가 발생해요.**
* A. Tesseract가 설치되지 않았거나, 코드 내의 `tesseract_cmd` 경로가 잘못되었습니다. 경로를 다시 확인해주세요.


* **Q. 검은 화면만 캡처돼요.**
* A. 크롬(Chrome)이나 게임의 경우 '하드웨어 가속' 때문에 캡처가 안 될 수 있습니다. 브라우저 설정을 끄거나, 프로그램을 관리자 권한으로 실행했는지 확인하세요.


* **Q. 창을 가려도 되나요?**
* A. 현재 사용된 `mss` 라이브러리는 **'보이는 화면 그대로'**를 캡처합니다. 다른 창이 감시 영역을 가리면 가리는 창을 읽게 되므로, 듀얼 모니터를 활용하거나 창을 겹치지 않게 배치해주세요.



---

## 🗺 Roadmap (향후 계획)

* [ ] **Telegram / Slack / Discord 연동:** 알림 발생 시 모바일로 메시지 전송 기능 추가
* [ ] **로그(Log) 저장:** 감시된 데이터 값을 CSV 파일로 자동 저장
* [ ] **다중 윈도우 감시:** 한 번에 여러 개의 프로그램을 동시에 감시

---

## 📝 License

This project is licensed under the MIT License. Feel free to use and modify!
