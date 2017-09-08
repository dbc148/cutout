import sys, os
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PIL import Image
from PIL.ImageQt import ImageQt
from collections import defaultdict

def PILimageToQImage(pilimage):
    """converts a PIL image to QImage"""
    imageq = ImageQt(pilimage) #convert PIL image to a PIL.ImageQt object
    qimage = QImage(imageq)
    return qimage




class placeholder:
    def __init__(self):
        self.scaling = 1
a = placeholder()
words = defaultdict(int)

def save_image(path,name,image):
    if not os.path.exists(path):
        os.makedirs(path)
    image.save(path + '/' + name + '.png', 'PNG')

def load_data():
    file_paths = [line.strip() for line in open('image_paths.txt')]
    return file_paths

image_paths = load_data()
image_names = [x.split('/')[-1].split('.')[0] for x in image_paths]
images = [Image.open(path) for path in image_paths]
image_idxs = {x[0]:x[1] for x in zip(image_paths, range(len(image_paths)))}
print image_names
class MainWindow(QMainWindow):

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.image_widget = ImageWindow(self) 
        self.setCentralWidget(self.image_widget)
        self.resize(self.image_widget.img_w,self.image_widget.img_h+30)
        self.prev = [-1,-1]
        self.popup = Popup()

    def mousePressEvent(self, QMouseEvent):
        point = QMouseEvent.pos()
        x = point.x()
        y = point.y()
        if self.prev[0] == -1:
            self.prev = [x,y]
        else:
            current_image_id = self.image_widget.current_image
            sub_image = images[int(current_image_id)].crop((int(self.prev[0]/a.scaling), int(self.prev[1]/a.scaling), int(x/a.scaling), int(y/a.scaling)))
            print a.scaling
            print self.prev, [x,y]
            self.popup.open_with_image(sub_image, [int(self.prev[0]/a.scaling), int(self.prev[1]/a.scaling)], [int(x/a.scaling), int(y/a.scaling)], current_image_id)
            self.prev = [-1,-1]
            self.popup.label.show()
        print x, y

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.popup.is_shown:
                self.popup.close()
            else:
                print 'previous stroke cleared'
                self.prev = [-1,-1]

    # def resizeEvent(self,resizeEvent):
    #     self.image_widget.set_scaling(self.width())

    #     print self.image_widget.width()
    #     print self.image_widget.img_w

    #     print "Window has been resized to " + str(self.width())

    # def paintEvent(self, QPaintEvent):
    #     self.image_widget.set_scaling(self.width())

    #     print self.image_widget.width()
    #     print self.image_widget.img_w

    #     print "Window has been resized to " + str(self.width())


class Popup(QWidget):
    def __init__(self, parent = None):
        QWidget.__init__(self)
        self.layout = QVBoxLayout(self)

        self.pixmap = None
        self.textbox = QLineEdit()
        self.label = QLabel()

        self.tr = None
        self.bl = None

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        self.buttons.accepted.connect(self.save)
        self.buttons.rejected.connect(self.close)
        self.textbox.returnPressed.connect(self.save)

        self.current_file = None
        self.offset_x = 0
        self.offset_y = 0

        self.image = None
        self.is_shown = False
    def open_with_image(self, image, tr, bl, current_image_id):
        self.image = image
        qim = PILimageToQImage(image)
        self.pixmap = QPixmap(qim)
        self.label.setPixmap(self.pixmap)
        self.img_h = self.pixmap.height()
        self.img_w = self.pixmap.width()
        self.tr = tr
        self.bl = bl
        self.current_image_id = current_image_id
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.textbox)
        self.layout.addWidget(self.buttons)
        self.is_shown = True

        self.show()

    def close(self):
        self.textbox.setText("")
        self.is_shown = False
        print 'cancelled'
        self.hide()
    def save(self):
        text = str(self.textbox.text())
        if text == '':
            self.close()
            return 0

        words[text] += 1
        if text[0] == '!':
            if self.current_file:
                self.current_file.close()
            self.current_file = open('bounding_boxes/' + text[1:] + '_' + str(words[text]) + '.txt', 'w')
            self.offset_x = self.tr[0]
            self.offset_y = self.tr[1]

            save_image('fields/' + text[1:], str(words[text]) + '_' + self.current_image_id + '_' 
                + str(self.tr[0]) + '_' + str(self.tr[1]) + '_' + str(self.bl[0]) + '_' + str(self.bl[1]), self.image)
        else:
            save_image('words/' + text, str(words[text]) + '_' + self.current_image_id + '_' 
                + str(self.tr[0]) + '_' + str(self.tr[1]) + '_' + str(self.bl[0]) + '_' + str(self.bl[1]), self.image)
            self.current_file.write(text + '\t' + str(self.tr[0]-self.offset_x) + '\t' + str(self.tr[1] - self.offset_y) + '\t' + str(self.bl[0]-self.offset_x) + '\t' + str(self.bl[1]-self.offset_y) + '\n')


        save_message = 'saved image at: ' + 'words/' + text + '/' +  str(words[text]) + '_' + image_names[int(self.current_image_id)] + '_' + str(self.tr[0]) + '_' + str(self.tr[1]) + '_' + str(self.bl[0]) + '_' + str(self.bl[1])

        print save_message

        self.textbox.setText("")
        self.is_shown = False
        self.hide()


class ImageWindow(QWidget):
    def __init__(self,parent):
        super(ImageWindow, self).__init__(parent)

        self.img_paths = load_data()

        self.label = QLabel(self)
        self.pixmap = QPixmap(os.getcwd() + '/' + self.img_paths[0])
        print os.getcwd() + '/' + self.img_paths[0]
        self.true_img_w = self.pixmap.width()
        self.scale = 1000
        a.scaling = float(self.scale)/self.true_img_w
        self.pixmap = self.pixmap.scaledToWidth(self.scale)

        self.current_image = '0'
        self.label.setPixmap(self.pixmap)

        self.img_h = self.pixmap.height()
        self.img_w = self.pixmap.width()
        self.resize(self.img_w,self.img_h+30)
         
        # Set window title
        self.setWindowTitle("demo")

        self.comboBox = QComboBox(self)
        for idx, identifier in enumerate(self.img_paths):
            self.comboBox.addItem(str(identifier))
        self.comboBox.move(0,self.img_h)

        self.comboBox.activated[str].connect(self.load_image)

    def set_scaling(self, scale):
        self.pixmap = QPixmap(os.getcwd() + '/' + self.img_paths[int(self.current_image)])
        self.scale = scale
        a.scaling = float(self.scale)/self.true_img_w
        self.pixmap = self.pixmap.scaledToWidth(self.scale)
        self.img_h = self.pixmap.height()
        self.img_w = self.pixmap.width()
        self.resize(self.img_w,self.img_h+30)
        self.label.setPixmap(self.pixmap)

    def load_image(self,identifier):
        self.pixmap = QPixmap(identifier)
        img_w = self.pixmap.width()

        a.scaling = float(self.scale)/img_w
        self.pixmap = self.pixmap.scaledToWidth(self.scale)
        self.current_image = str(image_idxs[str(identifier)])
        self.label.setPixmap(self.pixmap)
        self.img_h = self.pixmap.height()
        self.img_w = self.pixmap.width()
        self.resize(self.img_w,self.img_h+30)

# Create an PyQT4 application object.
qapp = QApplication(sys.argv)

test = MainWindow()
test.show()
sys.exit(qapp.exec_())
