## Мотор ##

class Motor():

    def __init__(self, Number):
        self.Number = Number
        Motor_Param_List = []
        for i in range(13): # Один мотор хранит в себе 13 параметров
            prm = 0
            Motor_Param_List.append(prm)

    def Handler(self, InMsg):  # Обработчик принимаемых параметров
        ParamN = can_msg.unpack(InMsg)[5]      # Изымаем номер полученного параметра
        ParamN = ParamN - self.Number*13       # Обрабатываем номера параметров     
        ### Тут нужно написать обработчик сообщения, определяющий длину информационного поля параметра и его тип
        Motor_Param_List[ParamN] = can_msg.unpack(InMsg)[7]
