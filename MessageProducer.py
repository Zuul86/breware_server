class MessageProducerFactory:

    @staticmethod
    def get_message(messageType):
        if (messageType == 'addsteps'):
            return StepsMessage()
        elif (messageType == 'state_change'):
            return StateChangeMessage()
        elif (messageType == 'send_temperature'):
            return TemperatureMessage()
            
class Message(object):

    def produceMessage(self, objectContext):
        pass
        
class StepsMessage(Message):

    def produceMessage(self, objectContext):
        localTemp = str(objectContext.stepTemperature)
        localDuration = str(objectContext.stepDuration)
        message = '{"Message":"Steps", "Payload":[{"Temperature":"' + localTemp + '","Duration":"' + localDuration + '"}]}'
        objectContext.write_message(message)
        
class StateChangeMessage(Message):
    
    def produceMessage(self, objectContext):
        state = str(objectContext.state)
        message = '{"Message":"StateChanged", "Payload":{"State":"' + state + '"}}'
        objectContext.write_message(message)
        
class TemperatureMessage(Message):

    def produceMessage(self, objectContext):
        temperature = str(objectContext.currentTemperature)
        message = '{"Message":"CurrentTemperature", "Payload":{"Temperature":"' + temperature + '"}}'
        objectContext.write_message(message)