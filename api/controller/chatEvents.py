from flask_socketio import Namespace, emit, join_room, leave_room
from .. import socketio
from flask_jwt_extended import verify_jwt_in_request,get_jwt_identity
from flask import  request


from api import app, mongo
from api.lib.helper import getId,getPersonName
from datetime import datetime
import uuid
import time
import random 




class Chatbot(Namespace):
    socket = {}
    def __setInit(self):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        self.name = 'Unknown Person'
        self.priority = 0
        self.lastAnswer = ''
        self.__setDayandWeek()
        self.lastReply = datetime.now()
    
    def getUserInfo(self,user_id):
        info = {}
        try: 
            result = mongo.db.miform.find_one({"user_id":user_id})
            #print(result)
            if result:
                info['name'] = result['name']
                info['priority'] = result['priority']
                count = len(result['result'])
                info['lastAnswer'] = result['result'][count-1]['answer']
                
                #print(info)
                return info['name'],info['priority'],info['lastAnswer']
            else:
                r = mongo.db.LAS.find_one({"mobile":int(user_id)})
                fwp = r['fwp']
                mongo.db.miform.insert({'user_id':user_id,'fwp':fwp,'name':self.name,'result':[],'created_at':datetime.now(),'priority':1})
                info['name'] = self.name
                info['priority'] = 1
                info['lastAnswer'] = ''
                return info['name'],info['priority'],info['lastAnswer']
        except:
            info['name'] = self.name
            info['priority'] = 1
            info['lastAnswer'] = ''
            #print(info)
            return info['name'],info['priority'],info['lastAnswer']
        
    
    def getLastBrand(self,user_id):
        try:
            result = mongo.db.miform.find_one({"user_id":user_id})
            #print(result)
            if result:
                return result['brands']
            return ''
        except:
            return ''
        
    def getUser(self):   
        verify_jwt_in_request() 
        return get_jwt_identity()
            
    def on_connect(self):
        try:
            """result = mongo.db.questions3.find().sort([('priority',1)])
            p = 0
            for row in result:
                p = p+1
                del row['_id']
                row['priority'] = p
                mongo.db.questions1.insert(row)"""
                
            self.__setInit()
            user_id = self.getUser()
            name, priority, lastAnswer = self.getUserInfo(user_id)
            #print(request.sid)
            print("You are connected : " + str(user_id))
            join_room(user_id)
            #time.sleep(1)
            
            self.__sendStatus({'type':'Connected','text':"You are connected : " + str(user_id)})
            self.__initMessage()
            self.__sendMessage(user_id)
            pass
        except Exception as e:
            pass
        pass
    
    """def on_reconnect(self):
        try:
            self.__setInit()
            user_id = self.getUser()
            #print(request.sid)
            print("You are Re-connected : " + str(user_id))
            join_room(user_id)
            #time.sleep(1)
            self.__sendStatus({'type':'Connected','text':"You are Re-connected : " + str(user_id)})
            self.__initMessage()
            self.__sendMessage()
            pass
        except Exception as e:
            pass
        pass"""

    def on_disconnect(self):
        try:
            user_id = self.getUser()
            leave_room(user_id)
            self.__sendStatus({'type':'Disconnected','text':"You are disconnected : " + str(user_id)})
            pass
        except Exception as e:
            pass

    
    def on_message(self, data):
        try:
            user_id = self.getUser()
            name, priority, lastAnswer = self.getUserInfo(user_id)
           
            try:
                increment = 1 #prirotiy increment value
               
                # Name recognization
                if priority == 1:
                    name = getPersonName(data['text'].strip())
                    if name.lower() == 'hi' or name.lower() == 'hello':
                        # What's your name?
                        self.__sendMessage(user_id,True)
                        return
                    name = name.capitalize()
                    
                #print(self.lastAnswer)   
                lastAnswer = data['text'].lower() 
                
                if priority == 9:
                    myquery = {"user_id":user_id}
                    newvalues = {"$set":{"brands":[lastAnswer]}}
                    mongo.db.miform.update_one(myquery, newvalues)
                    
                if priority == 12:
                    myquery = {"user_id":user_id}
                    newvalues = {"$push":{"brands":lastAnswer}}
                    mongo.db.miform.update_one(myquery, newvalues)
                    
                
                if priority == 12:
                    if lastAnswer == "this is the only brand i smoke":
                        increment = 2 
                    
                """if priority == 6:
                    if self.dayplan == "Weekday":
                        increment = 2"""
                    
                #Nothing Yes
                """nothing = False
                
                if priority == 11:
                    if lastAnswer.find('nothing') < 0: #Not Nothing
                        increment = 2 
                    else:
                        nothing = True
                        
                reply = None   
                if nothing == False:"""
                
                reply =  self.__getReply(name,priority,data['text'])
                
                #print(data)
               
                myquery = {"user_id":user_id}
                newvalues = {"$set":{"name":name},"$inc": {"priority": int(increment)}, "$addToSet": {"result":{'question':data['question'],"answer":data['text'],"reply":reply,"sent_at":datetime.now()}}}
                mongo.db.miform.update_one(myquery, newvalues)
                
                if reply != None:
                    time.sleep(1)
                    self.__sendReply(reply)
                    #time.sleep(1)
                    
                    
            except Exception as e:
                print("On Message Error1 : " + str(e))
            
            time.sleep(2)
            #self.__sendStatus({'type':'Received','messageId':data['messageId'],'receive_at':str(datetime.now()),'text':'Message Received'})
            self.__sendMessage(user_id)
           
        except Exception as e:
           print("On Message Error : " + str(e))
           pass
    
    def __sendMessage(self,user_id,repleat = False):
        try:
            name, priority, lastAnswer = self.getUserInfo(user_id)
            result = mongo.db.questions1.find_one({'priority':priority})
            #print(name,priority,lastAnswer,result)
            messageId = str(uuid.uuid4())
            
            currentDT = datetime.now()
            sent_at = currentDT.strftime("%I:%M %p")
            
            data = {}
            if result:
                #result.pop('_id') 
                result['_id'] = str(result['_id'])
                options = []
                lastNode = []
                brands = []
                
                #check and get Last brand
                if priority == 12 or priority == 15:
                    brands = self.getLastBrand(user_id)
                    
                    
                for row in result['options']:
                    image = row.strip().lower().replace(' ','_').replace('/','_')
                    
                    if (result['type'] == 'MCQ9' or result['type'] == 'MCQ12') and image == 'any_other':
                        image = 'product_'+image
                    
                    if priority == 12 or priority == 15: 
                        #print("Send :", priority,row.lower(),brands)
                        if row.lower() not in brands:
                            options.append({'name':row,'image':image})
                    else:     
                        options.append({'name':row,'image':image})
                
                
                    
                    #print(options)
                result['options'] = options
               
                result['label'] = result['label'].replace("{name}",name)
                result['label'] = result['label'].replace("{day}",self.day)
                result['label'] = result['label'].replace("{dayplan}",self.dayplan)
                
                if priority == 1 and repleat:
                    result['label'] = "What's your name?"
                
                data = {'messageId':messageId,'type':'in','priority':priority,'question':result,'sent_at':str(sent_at)+', Today'}
            else:
                default_data = {
                    "label" : "Thank you "+name+" for your time. It was great to meet you. Wish you all the best in your endeavours.",
                    "type" : "CLOSE",
                    "priority" :0,
                    "status" : 1
                }
                data = {'messageId':messageId,'type':'in','priority':0,'question':default_data,'sent_at':str(sent_at)+', Today'}
                #For Testing purpose we are deliting data
                #mongo.db.miform.update_one({"user_id":user_id}, {"$set":{"priority":1,'result':[]}})
            #print(data)
            emit('message',data,room=user_id)   
        except Exception as e:
            print("Error : ",str(e))
            pass   
    
    def on_status(self, data):
        try:
            user_id = self.getUser()
            print(data)
        except Exception as e:
            print(e)
            pass
            
    def __sendStatus(self,data):
        user_id = self.getUser()
        emit('status',data,room=user_id)
     
    
            
    
    
    
    def getPriority(self):
        try:    
            user_id = self.getUser()
            result = mongo.db.miform.find_one({"user_id":user_id})
            #print(result)
            if result:
                myquery = {"user_id":user_id}
                newvalues = {"$inc": {"priority": int(1)} }
                #mongo.db.miform.update_one(myquery, newvalues)
                #self.priority = result['priority'];
                return result['priority'];
            else:
                mongo.db.miform.insert({'user_id':user_id,'name':self.name,'result':[],'created_at':datetime.now(),'priority':1})
                return 1
        except:
            return 1

    
    
    
    def __initMessage(self):
        #priority = self.getPriority();
        priority = 0
        try:
            user_id = self.getUser()
            questions = {}
            result = mongo.db.questions1.find()
            for row in result:
                row['_id'] = str(row['_id'])
                questions[str(row['_id'])] = row
                
            
            result = mongo.db.miform.find_one({"user_id":user_id})
            
            if result:
                name = result['name'].capitalize()
                
                #print(result)
                brands = []
                if 'brands' in result:
                    brands = result['brands']
                
                for row in result['result']:
                    messageId = str(uuid.uuid4())
                    #priority = priority + 1
                    
                    currentDT = datetime.now()
                    sent_at = currentDT.strftime("%I:%M %p")
                   
                    t = questions[row['question']]
                    priority = t['priority']
                    
                    options = []
                    firstNode = []
                    
                    
                    for row1 in t['options']:
                        image = row1.strip().lower().replace(' ','_').replace('/','_')
                        
                        if (t['type'] == 'MCQ9' or t['type'] == 'MCQ12') and image == 'any_other':
                            image = 'product_'+image
                        
                        if priority == 12 or priority == 15: 
                            #print("INIT : ", priority,row1.lower(),brands)
                            if row['answer'] == row1:
                                options.append({'name':row1,'image':image})
                            elif row1.lower() not in brands:
                                options.append({'name':row1,'image':image})
                        else:     
                            options.append({'name':row1,'image':image})
                        
                        
                    
                    t['options'] = options
                    
                    t['label'] = t['label'].replace("{name}",name)
                    t['label'] = t['label'].replace("{day}",self.day).replace("{dayplan}",self.dayplan)
                    
                    #Message text
                    data = {'messageId':messageId,'type':'in','priority':priority,'question':t,'sent_at':str(sent_at)+', Today'}
                    emit('initMessage',data,room=user_id)
                    
                    #print(data)
                    
                    #print(data)
                    #User Reply
                    
                    #print(row['answer'])
                    data1 = {'messageId':messageId,'type':'out','answer':row['answer'],'question':t,'sent_at':str(sent_at)+', Today'}
                    emit('initMessage',data1,room=user_id)
                    #self.lastAnswer = row['answer'].lower()
                    #print(data1)
                    
                    #server Auto Reply text
                    if row['reply'] != None:
                        default_data = {
                            "label" : row['reply'].replace("{name}",name),
                            "type" : "OPEN",
                            "priority" :0,
                            "status" : 1
                        }
                        data = {'messageId':messageId,'type':'reply','priority':0,'question':default_data,'sent_at':str(sent_at)+', Today'}
                        emit('message',data,room=user_id)
                        
                        #print(data)
                        
                    #print(data)
        except Exception as e:
            print(e)
            pass
    
    
    def __sendReply(self,reply):
        try:
            user_id = self.getUser()
            messageId = str(uuid.uuid4())
            currentDT = datetime.now()
            sent_at = currentDT.strftime("%I:%M %p")
            
            default_data = {
                "label" : reply,
                "type" : "REPLY",
                "priority" :0,
                "status" : 1
            }
            data = {'messageId':messageId,'type':'reply','priority':0,'question':default_data,'sent_at':str(sent_at)+', Today'}
            emit('message',data,room=user_id)
        except:
            pass
                    
    def __getReply(self,name,priority,answer = ''):
        try:
            
            if priority == 8:
                return self.__getHangoutReply(answer)
            if priority == 9:
                r = self.__getBrandReply(answer)
                if r:
                    return r
            
            
            result = mongo.db.questions1.find_one({'priority':priority})
            data = {}
            template = None
           # print(answer)
            
            if result:
                templates = result['templates']
                templates1 = result['templates1']
                #print(templates1)
                if len(templates) > 0:
                    if len(templates) == 1:
                        template = templates[0]
                    else:
                        r1 = random.randrange(0,len(templates) - 1) 
                        template = templates[r1]
                    template = template.replace("{name}",name)
                    
                else:
                    if answer in templates1:
                        template = templates1[answer]
                        template = template.replace("{name}",name)
                    elif 'Any Other' in templates1:
                        template = templates1['Any Other']
                        template = template.replace("{name}",name)
                        
                        
                    
            return template
        except:
            return []
    
    def __setDayandWeek(self):
        date = datetime.today()
        weekno = date.weekday()
        
        self.day = date.strftime("%A")

        if weekno<5:
            self.dayplan = "Weekday"
        else:
            self.dayplan = "Weekend"
    
    
    
    
    def __getHangoutReply(self,answer):
        data = answer.split(' ')
        #print(data)
      
        option1 = "Ah, a great way to unwind after busy weekdays 🕺🏻."
        option2 = "Nothing like getting your favourite food in peace ☕️."
        option3 = "Nice. That's a great way to rejuvinate 🏃‍♂️. "
        option4 = "That's great! I should pick up a few books myself 📚 ."
        option5 = "Well, retail therapy is the best. Isnt it?! 🎁 "
        option6 = "Cool, noted. 😄"
        
        key = {'pubs':option1,'clubs':option1,'bars':option1,'party':option1,
               'cafes':option2,'restaurants':option2,'hotels':option2,'coffee':option2,
               'parks':option3,'gardens':option3,
               'book':option4,'books':option4,'cafes':option4,'libraries':option4,'bookshops':option4,
               'markets':option5,'malls':option5,'shopping':option5,'centers':option5}
        #print(key)
        
        """new_dict = {k: v for k in data if k in key}
        print(new_dict)"""
        
        for k in data:
            k = k.lower().replace(",","")
            
            if k in key:
                return key[k]
            elif k+"s" in key:
                return key[k+"s"]
        return option6
    
    def __getBrandReply(self,answer):
        data = answer.split(' ')
        
        options = "Okay.","Oh, I see","Thanks for your answer.","Thanks.","Hmm, interesting 🤔."


        key = {'marlboro':True,'parliament':True}
       
        for k in data:
            k = k.lower().replace(",","")
            if k in key:
                return "Hmm, interesting 🤔."
        return False
        
   
        
socketio.on_namespace(Chatbot())


  