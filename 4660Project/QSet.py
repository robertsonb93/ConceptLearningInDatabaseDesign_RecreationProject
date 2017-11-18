import random as rand
import time as time
class QSet(object):
    #Used to generate a list of Queries, the ordering of the list will be dependant on the type asked for
    #  All queries use random generation for their placeholder values
    #  The return on a query is not actually in query form, but as a feature vector
    #  Each query is of one or more atoms where an atom is (attribute,operation,value), these go into our feature vectors
    #  Attribute : the name of an attribute of a relation
    #  Operation : is a comparison operator from the set  { = , < > , <= , >= }. Note that < > stands for inequality
    #  Value : is either a constant that is type-compatible with Attribute, or the name of an attribute with which Attribute can be joined
    #   Each feature vector is a list (for each atom) inside our list of queries

    #Note that join is represented as 2 atoms where when a join b is done, its (a=b)(b=a)
    #Note that select is represented as a question mark ?, and the op is blank #see page 273,274 (section 2.4)


    #Database design
    #ACCOUNT (actno, bal, cust—name) 
    #TRANSACTION (tno, type, bal_change, tactno, tatmno) ... tactno is transaction of acount, tatmno is transaction of atm 
    #CUSTOMER (ssno, name, age, street, city, num_kids, married) 
    #ATM (atmno, num_trans, location, disabled_ time)


    #This is from the paper, as they said they had 1000 queries per set, with each query getting equal copies, ceil(1000/13) = 77, #note that 77*13 = 1001
    numSamplesGenerate = 77 
    querySet = list()
       
    #Query1 : Balance of account x
    #ACCOUNT (actno, bal, cust—narne) 
    def _genQuery1(self):
        rand.seed(time.time())
        ret = list()
            
        for i in range(self.numSamplesGenerate):

            #Find the account
            featureVec = list()
            attribute = "actno"
            operation = "="
            value = rand.randint(1000,1100) #These are magic, but i figured its a healthy range for the RNG
            featureVec += [[attribute,operation,value]]
                
            #Find the bal 
            attribute = "bal"
            operation = ""
            value = "?"
            featureVec += [[attribute,operation,value]]

            #Add the featureVec to the return list
            ret += [featureVec]

        return ret


    #Transactions of account of customer x
    #TRANSACTION (tno, type, bal_change, tactno, tatmno) 
    #ACCOUNT (actno, bal, cust_name) 
    def _genQuery2(self):
        rand.seed(time.time())
        ret = list()
        for i in range(self.numSamplesGenerate):
            featureVec = list()

            #find Customer x
            attribute = "cust_name"
            operation = "="
            nameLen = rand.randint(3,10) #Choose a random name length
            value = ""
            for i in range(nameLen):
                value += chr(rand.randint(65,90)) #choose a random uppercase letter
            featureVec += [[attribute, operation,value]]

            #Find transactions matching the account number , a Join
            attribute = "tactno"
            operation = "="
            value = "actno"
            featureVec +=[[attribute,operation,value]]
            attribute = "actno"
            operation ="="
            value = "tactno"
            featureVec +=[[attribute,operation,value]]

            ret += [featureVec]

        return ret


    #Address, SSN, transactions of account of customer x
    #Almost the same as query2
    #CUSTOMER (ssno, name, age, street, city, num_kids, married)
    #TRANSACTION (tno, type, bal_change, tactno, tatmno) 
    #ACCOUNT (actno, bal, cust_name) 
    def _genQuery3(self):
        rand.seed(time.time())
        ret = list()
        for i in range(self.numSamplesGenerate):
            featureVec = list()
                
            #find Customer x
            name = ""
            attribute = "cust_name"
            operation = "="
            nameLen = rand.randint(3,10) #Choose a random name length
            for i in range(nameLen):
                name += chr(rand.randint(65,90)) #choose a random uppercase letter
            value = name
            featureVec += [[attribute, operation,value]]

            #Join on transactions with matching account numbers
            attribute = "tactno"
            operation = "="
            value = "actno"
            featureVec += [[attribute,operation,value]]
            attribute = "actno"
            operation = "="
            value = "tactno"
            featureVec += [[attribute,operation,value]]


            #Find the Customer by name now 
            attribute = "name"
            operation = "="
            value = name #from the above find customer x
            featureVec += [[attribute,operation,value]]

            #get the SSNO
            attribute = "ssno"
            operation = ""
            value = "?"
            featureVec += [[attribute,operation,value]]

            #get the address
            attribute = "street"
            operation = ""
            value = "?"
            featureVec +=[[attribute,operation,value]]

            ret += [featureVec]
        return ret

    #customers with withdrawals of more than x
    #TRANSACTION (tno, type, bal_change, tactno, tatmno)
    #ACCOUNT (actno, bal, cust_name)
    #CUSTOMER (ssno, name, age, street, city, num_kids, married)
    def _genQuery4(self):
        rand.seed(time.time())
        ret = list()
        for i in range(self.numSamplesGenerate):
            featureVec = list()

            #Get withdrawals of more than x, we dont have strictly greater then, so add a 1 to x, but we are using RNG, so it doesnt matter anyways.
            attribute = "bal_change"
            operation = "<="
            value = rand.randint(-100,0)
            featureVec += [[attribute,operation,value]]

            #get the matching account, this is a join
            attribute = "actno"
            operation = "="
            value = "tactno"
            featureVec += [[attribute,operation,value]]
            attribute = "tactno"
            operation = "="
            value = "actno"
            featureVec += [[attribute,operation,value]]
                
            #get the customer now, this is a join
            attribute = "name"
            operation = "="
            value = "cust_name"
            featureVec += [[attribute,operation,value]]
            attribute = "cust_name"
            operation = "="
            value = "name"
            featureVec += [[attribute,operation,value]]

            ret += [featureVec]
        return ret

    #customers with withdrawals between x and y
    #TRANSACTION (tno, type, bal_change, tactno, tatmno)
    #ACCOUNT (actno, bal, cust_name)
    #CUSTOMER (ssno, name, age, street, city, num_kids, married)
    def _genQuery5(self):
        rand.seed(time.time())
        ret = list()
        for i in range(self.numSamplesGenerate):
            featureVec = list()

            #Find all that are greater then x
            attribute = "bal_change"
            operation = "<="
            minValue = rand.randint(-100,0)
            featureVec += [[attribute,operation,minValue]]
               
            #Find those that are then less then y
            attribute ="bal_change"
            operation = "<="
            maxValue = rand.randint(minValue,0)
            featureVec += [[attribute,operation,maxValue]]

            #get the matching account, this is a join
            attribute = "actno"
            operation = "="
            value = "tactno"
            featureVec += [[attribute,operation,value]]
            attribute = "tactno"
            operation = "="
            value = "actno"
            featureVec += [[attribute,operation,value]]
                
            #get the customer now, this is a join
            attribute = "name"
            operation = "="
            value = "cust_name"
            featureVec += [[attribute,operation,value]]
            attribute = "cust_name"
            operation = "="
            value = "name"
            featureVec += [[attribute,operation,value]]

            ret += [featureVec]
        return ret

    #Customers with account balances of more than x
    #ACCOUNT (actno, bal, cust_name)
    #CUSTOMER (ssno, name, age, street, city, num_kids, married)
    def _genQuery6(self):
        rand.seed(time.time())
        ret = list()
        for i in range(self.numSamplesGenerate):
            featureVec = list()

            #Find all accounts balances greater then x
            attr = "bal"
            op = ">=" 
            value = rand.randint(0,100)#1million
            featureVec += [[attr,op,value]]

            #Find the customers now, a join
            attr = "name"
            op = "="
            value = "cust_name"
            featureVec += [[attr,op,value]]
            attr = "cust_name"
            op = "="
            value = "name"
            featureVec += [[attr,op,value]]

            ret += [featureVec]
        return ret
        
    #Age of customers with accounts whose balance is greater than x
    #ACCOUNT (actno, bal, cust_name)
    #CUSTOMER (ssno, name, age, street, city, num_kids, married)
    def _genQuery7(self):
        rand.seed(time.time())
        ret = list()
        for i in range(self.numSamplesGenerate):
            featureVec = list()

            #Find all accounts balanaces greater then x
            attr = "bal"
            op = ">=" 
            value = rand.randint(0,100)#1million
            featureVec += [[attr,op,value]]

            #Find the customers now, This is a join
            attr = "name"
            op = "="
            value = "cust_name"
            featureVec += [[attr,op,value]]
            attr = "cust_name"
            op = "="
            value = "name"
            featureVec += [[attr,op,value]]

            #find the age
            attr = "age"
            op = ""
            value = "?"
            featureVec += [[attr,op,value]]

            ret += [featureVec]
        return ret

    #SSNO of customers with accounts whose balance is greater than x
    #ACCOUNT (actno, bal, cust_name)
    #CUSTOMER (ssno, name, age, street, city, num_kids, married)
    def _genQuery8(self):
        rand.seed(time.time())
        ret = list()
        for i in range(self.numSamplesGenerate):
            featureVec = list()

            #Find all accounts balanaces greater then x
            attr = "bal"
            op = ">=" 
            value = rand.randint(0,100)#1million
            featureVec += [[attr,op,value]]

            #Find the customers now, This is a join
            attr = "name"
            op = "="
            value = "cust_name"
            featureVec += [[attr,op,value]]
            attr = "cust_name"
            op = "="
            value = "name"
            featureVec += [[attr,op,value]]

            #find the SSNO
            attr = "SSNO"
            op = ""
            value = "?"
            featureVec += [[attr,op,value]]

            ret += [featureVec]
        return ret

    #Marital status of customers with accounts who balance is greater than x
    #ACCOUNT (actno, bal, cust_name)
    #CUSTOMER (ssno, name, age, street, city, num_kids, married)
    def _genQuery9(self):
        rand.seed(time.time())
        ret = list()
        for i in range(self.numSamplesGenerate):
            featureVec = list()
            #Find all accounts balanaces greater then x
            attr = "bal"
            op = ">=" 
            value = rand.randint(0,100)
            featureVec += [[attr,op,value]]

            #Find the customers now, This is a join
            attr = "name"
            op = "="
            value = "cust_name"
            featureVec += [[attr,op,value]]
            attr = "cust_name"
            op = "="
            value = "name"
            featureVec += [[attr,op,value]]

            #find the MarriageStatus
            attr = "married"
            op = ""
            value = "?"
            featureVec += [[attr,op,value]]

            ret += [featureVec]
        return ret

    #ATMS with transactions on accounts who balance is greater than x
    def _genQuery10(self):
        rand.seed(time.time())
        ret = list()
        for i in range(self.numSamplesGenerate):
            featureVec = list()

            #Find all accounts balanaces greater then x
            attr = "bal"
            op = ">=" 
            value = rand.randint(0,100)#1million
            featureVec += [[attr,op,value]]

            #Find the transactions on those accounts, join
            attr = "tactno"
            op = "="
            value = "actno"
            featureVec += [[attr,op,value]]
            attr = "actno"
            op = "="
            value = "tactno"
            featureVec += [[attr,op,value]]

            #find the ATMS, join
            attr = "atmno"
            op = "="
            value = "tatmno"
            featureVec += [[attr,op,value]]
            attr = "tatmno"
            op = "="
            value = "atmno"
            featureVec += [[attr,op,value]]

            ret += [featureVec]
        return ret

    #Disabled times of ATMs with transactions on accounts whose balance is greater than x
        #ATM (atmno, num_trans, location, disabled_ time)
    def _genQuery11(self):
        rand.seed(time.time())
        ret = list()
        for i in range(self.numSamplesGenerate):
            featureVec = list()

            #Find all accounts balanaces greater then x
            attr = "bal"
            op = ">=" 
            value = rand.randint(0,100)
            featureVec += [[attr,op,value]]

            #Find the transactions on those accounts, join
            attr = "tactno"
            op = "="
            value = "actno"
            featureVec += [[attr,op,value]]
            attr = "actno"
            op = "="
            value = "tactno"
            featureVec += [[attr,op,value]]

            #find the ATMS, join
            attr = "atmno"
            op = "="
            value = "tatmno"
            featureVec += [[attr,op,value]]
            attr = "tatmno"
            op = "="
            value = "atmno"
            featureVec += [[attr,op,value]]

            #find the Disabled times
            attr = "disabled_time"
            op = ""
            value = "?"
            featureVec += [[attr,op,value]]

            ret += [featureVec]
        return ret    

    #Number of transactions and disabled times of ATMS with transactions on accounts whose balance is greater than x
    def _genQuery12(self):
        rand.seed(time.time())
        ret = list()
        for i in range(self.numSamplesGenerate):
            featureVec = list()

            #Find all accounts balanaces greater then x
            attr = "bal"
            op = ">=" 
            value = rand.randint(0,100)
            featureVec += [[attr,op,value]]

            #Find the transactions on those accounts, join
            attr = "tactno"
            op = "="
            value = "actno"
            featureVec += [[attr,op,value]]
            attr = "tactno"
            op = "="
            value = "actno"
            featureVec += [[attr,op,value]]

            #find the ATMS, join
            attr = "atmno"
            op = "="
            value = "tatmno"
            featureVec += [[attr,op,value]]
            attr = "tatmno"
            op = "="
            value = "atmno"
            featureVec += [[attr,op,value]]

            #find the Disabled times
            attr = "disabled_time"
            op = ""
            value = "?"
            featureVec += [[attr,op,value]]

            #find the number of transactions
            attr = "num_trans"
            op = ""
            value = "?"
            featureVec += [[attr,op,value]]

            ret += [featureVec]
        return ret    

    #Balance of customers with more than x kids
    #ACCOUNT (actno, bal, cust—name) 
    #CUSTOMER (ssno, name, age, street, city, num_kids, married) 
    def _genQuery13(self):
        rand.seed(time.time())
        ret = list()
        for i in range(self.numSamplesGenerate):
            featureVec = list()

            #Find the customers with more than x kids
            attr = "num_kids"
            op  = ">="
            value = rand.randint(0,10)
            featureVec += [[attr,op,value]]

            #Join on names 
            attr = "cust_names"
            op = "="
            value = "name"
            featureVec += [[attr,op,value]]
            attr = "names"
            op = "="
            value = "cust_name"
            featureVec += [[attr,op,value]]

            #find the blaances
            attr = "bal"
            op = ""
            value = "?"
            featureVec += [[attr,op,value]]
            ret += [featureVec]
        return ret



    #our Query selection is batched together
    def _genOption1(self):
        ret = self._genQuery1()
        ret += self._genQuery2()
        ret += self._genQuery3()
        ret += self._genQuery4()
        ret += self._genQuery5()
        ret += self._genQuery6()
        ret += self._genQuery7()
        ret += self._genQuery8()
        ret += self._genQuery9()
        ret += self._genQuery10()
        ret += self._genQuery11()
        ret += self._genQuery12()
        ret += self._genQuery13()
        return ret

    #Our query selection is cyclic
    def _genOption2(self):
        ret = list(13 *[None])#initial sizing
        ret[0] = self._genQuery1()
        ret[1] = self._genQuery2()
        ret[2] = self._genQuery3()
        ret[3] = self._genQuery4()
        ret[4] = self._genQuery5()
        ret[5] = self._genQuery6()
        ret[6] = self._genQuery7()
        ret[7] = self._genQuery8()
        ret[8] = self._genQuery9()
        ret[9] = self._genQuery10()
        ret[10] = self._genQuery11()
        ret[11] = self._genQuery12()
        ret[12] = self._genQuery13()

        actualRet = list(1001 *[None])
        i=0
        for j in range(self.numSamplesGenerate):
            for k in range(13):
                actualRet[i] = ret[k][j]
                i += 1
        return actualRet

    #Randomly shuffle our queries
    def _genOption3(self):
        ret = self._genQuery1()
        ret += self._genQuery2()
        ret += self._genQuery3()
        ret += self._genQuery4()
        ret += self._genQuery5()
        ret += self._genQuery6()
        ret += self._genQuery7()
        ret += self._genQuery8()
        ret += self._genQuery9()
        ret += self._genQuery10()
        ret += self._genQuery11()
        ret += self._genQuery12()
        ret += self._genQuery13()
        rand.shuffle(ret)
        return ret


    #Use to Generate the set, and then set the
    #  1 :the queries 1-13 have all the their queries in groups, ie, if there are 77 examples of query 1, then they are indices 0-76
    #  2 :provide with cycles of queries 1-13, ie, indices 0, 13, 26,39.... will be query 1, while indices 1,14,27... = query 2
    #  3 :randomly thrown in there.
    def GenerateSet(self,option):
        if (option == 1):
            self.querySet = self._genOption1()
        elif(option == 2):
            self.querySet = self._genOption2()
        elif (option == 3):
            self.querySet = self._genOption3()

