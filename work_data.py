import pandas as pd
import datetime as dt

# This class if to work with the hours of shedules
class Hour:
    def __init__(self) -> None:
        pass
    @staticmethod
    def order_hours(str):
        new_str = list(map(lambda x: x.split("/"),str.split("-")))

        try_order = True
        while (try_order):
            try_order = False
            for i in range(len(new_str)-1):
                if (int(new_str[i][0])>int(new_str[i+1][0])):
                    # Change
                    new_str[i], new_str[i+1] = new_str[i+1], new_str[i] 
                    try_order = True

        new_str = "-".join(list(map(lambda x: f"{x[0]}/{x[1]}", new_str)))

        return new_str

    @staticmethod
    def add_hour(str, new_hour):
        if (str=="" and new_hour!=""):
            return new_hour
        elif (str!="" and new_hour==""):
            return str
        elif (str=="" and new_hour==""):
            return ""
        return Hour.order_hours(f"{str}-{new_hour}")

    @staticmethod
    def to_list(str):
        return list(map(lambda x: x.split("/"),str.split("-")))

    #Simplify schedules to one
    @staticmethod
    def reduce(list_data):
        new_list = [[] for i in range(6)]
        
        for data in list_data:
            for day in range(6):
                new_list[day].append(data[day])

        for j,day in enumerate(new_list):
            hours = ""
            for i in day:
                hours = Hour.add_hour(hours, i)
            new_list[j] = hours

        return new_list

#Work with data
class Data_Cleaned:
    def __init__(self) -> None:
        self.generate_data()
        
    def generate_data(self):
        self.days = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5}
        # Initialize data
        df = pd.read_csv("Data-test.csv")
        classroom = df["Classroom"].to_list()
        shedule = df["Shedule"].to_list()

        new_shedule = []
        for i in shedule:
            shedule_n = i[1:-1]
            shedule_n = shedule_n.split(",")

            shedule_n = list(map(lambda x: x.split("'")[1] if x.strip()!="''" else "", shedule_n))
            new_shedule.append(shedule_n)
        shedule = new_shedule

        # clean

        classroom = list(map(lambda x: str(x).split(","), classroom))

        self.query_classroom = {}
        for section in range(len(classroom)):
            # Clean classroom 
            sections_with_classroom = {}
            # Posible shedule count

            count_shedule = sum(map(lambda x: 1 if x!="" else 0,shedule[section]))
            
            #Delete the spaces after and before of the string
            classroom[section] = list(map(lambda x: x.strip(), classroom[section]))
            
            # Comprobation if is a VIRTU
            section_is_virtual = False
            if ("VIRTU" in classroom[section] and count_shedule!=len(classroom[section]) and count_shedule!=1):
                section_is_virtual = True


            # If it isn't virtual append each shedule to classroom
            # Second condition is for the hybrid classes
            if ((section_is_virtual and (count_shedule<len(classroom[section]) or count_shedule>len(classroom[section]))) or len(classroom[section])==1):
                count_section = 0 
                
                name_classroom = classroom[section][count_section]
                
                for i in range(len(shedule[section])):
                    if (shedule[section][i]!=""):
                        list_shedule = ["" for j in range(6)]
                        list_shedule[i] = shedule[section][i]
                        

                        ##APPEND DATA TO QUERY
                        actual_data = self.query_classroom.get(name_classroom, [])
                        actual_data.append(list_shedule)
                        if (name_classroom!="VIRTU"):
                            self.query_classroom[name_classroom] = actual_data

            elif ((len(classroom[section])!=count_shedule and not section_is_virtual) or ("VIRTU" in classroom[section] and (count_shedule==len(classroom[section])))):
                for name_classroom in classroom[section]:
                    
                    for i in range(len(shedule[section])):
                        if (shedule[section][i]!=""):
                            list_shedule = ["" for j in range(6)]
                            list_shedule[i] = shedule[section][i]
                            ##APPEND DATA TO QUERY
                            actual_data = self.query_classroom.get(name_classroom, [])
                            actual_data.append(list_shedule)


                            if (name_classroom!="VIRTU"):
                                self.query_classroom[name_classroom] = actual_data    
            else:
                count_section = -1
                
                for i in range(len(shedule[section])):
                    if (shedule[section][i]!=""):  
                        list_shedule = ["" for j in range(6)]   
                        count_section += 1   
                        
                        name_classroom = classroom[section][count_section]        
                        list_shedule[i] = shedule[section][i]

                        sections_with_classroom[name_classroom] = list_shedule
                        
                        ##APPEND DATA TO QUERY
                        actual_data = self.query_classroom.get(name_classroom, [])
                        actual_data.append(list_shedule)
                        if (name_classroom!="VIRTU"):
                            self.query_classroom[name_classroom] = actual_data
        # Clean shedule
        for key,value in self.query_classroom.items():
            self.query_classroom[key] = Hour.reduce(self.query_classroom[key])

    def comprobate_classroom(self, day, hour, classroom):
        classroom = list(map(lambda x: Hour.to_list(x),classroom))
        available = True
        for data in classroom[self.days[day]]:
            if (data[0]!=""):
                a,b = int(data[0]), int(data[1])
                # Verify intervals
                if (hour>=a and hour<b):
                    available = False
                    break
        return available

    # Comprobate if there are more clases on that day
    def next_hours(self, day, hour, classroom, hour_indicated=None):
        result = False
        for i, next_hour in enumerate(Hour.to_list(self.query_classroom[classroom][self.days[day]])):
            if hour_indicated==None:
                if (next_hour[0]!=""):
                    if (int(hour)<int(next_hour[0])):
                        result = True
            else:
                result = True
                if (next_hour[0]!=""):
                    if (int(hour)<int(next_hour[0]) and hour_indicated>=int(next_hour[1])):
                        # print(classroom)
                        # print(next_hour)
                        result = False
                        break
        return result

# Return true if there aren't an hour before of the parameter
    def before_hours(self, day, hour, classroom):
        result = True
        for i, next_hour in enumerate(Hour.to_list(self.query_classroom[classroom][self.days[day]])):
            if (next_hour[0]!=''):
                # print(next_hour)
                if (int(hour)>int(next_hour[0])):
                    result = False
                    break
        return result

    # Comprobate: it is to use the next_hours function
    def classroom_availables(self, day,hour, area:str=None, comprobate=None, until=None, comprobate_before=None):
        available = []
        for room, shedule in self.query_classroom.items():
            try:
                if (room!="VIRTU" and (room.startswith(area) if area!=None else True)):
                    if (self.comprobate_classroom(day,hour,shedule) and room[-1].isnumeric()):
                        
                        # Comprobate next hours
                        if (comprobate!=None or until!=None or comprobate_before!=None):
                            add_class = True
                            ## Checks are done here
                            if (comprobate_before==True and self.before_hours(day,hour,room)):
                                add_class = False
                            
                            if (not self.next_hours(day,hour,room, hour_indicated=until)):
                                add_class = False
                            
                            # Add or not
                            if (add_class):
                                available.append(room)
                        else:
                            available.append(room)
            except:
                pass
                # print(room)
        # print(f"ava: {available}")
        return available

# # # Comprobate hour
# classroom = Data_Cleaned()
# day = "Monday"
# hour = 12
# area = "GC"
# a = classroom.classroom_availables(day, hour,area=area)
# # a = classroom.classroom_availables(day=day, hour=hour, area=area, comprobate=True, until=20, comprobate_before=None)
# print(a)

# for i in a:
#     print(not classroom.before_hours(day,hour,i))
#     print(f"{i}: {(classroom.query_classroom[i][0])}")

# a = classroom.classroom_availables(day, hour,area=area, comprobate_before=True)
# print(a)