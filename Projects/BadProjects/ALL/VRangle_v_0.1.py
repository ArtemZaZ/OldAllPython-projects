###########################################################################################################
##### class VR_Angle - чтение и обработка приходящих из VR очков сообщений, преобразование их в углы. #####
##### class VR_Thread - запуск чтения и обработки сообщений с очков в отдельном потоке, а также класс #####
##### имеет встроенные функции, позволяющие за пределами потока затребовать углы и выйти из потока    #####
###########################################################################################################

import serial
import threading
import time

class VR_Angle():                                                               
        def __init__(self, portname, yaw=0,  pitch=0, roll=0):                  #конструктор
            self.port = serial.Serial(portname, baudrate=115200)                #открытие порта
            self.yaw = yaw              #                                        
            self.pitch = pitch          # углы поворота
            self.roll = roll            #
            
            self.yaw0 = yaw             #
            self.pitch0 = pitch         # нулевые углы, задаются кнопками старт/стоп на очках 
            self.roll0 = roll           #
            
            self.buff=b''               # буффер для строки, прилетевшей с очков
            self.listbuff=[]            # предыдущая строка, в которой слова разделены пробелами
            
            self.EXIT=False             # метка выхода из потока
            self.START=False            # метка нажатия кнопки старт

            self.PLAYING=1
            self.STOP=2
            self.STATE=2

            

        def _del_(self):                # деструктор
            port.close()                # закрытие порта

        def read_bytesstr(self):        # чтение строки,заключенной между < >, с очков и запись ее в буффер
            k=self.port.read()
            while k!=b'<':
                k=self.port.read()
            while k!=b'>':
                if k!=b'<':
                    self.buff+=k
                k=self.port.read()
                

        def convert_srtbuffer(self):                                    # сортировка сообщений с очков и перевод углов            
            self.listbuff = list(map(bytes, self.buff.split()))         # разделение сообщения на слова и запись их в список

            if self.listbuff[0]==b'ypr':                                # если первое слово ypr
                self.yaw = float(self.listbuff[1])                      # 
                self.pitch = float(self.listbuff[2])                    # преобразование байтовых слов в float
                self.roll = float(self.listbuff[-1])                    #
                

            if(self.START):                                             # если была нажата кнопка start
                self.yaw0 = self.yaw                                    #  
                self.pitch0 = self.pitch                                # текущие углы сделать нулевыми
                self.roll0 = self.roll                                  #
                self.START=False                                        #
            
                
            if self.listbuff[0]==b'*':                                  # если сообщение начинается с *
                print("\n COMMENT: ")                                   # вывод комментария
                print(str(self.buff))                                   #

            if self.listbuff[0]==b'start':                              # если пришло сообщение start(была нажата кнопка start)
                self.START=True                                         # сделать метку кнопки start активной
                self.STATE=self.PLAYING

            if self.listbuff[0]==b'stop':                               # если пришло сообщение stop(была нажата кнопка stop)
                self.START=False
                self.yaw0 = 0                                           #  
                self.pitch0 = 0                                         # сбросить текущие углы
                self.roll0 = 0                                          #
                self.STATE=self.STOP


        def VR_EXIT(self):                                              # функция закрывающая поток
            self.EXIT=True
            
        def get_yaw(self):                                              # доступ к yaw
            return self.yaw-self.yaw0
        
        def get_pitch(self):                                            # доступ к pitch
            return self.pitch-self.pitch0
        
        def get_roll(self):                                             # доступ к roll
            return self.roll-self.roll0
        
        def get_ypr_list(self):                                         # доступ к списку координат
            if (self.STATE==self.PLAYING):
                A=[self.yaw-self.yaw0, self.pitch-self.pitch0, self.roll-self.roll0]
            else:
                A = [None, None, None]
            return A

        def get_state(self):
            return self.STATE


        def start_read_VR_angle(self):                  # начать чтение с очков
            self.read_bytesstr()                                        
            self.buff=b''
            time.sleep(1)
            self.port.write(b'g')                       # для того, чтоб очки начали передавать координаты, необходимо отправить символ на них 
            while not self.EXIT:                        # пока поток не закрыт           
                self.read_bytesstr()                    
                self.convert_srtbuffer()
                self.buff=b''


class VR_thread(threading.Thread):                      # потоковый класс
    def __init__(self, Portname):                       # конструктор
        threading.Thread.__init__(self)                 # функция инициализирующая поток
        self.portname=Portname
        self.VR = VR_Angle(self.portname)               # создание объекта класса VR_Angle

    def run(self):                                      # функция запуска потока       
        self.VR.start_read_VR_angle()                   # циклится, пока не придет метка закрытия потока
        print("VR_THREAD stopped")

    def Exit(self):                                     # функция выхода их потока за пределами потока
        self.VR.VR_EXIT()

    def get_angle(self):                                # функция доступа к углам за пределами потока
        return self.VR.get_ypr_list()

    def get_state(self):
        return self.VR.get_state()


###########################################################################################################
###########################################################################################################
##### Пример программы, использующей эти классы:                                                      #####
#####                                                                                                 #####
##### import VRangle                                                                                  #####
##### import time                                                                                     #####
##### VR_TH=VRangle.VR_thread("/dev/ttyUSB0")   # созданее переменное класса VR_thread/открытие порта #####
#####                                           # по адресу /dev/ttyUSB0                              #####
##### VR_TH.start()                                                                                   #####
##### time.sleep(10)                                                                                  #####
##### angle=VR_TH.get_angle()                   # получение списка углов с очков                      #####                  
##### print(angle)                                                                                    #####          
##### VR_TH.Exit()                              # выход из потока                                     #####
#####                                                                                                 #####
###########################################################################################################
###########################################################################################################
