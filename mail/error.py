class GroupChatException(Exception):
    def __init__(self, *args):
        if args:
            self.__message=args[0]
        else:
            self.__message=None

    def __str__(self):
        if self.__message:
            return "GroupChatException: {0}".format(self.__message)
        else:
            return "A GroupChatException occured"

if __name__ == '__main__':
    raise GroupChatException("A problem")