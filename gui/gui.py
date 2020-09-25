# window.progressbar.    = od.busvoltage()
# pyuic5 mainwindow.ui -o MainWindow.py
#while (1):
	#app.exec()
	
from PyQt5 import QtWidgets, uic , QtCore  
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
#from pyqtgraph import PlotWidget
#import pyqtgraph as pg
import sys
import time
import odrive

b = 0
window = 0
b1 = 0
# #
# class WorkerThread(QtCore.QObject):
#     signalExample = QtCore.pyqtSignal(str, int)
 
#     def __init__(self):
#         super().__init__()
 
#     @QtCore.pyqtSlot()
#     def run(self):
#         while True:
#             # Long running task ...
#             self.signalExample.emit("leet", 1337)
#             time.sleep(5)


class Worker(QRunnable):
    '''
    Worker thread
    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
    :param callback: The function callback to run on this worker thread. Supplied args and 
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    '''
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        self.fn(*self.args, **self.kwargs)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi('mainwindow.ui', self)
        #self.show()
        self.threadpool = QThreadPool()
        self.show()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.pushButton.clicked.connect(self.pressed)
        self.odrv0 = self.ConnectOdrive()
       
        self.startWorkers()
        self.odriveConnect.clicked.connect(self.startWorkers)
        self.closedLoopAxis1CheckBox.clicked.connect(self.closedLoop)
        #self.showVolt()
        #self.velocity_in_X()
       # self.batteryCheck() 

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.limitVelocity_in_X)
        self.timer.start()

        # timer for updating battery voltage
        self.batteryUpdateTimer = QTimer()
        self.batteryUpdateTimer.setInterval(5000)
        self.batteryUpdateTimer.timeout.connect(self.batteryUpdatevalue)
        self.batteryUpdateTimer.start()

    def closedLoop(self):
        if self.closedLoopAxis1CheckBox.isChecked():
            try:            
                self.odrv0.axis1.requested_state = 8
            except:
                pass

    def batteryUpdatevalue(self):
        #print("trying")
        try:
            #print(self.odrv0.vbus_voltage)
            vbusVoltage = self.odrv0.vbus_voltage
            self.batteryVoltage.setText(str(vbusVoltage))
            self.lcdNumber.setProperty("value",vbusVoltage)
        except:
            pass


    def limitVelocity_in_X(self):
        max_vel = self.velocityLimitX.value()  
        self.lcd_vel.setProperty("value",max_vel) 
            
    def startWorkers(self):        
        # Pass the function to execute
        worker   = Worker(self.batteryUpdatevalue)
        
        worker3  = Worker(self.movePosX)
        if self.odriveConnect.isChecked():
            worker2  = Worker(self.ConnectOdrive)
            #worker2.signals.finished.connect(self.batteryUpdatevalue)
            self.threadpool.start(worker2)
        # Execute
        self.threadpool.start(worker)
        self.threadpool.start(worker3)

    def ConnectOdrive(self):
        print("connecting odrive")
        # connect odrive and return object for all other funciton.
        # This must be proteced by a Mutex!!!! or Signals!!
        odrv0 = odrive.find_any()
        print("odrive connected")
        return odrv0

    def pressed(self):        
        self.progressBar.setProperty("value",self.progressBar.value()+1)
        #print("1")
        self.batteryVoltage.setText("hejhej")
        if(self.checkBox.isChecked()):
            #print("hej")
            self.batteryCheck()

 

    def batteryCheck(self):
    # Pass the function to execute
        worker  = Worker(self.batteryUpdatevalue)
    # Execute
        self.threadpool.start(worker)
   
    def movePosX(self):
        while(True):
            posX = self.posInX.value()
            print(posX)
            self.lcd_vel.setProperty("value",posX) 
            try:
                print("trying to move")
                self.odrv0.axis1.controller.move_incremental(posX,1)
            except:
                pass
            
        

    
        
def main():
    global window
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    
    #global b 
    #b = MainWindow()
    #b= QtWidgets.QApplication.processEvents()
    #window.show()       
    sys.exit(app.exec_())
       
    

if __name__ == '__main__':   
    #while(True):
     #   print("hej")     
    main()
