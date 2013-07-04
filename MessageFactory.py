import json

class MessageFactory():

    @staticmethod
    def get_message(jsonMessage):
        messageObject = json.loads(jsonMessage)
        if messageObject['message'] == 'start':
            return StartMessage()
        elif messageObject['message'] == 'stop':
            return StopMessage()
        elif messageObject['message'] == 'addSteps':
            addStepsMessage = AddStepsMessage()
            addStepsMessage.payload = messageObject['payload']
            return addStepsMessage
        elif messageObject['message'] == 'removeSteps':
            return RemoveStepsMessage()

# Message Interface
class Message(object):
    payload = ''
    def processMessage(self, objectContext):
        pass
    
# Message Interface
class StartMessage(Message):
    def processMessage(self, objectContext):
        objectContext.thread.start()
        print('processing start')

class StopMessage(Message):
    def processMessage(self, objectContext):
        objectContext.thread.stop()
        print('processing stop')

class AddStepsMessage(Message):
    def processMessage(self, objectContext):
        print('processing add')
        objectContext.stepTemperature = self.payload['Temperature']

class RemoveStepsMessage(Message):
    def processMessage(self, objectContext):
        print('processing remove')


