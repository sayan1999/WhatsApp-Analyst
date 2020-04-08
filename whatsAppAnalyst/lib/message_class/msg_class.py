class Msg:

    def __init__(self, msg=""):
        self.__messages=[]
        if msg != "":
            self.__messages+=msg

    def new_msg(self, msg):
        self.__messages.append(msg)

    def get_msg(self):
        return self.__messages