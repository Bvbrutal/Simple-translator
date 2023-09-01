import sys
import json
import ssl
import random
import string

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, \
    QPushButton, QMessageBox, QAction, QFileDialog, QInputDialog, QDesktopWidget, QDialog, QTableWidgetItem, \
    QTableWidget, QTextEdit
from PyQt5.QtGui import QFont, QIcon
from urllib import request, parse
from googletrans import Translator

punc = string.punctuation


ua_list = [
    'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',
]
class TranslationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        icon = QIcon("Find.ico")
        self.setWindowIcon(icon)
        self.title = "翻译软件"
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 400

        self.dictionary = self.load_dictionary()
        self.dictionary_desc=self.load_dictionary_desc(self.dictionary)
        self.translator = Translator()

        self.init_ui()

    def init_ui(self):
        # 设置窗口标题和尺寸
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        #创建主窗口
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 创建左部件和布局
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)

        # 计算中心位置
        center = QDesktopWidget().availableGeometry().center()
        x = center.x()
        y = center.y()
        old_x,old_y,old_width,old_height=self.frameGeometry().getRect()
        new_x=int(x-old_width/2)
        new_y=int(y-old_height/2)
        self.move(new_x,new_y)

        # 创建单词输入区域
        word_layout = QHBoxLayout()
        word_label = QLabel("英文单词：")
        word_layout.addWidget(word_label)
        self.word_entry = QLineEdit()
        word_layout.addWidget(self.word_entry)
        left_layout.addLayout(word_layout)

        # 创建中文解释输入区域
        meaning_layout = QHBoxLayout()
        meaning_label = QLabel("中文解释：")
        meaning_layout.addWidget(meaning_label)
        self.meaning_entry = QLineEdit()
        meaning_layout.addWidget(self.meaning_entry)
        left_layout.addLayout(meaning_layout)

        # 创建添加单词按钮
        add_word_button = QPushButton("添加单词")
        add_word_button.clicked.connect(self.add_word)
        left_layout.addWidget(add_word_button)

        # 创建英文句子输入区域
        sentence_layout = QHBoxLayout()
        sentence_label = QLabel("翻译内容：")
        sentence_layout.addWidget(sentence_label)
        self.sentence_entry = QLineEdit()
        sentence_layout.addWidget(self.sentence_entry)
        left_layout.addLayout(sentence_layout)

        button_layout=QHBoxLayout()
        # 创建本地翻译按钮
        translate_button_local = QPushButton("本地翻译")
        translate_button_local.clicked.connect(self.translate_sentence_local)
        button_layout.addWidget(translate_button_local)

        # 创建在线翻译按钮
        translate_button_online = QPushButton("在线翻译")
        translate_button_online.clicked.connect(self.translate_sentence_online)
        button_layout.addWidget(translate_button_online)

        # 按钮布局加入左部分布局
        left_layout.addLayout(button_layout)


        #创建翻译结果标签
        translation_result_label = QLabel("翻译结果:")
        left_layout.addWidget(translation_result_label)

        # 创建翻译结果显示框
        translation_result_layout1 = QHBoxLayout()
        self.translation_result_text_edit1 = QTextEdit()
        self.translation_result_text_edit1.setReadOnly(True)  # 设置为只读
        translation_result_layout1.addWidget(self.translation_result_text_edit1)
        left_layout.addLayout(translation_result_layout1)

        #创建右部窗口
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        translation_result_layout2 = QVBoxLayout()
        self.translation_hint_label = QLabel("使用提示")
        self.translation_hint_label.setAlignment(Qt.AlignCenter)
        self.translation_hint_label.setStyleSheet("border: 1px solid gray;")
        translation_result_layout2.addWidget(self.translation_hint_label)

        self.translation_result_text_edit2 = QTextEdit()
        self.translation_result_text_edit2.setReadOnly(True)  # 设置为只读
        translation_result_layout2.addWidget(self.translation_result_text_edit2)
        right_layout.addLayout(translation_result_layout2)
        self.display_hint()

        #添加左右部件
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        # 创建菜单栏
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("操作")
        edit_menu = menu_bar.addMenu("查看")

        # 创建添加单词菜单项
        add_word_action = QAction("添加单词", self)
        add_word_action.triggered.connect(self.add_word_dialog)
        add_word_action.setStatusTip("")
        file_menu.addAction(add_word_action)

        # 创建删除单词菜单项
        delete_word_action = QAction("删除单词", self)
        delete_word_action.triggered.connect(self.delete_word)
        delete_word_action.setStatusTip("")
        file_menu.addAction(delete_word_action)

        # 创建清空字典菜单项
        clear_dictionary_action = QAction("清空字典", self)
        clear_dictionary_action.triggered.connect(self.clear_dictionary)
        file_menu.addAction(clear_dictionary_action)

        # 创建保存字典菜单项
        save_dictionary_action = QAction("保存字典", self)
        save_dictionary_action.triggered.connect(self.save_dictionary)
        file_menu.addAction(save_dictionary_action)

        # 创建加载字典菜单项
        load_dictionary_action = QAction("加载字典", self)
        load_dictionary_action.triggered.connect(self.load_dictionary_from_file)
        file_menu.addAction(load_dictionary_action)

        # 创建退出菜单项
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.window_exit)
        file_menu.addAction(exit_action)

        # 创建显示字典内容菜单项
        display_dictionary_action = QAction("显示字典内容", self)
        display_dictionary_action.triggered.connect(self.display_dictionary)
        edit_menu.addAction(display_dictionary_action)

        # 创建统计字典词数菜单项
        count_words_action = QAction("统计字典词数", self)
        count_words_action.triggered.connect(self.count_words)
        edit_menu.addAction(count_words_action)

        # 设置字体
        font = QFont("Arial", 10)
        self.setFont(font)

    def add_word_dialog(self):
        word, ok = QInputDialog.getText(self, "添加单词", "请输入英文单词:")
        if len(word)==0 and ok:
            QMessageBox.information(self, "提示", "请完整输入英文单词和中文解释！")
        elif ok:
            meaning, ok = QInputDialog.getText(self, "添加单词", "请输入中文解释:")
            if len(word)==0 and ok:
                QMessageBox.information(self, "提示", "请完整输入英文单词和中文解释！")
            elif ok:
                if self.dictionary.get(word.lower(), 0)!=0:
                    QMessageBox.information(self, "提示", "单词已添加过了！")
                else:
                    self.dictionary[word.lower()] = meaning
                    self.dictionary_desc[meaning] = word.lower()
                    QMessageBox.information(self, "成功", "单词已添加到字典！")
                    self.word_entry.clear()
                    self.meaning_entry.clear()


    def add_word(self):
        word = self.word_entry.text().strip()
        meaning = self.meaning_entry.text().strip()
        if word and meaning:
            print(self.dictionary.get(word.lower(), 0))
            if self.dictionary.get(word.lower(), 0) != 0:
                QMessageBox.information(self, "提示", "单词已添加过了！")
            else:
                self.dictionary[word.lower()] = meaning
                self.dictionary_desc[meaning] = word.lower()
                QMessageBox.information(self, "成功", "单词已添加到字典！")
                self.word_entry.clear()
                self.meaning_entry.clear()
        else:
            QMessageBox.information(self, "失败", "请完整输入英文单词和中文解释！")
            self.word_entry.clear()
            self.meaning_entry.clear()



    def delete_word(self):
        word, ok = QInputDialog.getText(self, "删除", "请输入要删除的英文单词:")
        if len(word)==0 and ok:
            QMessageBox.information(self, "提示", "请完整输入英文单词和中文解释！")
        elif ok:
            if word and word.lower() in self.dictionary:
                confirm = QMessageBox.question(self, "确认删除", f"确定要删除单词 '{word}' 吗？",
                                               QMessageBox.Yes | QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    del self.dictionary[word.lower()]
                    QMessageBox.information(self, "成功", "单词已从字典中删除！")
            else:
                QMessageBox.warning(self, "警告", "字典中不存在该单词！")
                confirm=QMessageBox.question(self, "提示", "是否产看字典列表？",
                                     QMessageBox.Yes | QMessageBox.No)
                if confirm:
                    self.display_dictionary()

    def clear_dictionary(self):
        confirm = QMessageBox.question(self, "确认清空", "确定要清空字典吗？", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.dictionary.clear()
            QMessageBox.information(self, "成功", "字典已清空！")

    def translate_sentence_local(self):
        sentence = self.sentence_entry.text().strip()
        if len(sentence)!=0:
            if self.is_english(sentence):
                translated_sentence = self.translate_text_english(sentence)
                self.display_translation(translated_sentence)
                self.clear_sentence_entry()
            if self.is_chinese(sentence):
                translated_sentence = self.translate_text_chinese(sentence)
                self.display_translation(translated_sentence)
                self.clear_sentence_entry()
        else:
            QMessageBox.information(self, "提示", "请输入要翻译的英文单词或句子！")


    def translate_text_english(self, text):
        translated_text = []
        words = text.split()
        for word in words:
            if word.endswith(",") or word.endswith("，"):
                word=word.strip(',')
                word = word.strip('，')
                translated_word = self.dictionary.get(word.lower(), word)
                translated_text.append(translated_word)
                translated_text.append(',')
            else:
                translated_word = self.dictionary.get(word.lower(), word)
                translated_text.append(translated_word)
        return "".join(translated_text)

    def translate_text_chinese(self, text):
        translated_text = []

        for word in text:
            if word in punc:
                translated_text.append(word)
            else:
                translated_word = self.dictionary_desc.get(word, word)
                translated_text.append(translated_word)
        return " ".join(translated_text)


    def display_translation(self, translation):
        self.translation_result_text_edit1.setText(translation)

    def is_english(self,word):
        for char in word:
            if not ('a' <= char <= 'z' or 'A' <= char <= 'Z' or char ==' '):
                return False
        return True

    def is_chinese(self,input_string):
        for char in input_string:
            if not ('\u4e00' <= char <= '\u9fff' or char ==' '):
                return False
        return True

    def display_hint(self):
        text="\n1.目前只支持中英互译；" \
             "\n2.翻译时会自动识别语言；" \
             "\n3.翻译结果语法可能有出入；" \
             "\n4.可以自己添加单词；" \
             "\n5.可以在线查询；" \
             "\n6.可以在线添加单词；" \
             "\n7.可以加载自己的字典；" \
             "\n8.可以清空单词；" \
             "\n9.可以查看单词列表以及单词计数；" \
             "\n10.在线翻译可能有些许卡顿，属于正常现象。" \
             "\n11.本地翻译字典中没有的单词，默认输入什么就返回什么"
        self.translation_result_text_edit2.setText(text)


    def clear_sentence_entry(self):
        self.sentence_entry.clear()

    def load_dictionary(self):
        try:
            with open("dictionary.json", "r") as file:
                result=json.load(file)
                return result
        except FileNotFoundError:
            return {}

    def save_dictionary(self):
        with open("dictionary.json", "w") as file:
            json.dump(self.dictionary, file, ensure_ascii=False, indent=4)
        QMessageBox.information(self, "成功", "字典已保存！")

    def load_dictionary_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "加载字典", "", "JSON文件 (*.json)")
        if file_path:
            try:
                with open(file_path, "r") as file:
                    self.dictionary = json.load(file)
                QMessageBox.information(self, "成功", "字典已加载！")
            except (FileNotFoundError, json.JSONDecodeError):
                QMessageBox.critical(self, "错误", "无法加载字典文件！")

    def count_words(self):
        word_count = len(self.dictionary)
        QMessageBox.information(self, "字典词数", f"字典中共有 {word_count} 个单词")

    def closeEvent(self, event):
        confirm = QMessageBox.question(self, "确认退出", "确定要退出吗？", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            confirm = QMessageBox.question(self, "提示", "字典还没保存，是否保存？", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.save_dictionary()
                event.accept()
        else:
            event.ignore()

    def window_exit(self):
        self.close()

    def display_dictionary(self):
        if self.dictionary:
            self.dialog = DisplayDictionaryDialog(self.dictionary)
            self.dialog.show()
        else:
            QMessageBox.warning(self, "警告", "字典为空！")

    def load_dictionary_desc(self,dictionary):
        reverse_dictionary = {}
        for key, value in dictionary.items():
            reverse_dictionary[value] = key
        return reverse_dictionary

    def loadPage(self,url, word):
        # 在ua_list列表中随机选择一个UserAgent
        userAgent = random.choice(ua_list)
        headers = {
            'User-Agent': userAgent
        }
        # 发起一个请求
        req = request.Request(url, headers=headers)
        # 创建未经过验证的上下文的代码
        context = ssl._create_unverified_context()
        data = {
            'i': word,
            'from': 'AUTO',
            'to': 'AUTO',
            'smartresult': 'dict',
            'client': 'fanyideskweb',
            'salt': '16002154063071',
            'sign': '37d97277cb051e71959e772b91309b2b',
            'lts': '1600215406307',
            'bv': '7e14dfdb6b3686cc5af5e5294aaded19',
            'doctype': 'json',
            'version': '2.1',
            'keyfrom': 'fanyi.web',
            'action': 'FY_BY_REALTlME'
        }
        data = parse.urlencode(data).encode('utf-8')
        # 打开响应的对象
        response = request.urlopen(req, context=context, data=data)
        # 获取响应的内容
        html = response.read()
        # 对获取到的unicode编码进行解码
        content = html.decode('utf-8')

        return content

    def fanyi(self,word):
        url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule'
        content = self.loadPage(url, word)
        jsondicts = json.loads(content)
        return jsondicts['translateResult'][0][0]['tgt']

    def translate_sentence_online(self):
        self.translation_result_text_edit1.setText("正在联网翻译，请稍等...")
        QTimer.singleShot(1000, self.translate_online)


    def add_online_chinese(self,word,meaning):
        self.dictionary[meaning] = word.lower()
        self.dictionary_desc[word.lower()]=meaning
        QMessageBox.information(self, "成功", "单词已添加到字典！")

    def add_online_english(self,word,meaning):
        self.dictionary[word.lower()] = meaning
        self.dictionary_desc[meaning] = word.lower()
        QMessageBox.information(self, "成功", "单词已添加到字典！")

    def translate_online(self):
        try:
            sentence = self.sentence_entry.text().strip()
            if len(sentence) != 0:
                translated_sentence = self.fanyi(sentence)
                self.display_translation(translated_sentence)
                if self.is_chinese(sentence):
                    translated_sentence = translated_sentence.split()
                    if len(translated_sentence) == 1:
                        if self.dictionary_desc.get(sentence, 0) == 0:
                            confirm = QMessageBox.question(self, "提示", "字典中没有此单词，是否添加？", QMessageBox.Yes | QMessageBox.No)
                            if confirm==QMessageBox.Yes:
                                self.add_online_chinese(sentence,translated_sentence)
                if self.is_english(sentence):
                    sentence = sentence.split()
                    if len(sentence) == 1:
                        if self.dictionary.get(sentence[0].lower(), 0) == 0:
                            confirm = QMessageBox.question(self, "提示", "字典中没有此单词，是否添加？", QMessageBox.Yes | QMessageBox.No)
                            if confirm==QMessageBox.Yes:
                                self.add_online_english(sentence[0],translated_sentence)
            else:
                QMessageBox.information(self, "提示", "请输入要翻译的英文单词或句子！")
        except:
            QMessageBox.information(self, "失败", "请检查你的网络或者其他原因！")

        self.clear_sentence_entry()


class DisplayDictionaryDialog(QDialog):
    def __init__(self, dictionary):
        super().__init__()
        icon = QIcon("Find.ico")
        self.setWindowIcon(icon)
        self.setWindowTitle("字典内容")
        self.setMinimumSize(400, 300)

        self.dictionary = dictionary

        layout = QVBoxLayout(self)
        self.table_widget = QTableWidget(self)
        layout.addWidget(self.table_widget)

        self.populate_table()

        # 使用 QTimer.singleShot 延迟执行移动操作
        QTimer.singleShot(0, self.delayed_move)

    def delayed_move(self):
        center = QDesktopWidget().availableGeometry().center()
        new_pos = center - self.rect().center()
        self.move(new_pos)

    def populate_table(self):
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["单词", "解释"])
        self.table_widget.setRowCount(len(self.dictionary))

        row = 0
        for word, meaning in self.dictionary.items():
            word_item = QTableWidgetItem(word)
            meaning_item = QTableWidgetItem(meaning)

            self.table_widget.setItem(row, 0, word_item)
            self.table_widget.setItem(row, 1, meaning_item)

            row += 1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslationApp()
    window.show()
    sys.exit(app.exec_())
