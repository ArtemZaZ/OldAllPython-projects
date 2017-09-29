import socket
import time, datetime
import struct
import threading
from ParamList import *
ISREADY=1
NOTREADY=0


###### Устройства ######


class Robot():
    
    def __init__(self):

        self.EXIT = False
        
        self.Motors_Contr_List = []
        self.Steppers_Contr_List = []
    ###### Индикатор отправки онлайн метки ######
        self.Online = False

    ###### Создаем пустую очередь для дальнейшего заполнения сообщениями отправки ######
        self.queue = []     
        self.Start_Send_Queue()
    ###### Создаем сокет ######
        self.s = socket.socket()       # Создание сокета s
        self.s_lock = threading.Lock() # Создаем s_lock - замок для сокета s

    ###### Индикатор подключения (Отключения) к устройству ######
        self.connected = False

    ###### Запускаем функцию, слушающую подклассы - контроллеры ######
        self.Listen_Cmd_to_Contr()

    def Exit(self):
        self.EXIT = True
    
    def Connect(self, IP, Port):
        if not self.connected:
            try:
                self.s.connect((IP, Port))
                self.Send_Online()
            except OSError as msg:
                print("Не могу связаться с сокет-сервером: %s\n " % msg)
            else:
                print(IP + " connected")
                self.connected = True

    def Disconnect(self):
        self.Online = False
        self.s.close()
        self.connected = False
        self.Exit()

        
    ###### Отправка сообщения на подключенное устройство ######
    def Send_Msg(self, data):
#        self.s_lock.acquire(True)     # Ожидает доступа к сокету, и если сокет доступен - захватывает его.
        try:
            self.s.send(data)
            now = datetime.datetime.now()
            #print("\n", now.second, ":", now.microsecond, "DATA TO SEND", data)
            time.sleep(0.05)
            self.SEND_SUCCESS = True
#            self.s_lock.release()
        except OSError: #self.s.error: # здесь нужно указать ошибку сокета(изучить их)
            print ("Socket error\n")
            time.sleep(0.1)


    def Add_to_queue(self, msg):        # Добавляем сообщение в очередь
        self.queue.append(msg)

    def Send_Queue(self):

        while not self.EXIT: ## /Not exit
            self.SEND_SUCCESS = False
            if len(self.queue) != 0:             # Если очередь не пуста 
                self.Send_Msg(self.queue[0])     # Отправляем первый элемент очереди и удаляем его
                if self.SEND_SUCCESS:
                    self.queue.pop(0)
                
            else:
                time.sleep(0.1)
    def Start_Send_Queue(self):             # Запускаем отправку очереди в отдельном потоке
        t = threading.Thread( target = self.Send_Queue)
        t.start()
        self.Start_Send_Queue = self.function_coffin         # отправляем функцию в гроб

    ###### ГРОБ ######
    def function_coffin(self):      # Делает невозможным повторный запуск функций которые сюда сослали
        pass
    ##################
    
    ### Отправка онлайна ### 
    def Send_Online_msg(self):
        can_msg_online = struct.Struct('I 4B')
        can_msg_online_data = can_msg_online.pack(0x600, 0, 0, 0, 0)
        while not self.EXIT:
            if self.Online:
                self.Add_to_queue(can_msg_online_data)            # Отправка переменной can_a с сокета s 
                time.sleep(1.9)
            time.sleep(0.1)
            
        
    def Send_Online(self):
        self.Online = True
        t = threading.Thread( target = self.Send_Online_msg)
        t.start()
        self.Send_Online = self.function_coffin     # отправляем функцию в гроб

    def Set_Online(self, value):
        self.Online = value

    def Is_Online(self):
        return (self.Online)


    ###### Обработка полученных сообщений ######

    def Recv_Msg(self):   # Получаем сообщение

        can_msg = struct.Struct('=I 12B')
        while not self.EXIT:
            
            try:
                InMsg = self.s.recv(can_msg.size)   # Получаем сообщение и записываем его в переменную InMsg
                Success = True
                
            except OSError as msg:
                print("Socket error: %s\n " %  msg)
                Success = False

            if Success:
                self.Msg_Handler(InMsg)

            time.sleep(0.01)



    def Msg_Handler(self, InMsg):   # Обрабатываем сообщение
        can_msg = struct.Struct('=I 12B')
        list_len = len(self.Motors_Contr_List)
        for i in range(list_len):
            if can_msg.unpack(InMsg)[0] == self.Motors_Contr_List[i].can_addr:    # Сравниваем айди сообщения с айди контроллера
                self.Motors_Contr_List[i].Handler(InMsg)  # Отправляем номер полученного параметра и само сообщение в обработчик   
        
    def Listen(self):
        t = threading.Thread( target = self.Recv_Msg)
        t.start()

    ###### Работа с контроллерами ######

    def add_Motor_Controller(self, Controller_Number):
        self.Motors_Contr_List.append(Motor_Controller(Controller_Number))
    
    def add_Stepper_Controller(self, Controller_Number):
        self.Steppers_Contr_List.append(Stepper_Controller(Controller_Number))    

    def Recv_Msg_from_Device(self):
        while not self.EXIT:
            # Для мотора
            for Motor_Controller in (self.Motors_Contr_List):
                self.queue.extend((Motor_Controller.queue))
                Motor_Controller.queue.clear()

            # Для шаговика
            for Stepper_Controller in (self.Steppers_Contr_List):
                self.queue.extend((Stepper_Controller.queue))
                Stepper_Controller.queue.clear()
            time.sleep(0.01)

        
    def Listen_Cmd_to_Contr(self):
        t = threading.Thread( target = self.Recv_Msg_from_Device)
        t.start()
  
### Шаблон устройства ###
        
class Base_Controller():

    def __init__(self):
        self.queue = []

    def Add_to_queue(self, msg):        # Добавляем сообщение в очередь
        self.queue.append(msg)
        now = datetime.datetime.now()
#        print("\n", now.second, ":", now.microsecond, "CONTROLLER", self.queue)
    def Set_ShortInt_Param(self, can_addr, PrmN, Prm):
        can_msg_shortint_param = struct.Struct('=I 6B h')
        сan_msg_shortint_param_data = can_msg_shortint_param.pack(can_addr, 4, 0, 0, 0, PrmN, 2, Prm)
        self.Add_to_queue(сan_msg_shortint_param_data)   
        
### Мотор Контроллер ###
        
class Motor_Controller(Base_Controller):

    def __init__(self, Controller_Number):
        Base_Controller.__init__(self) # Наследуем Base_Device
        self.Controller_Number = Controller_Number 
        self.can_addr = Controller_Number + 0x200
        M1 = Motor(0)
        M2 = Motor(1)
        Motors = [M1, M2]

    def Set_Motor_Speed(self, ParamN, speed):
        self.Set_ShortInt_Param(self.can_addr, ParamN, speed)

    def MotorA(self, speed):
        self.Set_Motor_Speed(0xA, speed)

    def MotorB(self, speed):
        self.Set_Motor_Speed(0xB, speed)

    def Initialize(self, work_mode):      # 1 - рабочий режим
        #self.can_addr = 0x200 
        can_msg_init = struct.Struct('=I 6B')
        can_msg_init_data = can_msg_init.pack(self.can_addr, 2, 0, 0, 0, 200, work_mode)
        self.Add_to_queue(can_msg_init_data)
        time.sleep(1)
        
    def Handler(self, InMsg):
        ParamN = can_msg.unpack(InMsg)[5]      # Изымаем номер полученного параметра
        if ParamN < 13:
            Number = 0
            Motors[Number].Handler(InMsg)
        if (ParamN >= 13) and (ParamN < 26):
            Number = 1
            Motors[Number].Handler(InMsg)
        else:
            pass # тут должен быть парамлист остальных (>26) параметров
            

### Шаговый двигатель Контроллер ###
       
class Stepper_Controller(Base_Controller):        

    def __init__(self, Controller_Number):
        Base_Controller.__init__(self) # Наследуем Base_Device
        self.Controller_Number = Controller_Number
        self.can_addr = Controller_Number + 0x230

    def Set_Stepper_Pos(self, stepperN, steps):
        can_msg_stepper_pos = struct.Struct('=I 6B H')
        can_msg_stepper_pos_data = can_msg_stepper_pos.pack(self.can_addr, 4, 0, 0, 0, 0xCE, stepperN, steps)
        self.Add_to_queue(can_msg_stepper_pos_data)

    def Set_Steppers_Pos(self, steps1, steps2, steps3):
        can_msg_steppers_pos = struct.Struct('=I 5B 3H')
        can_msg_steppers_pos_data = can_msg_steppers_pos.pack(self.can_addr, 7, 0, 0, 0, 0xD0, steps1, steps2, steps3)
        self.Add_to_queue(can_msg_steppers_pos_data)

    def Initialize(self, work_mode):
        work_mode = work_mode+1 # Чтобы ISREADY можно было писать
        self.Init_Stepper(0,work_mode)
        self.Init_Stepper(1,work_mode)
        self.Init_Stepper(2,work_mode)        

    def Calibrate(self):
        self.Calib_Stepper(0)
        self.Calib_Stepper(1)
        self.Calib_Stepper(2)
        
    def Calib_Stepper(self, stepperN):
        can_msg_calib_head = struct.Struct('I 4B B B H')
        can_msg_calib_head_data = can_msg_calib_head.pack(self.can_addr, 4, 0, 0, 0, 0xCF, stepperN, 60)
        self.Add_to_queue(can_msg_calib_head_data)

        
    def Init_Stepper(self, stepperN, work_mode):    # 2 - рабочий режим
        #self.can_addr = 0x230
        can_msg_init = struct.Struct('=I 7B')
        can_msg_init_data = can_msg_init.pack(self.can_addr, 3, 0, 0, 0, 0xC8, stepperN, work_mode)
        self.Add_to_queue(can_msg_init_data)

    def Calib_Axes(self, stepperN):
        can_msg_calib_axes = struct.Struct('=I 6B H')
        can_msg_calib_axes_data = can_msg_calib_axes.pack(self.can_addr, 4, 0, 0, 0, 0xCF, stepperN, 0x3C)
        self.Add_to_queue(can_msg_calib_axes_data)

    def Print_APCHHI(self):
        print("APPCHHI")

  

###### MAIN ######
if __name__ == "__main__":      # Для того чтобы программа не запускалась при её импортирование
    pass
